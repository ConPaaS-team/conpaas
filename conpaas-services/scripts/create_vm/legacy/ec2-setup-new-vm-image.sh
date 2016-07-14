#!/bin/bash
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
# This script should be run inside a VM to install all dependencies needed by
# the ConPaaSWeb project. The resulting system installation is capable of
# hosting any of the ConPaaSWeb components such as web servers, proxies and
# PHP processes.
# 
##


PREFIX=/
DEBIAN_DIST=squeeze

function install_deb() {
  sed --in-place '/non-free/!s/main/main non-free/' /etc/apt/sources.list
  sed --in-place '/contrib/!s/main/main contrib/' /etc/apt/sources.list
  apt-get -y update
 
  export LC_ALL=C
  # set keyboard layout
  echo "debconf keyboard-configuration/variant  select  USA" | debconf-set-selections

  # install and configure locale 
  apt-get -f -y install locales
  sed --in-place 's/^# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen
  locale-gen
  update-locale LANG=en_US.UTF-8

  # install packages
  apt-get -f -y install openssh-server curl \
        python python-pycurl python-cheetah python-openssl \
        python-m2crypto python-mysqldb python-netaddr \
        nginx tomcat6-user memcached ganglia-monitor gmetad rrdtool logtail \
        make gcc g++ erlang ant libxslt1-dev yaws subversion git \
        xvfb xinit unzip
  update-rc.d memcached disable
  update-rc.d nginx disable
  update-rc.d yaws disable
  update-rc.d gmetad disable
  update-rc.d ganglia-monitor disable

  # pre-accept sun-java6 licence
  echo "debconf shared/accepted-sun-dlj-v1-1 boolean true" | debconf-set-selections
  DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade \
        install mysql-server sun-java6-jdk
  update-rc.d mysql disable

  # add dotdeb repo for php fpm
  echo "deb http://packages.dotdeb.org $DEBIAN_DIST all" >> /etc/apt/sources.list
  wget -O - http://www.dotdeb.org/dotdeb.gpg 2>/dev/null | apt-key add -
  apt-get -y update
  apt-get -f -y --no-install-recommends --no-upgrade install php5-fpm php5-curl \
              php5-mcrypt php5-mysql php5-odbc \
              php5-pgsql php5-sqlite php5-sybase php5-xmlrpc php5-xsl \
              php5-adodb php5-memcache php5-gd
  update-rc.d php5-fpm disable

  # remove dotdeb repo
  sed --in-place "s%deb http://packages.dotdeb.org $DEBIAN_DIST all%%" /etc/apt/sources.list

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
  
  # recent versions of iceweasel and chrome
  echo "deb http://backports.debian.org/debian-backports $DEBIAN_DIST-backports main" >> /etc/apt/sources.list
  echo "deb http://mozilla.debian.net/ $DEBIAN_DIST-backports iceweasel-esr" >> /etc/apt/sources.list
  echo "deb http://dl.google.com/linux/deb/ stable main" >> /etc/apt/sources.list

  apt-get -y update
  apt-get -f -y --force-yes install -t $DEBIAN_DIST-backports iceweasel
  apt-get -f -y --force-yes install google-chrome-stable

  # add cloudera repo for hadoop
  echo "deb http://archive.cloudera.com/debian $DEBIAN_DIST-cdh3 contrib" >> /etc/apt/sources.list
  wget -O - http://archive.cloudera.com/debian/archive.key 2>/dev/null | apt-key add -
  apt-get -y update
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
  sed --in-place "s%deb http://archive.cloudera.com/debian $DEBIAN_DIST-cdh3 contrib%%" /etc/apt/sources.list

  # add scalaris repo
  echo "deb http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0 /" >> /etc/apt/sources.list
  wget -O - http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0/Release.key 2>/dev/null | apt-key add -
  apt-get -y update
  apt-get -f -y --no-install-recommends --no-upgrade install scalaris screen
  update-rc.d scalaris disable
  # remove scalaris repo
  sed --in-place 's%deb http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0 /%%' /etc/apt/sources.list

  # add xtreemfs repo
  echo "deb http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0 /" >> /etc/apt/sources.list
  wget -O - http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0/Release.key 2>/dev/null | apt-key add -
  apt-get -y update
  apt-get -f -y --no-install-recommends --no-upgrade install xtreemfs-server xtreemfs-client xtreemfs-tools
  update-rc.d xtreemfs-osd disable
  update-rc.d xtreemfs-mrc disable
  update-rc.d xtreemfs-dir disable
  # remove xtreemfs repo
  sed --in-place 's%deb http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0 /%%' /etc/apt/sources.list
  apt-get -y update

  echo "deb http://www.grid-appliance.org/files/packages/deb/ stable contrib" >> /etc/apt/sources.list
  wget -O - http://www.grid-appliance.org/files/packages/deb/repo.key | apt-key add -
  apt-get update
  apt-get -f -y install ipop

  # remove cached .debs from /var/cache/apt/archives to save disk space
  apt-get clean

  # install latest nginx (1.2.2) and other packages required by CDS
  DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade \
      install libpcre3-dev libssl-dev libgeoip-dev libperl-dev
  wget http://nginx.org/download/nginx-1.2.2.tar.gz
  tar xzf nginx-1.2.2.tar.gz
  cd nginx-1.2.2
  ./configure --sbin-path=/usr/sbin/nginx --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-client-body-temp-path=/var/lib/nginx/body --http-fastcgi-temp-path=/var/lib/nginx/fastcgi --http-log-path=/var/log/nginx/access.log --http-proxy-temp-path=/var/lib/nginx/proxy --lock-path=/var/lock/nginx.lock --pid-path=/var/run/nginx.pid --with-debug --with-http_dav_module --with-http_flv_module --with-http_geoip_module --with-http_gzip_static_module --with-http_realip_module --with-http_stub_status_module --with-http_ssl_module --with-http_sub_module --with-ipv6 --with-mail --with-mail_ssl_module --with-http_perl_module
  make
  make install
  cd ..
  rm -rf nginx-1.2.2*

  # To allow contextualization to run after snapshotting this instance
  rm /var/lib/ec2-bootstrap/*
}

# Make swap partition to solve the map-reduce memory issues
# Note: TODO Temporary solution
dd if=/dev/zero of=/usr/local/swapfile bs=1M count=1024
chmod 600 /usr/local/swapfile
mkswap /usr/local/swapfile
swapon /usr/local/swapfile
echo "/usr/local/swapfile swap swap defaults 0 0" >> /etc/fstab

mkdir -p $PREFIX

install_deb

## install ec2 startup scripts
{
cat <<_EOF_
#!/bin/bash
### BEGIN INIT INFO
# Provides:          ec2-get-credentials
# Required-Start:    \$remote_fs
# Required-Stop:
# Should-Start:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Retrieve the ssh credentials and add to authorized_keys
# Description:
#
### END INIT INFO
_EOF_
wget -O - https://ec2ubuntu.googlecode.com/svn/trunk/etc/init.d/ec2-get-credentials
} >/etc/init.d/ec2-get-credentials

{
cat <<_EOF_
#!/bin/sh
### BEGIN INIT INFO
# Provides:          ec2-ssh-host-key-gen
# Required-Start:    \$remote_fs
# Required-Stop:
# Should-Start:      sshd
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Generate new ssh host keys on first boot
# Description:       Re-generates the ssh host keys on every
#                    new instance (i.e., new AMI). If you want
#                    to keep the same ssh host keys for rebundled
#                    AMIs, then disable this before rebundling
#                    using a command like:
#                       rm -f /etc/rc?.d/S*ec2-ssh-host-key-gen
#
### END INIT INFO
_EOF_
wget -O - https://ec2ubuntu.googlecode.com/svn/trunk/etc/init.d/ec2-ssh-host-key-gen
} >/etc/init.d/ec2-ssh-host-key-gen

{
cat <<_EOF_
#!/bin/bash
### BEGIN INIT INFO
# Provides:          ec2-run-user-data
# Required-Start:    \$all
# Required-Stop:
# Should-Start:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Run instance user-data if it looks like a script.
# Description:       Only retrieves and runs the user-data script once per
#                    instance. If you want the user-data script to run again
#                    (e.g., on the next boot) then add this command in the
#                    user-data script:
#                    rm -f /var/ec2/ec2-run-user-data.*
### END INIT INFO
_EOF_
wget -O - https://ec2ubuntu.googlecode.com/svn/trunk/etc/init.d/ec2-run-user-data
} >/etc/init.d/ec2-run-user-data

## fix gzip detection in ec2-run-user-data
## "file -bi" output looks like "application/x-gzip; charset=binary"
## "file -b --mime-type" output looks like "application/x-gzip"
sed -i -e 's/$(file -bi /$(file -b --mime-type /' /etc/init.d/ec2-run-user-data

## enable ec2 startup scripts
chmod a+x /etc/init.d/ec2-*
update-rc.d ec2-get-credentials defaults
update-rc.d ec2-ssh-host-key-gen defaults
update-rc.d ec2-run-user-data defaults

# Never run fsck
tune2fs -i 0 /dev/sda1
