#!/bin/sh

if [ `id -u` -ne "0" ]
then
    echo "E: Please run this script as root"
    exit 1
fi

# Installing required Debian packages
apt-get update
apt-get -y --force-yes install libapache2-mod-php5 php5-curl

# Copying the www directory underneath the web server document root
cp -a www/ /var/

# Copy conf/main.ini and conf/welcome.txt in the ConPaaS Director configuration folder
# (if these are not already there)
if [ ! -e "/etc/cpsdirector/main.ini" ] ; then
    cp conf/main.ini /etc/cpsdirector/
fi
if [ ! -e "/etc/cpsdirector/welcome.txt" ] ; then
    cp conf/welcome.txt /etc/cpsdirector/
fi

# Configuring Apache
a2enmod ssl
a2ensite default-ssl

# Restarting apache
service apache2 restart
