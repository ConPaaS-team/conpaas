#!/bin/sh

set -e

if [ ! -x "/usr/bin/lynx" ]
then
    echo "lynx not found. Exiting" > /dev/stderr
    exit 1
fi

if [ ! -x "/usr/bin/ts" ]
then
    echo "ts not found. Please install debian-goodies Exiting" > /dev/stderr
    exit 1
fi

for service in `find -mindepth 1 -maxdepth 1 -type d | grep -v .svn`
do
    cd $service 
    echo "Running test $service"
    ./run-test.sh
    cd ..
done
