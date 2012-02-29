#!/bin/bash

PWD=`pwd`
PYTHONPATH=${PWD}/../src
PYTHONPATH=${PYTHONPATH} python ${PWD}/../src/conpaas/mysql/client/agent_client.py $* &
