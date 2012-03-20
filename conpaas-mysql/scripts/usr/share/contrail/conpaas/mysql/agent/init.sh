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
apt-get install -y unzip python python-mysqldb python-pycurl python-dev python-setuptools python-pip subversion mysql-server supervisor
# Install conpaas-mysql
apt-get install conpaas-mysql

#cd /root
#svn co svn://svn.forge.objectweb.org/svnroot/contrail/trunk/conpaas/conpaas-mysql conpaassql
#cd conpaassql
#make build
#make install

# This is where it is installed
VERSION="0.1"
PACKAGE="/usr/lib/python2.6/site-packages/conpaassql_server-$VERSION-py2.6.egg"
EXEC="conpaas/mysql/server/manager/server.py"
CONF="/etc/contrail/conpaas/conpaas-mysql-agent.cnf"
RUN_SCRIPT="/usr/share/contrail/conpaas/mysql/conpaas-mysql-agent-server"
CONF_WHOLE_PATH="$CONF"
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

cat >  $CONF_WHOLE_PATH << EOF
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
agent_port=$PORT
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

nohup $RUN_SCRIPT $IP_PUBLIC $PORT $CONF_WHOLE_PATH &
