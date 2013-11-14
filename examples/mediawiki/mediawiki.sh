#!/bin/bash

[ -d "/var/tmp/data" ] || mkdir /var/tmp/data
chown www-data: /var/tmp/data
usermod -a -G fuse www-data
su - www-data -c "mount.xtreemfs $XTREEMFS_IP/data /var/tmp/data"

PHP_IP=`awk '/^MY_IP/ { print $2 }' /root/config.cfg`
echo "env[PHP_IP]='$PHP_IP'" >> /root/ConPaaS/src/conpaas/services/webservers/etc/fpm.tmpl
