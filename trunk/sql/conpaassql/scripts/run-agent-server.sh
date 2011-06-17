#!/bin/bash

PIDFILE="/tmp/conpaassql.pid"
PWD=`pwd`
PYTHONPATH=${PWD}/../src
eval PYTHONPATH=${PYTHONPATH} python ${PWD}/../src/conpaas/mysql/server/agent/server.py &
PYPID=`echo $!`
touch ${PIDFILE}
rm ${PIDFILE}
echo ${PYPID} > ${PIDFILE}
