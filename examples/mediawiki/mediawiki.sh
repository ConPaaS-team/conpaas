#!/bin/bash

echo $XTREEMFS_CERT | base64 --decode > /tmp/certificate.p12
chown www-data: /tmp/certificate.p12

[ -d "/var/tmp/data" ] || mkdir /var/tmp/data
chown www-data: /var/tmp/data
usermod -a -G fuse www-data
su - www-data -c "mount.xtreemfs $XTREEMFS_IP/data /var/tmp/data --pkcs12-file-path /tmp/certificate.p12 --pkcs12-passphrase $XTREEMFS_PASSPHRASE"

rm /tmp/certificate.p12

PHP_IP=`awk '/^MY_IP/ { print $2 }' /root/config.cfg`
echo "env[PHP_IP]='$PHP_IP'" >> /root/ConPaaS/src/conpaas/services/webservers/etc/fpm.tmpl
