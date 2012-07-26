#!/bin/bash

if [[ -z $1 || -z $2 ]]; then
    echo "usage: run_command.sh <host> <command>"
    exit
fi

BASE_DIR="/usr/local/cds"
HOST=$1
USER=ubuntu
KEY="$BASE_DIR/cds.pem"
shift
CMD=$1
shift

if [ ! -f $KEY ]; then
    echo Cannot access key for edge locations
    exit 1
fi

CMD="commands/$CMD.sh"

if [ ! -x $BASE_DIR/$CMD ]; then
    echo Command $BASE_DIR/$CMD not found or not executable
    exit 1
fi

rsync $BASE_DIR/$CMD -e "ssh -i $KEY" $USER@$HOST:control/$CMD
ssh -i $KEY $USER@$HOST "control/$CMD $@"
