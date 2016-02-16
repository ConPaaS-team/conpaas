#!/bin/bash

# supported_comps=('director' 'manager' 'lib' 'tools' 'frontend')
#CPSVERSION="100"
CPSVERSION="2.0"
director="cpsdirector-$CPSVERSION.tar.gz" 
manager="ConPaaS-$CPSVERSION.tar.gz" 
lib="cpslib-$CPSVERSION.tar.gz"
tools="cps-tools-$CPSVERSION.tar.gz"
frontend="cpsfrontend-$CPSVERSION.tar.gz"

taballs=""

#IP_PREFIX=172.16.0
IP_PREFIX=10.158.114

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

ls $lib > /dev/null 2>&1 &&
{
cat <<EOT >> $TMPFILE
sudo rm -r /usr/local/lib/python2.7/dist-packages/cpslib-*-py2.7.egg/
sudo easy_install cpslib-*.tar.gz
rm cpslib-*.tar.gz
EOT
taballs+="$lib "
}


ls $director > /dev/null 2>&1 && 
{
cat <<EOT >> $TMPFILE
echo "#installing director"
#cp /etc/cpsdirector/director.cfg .
sudo rm -rf /usr/local/lib/python2.7/dist-packages/cpsdirector-*-py2.7.egg
tar -xaf cpsdirector-*.tar.gz
rm -f cpsdirector-*.tar.gz
cd cpsdirector-* 
echo \$IP_ADDRESS | sudo  make install
cd ..
sudo rm -rf cpsdirector-*
#mv director.cfg /etc/cpsdirector/
sudo sqlite3 /etc/cpsdirector/director.db 'delete from resource; delete from service'
sudo service apache2 restart
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


ls $tools > /dev/null 2>&1 && 
{
cat <<EOT >> $TMPFILE
sudo rm -rf /usr/local/lib/python2.7/dist-packages/cps_tools/
tar xaf cps-tools*
cd cps-tools-*
./configure --sysconf=/etc
sudo make install
#mkdir -p $HOME/.conpaas
cd ..
sudo rm -rf cps-tools*

EOT
taballs+="$tools "
}


ls $frontend > /dev/null 2>&1 && 
{
cat <<EOT >> $TMPFILE
tar -xaf cpsfrontend*.tar.gz
rm cpsfrontend*.tar.gz
sudo cp -r cpsfrontend-*/www/* /var/www/
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
