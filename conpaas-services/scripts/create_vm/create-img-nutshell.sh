#!/bin/bash -e
# Copyright (c) 2010-2012, Contrail consortium.
# All rights reserved.
#
# Redistribution and use in source and binary forms, 
# with or without modification, are permitted provided
# that the following conditions are met:
#
#  1. Redistributions of source code must retain the
#     above copyright notice, this list of conditions
#     and the following disclaimer.
#  2. Redistributions in binary form must reproduce
#     the above copyright notice, this list of 
#     conditions and the following disclaimer in the
#     documentation and/or other materials provided
#     with the distribution.
#  3. Neither the name of the Contrail consortium nor the
#     names of its contributors may be used to endorse
#     or promote products derived from this software 
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

##
# THIS SCRIPT HAS BEEN __GENERATED__ from the configuration file 'create-img-script.cfg'
# running command 'python create-img-script.py'.
#
# This script generates a VM image for ConPaaS, to be used for OpenNebula with KVM.
# The script should be run on a Debian or Ubuntu system.
# Before running this script, please make sure that you have the following
# executables in your $PATH:
#
# dd parted losetup kpartx mkfs.ext3 tune2fs mount debootstrap chroot umount grub-install (grub2)
# 
# NOTE: This script requires the installation of Grub 2 (we recommend Grub 1.98 or newer,
# as we experienced problems with 1.96). 
##

#########################
export LC_ALL=C

# Function for displaying highlighted messages.
function cecho() {
  echo -en "\033[1m"
  echo -n "#" $@
  echo -e "\033[0m"
}

# Section: variables from configuration file

# The name and size of the image file that will be generated.
FILENAME=nutshell.img
CONT_FILENAME=conpaas.img
FILESIZE=6656

HOST=nutshell
DEBIAN_DIST=precise
DEBIAN_MIRROR=http://archive.ubuntu.com/ubuntu/

CREATE_CONT=true

CLOUD=opennebula
ARCH=amd64
OPTIMIZE=true
KERNEL=3.5.0-41-generic


# Section: 003-create-image
if [ `id -u` -ne 0 ]; then
  cecho 'need root permissions for this script';
  exit 1;
fi


# System rollback function
function cleanup() {
    # Set errormsg if something went wrong
    [ $? -ne 0 ] && errormsg="Script terminated with errors"

    #stop and remove container
    if [ -d /var/lib/lxc/$HOST ];
    then
      lxc-shutdown -n $HOST
      sleep 10s
      lxc-destroy -n $HOST
    fi
    
    for mpoint in /dev/pts /dev /proc /
    do
      mpoint="${ROOT_DIR?:not set}${mpoint}"

      # Only attempt to umount $ROOT_DIR{/dev/pts,/dev,/proc,/} if necessary
      if [ -d $mpoint ]
      then
        cecho "Umounting $mpoint"
        umount -l $mpoint || true
      fi
    done
 
    sleep 1s
    losetup -d $LOOP_DEV_P
    sleep 1s
    kpartx -ds $LOOP_DEV

    sleep 1s
    losetup -d $LOOP_DEV
    sleep 1s
    rmdir $ROOT_DIR
    # Print "Done" on success, $errormsg otherwise
    cecho "${errormsg:-Done}"
}




# Check if required binaries are in $PATH
for bin in dd parted losetup kpartx mkfs.ext3 tune2fs mount debootstrap chroot umount grub-install lxc-start
do
  if [ -z `which $bin` ]
  then
    if [ -x /usr/lib/command-not-found ]
    then
      /usr/lib/command-not-found $bin
    else
      echo "$bin: command not found"
    fi
    exit 1
  fi
done

cecho "Creating empty disk image at" $FILENAME
dd if=/dev/zero of=$FILENAME bs=1M count=1 seek=$FILESIZE

cecho "Writing partition table"
parted -s $FILENAME mklabel msdos

cecho "Creating primary partition"
cyl_total=`parted -s $FILENAME unit s print | awk '{if (NF > 2 && $1 == "Disk") print $0}' | sed 's/Disk .* \([0-9]\+\)s/\1/'`
cyl_partition=`expr $cyl_total - 2048`
parted -s $FILENAME unit s mkpart primary ext3 2048 $cyl_partition

cecho "Setting boot flag"
parted -s $FILENAME set 1 boot on


LOOP_DEV=`losetup -f`
cecho "Going to use" $LOOP_DEV
losetup $LOOP_DEV $FILENAME


dname=`kpartx -l $LOOP_DEV | awk '{print $1}'`
PART_DEV=/dev/mapper/$dname
cecho "Mapping partition to device"
kpartx -as $LOOP_DEV


cecho "Creating ext3 filesystem"

echo 'y' | mkfs.ext3 $PART_DEV
cecho "Setting label 'root'"
tune2fs $PART_DEV -L root

ROOT_DIR=`mktemp -d`
cecho "Using $ROOT_DIR as mount point"

cecho "Mounting disk image"

LOOP_DEV_P=`losetup -f`
losetup $LOOP_DEV_P $PART_DEV
mount $LOOP_DEV_P $ROOT_DIR
#mount $PART_DEV $ROOT_DIR

# Always clean up on exit
trap "cleanup" EXIT

cecho "Starting debootstrap"
debootstrap --arch $ARCH --include locales $DEBIAN_DIST $ROOT_DIR $DEBIAN_MIRROR

opennebula_specific="iface eth0 inet static"

ec2_specific=$(cat <<EOF
allow-hotplug eth0
iface eth0 inet dhcp
EOF
)

if [ "$CLOUD" == "opennebula" ] ; then
    net_config="$opennebula_specific"
elif [ "$CLOUD" == "ec2" ] ; then
    net_config="$ec2_specific"
else
  cecho 'Something went wrong. "CLOUD" shell variable is not properly defined.';
  exit 1;
fi


cecho "Writing fstab"
echo "/dev/sda1 / ext3 defaults 0 1" > $ROOT_DIR/etc/fstab

cecho "Writing /etc/network/interfaces"
cat <<EOF > $ROOT_DIR/etc/network/interfaces
auto lo
iface lo inet loopback
auto eth0
$net_config
EOF
cecho "Removing udev persistent rules"
rm $ROOT_DIR/etc/udev/rules.d/70-persistent* || true

cecho "Changing hostname"
cat <<EOF > $ROOT_DIR/etc/hostname
$HOST
EOF

sed -i "1i 127.0.0.1  $HOST" $ROOT_DIR/etc/hosts


sed --in-place 's/main/main universe multiverse/'  $ROOT_DIR/etc/apt/sources.list 
echo  'deb http://security.ubuntu.com/ubuntu precise-security main universe multiverse restricted' >>  $ROOT_DIR/etc/apt/sources.list


# mount /dev/pts to avoid error message: Can not write log, openpty() failed (/dev/pts not mounted?) 
cecho "Mounting /dev, /dev/pts and /proc in chroot"
mount -obind /dev $ROOT_DIR/dev
mount -obind /dev/pts $ROOT_DIR/dev/pts
mount -t proc proc $ROOT_DIR/proc

cecho "Setting keyboard layout"
chroot $ROOT_DIR /bin/bash -c "echo 'debconf keyboard-configuration/variant  select  USA' | debconf-set-selections"

cecho "Generating and setting locale"
chroot $ROOT_DIR /bin/bash -c 'locale-gen en_US.UTF-8'
chroot $ROOT_DIR /bin/bash -c 'update-locale LANG=en_US.UTF-8'

cecho "Running apt-get update"
chroot $ROOT_DIR /bin/bash -c 'apt-get -y update'

chroot $ROOT_DIR /bin/bash -c "echo grub-pc grub-pc/install_devices multiselect $LOOP_DEV | debconf-set-selections -v"

cecho "Installing $KERNEL"
chroot $ROOT_DIR /bin/bash -c "apt-get -y install $KERNEL"
#cecho "Installing grub package"
#chroot $ROOT_DIR /bin/bash -c 'DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install grub'

mkdir -p $ROOT_DIR/boot/grub
cat <<EOF > $ROOT_DIR/boot/grub/device.map 
(hd0)   $LOOP_DEV
(hd0,1) $LOOP_DEV_P
EOF

chroot $ROOT_DIR grub-mkconfig -o /boot/grub/grub.cfg

VMLINUZ=/boot/$(chroot $ROOT_DIR ls /boot/ | grep vmlinuz | head -n 1)
INITRD=/boot/$(chroot $ROOT_DIR ls /boot/ | grep initrd | head -n 1)

cecho "Writing /boot/grub/grub.cfg"
cat <<EOF > $ROOT_DIR/boot/grub/grub.cfg
set default=0
set timeout=0
menuentry '$(basename $VMLINUZ)' {
  insmod ext2
  set root='(hd0,1)'
  linux  $VMLINUZ root=/dev/sda1
  initrd $INITRD
}
EOF

if [ "$CLOUD" == "ec2" ] ; then
  cecho "Writing /boot/grub/menu.lst"
  cat <<EOF > $ROOT_DIR/boot/grub/menu.lst
default 0
timeout 0

title $(basename $VMLINUZ)
  root (hd0,0)
  kernel $VMLINUZ root=/dev/xvda1 ro
  initrd $INITRD
EOF
fi

cecho "Running grub-install"
grub-install --no-floppy --recheck --root-directory=$ROOT_DIR --modules=part_msdos  $LOOP_DEV



# disable auto start after package install
cat <<EOF > $ROOT_DIR/usr/sbin/policy-rc.d
#!/bin/sh
exit 101
EOF
chmod 755 $ROOT_DIR/usr/sbin/policy-rc.d

#Section 701-embed-container-image-nutshell

DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
if $CREATE_CONT ; then
  sed --in-place 's/nutshell = true/nutshell = false/' $DIR/create-img-script.cfg
  python $DIR/create-img-script.py
  
  #$DIR/create-img-conpaas.sh
  CONT_IMG=$FILENAME
  $OPTIMIZE && CONT_IMG="optimized-$CONT_FILENAME"

  sed --in-place 's/nutshell = false/nutshell = true/' $DIR/create-img-script.cfg
fi

mkdir -p $ROOT_DIR/nutshell
chmod a+w $ROOT_DIR/nutshell
cp $DIR/$CONT_IMG $ROOT_DIR/nutshell

#Section 702-depend-nutshell

# Generate a script that will install the dependencies in the system. 
cat <<EOF > $ROOT_DIR/nutshell_install
#!/bin/bash
# Function for displaying highlighted messages.
function cecho() {
  echo -en "\033[1m"
  echo -n "#" \$@
  echo -e "\033[0m"
}

# set root passwd
echo "root:contrail" | chpasswd


# install dependencies
apt-get -f -y update
# pre-accept sun-java6 licence
echo "debconf shared/accepted-sun-dlj-v1-1 boolean true" | debconf-set-selections
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade \
        install openssh-server wget git iptables-persistent patch libvirt-bin \
                python python-pycurl python-openssl python-m2crypto \
                python-cheetah python-netaddr libxslt1-dev subversion unzip less vim \
                build-essential python-setuptools python-dev \
                libapache2-mod-wsgi libcurl4-openssl-dev ntpdate
            

# remove cached .debs from /var/cache/apt/archives to save disk space
apt-get clean

#add the iptables rules for correcting checksums
iptables -A POSTROUTING -t mangle -p udp --dport bootpc -j CHECKSUM --checksum-fill
iptables-save > /etc/iptables/rules.v4

exit 0
EOF

# Execute the script for installing the dependencies.
chmod a+x $ROOT_DIR/nutshell_install
chroot $ROOT_DIR /bin/bash /nutshell_install
rm -f $ROOT_DIR/nutshell_install

#Section 703-devstack-nutshell

DEST=/opt/stack
STACK_USER=stack

cat <<EOF > $ROOT_DIR/devstack_config
#!/bin/bash


echo "Creating $STACK_USER group, user and set privileges"
groupadd $STACK_USER
useradd -g $STACK_USER -s /bin/bash -d $DEST -m $STACK_USER
grep -q "^#includedir.*/etc/sudoers.d" /etc/sudoers ||
    echo "#includedir /etc/sudoers.d" >> /etc/sudoers
( umask 226 && echo "$STACK_USER ALL=(ALL) NOPASSWD:ALL" \
    > /etc/sudoers.d/50_stack_sh )

echo "stack:contrail" | chpasswd
su - stack -c "git clone https://github.com/openstack-dev/devstack.git"
sed --in-place 's/:80/:8080/' $DEST/devstack/files/apache-horizon.template

exit 0
EOF

chmod a+x $ROOT_DIR/devstack_config
chroot $ROOT_DIR /bin/bash /devstack_config
rm -f $ROOT_DIR/devstack_config

rm -f $ROOT_DIR/usr/sbin/policy-rc.d

cat <<EOF >> $ROOT_DIR/opt/stack/.bashrc
/opt/stack/devstack/my-rejoin-stack.sh
source /opt/stack/devstack/openrc admin admin  &>/dev/null
EOF

LIB_VIRT=lxc
$CREATE_CONT || LIB_VIRT=kvm

sed -i -r "s/(LIBVIRT_TYPE *= *).*/\1$LIB_VIRT/" $DIR/nutshell-config/localrc

cp $DIR/nutshell-config/localrc $ROOT_DIR/$DEST/devstack/
cp -r $DIR/nutshell-config/* $ROOT_DIR/nutshell
cp $DIR/nutshell-config/scripts/my-rejoin-stack.sh $ROOT_DIR/$DEST/devstack/
mkdir -p $ROOT_DIR/nutshell/img-creation
cp -r $DIR/nutshell-config $ROOT_DIR/nutshell/img-creation
cp $DIR/create-img-script.{cfg,py} $ROOT_DIR/nutshell/img-creation
#Section 704-conpaas-nutshell


cat <<EOF > $ROOT_DIR/$DEST/conpaas_install
#!/bin/bash

$DEST/devstack/stack.sh
sleep 1.5

echo "Authenticating..."
source $DEST/devstack/openrc admin admin
sleep 1.5

echo "Registering image"
glance image-create --name=conpaas --is-public=true --container-format=bare --disk-format=raw < /nutshell/$CONT_IMG

echo 'y' | rm /nutshell/$CONT_IMG

echo "create key pair"
nova keypair-add test > /nutshell/test.pem
chmod 600 /nutshell/test.pem

(cd /; patch -p1 < /nutshell/nbd.patch)
sed -i '/default_floating_pool/a auto_assign_floating_ip=True' /etc/nova/nova.conf
sed -i '/allow_resize_to_same_host/a ram_allocation_ratio=10' /etc/nova/nova.conf

wget -P /nutshell http://www.conpaas.eu/dl/cpsdirector-1.3.1.tar.gz
(cd /nutshell ; tar -zxvf cpsdirector-1.3.1.tar.gz)
rm /nutshell/cpsdirector-1.3.1.tar.gz

wget -P /nutshell http://www.conpaas.eu/dl/cpsclient-1.3.1.tar.gz

(cd /nutshell/cpsdirector-1.3.1/ ; echo '172.16.0.1' | sudo ./install.sh)
sudo easy_install /nutshell/cpsclient-1.3.1.tar.gz

sudo cpsadduser.py test@email test password

source devstack/eucarc
/nutshell/scripts/configconpaas.sh /nutshell/director.cfg 172.16.0.1


EOF

chmod a+x $ROOT_DIR/$DEST/conpaas_install


#Section 705-config-container-nutshell

mkdir -p /var/lib/lxc/$HOST

sed -i -r "s%(lxc.rootfs *= *).*%\1$ROOT_DIR%" $DIR/nutshell-config/lxc-config
sed -i -r "s/(lxc.utsname *= *).*/\1$HOST/" $DIR/nutshell-config/lxc-config

cp $DIR/nutshell-config/lxc-config /var/lib/lxc/$HOST/config


cat <<EOF > /var/lib/lxc/$HOST/fstab
proc            proc         proc    nodev,noexec,nosuid 0 0
sysfs           sys          sysfs defaults  0 0

EOF


cat <<"EOF" > $ROOT_DIR/etc/rc.local
#!/bin/sh
if ip link ls tap0
then true
else
  ip addr add 10.0.3.2/24 dev eth0
  ip route add default via 10.0.3.1

  ip tuntap add mode tap tap0
  ip addr add 172.16.0.1/24 dev tap0
  ip link set tap0 up
  echo "container started" | netcat 10.0.3.1 30000 -q 10
fi
EOF

cecho "Creating nutshell container"
lxc-start -n $HOST -d

cecho "Waiting for container to start"
nc -l 30000

echo 'y' | ssh-keygen -q -t rsa -N "" -f $DIR/id_rsa
mkdir -p $ROOT_DIR/root/.ssh
cat $DIR/id_rsa.pub > $ROOT_DIR/root/.ssh/authorized_keys
ssh -i $DIR/id_rsa -o "StrictHostKeyChecking no" root@10.0.3.2 'su - stack -c ./conpaas_install'
rm -f $DIR/id_rsa*

rm -f $ROOT_DIR/$DEST/conpaas_install

# Section: 997-opennebula

##### TO CUSTOMIZE: #####
# This part is for OpenNebula contextualization. The contextualization scripts (and possibly
# other necessary files) will be provided through OpenNebula to the VM as an ISO image.
# We need to mount this image and execute the contextualization scripts. You might need
# to change the dev file associated with the CD-ROM inside your virtual machine from
# "/dev/sr0" to something else (depending on your operating system and on the virtualization 
# software, it can be /dev/hdb, /dev/sdb etc.). You can check this in a VM that is already running
# in your OpenNebula system and that has been configured with contextualization.  
 
cat <<"EOF" > $ROOT_DIR/etc/rc.local
#!/bin/sh
mount -t iso9660 /dev/sr0 /mnt
 
if [ -f /mnt/context.sh ]; then
  . /mnt/context.sh
  if [ -n "$USERDATA" ]; then
    echo "$USERDATA" | /usr/bin/xxd -p -r | /bin/sh
  elif [ -e /mnt/init.sh ]; then
    . /mnt/init.sh
  fi
fi
umount /mnt

if ip link ls tap0
then true
else
  ip tuntap add mode tap tap0
  ip addr add 172.16.0.1/24 dev tap0
  ip link set tap0 up
  
  modprobe nbd
fi

exit 0
EOF

