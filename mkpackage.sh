#!/bin/bash 

release_dir=$1

mkdir $release_dir

cp -r conpaas-services $release_dir/
cp -r conpaas-frontend $release_dir/frontend

# TODO: temporary move the doc outside of conpaas-services
mv $release_dir/conpaas-services/doc $release_dir/
# clean the doc folder
rm $release_dir/doc/*.tex
rm $release_dir/doc/Makefile

cp LICENSE.txt $release_dir/
cp AUTHORS.txt $release_dir/
cp README.txt $release_dir/

cd $release_dir

rm -Rf `find . -name ".svn"`
rm -Rf `find . -name "*~"`

cp -r conpaas-services/scripts frontend/conf/
cp -r conpaas-services/config frontend/conf/

# Frontend doesn't need info about the agent
rm -fr frontend/conf/scripts/agent
rm -fr frontend/conf/config/agent
rm -fr frontend/conf/scripts/create_vm


# Make the ConPaaS archive and put it into frontend/www/download
cd conpaas-services
mkdir ConPaaS
cp -r bin config contrib misc sbin scripts src ConPaaS/
tar -zcvf ConPaaS.tar.gz ConPaaS
rm -fr ConPaaS
mv ConPaaS.tar.gz ../frontend/www/download/

# Also, move the aws-sdk dir inside frontend/lib
mv contrib/aws-sdk/* ../frontend/www/lib/aws-sdk/ 
rm -fr contrib/aws-sdk

# Go back and make the tarball
cd ../..
tar -zcvf $release_dir.tar.gz $release_dir
rm -fr $release_dir

