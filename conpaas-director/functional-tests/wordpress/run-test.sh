#!/bin/sh

# We assume that cpsclient is properly configured on the local machine, and
# that the director has no running services when the test begins. Furthermore,
# we need "ts" to be available (from the moreutils debian package).

cpsclient.py list | grep "No running services"

if [ "$?" -ne 0 ]
then
    echo "E: Check that cpsclient is configured properly and that no services are running."
    exit 1
fi

if [ ! -x "`which ts`" ]
then
    echo "E: Please install the 'moreutils' Debian package."
    exit 1
fi

wget "http://www.linux.it/~ema/conpaas/wordpress-test-code.tar.bz2"

tar xfj "wordpress-test-code.tar.bz2" > /dev/null

rm "wordpress-test-code.tar.bz2"

# Create and start a mysql and php web hosting service. Deploy wordpress on
# them.
./deploy-wordpress.sh wordpress-code wordpress-db.sql

rm -rf wordpress-code
rm wp-upload.tar.gz

# IP address of the freshly created PHP web app
web_ip=$(cpsclient.py info `cpsclient.py list | grep php  | awk '{ print $2 }'` | grep ^web | awk '{ print $2 }')

# Check if our wordpress homepage contains the 'ConPaaS Functional Test' string
lynx -dump http://$web_ip/ | grep "ConPaaS Functional Test" > /dev/null 

(if [ "$?" -eq 0 ]; then echo "Test passed!"; else echo "Test failed!"; fi) | ts

# Stop and terminate test services
cpsclient.py stop 1 | ts
cpsclient.py stop 2 | ts

for sid in 1 2
do
    while [ -z "`cpsclient.py info $sid | grep 'state: STOPPED'`" ]
    do
        sleep 2
    done

    cpsclient.py terminate $sid | ts
done

