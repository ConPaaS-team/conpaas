#!/bin/bash

# usage: phpsession.sh path_to_code_dir path_to_session_php

FILES=`find $1 -name "*.php"`

for file in $FILES
do
	grep -q "session_start()" $file && sed -i "1i\<?php require_once '$2' ?>" $file 
done



