#!/bin/bash
 
if [ -f /mnt/context.sh ]; then
  . /mnt/context.sh
fi

ifconfig eth0 $IP_PUBLIC netmask $NETMASK
route add default gw $IP_GATEWAY eth0
echo nameserver $NAMESERVER > /etc/resolv.conf

# installation
apt-get update
apt-get install -y unzip python python-mysqldb python-pycurl python-dev python-setuptools python-pip subversion

cd /root
svn co svn://svn.forge.objectweb.org/svnroot/contrail/trunk/conpaas/conpaas-mysql conpaassql
cd conpaassql
python setup.py bdist_egg
easy_install dist/conpaas*

cat > /root/conpaassql/src/conpaas/mysql/server/manager/configuration.cnf << EOF
[iaas]
DRIVER=OPENNEBULA_XMLRPC
OPENNEBULA_URL=http://10.30.1.14:2633/RPC2
OPENNEBULA_USER=oneadmin
OPENNEBULA_PASSWORD=oneadmin
OPENNEBULA_IMAGE_ID = 221
OPENNEBULA_SIZE_ID = 1
OPENNEBULA_NETWORK_ID = 205
OPENNEBULA_NETWORK_GATEWAY=$IP_GATEWAY
OPENNEBULA_NETWORK_NAMESERVER=$NAMESERVER

[manager]
find_existing_agents = true
logfile=/var/log/conpaassql-stdout.log

[onevm_agent_template]
FILENAME=/root/conpaassql/scripts/one-scripts/agent/agent.template
USERDATA=/root/conpaassql/scripts/one-scripts/agent/init.sh
NAME=conpaassql_server
CPU=0.2
MEM_SIZE=256
DISK=readonly=no
OS=arch=x86_64,boot=hd
IMAGE_ID=221
NETWORK_ID=205
CONTEXT=vmid=$VMID,vmname=$NAME,ip_public="$NIC[IP, NETWORK=\"private-lan\"]",ip_gateway="$IP_GATEWAY",netmask="$NETMASK",nameserver="$NAMESERVER",userdata=$AGENT_USER_DATA
EOF

nohup python /root/conpaassql/src/conpaas/mysql/server/manager/server.py -p 50000 -b $IP_PUBLIC -c /root/conpaassql/src/conpaas/mysql/server/manager/configuration.cnf 1> /var/log/conpaassql-stdout.log 2> /var/log/conpaassql-err.log &
