#!/bin/sh

wordpress_dir=$1
mysql_dump=$2

if [ ! -d "$wordpress_dir" ] || [ ! -f "$mysql_dump" ]
then
    echo "Usage: $0 wordpress_dir mysqldump.sql"
    exit 1
fi

start_service() {
    service_type=$1
    manager_ip=`cpsclient.py create $1 | awk '{ print $5 }' | sed s/...$//`
    sid=`cpsclient.py list | grep $manager_ip | awk '{ print $2 }'`

    cpsclient.py start $sid > /dev/null
    return $sid
}

wait_for_running() {
    sid=$1

    while [ -z "`cpsclient.py info $sid | grep 'state: RUNNING'`" ]
    do
        sleep 2
    done
}

echo "WordPress deployment started" | ts

start_service "mysql"
mysql_sid="$?"

start_service "php"
php_sid="$?"

wait_for_running $mysql_sid
mysql_ip=`cpsclient.py info $mysql_sid | grep master | sed s#.*//## | sed s#:.*##`

echo "MySQL server running on $mysql_ip" | ts

mysql_password=`echo | mkpasswd -`
cpsclient.py set_password "$mysql_sid" "$mysql_password" > /dev/null

echo "Loading MySQL dump" | ts
mysql -u mysqldb -h $mysql_ip --password=$mysql_password < $mysql_dump
echo "MySQL dump loaded" | ts

wait_for_running $php_sid

php_ip=`cpsclient.py info $php_sid | grep web | awk '{ print $2 }'`

echo "Web server running on $php_ip" | ts

sed -i s/"define('DB_HOST', .*);"/"define('DB_HOST', '$mysql_ip');"/g $wordpress_dir/wp-config.php
sed -i s#"define('DB_PASSWORD'.*"#"define('DB_PASSWORD', '$mysql_password');"# $wordpress_dir/wp-config.php

tar czf wp-upload.tar.gz -C $wordpress_dir .

code_revision=`cpsclient.py upload_code $php_sid wp-upload.tar.gz | awk '{ print $3 }'`

cpsclient.py enable_code $php_sid $code_revision > /dev/null

while [ -z "`cpsclient.py list_uploads $php_sid | grep \* | grep -v code-default`" ]
do
    sleep 1
done

echo "WordPress available at http://$php_ip" | ts
