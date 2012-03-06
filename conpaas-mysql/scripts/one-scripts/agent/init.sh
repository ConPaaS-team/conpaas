#!/bin/bash

if [ -f /mnt/context.sh ]; then
  . /mnt/context.sh
fi

ifconfig eth0 $IP_PUBLIC netmask $NETMASK
route add default gw $IP_GATEWAY eth0
echo nameserver $NAMESERVER > /etc/resolv.conf

# installation
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y unzip python python-mysqldb python-pycurl python-dev python-setuptools python-pip subversion mysql-server supervisor

cd /root
svn co svn://svn.forge.objectweb.org/svnroot/contrail/trunk/conpaas/conpaas-mysql conpaassql
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

cat >  /root/conpaassql/config/agent/configuration.cnf << EOF
[MySQL_root_connection]
location=localhost
password=contrail
username=contrail

[MySQL_configuration]
my_cnf_file=/etc/mysql/my.cnf

[supervisor]
user = root
password = root
port = 9001

[ConPaaSSQL]
agent_interface=0.0.0.0
agent_port=60000
manager_ip=$MANAGER_IP
manager_port=$MANAGER_PORT
vm_id=$VMID
vm_name=$NAME
EOF

# Run the agent command in the background
/etc/init.d/mysql stop
sleep 5
service supervisor stop
sleep 5
service supervisor start
sleep 5

nohup python /root/conpaassql/src/conpaas/mysql/server/agent/server.py -p 60000 -b $IP_PUBLIC -c /root/conpaassql/config/agent/configuration.cnf 1> /var/log/conpaassql-stdout.log 2> /var/log/conpaassql-err.log &
