#!/bin/sh

manifest='{ "Application" : "Taskfarm", "Services" : [ { "Type" : "taskfarm", "ServiceName" : "Taskfarm test", "Start" : 0 } ] }'

# Create and start service
echo "Taskfarm functional test started" | ts

echo $manifest > /tmp/testmanifest
cpsclient.py manifest /tmp/testmanifest | ts
taskfarm_sid=`cpsclient.py list | grep taskfarm | awk '{ print $2 }'`
rm /tmp/testmanifest

echo "Taskfarm service running" | ts

# Select service mode
cpsclient.py set_mode $taskfarm_sid REAL

# Creating BOT file
seq 70 | sed s/^.*/'sleep 1 \; echo "slept for 1 seconds" >> \/tmp\/log'/ > file.bot

# Uploading BOT file
upload_result="`cpsclient.py upload_bot $taskfarm_sid file.bot /tmp/ | sed s/.$// | ts`"
echo "$upload_result"

# Removing BOT file
rm file.bot

echo $upload_result | grep ERROR > /dev/null
if [ $? -eq 0 ]
then
    echo "Aborting ..." | ts
else
    # Waiting for all the tasks to be completed
    while [ -z "`cpsclient.py info $taskfarm_sid | grep 'completed tasks: 70'`" ]
    do
	sleep 10
	echo "Waiting for tasks completion" | ts
    done
fi

appid=`cpsclient.py listapp | grep Taskfarm | awk '{ print $1 }'`
cpsclient.py deleteapp $appid | ts
