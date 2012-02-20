#!/bin/bash
 
if [ -f /mnt/context.sh ]; then
  . /mnt/context.sh
fi

ifconfig eth0 $IP_PRIVATE netmask $NETMASK
route add default gw $IP_GATEWAY eth0
echo nameserver $NAMESERVER > /etc/resolv.conf

# installation
apt-get update
apt-get install -y unzip python python-mysqldb python-pycurl python-dev python-setuptools python-pip subversion

cd /root
svn co svn://svn.forge.objectweb.org/svnroot/contrail/trunk/conpaas/sql/conpaassql
cd conpaassql
python setup.py bdist_egg
easy_install dist/conpaas*

cat > /root/conpaassql/src/conpaas/mysql/server/manager/configuration.cnf << EOF
[iaas]
DRIVER=OPENNEBULA_XMLRPC
OPENNEBULA_URL=http://10.30.1.14:2633/RPC2
OPENNEBULA_USER=oneadmin
OPENNEBULA_PASSWORD=oneadmin
OPENNEBULA_IMAGE_ID = 205
OPENNEBULA_SIZE_ID = 1
OPENNEBULA_NETWORK_ID = 205
OPENNEBULA_NETWORK_GATEWAY = 10.1.0.254
OPENNEBULA_NETWORK_NAMESERVER = 10.1.0.254

[manager]
find_existing_agents = true

[onevm_agent_template]
FILENAME=/root/conpaassql/bin/agent.template
NAME=conpaassql_server
CPU=0.2
MEM_SIZE=256
DISK=bus=scsi,readonly=no
OS=arch=i686,boot = hd, root = hda
IMAGE_ID=205
NETWORK_ID=205
CONTEXT=target=sdc,files=/home/contrail/sql/agent/install.sh
EOF

nohup python /root/conpaassql/src/conpaas/mysql/server/manager/server.py -c /root/conpaassql/src/conpaas/mysql/server/manager/configuration.cnf 1> /var/log/conpaassql-stdout.log 2> /var/log/conpaassql-err.log &
