#!/bin/sh -x

# Create cps-tools tarball
cp -a conpaas-services/bin cps-tools

cat <<EOF > cps-tools/README
To use the cps-tools (on debian/ubuntu):

   $ apt-get install python python-pycurl
   $ export PYTHONPATH=/path/to/cps-tools
   $ export CONPAAS_CERTS_DIR=/path/to/conpaas/certs
   $ /path/to/cps-tools/cpsclient.xxx http://ip:port command
EOF

cp -a conpaas-services/src/conpaas cps-tools/

# Removing jars as we do not need them for the command line tools
find cps-tools -type f -name \*.jar | xargs rm

# Removing .svn dirs
find cps-tools -type d -name ".svn" | xargs rm -rf

tar czf cps-tools.tar.gz cps-tools

rm -rf cps-tools

echo "cps-tools.tar.gz created"
