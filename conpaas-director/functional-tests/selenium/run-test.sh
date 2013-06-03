#!/bin/sh

manifest='{ "Application" : "Selenium", "Services" : [ { "Type" : "selenium", "FrontendName" : "Selenium test", "Start" : 1 } ] }'

# Create and start service
echo "Selenium functional test started" | ts

echo $manifest > /tmp/testmanifest
cpsclient.py manifest /tmp/testmanifest | ts
selenium_sid=`cpsclient.py list | grep selenium | awk '{ print $2 }'`
rm /tmp/testmanifest

echo "Selenium service running" | ts

selenium_hub_url=`cpsclient.py info $selenium_sid | awk '/^hub/ { print $3 }'`
lynx -dump $selenium_hub_url | grep "You are using grid" > /dev/null

(if [ "$?" -eq 0 ]; then echo "Test passed!"; else echo "Test failed!"; fi) | ts

cpsclient.py stop $selenium_sid | ts

while [ -z "`cpsclient.py info $selenium_sid | grep 'state: STOPPED'`" ]
do
    sleep 2
done

appid=`cpsclient.py listapp | grep Selenium | awk '{ print $1 }'`
cpsclient.py deleteapp $appid | ts
