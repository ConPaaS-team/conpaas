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
OPENNEBULA_URL=$ONE_URL
OPENNEBULA_USER=$ONE_USERNAME
OPENNEBULA_PASSWORD=$ONE_PASSWORD
OPENNEBULA_IMAGE_ID = $AGENT_IMAGE_ID
OPENNEBULA_SIZE_ID = 1
OPENNEBULA_NETWORK_ID = $AGENT_NETWORK_ID
OPENNEBULA_NETWORK_GATEWAY=$IP_GATEWAY
OPENNEBULA_NETWORK_NAMESERVER=$NAMESERVER

[manager]
find_existing_agents = true

[onevm_agent_template]
FILENAME=/root/conpaassql/bin/agent.template
NAME=conpaassql_server
CPU=0.2
MEM_SIZE=256
DISK=bus=virtio,readonly=no,driver=qcow2,dev_prefix=vd,target=vda
OS=arch=x86_64,boot=hd
IMAGE_ID=$AGENT_IMAGE_ID
NETWORK_ID=$AGENT_NETWORK_ID
CONTEXT=vmid=$VMID,vmname=$NAME,ip_private="$NIC[IP, NETWORK=$NETWORK"]",ip_gateway="$IP_GATEWAY",netmask="$NETMASK",nameserver="$NAMESERVER",target=sdc,files=$AGENT_FILES
EOF

nohup python /root/conpaassql/src/conpaas/mysql/server/manager/server.py -c /root/conpaassql/src/conpaas/mysql/server/manager/configuration.cnf 1> /var/log/conpaassql-stdout.log 2> /var/log/conpaassql-err.log &
