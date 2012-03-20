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

# Insert Contrail unstable repo
cat >> /etc/apt/sources.list << EOF
deb http://contrail.ow2.org/repositories/binaries/testing/Debian_6.0/ ./
EOF

cat > /root/key << EOF
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.5 (GNU/Linux)

mQGiBE85LAYRBADEYEs3No4mXHRScVtYDUTCkvijA2ZqXgF29MQpBrm2qAi26ato
zpxzTyuY9dPBsjjmfDJWjg3yi6RT6VVdNxmCwuqv7WsTLLq9bOb73v43OA4HtF0K
6lqGsMIrYifY3qeiSZlzw4IjfE3A9sJ5MXPf3a6lJC7jR51GuS5SnvHaLwCgjSOI
au29uH7H3+8bhNXKeiBaNwUD/2JeQqKGuRg64r5XlgsSerYk/aQiU6lrOogVFE9C
ovNb5zFrjb/WAWhzZR6pFKrkObySH9lPUif2Z707KfJMsLuNfT/ySf4NdVMkWBpr
uczEohjXlzq2gBjhd7R61da2msxT6uy6KHnvBRB92CGNmHgHFdXDak289suc/HTY
6ct3A/0fDkN5AmGnbQkl70HkMxJDcWBLWHZHBy4jW2jdBYP3aw9+xnVuuJqLiDlG
76QWQ898uy/oH37Fuofy9QXKY5rX+6+PE4tLG03YidglcPVnJN9u0ytn0Ae3T3zR
LqOBjs/wA5W5DDT3pVBuF2JvZqvs/ztxaS3VNgtoCBmTGXDYmLQ8aG9tZTpjb250
cmFpbCBPQlMgUHJvamVjdCA8aG9tZTpjb250cmFpbEBidWlsZC5vcGVuc3VzZS5v
cmc+iGYEExECACYFAk85LAYCGwMFCQQesAAGCwkIBwMCBBUCCAMEFgIDAQIeAQIX
gAAKCRBtf1QFRtf7grmeAJ4vBCts/3rJcsldsk0tc2kyFxyR4ACbBGLkLyvW9sRC
VuxbPZNyRImlIjiIRgQTEQIABgUCTzksBgAKCRA7MBG3a51lI0+pAKCEXuxaMDTm
NZlPcEWri4JLRWyJzwCbBC3fwmDmtQTYY0EVIi/VUFg1z7o=
=RfsE
-----END PGP PUBLIC KEY BLOCK-----
EOF

sudo apt-key add /root/key

apt-get update
apt-get install -y unzip python python-mysqldb python-pycurl python-dev python-setuptools python-pip subversion
# Install conpaas-mysql
apt-get install conpaas-mysql

#cd /root
#svn co svn://svn.forge.objectweb.org/svnroot/contrail/trunk/conpaas/conpaas-mysql conpaassql
#cd conpaassql
#python setup.py bdist_egg
#easy_install dist/conpaas*
#make install

# This is where it is installed
VERSION="0.1"
PACKAGE="/usr/lib/python2.6/site-packages/conpaassql_server-${VERSION}-py2.6.egg"
EXEC="conpaas/mysql/server/manager/server.py"
CONF="/etc/contrail/conpaas/conpaas-mysql-manager.cnf"
RUN_SCRIPT="/usr/share/contrail/conpaas/mysql/conpaas-mysql-manager-server"
CONF_WHOLE_PATH="${CONF}"
PORT=50000

cat > ${CONF_WHOLE_PATH} << EOF
[iaas]
DRIVER=OPENNEBULA_XMLRPC
OPENNEBULA_URL= http://10.30.1.14:2633/RPC2
OPENNEBULA_USER = oneadmin
OPENNEBULA_PASSWORD=oneadmin
OPENNEBULA_IMAGE_ID =  221
OPENNEBULA_SIZE_ID = 1
OPENNEBULA_NETWORK_ID = 205
OPENNEBULA_NETWORK_GATEWAY=$IP_GATEWAY
OPENNEBULA_NETWORK_NAMESERVER=$NAMESERVER

[manager]
find_existing_agents = true
logfile=/var/log/conpaassql-stdout.log
poll_agents_timer=10

[onevm_agent_template]
FILENAME=/usr/share/contrail/conpaas/mysql/agent/agent.template
USERDATA=/usr/share/contrail/conpaas/mysql/agent/init.sh
NAME=conpaassql_server
CPU=0.2
MEM_SIZE=256
DISK=readonly=no
OS=arch=x86_64,boot=hd
IMAGE_ID=221
NETWORK_ID=205
CONTEXT=ip_gateway="$IP_GATEWAY",netmask="$NETMASK",nameserver="$NAMESERVER"
EOF

nohup ${RUN_SCRIPT} ${IP_PUBLIC} ${PORT} ${CONF_WHOLE_PATH} &
