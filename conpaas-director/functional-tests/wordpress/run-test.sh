#!/bin/sh

wget "http://www.linux.it/~ema/conpaas/wordpress-test-code.tar.bz2"

tar xfj "wordpress-test-code.tar.bz2" > /dev/null

# Create and start a mysql and php web hosting service. Deploy wordpress on
# them.
./deploy-wordpress.sh wordpress-code wordpress-db.sql

rm -rf wordpress-code
rm wp-upload.tar.gz

# IP address of the freshly created PHP web app
web_ip=$(cpsclient.py info `cpsclient.py list | grep php  | awk '{ print $2 }'` | grep ^web | awk '{ print $2 }')

# Check if our wordpress homepage contains the 'ConPaaS Functional Test' string
lynx -dump http://$web_ip/ | grep "ConPaaS Functional Test" > /dev/null 

if [ "$?" -eq 0 ]; then echo "Test passed!"; else echo "Test failed!"; fi
