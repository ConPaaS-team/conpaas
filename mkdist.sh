#!/bin/bash

supported_comps=('director' 'manager' 'lib' 'tools' 'frontend')
if [ -z "$1" ]
then
    echo "Usage: $0 conpaas_version [components] (eg: $0 1.1.0 director frontend)"
    echo "The supported components are: ${supported_comps[@]}"
    exit 1
fi

CPSVERSION="$1"

param_comps=( "$@" )
wrong_comps=( "$@" )
wrong_comps[0]="1"
right_comps=()
all=0


for (( i=0; i<${#param_comps[@]}; i++ )); do
    param_comp=${param_comps[$i]}
    for supp_comp in ${supported_comps[@]}; do 
        if [ $param_comp = $supp_comp ] ; then
            wrong_comps[$i]=1
            right_comps+=($param_comp)
        fi
    done
done
str_wrong_comp=''
for wrong_comp in ${wrong_comps[@]}; do 
    if [ $wrong_comp != "1" ] ; then
        str_wrong_comp+="$wrong_comp "
    fi 
done 

if [ ${#str_wrong_comp} != "0"  ] ; then
    echo "The following components are not supported and will be ignored:"
    echo "$str_wrong_comp"
fi


if [ ${#right_comps[@]} = "0" ] ; then
    all=1
    echo "Generating tarballs for all the components"
fi




containsElement () {
  if [ "$1" = "1" ] ; then return 0; fi
  local e
  for e in "${@:3}"; do [[ "$e" == "$2" ]] && return 0; done
  return 1
}


containsElement $all "director" "${right_comps[@]}" &&
{
# prepare director's contents
rm -rf conpaas-director/conpaas
mkdir -p conpaas-director/conpaas
cp -a conpaas-services/config/ conpaas-director/conpaas
cp -a conpaas-services/scripts/ conpaas-director/conpaas

# build PDF manual
cd docs 
#make latexpdf 
#cp _build/latex/ConPaaS.pdf ../conpaas-director 
#make clean
cd ..


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

# build cpsdirector
echo '###### build cpsdirector'
cd conpaas-director 
sed -i s/'^CPSVERSION =.*'/"CPSVERSION = \'$CPSVERSION\'"/ setup.py
make source > ../DIRECTOR.LOG 2>&1 || exit 1
cd ..
grep -i error DIRECTOR.LOG && exit 1

}

containsElement 0 "manager" "${right_comps[@]}" &&
{
cd conpaas-services
sh mkarchive.sh > ../SERVICES.LOG 2>&1
cd ..
if [ `cat SERVICES.LOG | wc -l` -gt 3 ]
then
    cat SERVICES.LOG
    exit 1
fi
mv conpaas-services/ConPaaS.tar.gz "ConPaaS-$CPSVERSION.tar.gz"
}

containsElement $all "lib" "${right_comps[@]}" &&
{
# build cpsclient and cpslib
echo '###### build cpslib'
for d in "conpaas-services/src"
do
    cd $d 
    sed -i s/'^CPSVERSION =.*'/"CPSVERSION = \'$CPSVERSION\'"/ setup.py
    python setup.py clean
    python setup.py sdist
    python setup.py clean
    cd -
done > LIB.LOG 2>&1
grep -i error LIB.LOG && exit 1
}


containsElement $all "tools" "${right_comps[@]}" &&
{
# build cps-tools
echo '###### build cps-tools'
cd cps-tools
sed -i "s/AC_INIT(\[cps-tools\], \[\(.*\)\]/AC_INIT(\[cps-tools\], \[$CPSVERSION\]/" configure.ac
autoconf && ./configure && make dist
mv cps-tools-$CPSVERSION.tar.gz ..
cd ..
}

containsElement $all "frontend" "${right_comps[@]}" &&
{
# build cpsfrontend
echo '###### build cpsfrontend'
cp -a conpaas-frontend cpsfrontend-$CPSVERSION
find cpsfrontend-$CPSVERSION -type d -name .svn | xargs rm -rf
tar cfz cpsfrontend-$CPSVERSION.tar.gz cpsfrontend-$CPSVERSION
rm -rf cpsfrontend-$CPSVERSION
}




for f in `find conpaas-{director,services/src}/dist -type f -name \*.tar.gz` 
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
