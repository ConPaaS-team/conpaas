#!/bin/bash
# this script is meant to be ran remotely on each edge location, to add a new
# application for content delivery

CDS_CONF_DIR=/etc/nginx/cds-enabled
ORIGIN=$1
if [ -z $ORIGIN ]; then
    echo Origin host not specified
    exit 1
fi

LINK=$2
if [ -z $LINK ]; then
    LINK="$ORIGIN"
fi

NGINX_CONF="location /$ORIGIN/ {
         proxy_pass http://$LINK/;
         proxy_cache cloudsurfing;
}"

# write the configuration patch for our app
sudo bash -c "echo '$NGINX_CONF' > $CDS_CONF_DIR/$ORIGIN"
# test if the configuration is OK
sudo nginx -t
if [ $? -ne 0 ]; then
    echo Configuration not correct. Abandon changes for $ORIGIN
    sudo rm -f $CDS_CONF_DIR/$ORIGIN
    exit 1
fi
# if the configuration is OK, start or reload it
if [ -z `cat /var/run/nginx.pid` ]; then
    echo Start nginx
    sudo nginx
else
    echo Reload nginx configuration
    sudo nginx -s reload
fi
