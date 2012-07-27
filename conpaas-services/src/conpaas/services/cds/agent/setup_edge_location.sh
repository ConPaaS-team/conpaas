#!/bin/bash

if [ -z $1 ]; then
    echo "usage: setup_edge_location <host>"
    exit
fi

HOST=$1
#KEY="/usr/local/cds/cds.pem"
KEY=cds.pem
USER=ubuntu

if [ ! -f $KEY ]; then
    echo Cannot access key for edge locations
    exit 1
fi

ssh -i $KEY $USER@$HOST "sudo apt-get install nginx; sudo chown -R ubuntu:ubuntu /etc/nginx; sudo mkdir /etc/nginx/cds-enabled/"
scp -i $KEY conf/nginx.conf $USER@$HOST:/etc/nginx/
scp -i $KEY conf/default $USER@$HOST:/etc/nginx/sites-enabled/
ssh -i $KEY $USER@$HOST "sudo mkdir /usr/local/cds; sudo chown ubuntu:ubuntu /usr/local/cds; cd /usr/local/cds/; mkdir -p cache; mkdir -p edge/commands"
scp -i $KEY edge.sh $USER@$HOST:/usr/local/cds/edge/
scp -i $KEY ../manager/commands/get_apps.sh $USER@$HOST:/usr/local/cds/edge/commands/