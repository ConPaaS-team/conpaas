#! /bin/bash -x

set -e

# default version
CPS_VERSION=1.3.x

# created user
USERNAME=xcv
PASSWORD=xcv

# default credits for ConPaaS web frontend
USER_CREDITS=5000

IPOP_TARBALL=ipop.zip
DEFAULT_IPOP=false
#VPN_BASE_NETWORK=192.168.0.0
#VPN_NETMASK=255.255.0.0
VPN_BASE_NETWORK=172.24.0.0
VPN_NETMASK=255.248.0.0
BRUNET_NAMESPACE=real_ufl_test0_04
BOOTSTRAP_PORT=40000

# deploy Debian image
DEPLOY="yes"


function display_help()
{
  echo    "Grid 5000 script to deploy ConPaaS using the provided clouds."
  echo    "Usage: $0 [-h|v] <list of \"cloud_name=frontent\">"
  echo -e "\t-h\tDisplay this help and exit"
  echo -e "\t-v version\tSet the ConPaaS version to install"
  echo -e "\t-n\tDo not deploy the Debian image"
if $DEFAULT_IPOP
then
  ENABLE_IPOP_DOC="(default)"
else
  DISABLE_IPOP_DOC="(default)"
fi
  echo -e "\t-i\tEnable IPOP ${ENABLE_IPOP_DOC}"
  echo -e "\t-j\tDisable IPOP ${DISABLE_IPOP_DOC}"
  exit 0
}

function error()
{
  echo "Error:" $*
  exit 1
}


if [ -z "$OAR_JOBID" ]
then
  error "This script must be run inside an interactive OAR reservation (missing env. var. OAR_JOBID)."
fi

ENABLE_IPOP=$DEFAULT_IPOP
while getopts hijnv: option
do
  case $option in
    h) display_help;;
    n) DEPLOY="no";;
    v) CPS_VERSION=$OPTARG;;
    i) ENABLE_IPOP=true;;
    j) ENABLE_IPOP=false;;
  esac
done
shift $(($OPTIND - 1))
CLOUDS_ARG=$@

if [ -z "$CLOUDS_ARG" ]
then
  error "Missing at least one cloud description."
fi

declare -A CLOUDS
for cloud_front in $CLOUDS_ARG
do
  CLOUDS[${cloud_front/=*/}]=${cloud_front/*=/}
done

for cloud in ${CLOUDS[@]}
do
  host $cloud > /dev/null 2>&1
  if [ $? -ne 0 ]
  then
    error "Unknown host \"$cloud\""
  fi
done

DEFAULT_CLOUD=$(echo ${!CLOUDS[@]} | cut -d ' ' -f 1)


CPS_DIR_SRC=cpsdirector-$CPS_VERSION.tar.gz
CPS_LIB_SRC=cpslib-$CPS_VERSION.tar.gz
CPS_CLIENT_SRC=cpsclient-$CPS_VERSION.tar.gz
CPS_FRONTEND_SRC=cpsfrontend-$CPS_VERSION.tar.gz
CPS_TOOLS_SRC=cps-tools-$CPS_VERSION.tar.gz
CPS_IMAGE=conpaas.img

echo "Installing ConPaaS $CPS_VERSION..."


# reserve one machine, two cores: one for the director, one for the frontend
## configure director.cfg with the N clouds

CPS_NODE=$(cat $OAR_FILE_NODES | sort -u)
BOOTSTRAP_IP=$(host $CPS_NODE | cut -d ' ' -f 4)

#---------------------
# Get info from clouds
#---------------------


declare -A ONE_USER
declare -A ONE_PASSWORD
declare -A ONE_INST_TYPE
declare -A ONE_OS_ARCH
declare -A ONE_OS_ROOT
declare -A ONE_DISK_TARGET
declare -A ONE_CONTEXT_TARGET
declare -A ONE_IMAGE_ID
declare -A ONE_NET_ID
declare -A ONE_GATEWAY
declare -A ONE_NETMASK
declare -A ONE_DNS
declare -A ONE_API_VERSION
declare -A CPS_DRIVER

function get_one_api_version()
{
  version=$(echo $1 | sed "s/\([^\.]*\.[^\.]*\)\..*/\1/" | tr -d '.')
  if [ $version -ge "38" ]
  then
      api_version="3.8"
  elif [ $version -ge "32" ]
  then
      api_version="3.2"
  elif [ $version -ge "30" ]
  then
      api_version="3.0"
  else
      api_version="2.2"
  fi
  echo $api_version
}
      


for CLOUD in ${!CLOUDS[@]}
do
  echo "Getting configuration from cloud $CLOUD..."
  FRONTEND=${CLOUDS[$CLOUD]}

  CPS_DRIVER[$CLOUD]=opennebula
  ONE_USER[$CLOUD]=oneadmin
  ONE_PASSWORD[$CLOUD]=password
  ONE_INST_TYPE[$CLOUD]=small
  ONE_OS_ARCH[$CLOUD]=x86_64
  ONE_OS_ROOT[$CLOUD]=hda
  ONE_DISK_TARGET[$CLOUD]=hda
  ONE_CONTEXT_TARGET[$CLOUD]=hdc

  ## Find conpaas image id
  ONE_IMAGE_LIST=oneimage-list-$CLOUD.log
  ssh root@$FRONTEND "oneimage list" > $ONE_IMAGE_LIST
  ONE_IMAGE_ID[$CLOUD]=$(grep 'conpa' $ONE_IMAGE_LIST | head -n 1 | awk '{print $1}')

  ### Find configuration of network id 0
  ONE_VNET_SHOW=onevnet-show-$CLOUD.log
  ONE_NET_ID[$CLOUD]=0
  ssh root@$FRONTEND "onevnet show ${ONE_NET_ID[$CLOUD]}" > $ONE_VNET_SHOW
  ONE_GATEWAY[$CLOUD]=$(grep 'GATEWAY=' $ONE_VNET_SHOW | sed 's/GATEWAY="\(.*\)"/\1/')
  ONE_NETMASK[$CLOUD]=$(grep 'NETWORK_MASK=' $ONE_VNET_SHOW | sed 's/NETWORK_MASK="\(.*\)"/\1/')
  ONE_DNS[$CLOUD]=$(grep 'DNS=' $ONE_VNET_SHOW | sed 's/DNS="\(.*\)"/\1/')

  ### Find OpenNebula version
  ONE_VERSION_LOG=one-version-$CLOUD.log
  ssh root@$FRONTEND "oneuser -V | egrep 'OpenNebula\s*[0-9]'" > $ONE_VERSION_LOG
  ONE_VERSION=$(sed 's/^.*\([0-9]\+\.[0-9]\+\.[0-9]\+\)/\1/' $ONE_VERSION_LOG)
  ONE_API_VERSION[$CLOUD]=$(get_one_api_version $ONE_VERSION)
done

## Generate ConPaaS configuration for extra clouds

EXTRA_CLOUDS=""
EXTRA_CLOUDS_CONFIG=""
for CLOUD in ${!CLOUDS[@]}
do
  if [ "$CLOUD" = "$DEFAULT_CLOUD" ]
  then
    continue
  fi
  EXTRA_CLOUDS="$EXTRA_CLOUDS,$CLOUD"
  EXTRA_CLOUDS_CONFIG="$EXTRA_CLOUDS_CONFIG

[$CLOUD]
URL = http://${CLOUDS[$CLOUD]}:4567
DRIVER = ${CPS_DRIVER[$CLOUD]}
USER = ${ONE_USER[$CLOUD]}
PASSWORD = ${ONE_PASSWORD[$CLOUD]}
INST_TYPE = ${ONE_INST_TYPE[$CLOUD]}
IMAGE_ID = ${ONE_IMAGE_ID[$CLOUD]}
OS_ARCH = ${ONE_OS_ARCH[$CLOUD]}
OS_ROOT = ${ONE_OS_ROOT[$CLOUD]}
DISK_TARGET = ${ONE_DISK_TARGET[$CLOUD]}
CONTEXT_TARGET = ${ONE_CONTEXT_TARGET[$CLOUD]}
NET_ID = ${ONE_NET_ID[$CLOUD]}
NET_GATEWAY = ${ONE_GATEWAY[$CLOUD]}
NET_NETMASK = ${ONE_NETMASK[$CLOUD]}
NET_NAMESERVER = ${ONE_DNS[$CLOUD]}
XMLRPC = http://${CLOUDS[$CLOUD]}:2633/RPC2
OPENNEBULA_VERSION = ${ONE_API_VERSION[$CLOUD]}
"
done


if [ -n "$EXTRA_CLOUDS" ]
then
  # remove first comma
  EXTRA_CLOUDS=${EXTRA_CLOUDS:1}
fi

if [ "$DEPLOY" = "yes" ]
then
  # deploy a basic Debian image to run the director
  kadeploy3 -e wheezy-x64-base -f $OAR_FILE_NODES -k $HOME/.ssh/id_rsa.pub
fi


#------------------------------
# Install and configure ConPaaS
#------------------------------

scp $CPS_DIR_SRC      root@$CPS_NODE:
scp $CPS_LIB_SRC      root@$CPS_NODE:
scp $CPS_CLIENT_SRC   root@$CPS_NODE:
scp $CPS_FRONTEND_SRC root@$CPS_NODE:
scp $IPOP_TARBALL     root@$CPS_NODE:
scp $CPS_TOOLS_SRC    root@$CPS_NODE:

CPS_CONFIG_SCRIPT=cps-conf.sh
cat > $CPS_CONFIG_SCRIPT < /dev/null
chmod 755 $CPS_CONFIG_SCRIPT

cat > $CPS_CONFIG_SCRIPT <<EOF
#!/bin/bash -x

set -e

export http_proxy=http://proxy:3128
export https_proxy=http://proxy:3128
export ftp_proxy=http://proxy:3128

# quiet non interactive deb commands
export DEBIAN_FRONTEND=noninteractive

# install dependencies
apt-get -y update
apt-get -q -y install build-essential python-setuptools python-dev
apt-get -q -y install python-pycurl 
# apt-get -q -y install python-netaddr python-flask python-libcloud
apt-get -q -y install libapache2-mod-wsgi libcurl4-openssl-dev
apt-get -q -y install ntp

# stop Apache2, restart when director and frontend are installed and configured
service apache2 stop

# install the director
rm -rf ${CPS_DIR_SRC%.tar.gz}
rm -rf /etc/cpsdirector
tar -xaf $CPS_DIR_SRC
cd ${CPS_DIR_SRC%.tar.gz}

# cpslib has been copied locally
sed -i "s|dependency_links=\[ .*cpslib-|dependency_links=\[ '\$HOME/cpslib-|" setup.py

# do not interactively ask for the hostname (correctly detected by default)
sed -i '/try:/ { N ; /hostname = sys.argv\[1\]/ { N ; /except IndexError:/ { N ; s/^/#/ ; s/\n/\n#/g ; /$/ i print "ConPaaS hostname is %s" % hostname
 } } }' cpsconf.py

make install

# Configure ConPaaS

DIR_CFG_FILE=/etc/cpsdirector/director.cfg

##

sed -i '
s/# DRIVER = opennebula/DRIVER = ${CPS_DRIVER[$DEFAULT_CLOUD]}/
/The image ID (an integer)/ {N ; N ; N ; s/\n\s*#\?\s*IMAGE_ID =.*/\n\nIMAGE_ID = ${ONE_IMAGE_ID[$DEFAULT_CLOUD]}/}
/Your OpenNebula user name./ { N ; N ; s/\n\s*#\?\s*USER = /\n\nUSER = ${ONE_USER[$DEFAULT_CLOUD]}/ }
/Your OpenNebula password./ { N ; N ; s/\n\s*#\?\s*PASSWORD =/\n\nPASSWORD = ${ONE_PASSWORD[$DEFAULT_CLOUD]}/ }
s|^\s*#\?\s*URL =.*|URL = http://${CLOUDS[$DEFAULT_CLOUD]}:4567|
s/^\s*#\?\s*NET_ID =.*/NET_ID = ${ONE_NET_ID[$DEFAULT_CLOUD]}/
s/^\s*#\?\s*NET_GATEWAY =.*/NET_GATEWAY = ${ONE_GATEWAY[$DEFAULT_CLOUD]}/
s/^\s*#\?\s*NET_NETMASK =.*/NET_NETMASK = ${ONE_NETMASK[$DEFAULT_CLOUD]}/
s/^\s*#\?\s*NET_NAMESERVER =.*/NET_NAMESERVER = ${ONE_DNS[$DEFAULT_CLOUD]}/
s/^\s*#\?\s*INST_TYPE =.*/INST_TYPE = ${ONE_INST_TYPE[$DEFAULT_CLOUD]}/
s/^\s*#\?\s*OS_ARCH =.*/OS_ARCH = ${ONE_OS_ARCH[$DEFAULT_CLOUD]}/
s/^\s*#\?\s*OS_ROOT =.*/OS_ROOT = ${ONE_OS_ROOT[$DEFAULT_CLOUD]}/
s/^\s*#\?\s*DISK_TARGET =.*/DISK_TARGET = ${ONE_DISK_TARGET[$DEFAULT_CLOUD]}/
s/^\s*#\?\s*CONTEXT_TARGET =.*/CONTEXT_TARGET = ${ONE_CONTEXT_TARGET[$DEFAULT_CLOUD]}/
s|^\s*#\?\s*XMLRPC =.*|XMLRPC = http://${CLOUDS[$DEFAULT_CLOUD]}:2633/RPC2|
s/^\s*#\?\s*OPENNEBULA_VERSION =.*/OPENNEBULA_VERSION = ${ONE_API_VERSION[$DEFAULT_CLOUD]}/
' \$DIR_CFG_FILE

if $ENABLE_IPOP
then
  sed -i '
s/^\s*#\?\s*VPN/VPN/
s/VPN_BASE_NETWORK =.*/VPN_BASE_NETWORK = $VPN_BASE_NETWORK/
s/VPN_NETMASK =.*/VPN_NETMASK = $VPN_NETMASK/
s|VPN_BOOTSTRAP_NODES =.*|VPN_BOOTSTRAP_NODES = udp://$BOOTSTRAP_IP:$BOOTSTRAP_PORT|
' \$DIR_CFG_FILE
else
  sed -i '
s/^\s*VPN/# VPN/
s/VPN_BASE_NETWORK =.*/VPN_BASE_NETWORK =/
s/VPN_NETMASK =.*/VPN_NETMASK =/
s|VPN_BOOTSTRAP_NODES =.*|VPN_BOOTSTRAP_NODES =|
' \$DIR_CFG_FILE  
fi

if [ -n "$EXTRA_CLOUDS" ]
then
  sed -i 's/# OTHER_CLOUDS =.*/OTHER_CLOUDS = $EXTRA_CLOUDS/' \$DIR_CFG_FILE
  echo "$EXTRA_CLOUDS_CONFIG" >> \$DIR_CFG_FILE
fi

# Start ConPaaS in Apache 2

a2enmod ssl
a2ensite conpaas-director


# Install the command line ConPaaS client

cd \$HOME
easy_install $CPS_CLIENT_SRC


# Install the web frontend client

cd \$HOME

## clean previous version
rm -rf ${CPS_FRONTEND_SRC%.tar.gz}
rm -rf /var/www/conpaas
rm -f /etc/cpsdirector/{main.ini,welcome.txt}

apt-get -q -y install libapache2-mod-php5 php5-curl
cd \$HOME
tar -xaf $CPS_FRONTEND_SRC
cd ${CPS_FRONTEND_SRC%.tar.gz}
cp -a www/ /var/www/conpaas

cp conf/{main.ini,welcome.txt} /etc/cpsdirector/
sed -i '
s|logfile =.*|logfile = /tmp/conpaas-frontend.log|
s|initial_credit =.*|initial_credit = $USER_CREDITS|
' /etc/cpsdirector/main.ini

cp www/config-example.php /var/www/conpaas/config.php
sed -i "
s|DIRECTOR_URL = 'https://.*:5555'|DIRECTOR_URL = 'https://$CPS_NODE:5555'|
s|CONPAAS_HOST = '.*'|CONPAAS_HOST = '\$(hostname)'|
" /var/www/conpaas/config.php

## Set higher maximum file size when uploading
sed -i '
s/post_max_size =.*/post_max_size = 20M/
s/upload_max_filesize =.*/upload_max_filesize = 20M/' /etc/php5/apache2/php.ini

## enable https on port 443
a2enmod ssl
a2ensite default-ssl

# director and web frontend installed and configured, now restart apache2
service apache2 restart

# Create one user
cpsadduser.py $USERNAME@mail.com $USERNAME $PASSWORD  $USER_CREDITS


## configuring IPOP bootstrap node
if $ENABLE_IPOP
then
 if [ ! -d /opt/ipop ]
 then
  cd \$HOME
  apt-get -q -y install unzip
  unzip $IPOP_TARBALL
  cd acisp2p
  apt-get -q -y install cronolog uml-utilities mono-gmcs libmono-system-runtime2.0-cil libmono-posix2.0-cil
  ./install_debian.sh

  cat > /opt/ipop/etc/bootstrap.config <<EOF2
<?xml version="1.0"?>
<NodeConfig>
  <BrunetNamespace>$BRUNET_NAMESPACE</BrunetNamespace>
  <EdgeListeners>
    <EdgeListener type="udp">
      <port>$BOOTSTRAP_PORT</port>
    </EdgeListener>
  </EdgeListeners>
  <RemoteTAs>
    <Transport>brunet.udp://$BOOTSTRAP_IP:$BOOTSTRAP_PORT</Transport>
  </RemoteTAs>
  <XmlRpcManager>
    <Enabled>true</Enabled>
    <Port>10000</Port>
  </XmlRpcManager>
  <NCService>
    <Enabled>true</Enabled>
    <OptimizeShortcuts>true</OptimizeShortcuts>
    <Checkpointing>false</Checkpointing>
  </NCService>
</NodeConfig>

EOF2
 fi
 service groupvpn_bootstrap.sh restart
else
  ## IPOP disable
  if [ -d /opt/ipop ]
  then
    service groupvpn_bootstrap.sh stop
  fi
fi

apt-get -q -y install bash-completion


# Install cps-tools client

apt-get -q -y install python-pip
pip install argcomplete

cd \$HOME
tar -xaf $CPS_TOOLS_SRC
cd cps-tools-$CPS_VERSION
./configure --sysconf=/etc
make install



### Install conpaas source (to get functional tests in particular)
#cd $HOME
#git clone https://github.com/ConPaaS-team/conpaas.git


### Install dependencies for functional tests

apt-get -q -y install moreutils whois lynx mysql-client


EOF

scp $CPS_CONFIG_SCRIPT root@$CPS_NODE:
ssh root@$CPS_NODE "./$CPS_CONFIG_SCRIPT"