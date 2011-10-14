#!/bin/bash

PWD=`pwd`
PYTHONPATH=${PWD}/../src:${PWD}/../contrib
PYTHONPATH=${PYTHONPATH} python ${PWD}/../src/conpaas/mysql/server/manager/server.py -c ${PWD}/../src/conpaas/mysql/server/manager/configuration.cnf
