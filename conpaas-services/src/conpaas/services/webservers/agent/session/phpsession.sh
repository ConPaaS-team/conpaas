#!/bin/bash

# usage:
# 	session.sh path_to_code_dir path_to_session_php

FILES=`find $1 -name "*.php"`

for file in $FILES
do
	cat $file | grep -q "session_start()" && \
		sed "1i\<?php require_once '$2' ?>" $file > /tmp/session.php && \
		mv /tmp/session.php $file
done



