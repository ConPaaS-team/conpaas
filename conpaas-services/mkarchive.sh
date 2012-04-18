#!/bin/bash 

# Cleanup if existing archive
rm -f ConPaaS.tar.gz

mkdir ConPaaS
cp -r bin config contrib misc sbin scripts src ConPaaS

# Cleanup if taken from svn
rm -Rf `find ConPaaS -name .svn`

tar -zcvf ConPaaS.tar.gz ConPaaS

# Cleanup temp folder
rm -fr ConPaaS
