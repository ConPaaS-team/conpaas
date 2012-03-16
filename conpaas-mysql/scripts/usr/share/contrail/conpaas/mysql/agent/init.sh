#!/bin/bash

if [ -f /mnt/context.sh ]; then
  . /mnt/context.sh
fi

/sbin/ifconfig eth0 $IP_PUBLIC
/sbin/ip route add default via $IP_GATEWAY
echo "nameserver $NAMESERVER" > /etc/resolv.conf

# fix dns record
grep -q 130.73.121.1 /etc/resolv.conf && echo "nameserver 130.73.79.13" > /etc/resolv.conf

# installation
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y unzip python python-mysqldb python-pycurl python-dev python-setuptools python-pip subversion mysql-server supervisor

cd /root
svn co svn://svn.forge.objectweb.org/svnroot/contrail/trunk/conpaas/conpaas-mysql conpaassql
cd conpaassql
make build
make install

# This is where it is installed
VERSION="0.1"
PACKAGE="/usr/local/lib/python2.6/dist-packages/conpaassql_server-${VERSION}-py2.6.egg"
EXEC="conpaas/mysql/server/manager/server.py"
CONF="/etc/contrail/conpaas/conpaas-mysql-agent.cnf"
RUN_SCRIPT="${PACKAGE}/usr/share/contrail/conpaas/mysql/conpaas-mysql-agent-server"
CONF_WHOLE_PATH="${PACKAGE}${CONF}"
PORT=60000

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

cat >  ${CONF_WHOLE_PATH} << EOF
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
agent_port= ${PORT}
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

chmod +x ${RUN_SCRIPT}
nohup ${RUN_SCRIPT} ${IP_PUBLIC} ${PORT} ${CONF_WHOLE_PATH} &
