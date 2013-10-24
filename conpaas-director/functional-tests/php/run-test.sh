#!/bin/bash

set -x
set -e

php_create=$(cpsclient.py create php)

PHP_MNG_IP=$(echo $php_create | awk '{sub("\.\.\.", ""); print $(NF-1)}')
php_info=$(cpsclient.py list | grep $PHP_MNG_IP)
PHP_SRV_ID=$(echo $php_info | awk '{print $2}')

if [ \! -r $HOME/.ssh/id_rsa.pub ]
then
    mkdir -p $HOME/.ssh
    ssh-keygen -t rsa -f $HOME/.ssh/id_rsa -P ''
    cat > $HOME/.ssh/config <<EOF
Host *
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  HashKnownHosts no
  User root
EOF
fi

cpsclient.py upload_key $PHP_SRV_ID  $HOME/.ssh/id_rsa.pub

DEBIAN_FRONTEND=noninteractive apt-get -q -y install git


rm -rf code
git clone git@$PHP_MNG_IP:code

tar -xaf wordpress-3.6.tar.gz -C code
cd code
git add -A *
git commit -m "init"
git_output=$(git push origin master 2<&1)

version_id=$(echo $git_output | grep codeVersionId | sed "s|.*codeVersionId': '\(.*\)'.*|\1|")

cpsclient.py list_uploads $PHP_SRV_ID | grep $version_id

cpsclient.py enable_code $PHP_SRV_ID $version_id

cpsclient.py list_uploads $PHP_SRV_ID | grep "* $version_id"

# WON'T work:
# cpsclient.py download_code $PHP_SRV_ID $version_id
# because you can download code with git

(if [ "$?" -eq 0 ]; then echo "OK"; else echo "FAILURE"; fi)

# Cleaning
cpsclient.py terminate $PHP_SRV_ID


