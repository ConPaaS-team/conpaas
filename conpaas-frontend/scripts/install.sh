#!/bin/bash

# These parameters are used for performing CAPTCHA[1] operations and they are
# issued for a specific domain. To generate a pair of keys for your domain,
# please go to the reCAPTCHA admin page[2] (it's hosted by Google, so you need
# a Google account).
#
# [1] http://www.google.com/recaptcha
# [2] https://www.google.com/recaptcha/admin/create
CAPTCHA_PUBLIC_KEY=""
CAPTCHA_PRIVATE_KEY=""

# Configuration values for Amazon EC2. The script will assume you want to
# deploy ConPaaS on EC2 if EC2_USER is not empty. If you want to use ConPaaS on
# another type of cloud, keep on reading this file.

# EC2_USER should be set to your EC2 user name. Beware: this is not the
# email address you normally use to login at the AWS management console. 
# An EC2 user name is a long opaque string. It can be found at
# https://aws-portal.amazon.com/gp/aws/developer/account/index.html?action=access-key#account_identifiers
# under the name "Access key ID"
EC2_USER=""

# EC2_PASSWORD should be set to the corresponding password.
# Again, this is a long opaque string. You can find it next to your
# Access Key ID by clicking "Show Secret Access Key".
EC2_PASSWORD=""

# Amazon EC2 region. 
# 
# Valid values are:
#
# - ec2.us-west-2.amazonaws.com # United States West (Oregon)
# - ec2.us-east-1.amazonaws.com # United States East (Northern Virginia) 
# - ec2.eu-west-1.amazonaws.com # Europe West (Ireland)
#
EC2_REGION="ec2.us-west-2.amazonaws.com" 

# This variable contains the identifier of the ConPaaS Amazon Machine Image.
# 
# Please set this value according to the region you want to use (see
# EC2_REGION).
#
AMI_ID="ami-c2941af2"  # United States West (Oregon)
#AMI_ID="ami-4b249322" # United States East (Northern Virginia)
#AMI_ID="ami-99fcfaed" # Europe West (Ireland)

# This variable contains the created security group from the Web hosting
# service. Your security groups can be found under "NETWORK & SECURITY" on
# https://console.aws.amazon.com/ec2/ 
SECURITY_GROUP=""

# This variable contains the Key Pair name  to be used.  Your keypairs can be
# found under "NETWORK & SECURITY" on https://console.aws.amazon.com/ec2/
KEYPAIR=""

# This variable contains the type of EC2 instances to use. A good value to use
# inexpensive, low-performance instances is "t1.micro".
EC2_INSTANCE_TYPE="t1.micro"

# Amazon Account ID without dashes. Used for identification with Amazon EC2.
# Found in the AWS Security Credentials.
EC2_ACCOUNT_ID=""

# Your CanonicalUser ID. Used for setting access control settings in AmazonS3. Found in the AWS Security
# Credentials.
EC2_CANONICAL_ID=""

####################################################################
# The following values are only needed by the Task Farming service #
####################################################################

PORT="8889"

# A unique name used in the service to specify different clouds. 
# For Amazon EC2, 'ec2' is a good value. 
# For OpenNebula, use the OCCI server hostname.
CLOUD_ID="ec2" 

# The accountable time unit. Different clouds charge at different
# frequencies (e.g. Amazon charges per hour = 60 minutes)
TIMEUNIT="60" 

# The price per TIMEUNIT of this specific machine type on this cloud
COSTUNIT="1" 

# The maximum number of VMs that the system is allowed to allocate from this
# cloud
MAXNODES="20" 
SPEEDFACTOR="1" 

###########################################################################
# DON'T CHANGE ANYTHING BELOW THIS LINE UNLESS YOU WANT TO USE OPENNEBULA #
###########################################################################

# Configuration values for OpenNebula. The script will assume you want to
# deploy ConPaaS on OpenNebula if IMAGE is not empty.

# The image ID (an integer). You can list the registered OpenNebula
# images with command "oneimage list" command.
IMAGE=""

# OCCI defines 3 standard instance types: small medium and large. This
# variable should choose one of these.
ON_INSTANCE_TYPE="small"

# Your OpenNebula user name
ON_USER=""

# Your OpenNebula password
ON_PASSWD=""

# The network ID (an integer). You can list the registered OpenNebula
# networks with the "onevnet list" command.
NETWORK=""

# The URL of the OCCI interface at OpenNebula. Note: ConPaaS currently
# supports only the default OCCI implementation that comes together
# with OpenNebula. It does not yet support the full OCCI-0.2 and later
# versions.
URL=""

# The network gateway through which new VMs can route their traffic in
# OpenNebula (an IP address)
GATEWAY=""

# The DNS server that VMs should use to resolve DNS names (an IP address)
NAMESERVER=""

# The virtual machines OS architecture (eg: "x86_64")
OS_ARCH=""

# The device that will be mounted as root on the VM. Most often it
# is "sda" or "hda" for KVM, and "xvda2" for Xen.
# (corrseponds to the OpenNebula "ROOT" parameter from the VM template)
OS_ROOT="sda"

# The device on which the VM image disk is mapped. 
DISK_TARGET="sda"

# The device associated with the CD-ROM on the virtual machine. This
# will be used for contextualization in OpenNebula. Most often it is
# "sr0" for KVM and "xvdb" for Xen.
# (corresponds to the OpenNebula "TARGET" parameter from the "CONTEXT" 
# section of the VM template)
CONTEXT_TARGET="sr0"

# The TaskFarming service uses XMLRPC to talk to Opennebula. This is the url to
# the server (Ex. http://dns.name.or.ip:2633/RPC2)
XMLRPC=""


###########################################################################
# DON'T CHANGE ANYTHING BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING #
###########################################################################

if [ ! `id -u` = 0 ]
then
    echo "E: $0 requires root privileges" > /dev/stderr
    exit 1
fi

if [ ! -d "frontend" ]
then
    echo "E: $0 has to be run from the ConPaaS top-level directory" > /dev/stderr
    exit 1
fi

cd frontend 

CONPAAS_TARBALL="www/download/ConPaaS.tar.gz"

DESTDIR="/var/www"
CONFDIR="/etc/conpaas"
BACKUPDIR="/var/backups"

read -e -i "$DESTDIR" -p "Please enter the path where you want to install the frontend code: " input
DESTDIR="${input:-$DESTDIR}"

read -e -i "$CONFDIR" -p "Please enter the path where the ConPaaS configuration files should be installed: " input
CONFDIR="${input:-$CONFDIR}"

read -e -i "$BACKUPDIR" -p "Please enter the path where you want to backup your current $DESTDIR and $CONFDIR: " input
BACKUPDIR="${input:-$BACKUPDIR}"

# Backup $DESTDIR
if [ -d "$DESTDIR" ]
then
    mv $DESTDIR $BACKUPDIR/conpaas-docroot-`date +%s`
fi

# Backup $CONFDIR
if [ -d "$CONFDIR" ]
then
    mv $CONFDIR $BACKUPDIR/conpaas-confdir-`date +%s`
fi

# Install the application under $DESTDIR
cp -a www $DESTDIR

# Put the configuration files under $CONFDIR
cp -a conf $CONFDIR

# Uncompress the ConPaaS release we want to work with
cp $CONPAAS_TARBALL . && tar xfz `basename $CONPAAS_TARBALL`

# Copy the necessary scripts
cp -a ConPaaS/config $CONFDIR && rm -rf ConPaaS ConPaaS.tar.gz

# Fix permissions
chown -R www-data: $CONFDIR $DESTDIR

# Install the dependencies
apt-get update
apt-get -f -y install libapache2-mod-php5 php5-curl php5-mysql mysql-server mysql-client openssl unzip curl

# Get MySQL credentials
mysql_user=`awk '/^user/ { print $3 }' /etc/mysql/debian.cnf | head -n 1`
mysql_pass=`awk '/^password/ { print $3 }' /etc/mysql/debian.cnf | head -n 1`

# Change the DB config script
sed -i s/\'DB_USER\'/\'$mysql_user\'/ scripts/frontend-db.sql
sed -i s/\'DB_PASSWD\'/\'$mysql_pass\'/ scripts/frontend-db.sql
sed -i s/DB_NAME/conpaas/ scripts/frontend-db.sql
sed -i s/'^create user'/'-- create user'/ scripts/frontend-db.sql

# Create ConPaaS database
mysql -u $mysql_user --password=$mysql_pass < scripts/frontend-db.sql

/bin/echo -e '[mysql]\nserver = "localhost"' > $CONFDIR/db.ini
echo "user = \"$mysql_user\"" >> $CONFDIR/db.ini
echo "pass = \"$mysql_pass\"" >> $CONFDIR/db.ini
echo "db = \"conpaas\"" >> $CONFDIR/db.ini

# Get and install the AWS SDK
wget http://pear.amazonwebservices.com/get/sdk-latest.zip
unzip sdk-latest.zip
cp -a sdk-*/* $DESTDIR/lib/aws-sdk/
rm -rf sdk-*

cp $DESTDIR/lib/aws-sdk/config-sample.inc.php $DESTDIR/lib/aws-sdk/config.inc.php
sed -i s/"'key' => 'development-key',"/"'key' => '$EC2_USER', 'account_id' => '$EC2_ACCOUNT_ID',"/ $DESTDIR/lib/aws-sdk/config.inc.php
sed -i s/"'secret' => 'development-secret',"/"'secret' => '$EC2_PASSWORD', 'canonical_id' => '$EC2_CANONICAL_ID',"/ $DESTDIR/lib/aws-sdk/config.inc.php

if [ -f "/etc/apache2/sites-available/conpaas-ssl" ]
then
    mv /etc/apache2/sites-available/conpaas-ssl $BACKUPDIR/conpaas-apache-conf-`date +%s`
fi

cp conf/apache.conf.sample /etc/apache2/sites-available/conpaas-ssl

# Update apache's conf with the right configuration dir value
sed -i s#"/etc/conpaas"#"$CONFDIR"# /etc/apache2/sites-available/conpaas-ssl

# Bump php's upload_max_filesize
sed -i s/'.*upload_max_filesize.*'/'upload_max_filesize = 20M'/ /etc/php5/apache2/php.ini

# Create $DESTDIR/config.php
cp $DESTDIR/config-example.php $DESTDIR/config.php

# reCAPTCHA config
sed -i s/'const CAPTCHA_PRIVATE_KEY.*'/"const CAPTCHA_PRIVATE_KEY = \'$CAPTCHA_PRIVATE_KEY\';"/ $DESTDIR/config.php
sed -i s/'const CAPTCHA_PUBLIC_KEY.*'/"const CAPTCHA_PUBLIC_KEY = \'$CAPTCHA_PUBLIC_KEY\';"/ $DESTDIR/config.php

# If we are installing the frontend on EC2 
if [ -d "/var/lib/ec2-bootstrap" ]
then
    # Then we know the public hostname
    hostname=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`
    # Setting CONPAAS_HOST here to give a good default value to generate-certs.php
    sed -i s/'const CONPAAS_HOST.*'/"const CONPAAS_HOST = \'$hostname\';"/ $DESTDIR/config.php
fi

# SSL certificates 
read -e -i "y" -p "Do you want to generate a self-signed certificate? " input

if [ "$input" = "y" ]
then
    # Generate SSL certificates and ask for hostname confirmation
    php scripts/generate-certs.php $CONFDIR/certs

    certfile="$CONFDIR/certs/cert.pem"
else
    # Prompt for certificate/private key/ca certificate filenames

    unset certfile
    while [ ! -f "$certfile" ]
    do
        read -e -i "$CONFDIR/certs/cert.pem" -p "Please provide your certificate filename " certfile
    done

    sed -i s#"$CONFDIR/certs/cert.pem"#"$certfile"# /etc/apache2/sites-available/conpaas-ssl

    unset certkey
    while [ ! -f "$certkey" ]
    do
        read -e -i "$CONFDIR/certs/key.pem" -p "Please provide your private key filename " certkey
    done

    sed -i s#"$CONFDIR/certs/key.pem"#"$certkey"# /etc/apache2/sites-available/conpaas-ssl

    unset cacert
    while [ ! -f "$cacert" ]
    do
        read -e -i "$CONFDIR/certs/ca_cert.pem" -p "Please provide your CA certificate filename " cacert
    done

    sed -i s#"$CONFDIR/certs/ca_cert.pem"#"$cacert"# /etc/apache2/sites-available/conpaas-ssl
fi
    
# Get hostname
hostname=`openssl x509 -in $certfile -text -noout|grep role=frontend | sed s/.*CN=//g | sed s#/.*##`

# Keep on looping till we manage to ping the provided hostname. Certainly not a
# bullet-proof way to check whether the hostname makes sense, but better than
# nothing.
while [ 1 ]
do
    read -e -i "$hostname" -p "Please confirm your machine public hostname. It has to be reachable from ConPaaS instances " hostname
    ping -c1 -W1 "$hostname" > /dev/null 2>&1

    if [ "$?" = 0 ]
    then
        break
    else
        echo "WARNING: Unable to ping $hostname."
    fi
done

sed -i s/'const CONPAAS_HOST.*'/"const CONPAAS_HOST = \'$hostname\';"/ $DESTDIR/config.php

# Enable SSL and restart apache
a2enmod ssl
a2ensite conpaas-ssl
/etc/init.d/apache2 restart

# Edit conf/main.ini
sed -i s#^logfile.*#'logfile = "/var/log/conpaas-frontend.log"'# $CONFDIR/main.ini
touch /var/log/conpaas-frontend.log
chown www-data: /var/log/conpaas-frontend.log

# Deploy on EC2
if [ -n "$EC2_USER" ]
then
    echo "ami = \"$AMI_ID\"" > $CONFDIR/aws.ini
    echo "security_group = \"$SECURITY_GROUP\"" >> $CONFDIR/aws.ini
    echo "keypair = \"$KEYPAIR\"" >> $CONFDIR/aws.ini
    echo "instance_type = \"$EC2_INSTANCE_TYPE\"" >> $CONFDIR/aws.ini
    echo "region = \"$EC2_REGION\"" >> $CONFDIR/aws.ini

    /bin/echo -e "[iaas]\nDRIVER = EC2" > $CONFDIR/config/cloud/ec2.cfg
    echo "USER = $EC2_USER" >> $CONFDIR/config/cloud/ec2.cfg
    echo "PASSWORD = $EC2_PASSWORD" >> $CONFDIR/config/cloud/ec2.cfg
    echo "IMAGE_ID = $AMI_ID" >> $CONFDIR/config/cloud/ec2.cfg
    echo "SIZE_ID = $EC2_INSTANCE_TYPE" >> $CONFDIR/config/cloud/ec2.cfg
    echo "SECURITY_GROUP_NAME = $SECURITY_GROUP" >> $CONFDIR/config/cloud/ec2.cfg
    echo "KEY_NAME = $KEYPAIR" >> $CONFDIR/config/cloud/ec2.cfg
    echo "REGION = $EC2_REGION" >> $CONFDIR/config/cloud/ec2.cfg

    # Task Farming
    echo "PORT = $PORT" >> $CONFDIR/config/cloud/ec2.cfg
    echo "HOSTNAME = $CLOUD_ID" >> $CONFDIR/config/cloud/ec2.cfg
    echo "TIMEUNIT = $TIMEUNIT" >> $CONFDIR/config/cloud/ec2.cfg
    echo "COSTUNIT = $COSTUNIT" >> $CONFDIR/config/cloud/ec2.cfg
    echo "MAXNODES = $MAXNODES" >> $CONFDIR/config/cloud/ec2.cfg
    echo "SPEEDFACTOR = $SPEEDFACTOR" >> $CONFDIR/config/cloud/ec2.cfg
# Deploy on OpenNebula
elif [ -n "$IMAGE" ]
then
    sed -i s#^enable_ec2.*#'enable_ec2 = "no"'# $CONFDIR/main.ini
    sed -i s#^enable_opennebula.*#'enable_opennebula = "yes"'# $CONFDIR/main.ini

    echo "instance_type = \"$ON_INSTANCE_TYPE\"" > $CONFDIR/opennebula.ini
    echo "user = \"$ON_USER\"" >> $CONFDIR/opennebula.ini
    echo "passwd = \"$ON_PASSWD\"" >> $CONFDIR/opennebula.ini
    echo "image = \"$IMAGE\"" >> $CONFDIR/opennebula.ini
    echo "network = \"$NETWORK\"" >> $CONFDIR/opennebula.ini
    echo "url = \"$URL\"" >> $CONFDIR/opennebula.ini
    echo "gateway = \"$GATEWAY\"" >> $CONFDIR/opennebula.ini
    echo "nameserver = \"$NAMESERVER\"" >> $CONFDIR/opennebula.ini
    echo "os_arch = \"$OS_ARCH\"" >> $CONFDIR/opennebula.ini
    echo "os_root = \"$OS_ROOT\"" >> $CONFDIR/opennebula.ini
    echo "disk_target = \"$DISK_TARGET\"" >> $CONFDIR/opennebula.ini
    echo "context_target = \"$CONTEXT_TARGET\"" >> $CONFDIR/opennebula.ini

    /bin/echo -e "[iaas]\nDRIVER = OPENNEBULA" > $CONFDIR/config/cloud/opennebula.cfg
    echo "USER = $ON_USER" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "PASSWORD = $ON_PASSWD" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "URL = $URL" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "IMAGE_ID = $IMAGE" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "INST_TYPE = $ON_INSTANCE_TYPE" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "NET_ID = $NETWORK" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "NET_GATEWAY = $GATEWAY" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "NET_NAMESERVER = $NAMESERVER" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "OS_ARCH = $OS_ARCH" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "OS_ROOT = $OS_ROOT" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "DISK_TARGET = $DISK_TARGET" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "CONTEXT_TARGET = $CONTEXT_TARGET" >> $CONFDIR/config/cloud/opennebula.cfg

    # Task Farming
    echo "XMLRPC = $XMLRPC" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "PORT = $PORT" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "HOSTNAME = $CLOUD_ID" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "TIMEUNIT = $TIMEUNIT" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "COSTUNIT = $COSTUNIT" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "MAXNODES = $MAXNODES" >> $CONFDIR/config/cloud/opennebula.cfg
    echo "SPEEDFACTOR = $SPEEDFACTOR" >> $CONFDIR/config/cloud/opennebula.cfg
fi

echo "Installation completed!"
echo "Your ConPaaS system is online at the following URL: https://$hostname"
