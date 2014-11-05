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
FILENAME=conpaas.img
FILESIZE=3072 #MB

# The Debian distribution that you would like to have installed (we recommend squeeze).
DEBIAN_DIST=squeeze
DEBIAN_MIRROR=http://ftp.fr.debian.org/debian/

# The architecture and kernel version for the OS that will be installed (please make
# sure to modify the kernel version name accordingly if you modify the architecture).
CLOUD=opennebula
ARCH=amd64
KERNEL=linux-image-amd64


# Section: 003-create-image
if [ `id -u` -ne 0 ]; then
  cecho 'need root permissions for this script';
  exit 1;
fi

# System rollback function
function cleanup() {
    # Set errormsg if something went wrong
    [ $? -ne 0 ] && errormsg="Script terminated with errors"

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

vbox_specific=$(cat <<EOF
allow-hotplug eth0
iface eth0 inet dhcp

auto eth1
allow-hotplug eth1
iface eth1 inet dhcp
EOF
)


if [ "$CLOUD" == "opennebula" ] ; then
    net_config="$opennebula_specific"
elif [ "$CLOUD" == "ec2" ] ; then
    net_config="$ec2_specific"
elif [ "$CLOUD" == "vbox" ] ; then
    net_config="$vbox_specific"
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
conpaas
EOF

sed -i '1i 127.0.0.1  conpaas' $ROOT_DIR/etc/hosts

# mount /dev/pts to avoid error message: Can not write log, openpty() failed (/dev/pts not mounted?) 
cecho "Mounting /dev, /dev/pts and /proc in chroot"
mount -obind /dev $ROOT_DIR/dev
mount -obind /dev/pts $ROOT_DIR/dev/pts
mount -t proc proc $ROOT_DIR/proc

cecho "Setting keyboard layout"
chroot $ROOT_DIR /bin/bash -c "echo 'debconf keyboard-configuration/variant  select  USA' | debconf-set-selections"

cecho "Generating and setting locale"
chroot $ROOT_DIR /bin/bash -c "sed --in-place 's/^# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen"
chroot $ROOT_DIR /bin/bash -c 'locale-gen'
chroot $ROOT_DIR /bin/bash -c 'update-locale LANG=en_US.UTF-8'

cecho "Running apt-get update"
chroot $ROOT_DIR /bin/bash -c 'apt-get -y update'
cecho "Installing $KERNEL"
chroot $ROOT_DIR /bin/bash -c "apt-get -y install $KERNEL"
cecho "Installing grub package"
chroot $ROOT_DIR /bin/bash -c 'DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install grub'

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

# Section: 004-ConPaaS-core

GIT_SERVICE="false"

# Generate a script that will install the dependencies in the system. 
cat <<EOF > $ROOT_DIR/conpaas_install
#!/bin/bash
# Function for displaying highlighted messages.
function cecho() {
  echo -en "\033[1m"
  echo -n "#" \$@
  echo -e "\033[0m"
}

# set root passwd
echo "root:contrail" | chpasswd

# fix apt sources
sed --in-place 's/main/main contrib non-free/' /etc/apt/sources.list

export DEBIAN_FRONTEND=noninteractive

# install NTP to get the corret date for generated certificate
apt-get -q -y install ntp

# install curl that works better than wget in some scenarios
apt-get -q -y install curl


# install dependencies
apt-get -f -y update
# pre-accept sun-java6 licence
echo "debconf shared/accepted-sun-dlj-v1-1 boolean true" | debconf-set-selections
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade \
        install openssh-server wget \
                python python-pycurl python-openssl python-m2crypto \
                ganglia-monitor gmetad rrdtool logtail \
                python-cheetah python-netaddr libxslt1-dev yaws subversion unzip less
update-rc.d yaws disable
update-rc.d gmetad disable
update-rc.d ganglia-monitor disable

cecho "===== install IPOP package ====="
echo "deb http://www.grid-appliance.org/files/packages/deb/ stable contrib" >> /etc/apt/sources.list
wget -O - http://www.grid-appliance.org/files/packages/deb/repo.key | apt-key add -
apt-get update
apt-get -f -y install ipop

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

EOF

# Section: 501-php

cat <<EOF >> $ROOT_DIR/conpaas_install
cecho "===== add dotdeb repo for php fpm ====="
# add dotdeb repo for php fpm
echo "deb http://packages.dotdeb.org $DEBIAN_DIST all" >> /etc/apt/sources.list
wget -O - http://www.dotdeb.org/dotdeb.gpg 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install php5-fpm php5-curl \
        php5-mcrypt php5-mysql php5-odbc php5-pgsql php5-sqlite php5-sybase php5-xmlrpc \
        php5-xsl php5-adodb php5-memcache php5-gd nginx git tomcat6-user memcached

# For autoscaling
apt-get -f -y --no-install-recommends --no-upgrade install libatlas-base-dev libatlas3gf-base \
    python-dev python-scipy python-setuptools python-simplejson gfortran g++
easy_install numpy
easy_install -U numpy
easy_install pandas 
easy_install patsy 
easy_install statsmodels

update-rc.d php5-fpm disable
update-rc.d memcached disable
update-rc.d nginx disable

# remove dotdeb repo
sed --in-place 's%deb http://packages.dotdeb.org $DEBIAN_DIST all%%' /etc/apt/sources.list
apt-get -f -y update

# remove cached .debs from /var/cache/apt/archives to save disk space
apt-get clean

EOF

if [ $GIT_SERVICE = "false" ] ; then
GIT_SERVICE="true"

cat <<EOF >> $ROOT_DIR/conpaas_install
cecho "===== install GIT ====="
# add git user
useradd git --shell /usr/bin/git-shell --create-home -k /dev/null
# create ~git/.ssh and authorized_keys
install -d -m 700 --owner=git --group=git /home/git/.ssh
install -m 600 --owner=git --group=git /dev/null ~git/.ssh/authorized_keys
# create default repository
git init --bare ~git/code
# create SSH key for manager -> agent access
ssh-keygen -N "" -f ~root/.ssh/id_rsa
echo StrictHostKeyChecking no > ~root/.ssh/config
# allow manager -> agent passwordless pushes
cat ~root/.ssh/id_rsa.pub > ~git/.ssh/authorized_keys
# fix repository permissions
chown -R git:git ~git/code

EOF
fi

# Section: 502-galera

cat <<EOF >> $ROOT_DIR/conpaas_install

apt-get -f -y update
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade install \
		psmisc libaio1 libdbi-perl libdbd-mysql-perl mysql-client rsync python-mysqldb make

if [ $DEBIAN_DIST == "squeeze" ]
then
    cd /root/
#    wget https://launchpad.net/galera/2.x/23.2.4/+download/galera-23.2.4-amd64.deb 2>/dev/null
#    dpkg -i galera-23.2.4-amd64.deb

    wget https://launchpad.net/galera/2.x/25.2.8/+download/galera-25.2.8-$ARCH.deb 2>/dev/null
    dpkg -i galera-25.2.8-$ARCH.deb

#    wget https://launchpad.net/codership-mysql/5.5/5.5.29-23.7.3/+download/mysql-server-wsrep-5.5.29-23.7.3-amd64.deb 2>/dev/null
#    dpkg -i mysql-server-wsrep-5.5.29-23.7.3-amd64.deb

    wget https://launchpad.net/codership-mysql/5.5/5.5.34-25.9/+download/mysql-server-wsrep-5.5.34-25.9-$ARCH.deb 2>/dev/null
    dpkg -i mysql-server-wsrep-5.5.34-25.9-$ARCH.deb

    rm -f mysql-server-wsrep-5.5.34-25.9-$ARCH.deb
    rm -f galera-25.2.8-$ARCH.deb
    
    ## Fixing a bug in MySQL Galera (actually fixed in MySQL Galera 5.5.31-23.7.5 in June 2013)
#    sed 's.>>/dev/stderr.>\&2.' /usr/bin/wsrep_sst_common

elif [ $DEBIAN_DIST == "wheezy" ]
then
    cd /root/
#    # Galera version 3.x
#    wget https://launchpad.net/galera/3.x/25.3.1/+download/galera-25.3.1-$ARCH.deb 2>/dev/null
#    dpkg -i galera-25.3.1-$ARCH.deb

    # Pre-build package depends on libssl0.9.8 whereas wheezy ships with libssl1.0.0
    # Building and installing from source to link with libssl1.0.0
    DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade install \
        scons libssl-dev libboost-dev libboost-program-options-dev check
    wget https://launchpad.net/galera/3.x/25.3.1/+download/galera-25.3.1-src.tar.gz 2> /dev/null
    tar -xaf galera-25.3.1-src.tar.gz
    cd galera-25.3.1-src
    scons /
    cd ..
    rm -rf galera-25.3.1-src

#    # Galera version 2.x
#    DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade install libssl0.9.8
#    wget https://launchpad.net/galera/2.x/25.2.8/+download/galera-25.2.8-$ARCH.deb 2> /dev/null
#    dpkg -i galera-25.2.8-$ARCH.deb
    
    wget https://launchpad.net/codership-mysql/5.5/5.5.34-25.9/+download/mysql-server-wsrep-5.5.34-25.9-$ARCH.deb 2>/dev/null
    dpkg -i mysql-server-wsrep-5.5.34-25.9-$ARCH.deb

    rm -f mysql-server-wsrep-5.5.34-25.9-$ARCH.deb
    rm -f galera-25.3.1-src.tar.gz

else
    echo "ERROR: unknown Debian distribution '$DEBIAN_DIST': cannot select correct MySQL Galera packages."
    exit 1
fi


# Added more wait time before deciding whether the mysql daemon has failed to start (idem for stopping)
sed -i 's/1 2 3 4 5 6.*;/\$(seq 60);/' /etc/init.d/mysql


# Install Galera Load Balancer (glb)

#installation of prerequisites
apt-get -y install git autoconf libtool
#download the lastest version from git-hub  
git clone https://github.com/codership/glb
#configuration build and installation  
cd glb
./bootstrap.sh
./configure
make
make install
cp -a ./files/glbd.sh /etc/init.d/glbd
cp -a ./files/glbd.cfg /etc/default/glbd
# using default listen port 8010
sed -i 's/#LISTEN_ADDR/LISTEN_ADDR/' /etc/default/glbd
# using default listen port 8011
## wait 1 second after EOF to close nc
sed -i 's/#CONTROL_ADDR/CONTROL_ADDR/' /etc/default/glbd
sed -i 's/nc \$CONTROL_IP/nc -q 1 \$CONTROL_IP/' /etc/init.d/glbd
cd ..
rm -fr glb-\${glb_version} glb-\${glb_version}.tar.gz


EOF
# Section: 503-condor

cat <<EOF >> $ROOT_DIR/conpaas_install
cecho "===== install packages required by HTCondor ====="
# avoid warning: W: GPG error: http://mozilla.debian.net squeeze-backports Release: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 85A3D26506C4AE2A 
#apt-get install debian-keyring
wget -O - -q http://mozilla.debian.net/archive.asc | apt-key add -
# avoid warning: W: GPG error: http://dl.google.com stable Release: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY A040830F7FAC5991 
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# If things go wrong, you may want to read  http://research.cs.wisc.edu/htcondor/debian/
# 
# added [arch=amd64 trusted=yes] to avoid authentication warning
echo "deb [arch=amd64 trusted=yes] http://research.cs.wisc.edu/htcondor/debian/stable/ $DEBIAN_DIST contrib" >> /etc/apt/sources.list
apt-get update
if [ $DEBIAN_DIST == "squeeze" ]
then
    DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade \
        install sun-java6-jdk ant condor sudo xvfb
elif [ $DEBIAN_DIST == "wheezy" ]
then
    DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade \
        install openjdk-7-jre-headless ant condor sudo xvfb
else
    echo "Error: unknown Debian distribution '$DEBIAN_DIST': cannot select correct Condor packages."
    exit 1
fi

# next 12 lines moved here from conpaas-services/scripts/manager/htc-manager-start
apt-get update -y 
echo ==== python-setuptools 
apt-get install python-setuptools -y 
sleep 2
echo ==== pip  
easy_install -U distribute
easy_install pip 
sleep 2
echo PATH=$PATH 
export PATH=$PATH:/usr/local/bin
echo PATH=$PATH 
echo ==== xmltodict  
pip install xmltodict 

echo ===== check if HTCondor is running =====
ps -ef | grep condor
echo ===== stop condor =====
/etc/init.d/condor stop
echo ===== 

# remove cached .debs from /var/cache/apt/archives to save disk space
apt-get clean
EOF

# Section: 504-selenium

cat <<EOF >> $ROOT_DIR/conpaas_install
cecho "===== install SELENIUM ====="

if [ $DEBIAN_DIST == "squeeze" ]
then
    # recent versions of iceweasel and chrome
    echo "deb http://backports.debian.org/debian-backports $DEBIAN_DIST-backports main" >> /etc/apt/sources.list
    echo "deb http://mozilla.debian.net/ $DEBIAN_DIST-backports iceweasel-esr" >> /etc/apt/sources.list

    apt-get -f -y update
    apt-get -f -y --force-yes install -t $DEBIAN_DIST-backports iceweasel
    apt-get -f -y --force-yes install xvfb xinit chromium-browser sun-java6-jdk
elif [ $DEBIAN_DIST == "wheezy" ]
then
    apt-get -f -y update
    apt-get -f -y --force-yes install iceweasel xvfb xinit chromium-browser openjdk-7-jre-headless
else
    echo "Error: unknown Debian distribution '$DEBIAN_DIST': cannot select correct Selenium packages."
    exit 1
fi

EOF

# Section: 505-hadoop

cat <<EOF >> $ROOT_DIR/conpaas_install
cecho "===== install cloudera repo for hadoop ====="
# add cloudera repo for hadoop
if [ "$DEBIAN_DIST" == "wheezy" ]
then
  hadoop_dist="squeeze"
else
  hadoop_dist="$DEBIAN_DIST"
fi
echo "deb http://archive.cloudera.com/debian \${hadoop_dist}-cdh3 contrib" >> /etc/apt/sources.list
wget -O - http://archive.cloudera.com/debian/archive.key 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install \
  hadoop-0.20 hadoop-0.20-namenode hadoop-0.20-datanode \
  hadoop-0.20-secondarynamenode hadoop-0.20-jobtracker  \
  hadoop-0.20-tasktracker hadoop-pig hue-common  hue-filebrowser \
  hue-jobbrowser hue-jobsub hue-plugins hue-server dnsutils
update-rc.d hadoop-0.20-namenode disable
update-rc.d hadoop-0.20-datanode disable
update-rc.d hadoop-0.20-secondarynamenode disable
update-rc.d hadoop-0.20-jobtracker disable
update-rc.d hadoop-0.20-tasktracker disable
update-rc.d hue disable
# create a default config dir
mkdir -p /etc/hadoop-0.20/conf.contrail
update-alternatives --install /etc/hadoop-0.20/conf hadoop-0.20-conf /etc/hadoop-0.20/conf.contrail 99
# remove cloudera repo
sed --in-place "s%deb http://archive.cloudera.com/debian \${hadoop_dist}-cdh3 contrib%%" /etc/apt/sources.list
apt-get -f -y update


EOF

# Section: 506-scalaris

cat <<EOF >> $ROOT_DIR/conpaas_install
cecho "===== install scalaris repo ====="
# add scalaris repo
echo "deb http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0 /" >> /etc/apt/sources.list
wget -O - http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0/Release.key 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install scalaris screen erlang
update-rc.d scalaris disable
# remove scalaris repo
sed --in-place 's%deb http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0 /%%' /etc/apt/sources.list
apt-get -f -y update

EOF

# Section: 507-xtreemfs

cat <<EOF >> $ROOT_DIR/conpaas_install
cecho "===== install xtreemfs repo ====="
# add xtreemfs repo
if [ "$DEBIAN_DIST" == "squeeze" ]
then
    echo "deb http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0 /" >> /etc/apt/sources.list
    wget -O - http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0/Release.key 2>/dev/null | apt-key add -
elif [ "$DEBIAN_DIST" == "wheezy" ]
then
    echo "deb http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_7.0 /" >> /etc/apt/sources.list
    wget -O - http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_7.0/Release.key 2>/dev/null | apt-key add -
else
    echo "ERROR: unknown Debian distribution '$DEBIAN_DIST'."
    exit 1
fi
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install xtreemfs-server xtreemfs-client xtreemfs-tools
update-rc.d xtreemfs-osd disable
update-rc.d xtreemfs-mrc disable
update-rc.d xtreemfs-dir disable
# remove xtreemfs repo
sed --in-place 's%deb http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_..0 /%%' /etc/apt/sources.list
apt-get -f -y update

EOF

# Section: 995-rm-unused-pkgs

cat <<EOF > $ROOT_DIR/conpaas_rm
#!/usr/bin/python

from subprocess import Popen
from subprocess import PIPE
import re
import sys

# Define which are the 'root' packages (from
# which the dependency analysis starts)

print "rm unused packages script starting ..."

debian_pkgs = ['linux-image-xen-amd64', 'linux-image-amd64', 'linux-image-xen-686', 'linux-image-686',
               'initramfs-tools', 'bash', 'apt', 'apt-utils', 'cron',
               'vim-tiny', 'grub-common', 'grub', 'grub-pc', 'net-tools',
               'iputils-ping', 'rsyslog', 'binfmt-support', 'dbus',
               'avahi-daemon', 'libavahi-core7', 'libdaemon0', 'libnss-mdns',
               'bsdmainutils', 'resolvconf', 'netbase', 'iproute', 'ifupdown',
               'isc-dhcp-common', 'isc-dhcp-client', 'wget']

core_pkgs = ['openssh-server', 'python', 'python-pycurl', 'python-openssl',
             'python-m2crypto', 'python-cheetah', 'libxslt1-dev', 'yaws',
             'subversion', 'unzip', 'less', 'ipop', 'ntp', 'curl',
             'ganglia-monitor', 'gmetad', 'rrdtool', 'logtail', 'python-netaddr']

php_pkgs = ['php5-fpm', 'php5-curl', 'php5-mcrypt', 'php5-mysql', 'php5-odbc',
            'php5-pgsql', 'php5-sqlite', 'php5-sybase', 'php5-xmlrpc',
            'php5-xsl', 'php5-adodb', 'php5-memcache', 'php5-gd', 'nginx',
            'git', 'tomcat6-user', 'memcached', 'python-scipy', 'python-simplejson',
            'libatlas-base-dev', 'libatlas3gf-base', 'python-dev', 'python-setuptools']

galera_pkgs = ['galera', 'mysql-server-wsrep', 'python-mysqldb', 'rsync']

if "$DEBIAN_DIST" == "squeeze":
    condor_pkgs = ['sun-java6-jdk', 'ant', 'condor', 'sudo', 'xvfb']
else:
    condor_pkgs = ['openjdk-7-jre-headless', 'ant', 'condor', 'sudo', 'xvfb']

if "$DEBIAN_DIST" == "squeeze":
    selenium_pkgs = ['iceweasel', 'xvfb', 'xinit', 'chromium-browser','sun-java6-jdk']
else:
    selenium_pkgs = ['iceweasel', 'xvfb', 'xinit', 'chromium-browser','openjdk-7-jre-headless']

hadoop_pkgs =   ['hadoop-0.20', 'hadoop-0.20-namenode', 'hadoop-0.20-datanode',
                'hadoop-0.20-secondarynamenode', 'hadoop-0.20-jobtracker',
                'hadoop-0.20-tasktracker', 'hadoop-pig', 'hue-common',
                'hue-filebrowser', 'hue-jobbrowser', 'hue-jobsub',
                'hue-plugins', 'hue-server', 'dnsutils']

scalaris_pkgs = ['scalaris', 'screen', 'erlang']

xtreemfs_pkgs = ['xtreemfs-server', 'xtreemfs-client', 'xtreemfs-tools']

cds_pkgs = ['php5-fpm', 'php5-curl', 'php5-mcrypt', 'php5-mysql', 'php5-odbc',
            'php5-pgsql', 'php5-sqlite', 'php5-sybase', 'php5-xmlrpc',
            'php5-xsl', 'php5-adodb', 'php5-memcache', 'php5-gd git',
            'tomcat6-user', 'memcached',
            'libpcre3-dev', 'libssl-dev', 'libgeoip-dev', 'libperl-dev']


# Execute shell command
def shell_cmd(cmd):
    return Popen(cmd, stdout=PIPE, shell=True).stdout.read()

# Take the output of a shell command and return a list
# of tokens from it
def string_to_list(s):
    # Normalize whitespace to single spaces
    s = re.sub(r'\s+', ' ', s);
    return s.split()

def write_to_file(filename, data):
	f = open(filename, 'w')
	print >> f, data
	f.close()

def remove_pkg(pkg):
    return shell_cmd("apt-get -y purge %s 2>&1 " % pkg)

def force_remove_pkg(pkg):
    return shell_cmd("echo 'Yes, do as I say!' | apt-get -y --force-yes purge %s 2>&1 " % pkg)

def doublecheck_unneeded_pkgs(unneeded_pkgs):
    to_keep = []
    to_remove = []
    to_remove_with_wornings = []
    for pkg in unneeded_pkgs:
        output = shell_cmd('apt-get -s purge %s ' % pkg)
        warn = re.findall(r'WARNING: The following essential packages will be removed.', output)

        output = re.findall(r'The following packages will be REMOVED:(.*?)^\S', output, re.S | re.M)

        l = len(output)
        if l == 0:
            print  '%s does not have a remove list' % pkg
            continue

        if l > 1:
            sys.exit('Error: More than one list of packages to be removed.')

        # Unpack from list
        output = output[0]
        # Remove '*' chars
        output = re.sub(r'\*', '', output);
        output = string_to_list(output)
        output = set(output)

        if len(output.intersection(needed_pkgs)) > 0:
            to_keep.append(pkg)
        else:
            if warn:
                to_remove_with_wornings.append(pkg)
            else:
                to_remove.append(pkg)

    return to_keep, to_remove, to_remove_with_wornings


# Necessary packages
args = sys.argv[1:]
pkgs = []
pkgs.extend(debian_pkgs)
pkgs.extend(core_pkgs)

if len(args) == 0:
    sys.exit('The script needs at least one of the arguments: '
    '--all, --none, --php, --condor, --selenium, --hadoop, --scalaris, --xtreemfs, --cds, --debug.')

if '--debug' in args:
	dbg = True
	args.remove('--debug')
else:
	dbg = False

if '--all' in args:
    pkgs.extend(php_pkgs)
    pkgs.extend(condor_pkgs)
    pkgs.extend(selenium_pkgs)
    pkgs.extend(hadoop_pkgs)
    pkgs.extend(scalaris_pkgs)
    pkgs.extend(xtreemfs_pkgs)
    pkgs.extend(cds_pkgs)
    args.remove('--all')
elif '--none' in args:
    args.remove('--none')
else:
    if '--php' in args:
        pkgs.extend(php_pkgs)
        args.remove('--php')
    if '--galera' in args:
        pkgs.extend(galera_pkgs)
        args.remove('--galera')
    if '--condor' in args:
        pkgs.extend(condor_pkgs)
        args.remove('--condor')
    if '--selenium' in args:
        pkgs.extend(selenium_pkgs)
        args.remove('--selenium')
    if '--hadoop' in args:
        pkgs.extend(hadoop_pkgs)
        args.remove('--hadoop')
    if '--scalaris' in args:
        pkgs.extend(scalaris_pkgs)
        args.remove('--scalaris')
    if '--xtreemfs' in args:
        pkgs.extend(xtreemfs_pkgs)
        args.remove('--xtreemfs')
    if '--cds' in args:
        pkgs.extend(cds_pkgs)
        args.remove('--cds')

if args:
    sys.exit('Error: Unrecognized or duplicate arguments: %s' % str(args))

# Install apt-rdepends
print shell_cmd('apt-get -y install apt-rdepends 2>&1 ')

# Make a list of needed packages
needed_pkgs = set([])
for pkg in pkgs:
    print 'Processing ' + pkg
    needed_pkgs.add(pkg)
    dependencies = shell_cmd('apt-rdepends %s 2>&1 | awk -F"Depends:|PreDepends:" \'/Depends: / || /PreDepends: / { print \$2 }\' | awk \'{print \$1}\'| sort -u' % pkg)

    needed_pkgs.update(string_to_list(dependencies))

needed_pkgs = list(needed_pkgs)
needed_pkgs.sort()
needed_pkgs = set(needed_pkgs)

if (dbg):
    write_to_file('needed_pkgs', needed_pkgs)

# Useful
# shell_cmd("dpkg-query -Wf '\${Installed-Size}\t\t\${Package}\t\t\${Priority}\n' | sort -u")

# Make a list of installed packages
installed_pkgs = shell_cmd("dpkg-query -Wf '\${Package}\n' | sort -u")
installed_pkgs = string_to_list(installed_pkgs)
installed_pkgs = set(installed_pkgs)

if (dbg):
    write_to_file('installed_pkgs', installed_pkgs)

# Find unneeded packages
unneeded_pkgs = installed_pkgs.difference(needed_pkgs)
weird_pkgs = needed_pkgs.difference(installed_pkgs)

# Some of the packages in unneeded_pkgs can still be required
to_keep, to_remove, to_remove_with_wornings = \
    doublecheck_unneeded_pkgs(unneeded_pkgs)
needed_pkgs.update(to_keep)
unneeded_pkgs = to_remove + to_remove_with_wornings

if (dbg):
    write_to_file('to_remove', to_remove)
    write_to_file('to_remove_with_wornings', to_remove_with_wornings)


print "REMOVING PACKAGES ..."
for p in to_remove:
	print remove_pkg(p), "\n"
print shell_cmd('apt-get -y autoremove 2>&1')

# Free additional space
#apt-get -y install localepurge
#localepurge
#apt-get -y purge localepurge

print shell_cmd('rm -rf /usr/share/doc/ 2>&1')
print shell_cmd('rm -rf /usr/share/doc-base/ 2>&1')
print shell_cmd('rm -rf /usr/share/man/ 2>&1')

EOF
RM_SCRIPT_ARGS=' --php --galera --condor --selenium --hadoop --scalaris --xtreemfs'

# Section: 996-tail

cat <<EOF >> $ROOT_DIR/conpaas_install
apt-get -f -y clean
exit 0
EOF

# Execute the script for installing the dependencies.
chmod a+x $ROOT_DIR/conpaas_install
chroot $ROOT_DIR /bin/bash /conpaas_install
rm -f $ROOT_DIR/conpaas_install

rm -f $ROOT_DIR/usr/sbin/policy-rc.d

# Execute the script to remove unneeded pkgs.
if [ -f $ROOT_DIR/conpaas_rm ] ; then
    chmod a+x $ROOT_DIR/conpaas_rm
    chroot $ROOT_DIR /usr/bin/python /conpaas_rm $RM_SCRIPT_ARGS
    rm -f $ROOT_DIR/conpaas_rm
fi
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

exit 0
EOF

# Section: 999-resize-image

conpaas_resize=$(mktemp)

cat <<"EOF" > $conpaas_resize
#!/bin/bash

# Customizable
DEFAULT_FREE_SPACE=256 #MB


# Function for displaying highlighted messages.
function cecho() {
  echo -en "\033[1m"
  echo -n "#" $@
  echo -e "\033[0m"
}

cecho "resize script starting ..."

if [ `id -u` -ne 0 ]; then
	exec 1>&2; cecho "error: Need root permissions for this script."
 	exit 1
fi

if [ -z "$1" ] ; then
	exec 1>&2; cecho "error: No image specified."
	exit 1
fi

SRC_IMG=$1
DST_IMG=optimized-$1


FS_SPACE=40 #MB
if [ -z "$2" ] ; then
	FREE_SPACE=$DEFAULT_FREE_SPACE
elif [[ "$2" =~ ^[0-9]+$ ]] ; then
	FREE_SPACE=$2
else
	exec 1>&2; cecho "error: The 'FREE_SPACE' argument \
			should be a number."
	exit 1
fi


cecho "Mounting old image."
SRC_LOOP=`losetup -f`
losetup $SRC_LOOP $SRC_IMG

PARTITION=`kpartx -l $SRC_LOOP | awk '{ print $1 }'`
PARTITION=/dev/mapper/$PARTITION
kpartx -as $SRC_LOOP

SRC_DIR=`mktemp -d`
mount -o loop $PARTITION $SRC_DIR

USED_SPACE=`(cd $SRC_DIR ; df --total --block-size=M  . | tail -n 1 | awk '{print $3}' | tr -d 'M')`

DST_SIZE=`python -c "print ($USED_SPACE + $FS_SPACE + $FREE_SPACE)"`
## Use 1GB granularity for image size
#gb_size="1024.0"
#DST_SIZE=`python -c "import math; print int(math.ceil($DST_SIZE/$gb_size) * $gb_size)"`

umount $SRC_DIR
sleep 1s
kpartx -ds $SRC_LOOP
sleep 1s
losetup -d $SRC_LOOP
sleep 1s
rmdir $SRC_DIR


# Create new image
dd if=/dev/zero of=$DST_IMG bs=1M count=1 seek=$DST_SIZE

PART_OFFSET_IN_BYTES=`parted -s $SRC_IMG unit B print | awk \
	'/Number.*Start.*End/ { getline; print $2 }' | tr -d 'B'`
PART_OFFSET_IN_SECTORS=`parted -s $SRC_IMG unit S print | awk \
	'/Number.*Start.*End/ { getline; print $2 }' | tr -d 's'`

# Create filesystem on new image and mount it
cecho "Writing partition table."
parted -s $DST_IMG mklabel msdos

cecho "Creating primary partition."
cyl_total=`parted -s $DST_IMG unit s print | awk \
	'{if (NF > 2 && $1 == "Disk") print $0}' | sed \
	's/Disk .* \([0-9]\+\)s/\1/'`
cyl_partition=`expr $cyl_total - $PART_OFFSET_IN_SECTORS`
parted -s $DST_IMG unit s mkpart primary ext3 2048 $cyl_partition

cecho "Setting boot flag."
parted -s $DST_IMG set 1 boot on

DST_LOOP=`losetup -f`
losetup $DST_LOOP $DST_IMG

PARTITION=`kpartx -l $DST_LOOP | awk '{ print $1 }'`
PARTITION=/dev/mapper/$PARTITION
kpartx -as $DST_LOOP
DST_LOOP_P=`losetup -f`

cecho "Creating ext3 filesystem."
echo 'y' | mkfs.ext3 $PARTITION
cecho "Setting label 'root'."
tune2fs $PARTITION -L root

cecho "Mounting new image."
DST_DIR=`mktemp -d`
mount -o loop $PARTITION $DST_DIR

cecho "Mounting old image."
SRC_LOOP=`losetup -f`
losetup $SRC_LOOP $SRC_IMG

PARTITION=`kpartx -l $SRC_LOOP | awk '{ print $1 }'`
PARTITION=/dev/mapper/$PARTITION
kpartx -as $SRC_LOOP

SRC_DIR=`mktemp -d`
mount -o loop $PARTITION $SRC_DIR

# Copy files
cecho "Copying files."
( cd $SRC_DIR && tar -cf - . ) | ( cd $DST_DIR && tar -xpf -)


cecho "Running grub-install"

cat <<DEVICEMAP > $DST_DIR/boot/grub/device.map 
(hd0)   $DST_LOOP
(hd0,1) $DST_LOOP_P
DEVICEMAP

grub-install --no-floppy --recheck --root-directory=$DST_DIR --modules=part_msdos  $DST_LOOP

cecho "Clean."
umount $SRC_DIR
sleep 1s
kpartx -ds $SRC_LOOP
sleep 1s
losetup -d $SRC_LOOP
sleep 1s
rmdir $SRC_DIR

umount $DST_DIR
sleep 1s
kpartx -ds $DST_LOOP
sleep 1s
losetup -d $DST_LOOP
sleep 1s
rmdir $DST_DIR

rm -f $SRC_IMG
cecho "Done."

EOF


trap ":" EXIT
set +e
cleanup
chmod a+x $conpaas_resize
/bin/bash $conpaas_resize $FILENAME

rm -f $conpaas_resize
