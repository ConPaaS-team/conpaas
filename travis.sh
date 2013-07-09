#!/bin/sh

COVERAGE="`which python-coverage`"

if [ -z "$COVERAGE" ]
then
    COVERAGE="`which coverage`"
fi

cd $CI_HOME/conpaas-client
python setup.py install

cd $CI_HOME/conpaas-director

# Create fake files/directories not really needed for unit testing
touch ConPaaS.tar.gz
mkdir conpaas
cp -a ../conpaas-services/config conpaas
cp -a ../conpaas-services/scripts conpaas

mkdir -p cpsdirectorconf/certs

# We cannot use system-wide directories
sed -i s#/etc/cpsdirector#$PWD/cpsdirectorconf# director.cfg.example

python setup.py install

# Create certificates
DIRECTOR_TESTING=true python cpsconf.py localhost

# Fake tarball
touch cpsdirectorconf/ConPaaS.tar.gz

$COVERAGE run --source=cpsdirector test.py
$COVERAGE report -m

cd ../conpaas-services/src/tests/ 

$COVERAGE run --source=conpaas run_tests.py
$COVERAGE report -m
