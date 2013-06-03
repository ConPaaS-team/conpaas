#!/bin/sh

manifest='{ "Application" : "MapReduce", "Services" : [ { "Type" : "hadoop", "FrontendName" : "MapReduce test", "Start" : 1 } ] }'

# Create and start service
echo "Hadoop functional test started" | ts

echo $manifest > /tmp/testmanifest
cpsclient.py manifest /tmp/testmanifest | ts
hadoop_sid=`cpsclient.py list | grep hadoop | awk '{ print $2 }'`
rm /tmp/testmanifest

echo "Hadoop service running" | ts

echo "Waiting 30 seconds for the daemons to startup..." | ts
sleep 30

hadoop_namenode_url=`cpsclient.py info $hadoop_sid | awk '/^master namenode url/ { print $4 }'`
echo -n "Testing Hadoop Namenode ($hadoop_namenode_url)..."

lynx -dump $hadoop_namenode_url | grep 'DFS Health/Status' > /dev/null 

(if [ "$?" -eq 0 ]; then echo "OK"; else echo "FAILURE"; fi) | ts

hadoop_jobtracker_url=`cpsclient.py info $hadoop_sid | awk '/^master job tracker url/ { print $5 }'`
echo -n "Testing Hadoop Job tracker ($hadoop_jobtracker_url)..."

lynx -dump $hadoop_jobtracker_url | grep 'Hadoop Administration' > /dev/null

(if [ "$?" -eq 0 ]; then echo "OK"; else echo "FAILURE"; fi) | ts

hadoop_hue_url=`cpsclient.py info $hadoop_sid | awk '/master HUE/ { print $4 }'`
echo -n "Testing Hadoop HUE ($hadoop_hue_url)..."

lynx -dump $hadoop_hue_url | grep 'Launching Hue' > /dev/null

(if [ "$?" -eq 0 ]; then echo "OK"; else echo "FAILURE"; fi) | ts

appid=`cpsclient.py listapp | grep MapReduce | awk '{ print $1 }'`
cpsclient.py deleteapp $appid | ts
