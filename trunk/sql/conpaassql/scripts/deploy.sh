#!/bin/bash

if [ $# -ne 2 ]
then
	echo "Usage: `basename $0` user server command"
	echo "   first argument: server name"
	echo "   second argument: server to deploy to"
	echo "   third argument: command after the deployment (start-agent, start-manager)"
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

echo "tar-ing new code on local node - code to be deployed"
tar cvfz ${TAR_DEST} --exclude=.svn ${SOURCE} 1> /dev/null 2> /dev/null
echo "scp-ing new code to remote node"
scp ${TAR_DEST} ${USER}@${DEST_SERVER_IP}:~
#echo "Installing new and killing old remote existing instances."
echo "Installing new instance."
#ssh ${USER}@${DEST_SERVER_IP} "rm -fr ${PACKAGE_DIR}; tar xvfz ~/${PACKAGE_NAME} 1> /dev/null 2> /dev/null; if [ -e ${CONPAASSQLPID} ]; then kill -9 \`cat ${CONPAASSQLPID}\`; else exit 0; fi"
ssh ${USER}@${DEST_SERVER_IP} "rm -fr ${PACKAGE_DIR}; tar xvfz ~/${PACKAGE_NAME} 1> /dev/null 2> /dev/null"
#if [ ${COMMAND} == "start-agent" ]
#then
#	ssh ${USER}@${DEST_SERVER_IP} "cd ${PACKAGE_DIR}/scripts/; ./run-agent-server.sh"
#fi
