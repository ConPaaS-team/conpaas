#!/bin/sh

cd $CI_HOME/conpaas-client
python setup.py install

cd $CI_HOME/conpaas-director

# Create fake files/directories not really needed for unit testing
touch ConPaaS.tar.gz
mkdir -p conpaas/{config,scripts}

python setup.py install
coverage run --source=cpsdirector test.py
