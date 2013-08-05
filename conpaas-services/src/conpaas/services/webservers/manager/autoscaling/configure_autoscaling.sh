#!/bin/bash

apt-get -y --force-yes install libatlas-base-dev libatlas3gf-base python-dev python-scipy python-setuptools gfortran g++

easy_install numpy
easy_install -U numpy
#easy_install scipy
easy_install pandas
easy_install statsmodels
easy_install patsy
