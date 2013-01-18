#!/bin/bash

if [ -z "$1" ]
then
    echo "Usage: $0 conpaas_version (eg: $0 1.1.0)"
    exit 1
fi

CPSVERSION="$1"

# make documentation
cd doc 
make clean installation.pdf userguide.pdf > /dev/null
cp {installation,userguide}.pdf ../conpaas-director
cd ..

# prepare director's contents
rm -rf conpaas-director/conpaas
mkdir -p conpaas-director/conpaas
cp -a conpaas-services/config/ conpaas-director/conpaas
cp -a conpaas-services/scripts/ conpaas-director/conpaas

# build conpaas archive and ship it with the director
cd conpaas-services
sh mkarchive.sh > /dev/null 2>&1
cd ..
mv conpaas-services/ConPaaS.tar.gz conpaas-director

# build cpsclient and cpslib
for d in "conpaas-client" "conpaas-services/src"
do
    cd $d 
    sed -i s/'^CPSVERSION =.*'/"CPSVERSION = \'$CPSVERSION\'"/ setup.py
    python setup.py clean > /dev/null
    python setup.py sdist > /dev/null 2>&1
    python setup.py clean > /dev/null
    cd - > /dev/null
done

# build cpsdirector
cd conpaas-director 
sed -i s/'^CPSVERSION =.*'/"CPSVERSION = \'$CPSVERSION\'"/ setup.py
make source > /dev/null
cd ..

# build cpsfrontend
cp -a conpaas-frontend cpsfrontend-$CPSVERSION
find cpsfrontend-$CPSVERSION -type d -name .svn | xargs rm -rf
tar cfz cpsfrontend-$CPSVERSION.tar.gz cpsfrontend-$CPSVERSION
rm -rf cpsfrontend-$CPSVERSION

for f in `find conpaas-{client,director,services/src}/dist -type f -name \*.tar.gz` 
do 
    mv $f . 
done

# cleaning up
find . -name \*.egg-info -type d |xargs rm -rf

cd conpaas-director && make clean > /dev/null
cd ..

echo "TARBALLS BUILT:"
ls *$CPSVERSION*.tar.gz
