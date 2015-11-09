#!/bin/bash

# supported_comps=('director' 'manager' 'lib' 'tools' 'frontend')
CPSVERSION="100"
director="cpsdirector-$CPSVERSION.tar.gz" 
manager="ConPaaS-$CPSVERSION.tar.gz" 
lib="cpslib-$CPSVERSION.tar.gz"
tools="cps-tools-$CPSVERSION.tar.gz"
frontend="cpsfrontend-$CPSVERSION.tar.gz"

taballs=""

IP_PREFIX=192.168.13

rm -f *$CPSVERSION*.tar.gz

./mkdist.sh $CPSVERSION "$@" 

# TMPFILE=$(mktemp)
TMPFILE='/tmp/cpsinstall'

cat <<EOT >> $TMPFILE
#!/bin/bash

IP_ADDRESS="\$(ip addr show | perl -ne 'print "\$1\n" if /inet ([\d.]+).*scope global/' | grep "$IP_PREFIX" | head -1)"
#DIRECTOR_URL="https://\${IP_ADDRESS}:5555"
#echo \$DIRECTOR_URL

EOT


ls $director > /dev/null 2>&1 && 
{
cat <<EOT >> $TMPFILE
echo "#installing director"
#cp /etc/cpsdirector/director.cfg .
rm -rf /usr/local/lib/python2.7/dist-packages/cpsdirector-*-py2.7.egg
tar -xaf cpsdirector-*.tar.gz
rm -f cpsdirector-*.tar.gz
cd cpsdirector-* 
echo \$IP_ADDRESS |  make install
cd ..
rm -rf cpsdirector-*
#mv director.cfg /etc/cpsdirector/
sqlite3 /etc/cpsdirector/director.db 'delete from resource; delete from service'
service apache2 restart
EOT
taballs+="$director "
}

ls $manager > /dev/null 2>&1 && 
{
cat <<EOT >> $TMPFILE
mv $manager /etc/cpsdirector/ConPaaS.tar.gz
EOT
taballs+="$manager "
}

ls $lib > /dev/null 2>&1 && 
{
cat <<EOT >> $TMPFILE
rm -r /usr/local/lib/python2.7/dist-packages/cpslib-*-py2.7.egg/
easy_install cpslib-*.tar.gz
rm cpslib-*.tar.gz
EOT
taballs+="$lib "
}

ls $tools > /dev/null 2>&1 && 
{
cat <<EOT >> $TMPFILE
rm -rf /usr/local/lib/python2.7/dist-packages/cps_tools/
cd cps-tools-*
./configure --sysconf=/etc
make install
#mkdir -p $HOME/.conpaas
cd ..
rm -rf cps-tools*

EOT
taballs+="$tools "
}


ls $frontend > /dev/null 2>&1 && 
{
cat <<EOT >> $TMPFILE
tar -xaf cpsfrontend*.tar.gz
rm cpsfrontend*.tar.gz
cp -r cpsfrontend-*/www/* /var/www/html/
rm -rf cpsfrontend*
EOT
taballs+="$frontend "
}



echo ""
echo "Uploading tarballs and execution script:"

scp $TMPFILE $taballs conpaas:
ssh conpaas 'bash cpsinstall; rm cpsinstall'
# ssh conpaas 'cat cpsinstall; rm cpsinstall'

rm -f ${TMPFILE}