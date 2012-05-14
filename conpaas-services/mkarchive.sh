#!/bin/bash 

# Cleanup if existing archive
rm -f ConPaaS.tar.gz

# Compile the taskfarm code
export BATS_HOME=`pwd`/src/conpaas/services/taskfarm
export IPL_HOME=`pwd`/src/conpaas/services/taskfarm/ipl-2.2

$BATS_HOME/compile.sh

# Make the archive 
mkdir ConPaaS
cp -r bin config contrib misc sbin scripts src ConPaaS

# Cleanup if taken from svn
rm -Rf `find ConPaaS -name .svn`

tar -zcvf ConPaaS.tar.gz ConPaaS

# Cleanup temp folder
rm -fr ConPaaS
