#!/bin/bash 

release_dir=$1

if [ -z "$release_dir" ]
then
  echo "Please specify a name for the release. Exiting."
  exit 1
fi

if [ -d "$release_dir" ]
then
  echo "Release dir $release_dir already exists. Exiting."
  exit 1
fi

mkdir $release_dir

cp -r conpaas-services $release_dir/ > /dev/null
cp -r conpaas-frontend $release_dir/frontend > /dev/null

# Copy the documentation to the frontend
echo "Compiling documentation..."
(cd doc; make clean > /dev/null; make > /dev/null)
mkdir $release_dir/doc $release_dir/frontend/www/help
cp doc/*.{html,css,pdf} $release_dir/doc
cp doc/*.{html,css,pdf} $release_dir/frontend/www/help/

cp LICENSE.txt $release_dir/
cp AUTHORS.txt $release_dir/
cp README.txt $release_dir/

cd $release_dir

rm -Rf `find . -name ".svn"`
rm -Rf `find . -name "*~"`

cp -r conpaas-services/scripts frontend/conf/ > /dev/null
cp -r conpaas-services/config frontend/conf/ > /dev/null

# Frontend doesn't need info about the agent
rm -fr frontend/conf/scripts/agent
rm -fr frontend/conf/config/agent
rm -fr frontend/conf/scripts/create_vm

# Make the ConPaaS archive and put it into frontend/www/download
cd conpaas-services
. ./mkarchive.sh
mv ConPaaS.tar.gz ../frontend/www/download/

# Also, move the aws-sdk dir inside frontend/lib
mv contrib/aws-sdk/* ../frontend/www/lib/aws-sdk/ 
rm -fr contrib/aws-sdk

# Go back and make the tarball
cd ../..
tar -zcvf $release_dir.tar.gz $release_dir > /dev/null
rm -fr $release_dir

