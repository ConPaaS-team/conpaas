#!/bin/bash

PIDFILE="/tmp/conpaassql.pid"
touch ${PIDFILE}
rm ${PIDFILE}
PWD=`pwd`
PYTHONPATH=${PWD}/../src
PYTHONPATH=${PYTHONPATH} python ${PWD}/../src/conpaas/mysql/server/agent/server.py
#PYTHONPATH=${PYTHONPATH} python ${PWD}/../src/conpaas/mysql/server/agent/server.py &
#echo $! > ${PIDFILE}
