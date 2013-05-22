#!/bin/sh

start_service() {
    service_type=$1
    manager_ip=`cpsclient.py create $1 | awk '{ print $5 }' | sed s/...$//`
    sid=`cpsclient.py list | grep $manager_ip | awk '{ print $2 }'`

    cpsclient.py start $sid > /dev/null
    return $sid
}

wait_for_running() {
    sid=$1

    while [ -z "`cpsclient.py info $sid | grep 'state: RUNNING'`" ]
    do
        sleep 2
    done
}

# Create and start service
echo "Hadoop functional test started" | ts

start_service "hadoop"
hadoop_sid="$?"

echo "Hadoop service created" | ts

wait_for_running $hadoop_sid

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

cpsclient.py stop $hadoop_sid | ts

while [ -z "`cpsclient.py info $hadoop_sid | grep 'state: STOPPED'`" ]
do
    sleep 2
done

cpsclient.py terminate $hadoop_sid | ts
