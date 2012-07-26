#!/bin/bash

if [[ -z $1 || -z $2 || -z $3 ]]; then
    echo "usage: edge.sh <monitor_host> <port> <interval>"
    exit
fi

MONITOR_HOST=$1
MONITOR_PORT=$2
INTERVAL=$3

get_state() {
    case "$1" in
	'us-east-1')
	    STATE='US'
	    return 1;;
	'us-west-1')
	    STATE='US'
	    return 1;;
	'us-west-2')
	    STATE='US'
	    return 1;;
	'eu-west-1')
	    STATE='IE'
	    return 1;;
	'ap-southeast-1')
	    STATE='SG'
	    return 1;;
	'ap-northeast-1')
	    STATE='JP'
	    return 1;;
	'sa-east-1')
	    STATE='BR'
	    return 1;;
    esac
    return 0
}

HOST=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`
REGION=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/[a-z]$//'`

get_state $REGION
if [ -z $? ]; then
    echo "Could not find the country for region $REGION"
    exit 1
fi

while [ true ]; do
    echo "country=$STATE host=$HOST apps=`commands/get_apps.sh`" | nc $MONITOR_HOST $MONITOR_PORT
    sleep $INTERVAL
done
