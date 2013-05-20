#!/bin/sh

owncloud='{ "Application" : "Owncloud", "Services" : [ { "Type" : "php", "FrontendName" : "Php backend", "Archive" : "http://download.owncloud.org/community/owncloud-5.0.6.tar.bz2", "Start" : 1 }, { "Type" : "mysql", "FrontendName" : "Mysql backend" } ] }'
wordpress='{ "Application" : "Wordpress", "Services" : [ { "Type" : "php", "FrontendName" : "Php backend", "Archive" : "http://wordpress.org/wordpress-3.5.1.tar.gz", "Start" : 1 }, { "Type" : "mysql", "FrontendName" : "Mysql backend" } ] }'

# Start of the tests
echo "Manifest functional test started" | ts

# Start the Owncloud manifest
echo $owncloud > tmp-manifest
cpsclient.py manifest tmp-manifest | ts

# IP address of the freshly created PHP web app
web_ip=$(cpsclient.py info `cpsclient.py list | grep php  | awk '{ print $2 }'` | grep ^web | awk '{ print $2 }')

# Check if our ownCloud homepage is up & running
lynx -dump http://$web_ip/owncloud/index.php | grep "ownCloud" > /dev/null

(if [ "$?" -eq 0 ]; then echo "Test passed!"; else echo "Test failed!"; fi) | ts

# Remove the Owncloud application
appid=`cpsclient.py listapp | grep Owncloud | awk '{ print $1}'`
cpsclient.py deleteapp $appid | ts

# Start the Wordpress manifest
echo $wordpress > tmp-manifest
cpsclient.py manifest tmp-manifest | ts

# IP address of the freshly created PHP web app
web_ip=$(cpsclient.py info `cpsclient.py list | grep php  | awk '{ print $2 }'` | grep ^web | awk '{ print $2 }')

# Check if our WordPress homepage is up & running
lynx -dump http://$web_ip/wordpress/index.php | grep "wordpress" > /dev/null

(if [ "$?" -eq 0 ]; then echo "Test passed!"; else echo "Test failed!"; fi) | ts

# Remove the Wordpress application
appid=`cpsclient.py listapp | grep Wordpress | awk '{ print $1}'`
cpsclient.py deleteapp $appid | ts

rm tmp-manifest

# End of the test
echo "Manifest functional test ended" | ts
