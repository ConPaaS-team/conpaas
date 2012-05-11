#!/bin/bash 

# Cleanup if existing archive
rm -f ConPaaS.tar.gz

mkdir ConPaaS
cp -r bin config contrib misc sbin scripts src ConPaaS

# Compile the taskfarm code
export BATS_HOME=src/conpaas/services/taskfarm
export IPL_HOME=src/conpaas/services/taskfarm/ipl-2.2
. src/conpaas/services/taskfarm/compile.sh

# Cleanup if taken from svn
rm -Rf `find ConPaaS -name .svn`

tar -zcvf ConPaaS.tar.gz ConPaaS

# Cleanup temp folder
rm -fr ConPaaS
