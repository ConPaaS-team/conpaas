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
echo "XtreemFS functional test started" | ts

start_service "xtreemfs"
xtreemfs_sid="$?"

echo "XtreemFS service created" | ts

wait_for_running $xtreemfs_sid

echo "XtreemFS service running" | ts

# Create a new volume
cpsclient.py create_volume $xtreemfs_sid testvol > /dev/null
wait_for_running $xtreemfs_sid

# The list of volumes should contain "testvol"
if [ "testvol" = "`cpsclient.py list_volumes $xtreemfs_sid | awk '/testvol/ { print $1 }'`" ]
then 
    echo "Volume created successfully" | ts
else
    echo "Volume creation FAILED" | ts
    exit 1
fi

# Delete test volume
cpsclient.py delete_volume $xtreemfs_sid testvol > /dev/null
wait_for_running $xtreemfs_sid

if [ "testvol" = "`cpsclient.py list_volumes $xtreemfs_sid | awk '/testvol/ { print $1 }'`" ]
then 
    echo "Volume deletion FAILED" | ts
    exit 1
else
    echo "Volume deleted successfully" | ts
fi

cpsclient.py stop $xtreemfs_sid | ts

while [ -z "`cpsclient.py info $xtreemfs_sid | grep 'state: STOPPED'`" ]
do
    sleep 2
done

cpsclient.py terminate $xtreemfs_sid | ts
