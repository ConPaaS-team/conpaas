#!/bin/bash -e

# This script generates a VM image for ConPaaS, to be used for OpenNebula with KVM.
# The script should be run on a Debian or Ubuntu system.
# Before running this script, please make sure that you have the following
# executables in your $PATH:
#
# dd parted losetup kpartx mkfs.ext3 tune2fs mount debootstrap chroot umount grub-install (grub2)
# 
# NOTE: This script requires the installation of Grub 2 (we recommend Grub 1.98 or newer,
# as we experienced problems with 1.96). 

##### TO CUSTOMIZE: #####

# The name and size of the image file that will be generated.
FILENAME=conpaas.img
FILESIZE=2048 #MB

# The Debian distribution that you would like to have installed (we recommend squeeze).
DEBIAN_DIST=squeeze
DEBIAN_MIRROR=http://ftp.nl.debian.org/debian

# The architecture and kernel version for the OS that will be installed (please make
# sure to modify the kernel version name accordingly if you modify the architecture).
ARCH=i386
KERNEL_VERSION=2.6.32-5-686

#########################
export LC_ALL=C

# Function for displaying highlighted messages.
function cecho() {
  echo -en "\033[1m"
  echo -n "#" $@
  echo -e "\033[0m"
}

if [ `id -u` -ne 0 ]; then
  cecho 'need root permissions for this script';
  exit 1;
fi

# System rollback function
function cleanup() {
    # Set errormsg if something went wrong
    [ $? -ne 0 ] && errormsg="Script terminated with errors"

    for mpoint in /dev /proc /
    do
      mpoint="${ROOT_DIR?:not set}${mpoint}"

      # Only attempt to umount $ROOT_DIR{/dev,/proc,/} if necessary
      if [ -d $mpoint ]
      then
        cecho "Umounting $mpoint"
        umount $mpoint || true
      fi
    done

    sleep 1s
    losetup -d $LOOP_DEV_P
    sleep 1s
    kpartx -d $LOOP_DEV
    sleep 1s
    losetup -d $LOOP_DEV
    sleep 1s
    rm -r $ROOT_DIR
    # Print "Done" on success, $errormsg otherwise
    cecho "${errormsg:-Done}"
}

# Check if required binaries are in $PATH
for bin in dd parted losetup kpartx mkfs.ext3 tune2fs mount debootstrap chroot umount grub-install
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
dd if=/dev/zero of=$FILENAME bs=1M count=$FILESIZE

cecho "Writing partition table"
parted -s $FILENAME mklabel msdos

cecho "Creating primary partition"
cyl_total=`parted -s $FILENAME unit s print | awk '{if (NF > 2 && $1 == "Disk") print $0}' | sed 's/Disk .* \([0-9]\+\)s/\1/'`
cyl_partition=`expr $cyl_total - 2048`
parted -s $FILENAME unit s mkpart primary 2048 $cyl_partition

cecho "Setting boot flag"
parted -s $FILENAME set 1 boot on

LOOP_DEV=`losetup -f`
cecho "Going to use" $LOOP_DEV
losetup $LOOP_DEV $FILENAME

dname=`kpartx -l $LOOP_DEV | awk '{print $1}'`
PART_DEV=/dev/mapper/$dname
cecho "Mapping partition to device"
kpartx -a $LOOP_DEV

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

cecho "Writing fstab"
echo "/dev/sda1 / ext3 defaults 0 1" > $ROOT_DIR/etc/fstab
cecho "Writing /etc/network/interfaces"
cat <<EOF > $ROOT_DIR/etc/network/interfaces
auto lo
iface lo inet loopback
auto eth0
iface eth0 inet static
EOF
cecho "Removing udev persistent rules"
rm $ROOT_DIR/etc/udev/rules.d/70-persistent*

cecho "Changing hostname"
cat <<EOF > $ROOT_DIR/etc/hostname
conpaas
EOF

sed -i '1i 127.0.0.1  conpaas' $ROOT_DIR/etc/hosts

cecho "Mounting /dev and /proc in chroot"
mount -obind /dev $ROOT_DIR/dev
mount -t proc proc $ROOT_DIR/proc

cecho "Generating and setting locale"
chroot $ROOT_DIR /bin/bash -c "sed --in-place 's/^# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen"
chroot $ROOT_DIR /bin/bash -c 'locale-gen'
chroot $ROOT_DIR /bin/bash -c 'update-locale LANG=en_US.UTF-8'

cecho "Running apt-get update"
chroot $ROOT_DIR /bin/bash -c 'apt-get -y update'
cecho "Installing linux-image-$KERNEL_VERSION"
chroot $ROOT_DIR /bin/bash -c "apt-get -y install linux-image-$KERNEL_VERSION"
cecho "Installing grub package"
chroot $ROOT_DIR /bin/bash -c 'DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install grub'

mkdir -p $ROOT_DIR/boot/grub
cat <<EOF > $ROOT_DIR/boot/grub/device.map 
(hd0)   $LOOP_DEV
(hd0,1) $LOOP_DEV_P
EOF

#chroot $ROOT_DIR grub-mkconfig -o /boot/grub/grub.cfg
cecho "Writing /boot/grub/grub.cfg"
cat <<EOF > $ROOT_DIR/boot/grub/grub.cfg
set default=0
set timeout=0
menuentry 'linux-image-$KERNEL_VERSION' {
  insmod ext2
  set root='(hd0,1)'
  linux  /boot/vmlinuz-$KERNEL_VERSION root=/dev/sda1
  initrd /boot/initrd.img-$KERNEL_VERSION
}
EOF

cecho "Running grub-install"
grub-install --no-floppy --grub-mkdevicemap=$ROOT_DIR/boot/grub/device.map --root-directory=$ROOT_DIR $LOOP_DEV

# disable auto start after package install
cat <<EOF > $ROOT_DIR/usr/sbin/policy-rc.d
#!/bin/sh
exit 101
EOF
chmod 755 $ROOT_DIR/usr/sbin/policy-rc.d

# Generate a script that will install the dependencies in the system. 
cat <<EOF > $ROOT_DIR/conpaas_install
#!/bin/bash
# set root passwd
echo "root:contrail" | chpasswd

# fix apt sources
sed --in-place 's/main/main contrib non-free/' /etc/apt/sources.list

# install dependencies
apt-get -f -y update
# pre-accept sun-java6 licence
echo "debconf shared/accepted-sun-dlj-v1-1 boolean true" | debconf-set-selections
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade \
        install openssh-server \
        python python-pycurl python-cheetah nginx \
        tomcat6-user memcached mysql-server \
        make gcc g++ sun-java6-jdk erlang ant libxslt1-dev yaws subversion
update-rc.d -f memcached remove
update-rc.d -f nginx remove
update-rc.d -f yaws remove
update-rc.d -f mysql remove

# add dotdeb repo for php fpm
echo "deb http://packages.dotdeb.org stable all" >> /etc/apt/sources.list
wget -O - http://www.dotdeb.org/dotdeb.gpg 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install php5-fpm php5-curl \
              php5-mcrypt php5-mysql php5-odbc \
              php5-pgsql php5-sqlite php5-sybase php5-xmlrpc php5-xsl \
              php5-adodb php5-memcache python-mysqldb
update-rc.d -f php5-fpm remove

# remove dotdeb repo
sed --in-place 's%deb http://packages.dotdeb.org stable all%%' /etc/apt/sources.list
apt-get -f -y update
# remove cached .debs from /var/cache/apt/archives to save disk space
apt-get clean

# create directory structure
echo > /var/log/cpsagent.log
mkdir /etc/cpsagent/
mkdir /var/tmp/cpsagent/
mkdir /var/run/cpsagent/
mkdir /var/cache/cpsagent/
echo > /var/log/cpsmanager.log
mkdir /etc/cpsmanager/
mkdir /var/tmp/cpsmanager/
mkdir /var/run/cpsmanager/
mkdir /var/cache/cpsmanager/


# add cloudera repo for hadoop
echo "deb http://archive.cloudera.com/debian $DEBIAN_DIST-cdh3 contrib" >> /etc/apt/sources.list
wget -O - http://archive.cloudera.com/debian/archive.key 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install \
  hadoop-0.20 hadoop-0.20-namenode hadoop-0.20-datanode \
  hadoop-0.20-secondarynamenode hadoop-0.20-jobtracker  \
  hadoop-0.20-tasktracker hadoop-pig hue-common  hue-filebrowser \
  hue-jobbrowser hue-jobsub hue-plugins dnsutils
update-rc.d -f hadoop-0.20-namenode remove
update-rc.d -f hadoop-0.20-datanode remove
update-rc.d -f hadoop-0.20-secondarynamenode remove
update-rc.d -f hadoop-0.20-jobtracker remove
update-rc.d -f hadoop-0.20-tasktracker remove
update-rc.d -f hue remove
# create a default config dir
mkdir -p /etc/hadoop-0.20/conf.contrail
update-alternatives --install /etc/hadoop-0.20/conf hadoop-0.20-conf /etc/hadoop-0.20/conf.contrail 99
# remove cloudera repo
sed --in-place "s%deb http://archive.cloudera.com/debian $DEBIAN_DIST-cdh3 contrib%%" /etc/apt/sources.list
apt-get -f -y update


# add scalaris repo
echo "deb http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0 /" >> /etc/apt/sources.list
wget -O - http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0/Release.key 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install scalaris screen
update-rc.d -f scalaris remove
# remove scalaris repo
sed --in-place 's%deb http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0 /%%' /etc/apt/sources.list
apt-get -f -y update


# add xtreemfs repo
echo "deb http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0 /" >> /etc/apt/sources.list
wget -O - http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0/Release.key 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install xtreemfs-server xtreemfs-client
update-rc.d -f xtreemfs-osd remove
update-rc.d -f xtreemfs-mrc remove
update-rc.d -f xtreemfs-dir remove
# remove xtreemfs repo
sed --in-place 's%deb http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0 /%%' /etc/apt/sources.list
apt-get -f -y update


apt-get -f -y clean
exit 0
EOF

# Execute the script for installing the dependencies.
chmod a+x $ROOT_DIR/conpaas_install
chroot $ROOT_DIR /bin/bash /conpaas_install
rm -f $ROOT_DIR/conpaas_install

rm -f $ROOT_DIR/usr/sbin/policy-rc.d

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

exit 0
EOF




