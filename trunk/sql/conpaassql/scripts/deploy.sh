#!/bin/bash

if [ $# -ne 3 ]
then
	echo "Usage: `basename $0` user server command"
	echo "first argument: server name"
	echo "second argument: server to deploy to"
	echo "third argument: command after the deployment (start-agent, start-manager)"
	exit 1
fi

PACKAGE_DIR="~/conpaassql"
PACKAGE_NAME="conpaassql.tar.gz"
SOURCE="../../conpaassql"
TAR_DEST="../../conpaassql.tar.gz"
CONPAASROOT="/tmp"
CONPAASSQLPID="${CONPAASROOT}/conpaassql.pid"
CONPAASSQLERR="${CONPAASROOT}/conpaassql.err"
CONPAASSQLOUT="${CONPAASROOT}/conpaassql.out"

USER=$1
DEST_SERVER_IP=$2
COMMAND=$3

ssh-agent
tar cvfz ${TAR_DEST} --exclude=.svn ${SOURCE}
scp ${TAR_DEST} ${USER}@${DEST_SERVER_IP}:~
#echo "Removing ${PACKAGE_DIR} on remote server ${DEST_SERVER_IP}"
#ssh ${USER}@${DEST_SERVER_IP} rm -fr ${PACKAGE_DIR}
#echo "Untaring deployment package"
#ssh ${USER}@${DEST_SERVER_IP} tar xvfz ~/${PACKAGE_NAME}
ssh ${USER}@${DEST_SERVER_IP} "rm -fr ${PACKAGE_DIR}; tar xvfz ~/${PACKAGE_NAME}; if [ -e ${CONPAASSQLPID} ]; then kill -9 `cat ${CONPAASSQLPID}`; else exit 0; fi"
if [ ${COMMAND} == "start-agent" ]
then
	ssh ${USER}@${DEST_SERVER_IP} "cd ${PACKAGE_DIR}/scripts/; ./run-agent-server.sh 1> ${CONPAASSQLOUT} 2> ${CONPAASSQLERR} &"
fi
