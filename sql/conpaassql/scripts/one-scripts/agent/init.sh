#!/bin/bash

if [ -f /mnt/context.sh ]; then
  . /mnt/context.sh
fi

ifconfig eth0 $IP_PRIVATE netmask $NETMASK
route add default gw $IP_GATEWAY eth0
echo nameserver $NAMESERVER > /etc/resolv.conf

# installation
apt-get update
apt-get install -y unzip python python-mysqldb python-pycurl python-dev python-setuptools python-pip subversion mysql-server

cd /root
svn co svn://svn.forge.objectweb.org/svnroot/contrail/trunk/conpaas/sql/conpaassql
cd conpaassql
python setup.py bdist_egg
easy_install dist/conpaas*

cat >  /root/conpaassql/src/conpaas/mysql/server/agent/configuration.cnf << EOF
[MySQL_root_connection]
location=
password=contrail
username=root

[MySQL_configuration]
my_cnf_file=/etc/mysql/my.cnf
path_mysql_ssr=/etc/init.d/mysql
EOF

# Run the agent command in the background

nohup python /root/conpaassql/src/conpaas/mysql/server/agent/server.py -c /root/conpaassql/src/conpaas/mysql/server/agent/configuration.cnf 1> /var/log/conpaassql-stdout.log 2> /var/log/conpaassql-err.log &
