#!/bin/bash

if [ -f /mnt/context.sh ]; then
  . /mnt/context.sh
fi

ifconfig eth0 $IP_PRIVATE netmask $NETMASK
route add default gw $IP_GATEWAY eth0
echo nameserver $NAMESERVER > /etc/resolv.conf

# installation
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y unzip python python-mysqldb python-pycurl python-dev python-setuptools python-pip subversion mysql-server supervisor

cd /root
svn co svn://svn.forge.objectweb.org/svnroot/contrail/trunk/conpaas/sql/conpaassql
cd conpaassql
python setup.py bdist_egg
easy_install dist/conpaas*

cat >  /etc/supervisor/conf.d/mysql.conf << EOF
[program:mysqld]
command=/usr/sbin/mysqld
autostart=true
autorestart=true
EOF

cat >>  /etc/supervisor/supervisord.conf << EOF
[inet_http_server]
port = 0.0.0.0:9001
username = root
password = root
EOF

cat >  /root/conpaassql/src/conpaas/mysql/server/agent/configuration.cnf << EOF
[MySQL_root_connection]
location=
password=contrail
username=root

[MySQL_configuration]
my_cnf_file=/etc/mysql/my.cnf

[supervisor]
user = root
password = root
port = 9001

[ConPaaSSQL]
agent_interface=0.0.0.0
agent_port=60000
manager_ip=0.0.0.0
manager_port=50000
vm_id=10
vm_name=agent10
EOF

# Run the agent command in the background

service supervisor stop
service supervisor start

nohup python /root/conpaassql/src/conpaas/mysql/server/agent/server.py -c /root/conpaassql/src/conpaas/mysql/server/agent/configuration.cnf 1> /var/log/conpaassql-stdout.log 2> /var/log/conpaassql-err.log &
