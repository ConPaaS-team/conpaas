#!/bin/bash

IP=$2
#Use this in case of dynamic (public) IP
#IP=`ifconfig eth0 | sed -ne 's/.*inet addr:\([^ ]*\).*/\1/p'`

keystone ec2-credentials-list > creds
while read line
do
id=`echo $line | cut -d' ' -f2`
#echo $id
if [ "$id" == "admin" ]; then
access=`echo $line | cut -d' ' -f4`
secret=`echo $line | cut -d' ' -f6`
#echo "$access|$secret"
break
fi
done < creds

#source /devstack/eucarc
export EC2_ACCESS_KEY=$access
export EC2_SECRET_KEY=$secret
export EC2_URL=$(keystone catalog --service ec2 | awk '/ publicURL / { print $4 }')
euca-describe-images > imgs
while read line
do
id=`echo $line | cut -d' ' -f4`
if [ "$id" == "(conpaas)" ]; then
img=`echo $line | cut -d' ' -f2`
#echo "$img"
fi
done < imgs


sed -i "s/^\(DIRECTOR_URL\s*=\s*\).*$/\1https:\/\/$IP:5555/" $1
sed -i "s/^\(USER\s*=\s*\).*$/\1$access/" $1
sed -i "s/^\(PASSWORD\s*=\s*\).*$/\1$secret/" $1
sed -i "s/^\(HOST\s*=\s*\).*$/\1$IP/" $1
sed -i "s/^\(IMAGE_ID\s*=\s*\).*$/\1$img/" $1

sudo cp $1 /etc/cpsdirector/director.cfg
cpscheck.py
sudo service apache2 restart

rm creds imgs
