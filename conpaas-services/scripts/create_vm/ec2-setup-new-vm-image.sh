#!/bin/bash
# Copyright (C) 2010-2011 Contrail consortium.
# 
# This file is part of ConPaaS, an integrated runtime environment 
# for elastic cloud applications.
# 
# ConPaaS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ConPaaS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.

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
  apt-get -f -y update
 
  # install and configure locale 
  export LC_ALL=C
  apt-get -f -y install locales
  sed --in-place 's/^# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen
  locale-gen
  update-locale LANG=en_US.UTF-8

  # install packages
  apt-get -f -y install openssh-server \
        python python-pycurl python-cheetah nginx tomcat6-user memcached \
        make gcc g++ erlang ant libxslt1-dev yaws subversion
  update-rc.d -f memcached remove
  update-rc.d -f nginx remove
  /etc/init.d/memcached stop
  /etc/init.d/nginx stop
  update-rc.d -f yaws remove
  /etc/init.d/yaws stop

  # pre-accept sun-java6 licence
  echo "debconf shared/accepted-sun-dlj-v1-1 boolean true" | debconf-set-selections
  DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade \
        install mysql-server sun-java6-jdk
  update-rc.d -f mysql remove
  /etc/init.d/mysql stop

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

  # add scalaris repo
  echo "deb http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0 /" >> /etc/apt/sources.list
  wget -O - http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0/Release.key 2>/dev/null | apt-key add -
  apt-get -f -y update
  apt-get -f -y --no-install-recommends --no-upgrade install scalaris screen
  update-rc.d -f scalaris remove
  # remove scalaris repo
  sed --in-place 's%deb http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0 /%%' /etc/apt/sources.list

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
  # remove cached .debs from /var/cache/apt/archives to save disk space
  apt-get clean
	
  # To allow copntextualization to run after snapshotting this instance
  rm /var/lib/ec2-bootstrap/*
}

mkdir -p $PREFIX

install_deb
