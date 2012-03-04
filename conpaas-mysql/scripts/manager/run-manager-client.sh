#!/bin/bash

PWD=`pwd`
python ${PWD}/../../src/conpaas/mysql/client/manager_client.py $* &
