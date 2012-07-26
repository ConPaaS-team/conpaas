#!/bin/bash

CDS_CONF_DIR=/etc/nginx/cds-enabled
ORIGIN=$1

if [ -z $ORIGIN ]; then
    echo Origin host was not specified
    exit 1
fi

sudo rm $CDS_CONF_DIR/$ORIGIN
if [ $? -ne 0 ]; then
    echo Couldn\'t delete the configuration file
    exit 1
fi

echo $ORIGIN removed from `hostname`
# start or reload nginx
if [ -z `cat /var/run/nginx.pid` ]; then
    echo Start nginx
    sudo nginx
else
    echo Reload nginx configuration
    sudo nginx -s reload
fi
