#!/bin/sh

start_service() {
    service_type=$1
    manager_ip=`cpsclient.py create $1 | awk '{ print $5 }' | sed s/...$//`
    sid=`cpsclient.py list | grep $manager_ip | awk '{ print $2 }'`
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
echo "Taskfarm functional test started" | ts

start_service "taskfarm"
taskfarm_sid="$?"

echo "Taskfarm service created" | ts

wait_for_running $taskfarm_sid

echo "Taskfarm service running" | ts

# Creating BOT file
seq 70 | sed s/^.*/'sleep 1 \; echo "slept for 1 seconds" >> \/tmp\/log'/ > file.bot

# Uploading BOT file
cpsclient.py upload_bot $taskfarm_sid file.bot /tmp/ | sed s/.$// | ts

# Removing BOT file
rm file.bot

# Waiting for all the tasks to be completed
while [ -z "`cpsclient.py info $taskfarm_sid | grep 'completed tasks: 70'`" ]
do
    sleep 10
    echo "Waiting for tasks completion" | ts
done

cpsclient.py terminate $taskfarm_sid | ts
