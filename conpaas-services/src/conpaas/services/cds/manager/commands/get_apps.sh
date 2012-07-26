#!/bin/bash

CONF_DIR='/etc/nginx/cds-enabled/'
APPS=''
for site in `ls $CONF_DIR | sort`; do
    if [ -z $APPS ]; then
	APPS="$site"
    else
	APPS="$APPS,$site"
    fi
done
echo $APPS
