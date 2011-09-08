#!/bin/bash
E_BADARGS=65

test=false
# Test if the number of arguments is in array
for i in 3 4 5 6
do
	if [ $# -eq ${i} ]
	then
		test=true
	fi
done

if [ ! ${test} ]
then
	echo "Usage: `basename $0` command <hostname> <port> {additional parameters} "
	echo "        Command is one of"
	echo "         getMySQLServerState - gets state of the mysql server."
	echo "         createMySQLServer - starts mysql server."
	echo "         restartMySQLServer - restarts mysql server."
	echo "         stopMySQLServer - stops mysql server."
	echo "         configure_user - configures user, additional parameters: <username> <password>"
	echo "         get_all_users - gets all mysql users."
	echo "         remove_user - removes user from the database."
	echo "         setMySQLServerConfiguration - configures the mysql server." 
	echo "         send_mysqldump - creates a database based on given dump."
	exit $E_BADARGS
fi

PWD=`pwd`
PYTHONPATH=${PWD}/../src
PYTHONPATH=${PYTHONPATH} python ${PWD}/../src/conpaas/mysql/client/agent_client.py $* &
