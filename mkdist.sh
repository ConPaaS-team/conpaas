#!/bin/sh

# prepare director's contents
rm -rf conpaas-director/conpaas
mkdir -p conpaas-director/conpaas
cp -a conpaas-services/config/ conpaas-director/conpaas
cp -a conpaas-services/scripts/ conpaas-director/conpaas

# build conpaas archive and ship it with the director
cd conpaas-services
sh mkarchive.sh
cd -
mv conpaas-services/ConPaaS.tar.gz conpaas-director

# build cpsclient and cpslib
for d in "conpaas-client" "conpaas-services/src"
do
    cd $d 
    python setup.py clean 
    python setup.py sdist
    python setup.py clean 
    cd -
done

# build cpsdirector
cd conpaas-director && make source
cd -

echo "\n\n\nTARBALLS BUILT"
find . -type d -name dist |xargs ls -lh 

# cleaning up
find . -name \*.egg-info -type d |xargs rm -rf

cd conpaas-director && make clean
