#!/bin/bash

IP=`ifconfig eth0 | sed -ne 's/.*inet addr:\([^ ]*\).*/\1/p'`

export SERVICE_HOST=$IP
export HOST_IP=$IP
export OS_AUTH_URL="http://$IP:5000/v2.0"
export GLANCE_HOST=$IP


#cinder
sed -i -r "s/auth_host =.*/auth_host = $IP/" /etc/cinder/api-paste.ini

#glance
sed -i -r "s/auth_host =.*/auth_host = $IP/" /etc/glance/glance-api.conf
sed -i -r "s/auth_uri =.*/auth_uri = http:\/\/$IP:5000\//" /etc/glance/glance-api.conf
sed -i -r "s/auth_url =.*/auth_url = http:\/\/$IP:35357\/v2.0/" /etc/glance/glance-cache.conf

sed -i -r "s/auth_host =.*/auth_host = $IP/" /etc/glance/glance-registry.conf
sed -i -r "s/auth_uri =.*/auth_uri = http:\/\/$IP:5000\//" /etc/glance/glance-registry.conf

#nova 
sed -i -r "s/auth_host =.*/auth_host = $IP/" /etc/nova/api-paste.ini

sed -i -r "s/glance_api_servers =.*/glance_api_servers = $IP:9292/" /etc/nova/nova.conf
sed -i -r "s/ec2_dmz_host =.*/ec2_dmz_host = $IP/" /etc/nova/nova.conf
sed -i -r "s/xvpvncproxy_base_url =.*/xvpvncproxy_base_url = http:\/\/$IP:6081\/console/" /etc/nova/nova.conf
sed -i -r "s/novncproxy_base_url =.*/novncproxy_base_url = http:\/\/$IP:6080\/vnc_auto/" /etc/nova/nova.conf
sed -i -r "s/my_ip =.*/my_ip = $IP/" /etc/nova/nova.conf
sed -i -r "s/s3_host =.*/s3_host = $IP/" /etc/nova/nova.conf
sed -i -r "s/html5proxy_base_url =.*/html5proxy_base_url = http:\/\/$IP:6082\/spice_auto.html/" /etc/nova/nova.conf


#update keystone database
mysql --database=keystone --execute='select id, url from endpoint' > query_.sql
tail -n +2 query_.sql > query.sql

while read line
do 
id=`echo $line | cut -d' ' -f1`
url=`echo $line | cut -d' ' -f2`

urlp1=`echo $url | cut -d':' -f1`
urlp2=`echo $url | cut -d':' -f2`
urlp3=`echo $url | cut -d':' -f3`

newurl="$urlp1://$IP:$urlp3"

mysql --database=keystone --execute="update endpoint set url='$newurl' where id='$id'"
done < "query.sql"

rm -f *.sql

#source /home/genc/devstack/openrc admin admin
#/home/genc/devstack/rejoin-stack.sh
