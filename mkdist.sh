#!/bin/bash
if [ -z "$1" ]
then
    echo "Usage: $0 conpaas_version (eg: $0 1.1.0)"
    exit 1
fi

CPSVERSION="$1"

# prepare director's contents
rm -rf conpaas-director/conpaas
mkdir -p conpaas-director/conpaas
cp -a conpaas-services/config/ conpaas-director/conpaas
cp -a conpaas-services/scripts/ conpaas-director/conpaas

# build PDF manual
#cd docs 
#make latexpdf 
#cp _build/latex/ConPaaS.pdf ../conpaas-director 
#make clean
#cd ..

# build conpaas archive and ship it with the director
echo '###### build conpaas archive and ship it with the director'
cd conpaas-services
sh mkarchive.sh > ../SERVICES.LOG 2>&1
cd ..
if [ `cat SERVICES.LOG | wc -l` -gt 3 ]
then
    cat SERVICES.LOG
    exit 1
fi
mv conpaas-services/ConPaaS.tar.gz conpaas-director

# build cpsclient and cpslib
echo '###### build cpsclient and cpslib'
for d in "conpaas-client" "conpaas-services/src"
do
    cd $d 
    sed -i s/'^CPSVERSION =.*'/"CPSVERSION = \'$CPSVERSION\'"/ setup.py
    python setup.py clean
    python setup.py sdist
    python setup.py clean
    cd -
done > CLIENT+LIB.LOG 2>&1
grep -i error CLIENT+LIB.LOG && exit 1

# build cpsdirector
echo '###### build cpsdirector'
cd conpaas-director 
sed -i s/'^CPSVERSION =.*'/"CPSVERSION = \'$CPSVERSION\'"/ setup.py
make source > ../DIRECTOR.LOG 2>&1 || exit 1
cd ..
grep -i error DIRECTOR.LOG && exit 1

# build cpsfrontend
echo '###### build cpsfrontend'
cp -a conpaas-frontend cpsfrontend-$CPSVERSION
find cpsfrontend-$CPSVERSION -type d -name .svn | xargs rm -rf
tar cfz cpsfrontend-$CPSVERSION.tar.gz cpsfrontend-$CPSVERSION
rm -rf cpsfrontend-$CPSVERSION

# build cps-tools
# TODO(genc): generation of cps-tools tarball is currently commented due to the usage of python 2.6 on the director vm of the testbed
# uncomment when upgrading to 2.7
echo '###### build cps-tools'
cd cps-tools
sed -i "s/AC_INIT(\[cps-tools\], \[\(.*\)\]/AC_INIT(\[cps-tools\], \[$CPSVERSION\]/" configure.ac
./configure && make dist
mv cps-tools-$CPSVERSION.tar.gz ..
cd ..


for f in `find conpaas-{client,director,services/src}/dist -type f -name \*.tar.gz` 
do 
    mv $f . 
done

# cleaning up
find . -name \*.egg-info -type d |xargs rm -rf

echo ======= cleaning up ======= >> DIRECTOR.LOG
cd conpaas-director && make clean >> ../DIRECTOR.LOG
cd ..

echo "TARBALLS BUILT:"
ls *$CPSVERSION*.tar.gz
