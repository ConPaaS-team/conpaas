#!/bin/sh

cd $CI_HOME/conpaas-director
coverage run --source=cpsdirector test.py
