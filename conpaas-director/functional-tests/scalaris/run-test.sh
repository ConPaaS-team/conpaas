#!/bin/sh

manifest='{ "Application" : "Scalaris", "Services" : [ { "Type" : "scalaris", "ServiceName" : "Scalaris test", "Start" : 1 } ] }'

# Create and start service
echo "Scalaris functional test started" | ts

echo $manifest > /tmp/testmanifest
cpsclient.py manifest /tmp/testmanifest | ts
scalaris_sid=`cpsclient.py list | grep scalaris | awk '{ print $2 }'`
rm /tmp/testmanifest

echo "Scalaris service running" | ts

management_url=`cpsclient.py info $scalaris_sid | awk '/^management server url/ { print $4 }'`

sleep 5

lynx -dump $management_url | grep 'Scalaris Management Server Info Page' > /dev/null

(if [ "$?" -eq 0 ]; then echo "Test passed!"; else echo "Test failed!"; fi) | ts

cpsclient.py stop $scalaris_sid | ts

while [ -z "`cpsclient.py info $scalaris_sid | grep 'state: STOPPED'`" ]
do
    sleep 2
done

appid=`cpsclient.py listapp | grep Scalaris | awk '{ print $1 }'`
cpsclient.py deleteapp $appid | ts
