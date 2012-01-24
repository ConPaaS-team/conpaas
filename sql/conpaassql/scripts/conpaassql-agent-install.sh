#!/bin/bash
SERVER=contrail.xlab.si
PACKAGE_NAME=conpaassql.tar
DEST_DIR=/home/contrail/conpaassql

apt-get -y update

apt-get install -y unzip
apt-get install -y python
apt-get install -y python-mysqldb
apt-get install -y python-pycurl

mkdir -p ${DEST_DIR}
cd ${DEST_DIR}

wget ${SERVER}/${PACKAGE_NAME}

#wget https://github.com/lukaszo/python-oca/zipball/0.2.3
#wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz#md5=7df2a529a074f613b509fb44feefe74e

wget http://contrail.xlab.si/conpaassql/0.2.3
wget http://contrail.xlab.si/conpaassql/setuptools-0.6c11.tar.gz

tar xvfz setuptools-0.6c11.tar.gz
cd setuptools-0.6c11
python setup.py build
python setup.py install
cd ..
rm -rf setuptools
rm setuptools-0.6c11.tar.gz

unzip 0.2.3
cd lukaszo-python-oca-61992c1
python setup.py build
python setup.py install
cd ..
rm -rf lukaszo-python-oca-61992c1
rm 0.2.3

#tar xvfz testpackage.tar.gz
tar xvf ${PACKAGE_NAME}

#rm testpackage.tar.gz
rm ${PACKAGE_NAME}

cd src
PYTHONPATH=${DEST_DIR}/src:${DEST_DIR}/contrib python conpaas/mysql/server/agent/server.py -c ${DEST_DIR}/src/conpaas/mysql/server/agent/configuration.cnf

