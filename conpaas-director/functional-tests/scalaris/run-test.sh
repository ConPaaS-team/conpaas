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
echo "Scalaris functional test started" | ts

start_service "scalaris"
scalaris_sid="$?"

echo "Scalaris service created" | ts

wait_for_running $scalaris_sid

echo "Scalaris service running" | ts

management_url=`cpsclient.py info $scalaris_sid | awk '/^management server url/ { print $4 }'`

lynx -dump $management_url | grep 'Scalaris Management Server Info Page' > /dev/null

(if [ "$?" -eq 0 ]; then echo "Test passed!"; else echo "Test failed!"; fi) | ts

cpsclient.py stop $scalaris_sid | ts

while [ -z "`cpsclient.py info $scalaris_sid | grep 'state: STOPPED'`" ]
do
    sleep 2
done

cpsclient.py terminate $scalaris_sid | ts
