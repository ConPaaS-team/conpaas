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
echo "Selenium functional test started" | ts

start_service "selenium"
selenium_sid="$?"

echo "Selenium service created" | ts

wait_for_running $selenium_sid

echo "Selenium service running" | ts

selenium_hub_url=`cpsclient.py info $selenium_sid | awk '/^hub/ { print $3 }'`
lynx -dump $selenium_hub_url | grep "You are using grid" > /dev/null

(if [ "$?" -eq 0 ]; then echo "Test passed!"; else echo "Test failed!"; fi) | ts

cpsclient.py stop $selenium_sid | ts

while [ -z "`cpsclient.py info $selenium_sid | grep 'state: STOPPED'`" ]
do
    sleep 2
done

cpsclient.py terminate $selenium_sid | ts
