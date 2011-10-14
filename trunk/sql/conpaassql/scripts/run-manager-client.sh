#!/bin/bash

PWD=`pwd`
PYTHONPATH=${PWD}/../src:${PWD}/../contrib
PYTHONPATH=${PYTHONPATH} python ${PWD}/../src/conpaas/mysql/client/manager_client.py $* &
