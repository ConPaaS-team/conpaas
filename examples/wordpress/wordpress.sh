#!/bin/bash

TARBALL="http://online.conpaas.eu/wordpress/wp-content.tar.gz"

[ -d "/var/tmp/data" ] || mkdir /var/tmp/data
chown www-data: /var/tmp/data
usermod -a -G fuse www-data
su - www-data -c "mount.xtreemfs $XTREEMFS_IP/data /var/tmp/data"

if [ ! -d "/var/tmp/data/themes" ]
then
    wget --no-check-certificate $TARBALL -P /tmp
    su www-data -c "tar xfz /tmp/wp-content.tar.gz -C /var/tmp/data"
fi


# In case we are restarting the application, we need to change 
# the site's URL in its own database
PHP_IP="http://`awk '/^MY_IP/ { print $2 }' /root/config.cfg`"
OLD_PHP_IP=`echo "SELECT option_value FROM wp_options WHERE option_name='home';" | mysql -u mysqldb -h $MYSQL_IP --password='contrail123' wordpress | tail -n 1`

# Does the site seem to be working correctly?
TESTURL=$OLD_PHP_IP/wp-conpaas.txt
wget -t 2 -T 3 $TESTURL >> /tmp/wordpress.log
if [ "$?" != "0" ]; then 
    echo "UPDATE wp_options SET option_value = replace(option_value, '$OLD_PHP_IP', '$PHP_IP') WHERE option_name = 'home' OR option_name = 'siteurl';" | mysql -u mysqldb -h $MYSQL_IP --password='contrail123' wordpress

    echo "UPDATE wp_posts SET guid = REPLACE (guid, '$OLD_PHP_IP', '$PHP_IP');" | mysql -u mysqldb -h $MYSQL_IP --password='contrail123' wordpress

    echo "UPDATE wp_posts SET post_content = REPLACE (post_content, '$OLD_PHP_IP', '$PHP_IP');" | mysql -u mysqldb -h $MYSQL_IP --password='contrail123' wordpress
fi