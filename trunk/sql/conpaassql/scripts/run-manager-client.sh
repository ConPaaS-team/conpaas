#!/bin/bash

E_BADARGS=65
if [ $# -ne 3 ]
then
        if [ $# -ne 4 ]
        then
                  echo "Usage: `basename $0` command <hostname> <port> [id] [ agent | manager ]"
                  echo "        Command is one of"
                  echo "         listServiceNodes <hostname> <port> - lists all service nodes."
                  echo "         getMySQLServerState <hostname> <port> - gets the state of the manager."
                  echo "         createServiceNode <hostname> <port> [ agent | client ] - creates new node in the list of sql nodes. Additional argument is required: agent or manager. If not, agent is default."
                  echo "         deleteServiceNode <hostname> <port> [id]"
                  exit $E_BADARGS
        fi
fi

PWD=`pwd`
PYTHONPATH=${PWD}/../src
PYTHONPATH=${PYTHONPATH} python ${PWD}/../src/conpaas/mysql/client/manager_client.py $* &

