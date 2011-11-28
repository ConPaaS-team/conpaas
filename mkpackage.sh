#!/bin/bash 

rm -Rf base map-reduce scalaris bag-of-tasks sql

rm -Rf `find . -name .svn`

mv web-servers ConPaaSWeb
tar czvf ConPaaSWeb.tar.gz ConPaaSWeb
mv ConPaaSWeb.tar.gz frontend/www/code/
mv ConPaaSWeb web-servers

cp web-servers/scripts/* frontend/www/code/

mv frontend/www/code/ec2-manager-user-data frontend/conf/
mv frontend/www/code/opennebula-manager-user-data frontend/conf/

wget http://pear.amazonwebservices.com/get/sdk-latest.zip
unzip sdk-latest.zip
mv sdk-1.4.2.1/sdk-1.4.2.1 frontend/www/lib/aws-sdk 
rm -Rf sdk-1.4.2.1 sdk-latest.zip

rm PACKAGING-INSTRUCTIONS.txt
rm mkpackage.sh
