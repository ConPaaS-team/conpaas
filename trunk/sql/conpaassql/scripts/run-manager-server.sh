#!/bin/bash

PWD=`pwd`
PYTHONPATH=${PWD}/../src
PYTHONPATH=${PYTHONPATH} python ${PWD}/../src/conpaas/mysql/server/manager/server.py -c ${PWD}/../src/conpaas/mysql/server/manager/sql_manager_configuration.cnf
