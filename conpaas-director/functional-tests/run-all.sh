#!/bin/sh

set -e

[ -x "/usr/bin/lynx" ] || exit 1

for service in `find -mindepth 1 -maxdepth 1 -type d | grep -v .svn`
do
    cd $service 
    echo "Running test $service"
    ./run-test.sh
    cd ..
done
