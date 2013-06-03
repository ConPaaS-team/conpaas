#!/bin/sh

manifest='{ "Application" : "Taskfarm", "Services" : [ { "Type" : "taskfarm", "FrontendName" : "Taskfarm test", "Start" : 1 } ] }'

# Create and start service
echo "Taskfarm functional test started" | ts

echo $manifest > /tmp/testmanifest
cpsclient.py manifest /tmp/testmanifest | ts
taskfarm_sid=`cpsclient.py list | grep taskfarm | awk '{ print $2 }'`
rm /tmp/testmanifest

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

appid=`cpsclient.py listapp | grep Taskfarm | awk '{ print $1 }'`
cpsclient.py deleteapp $appid | ts
