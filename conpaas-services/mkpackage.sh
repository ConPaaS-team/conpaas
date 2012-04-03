#!/bin/bash 

# Cleanup if taken from svn
rm -Rf `find . -name .svn`
# Cleanup if existing archive
rm -f ConPaaS.tar.gz
# Make archive
mkdir ConPaaS
cp -r bin config contrib misc sbin scripts src ConPaaS
tar -zcvf ConPaaS.tar.gz ConPaaS
rm -fr ConPaaS
