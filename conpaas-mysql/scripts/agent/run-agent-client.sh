#!/bin/bash

PWD=`pwd`
python ${PWD}/../../src/conpaas/mysql/client/agent_client.py $* &
