#!/bin/sh

cd $CI_HOME/conpaas-client
python setup.py install

cd $CI_HOME/conpaas-director

# Create fake files/directories not really needed for unit testing
touch ConPaaS.tar.gz
mkdir conpaas
cp -a ../conpaas-services/{config,scripts} conpaas

# We cannot use system-wide directories
sed -i s#/etc/cpsdirector#$PWD/cpsdirectorconf# director.cfg.example

# Create certificates
DIRECTOR_TESTING=true python cpsconf.py localhost

touch cpsdirectorconf/ConPaaS.tar.gz

python setup.py install
coverage run --source=cpsdirector test.py
