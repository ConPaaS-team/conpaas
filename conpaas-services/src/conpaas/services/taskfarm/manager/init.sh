#!/bin/bash

export IP_PUBLIC
export SAMPLING_WORKERS

port=8999
iplServerOutput=/root/iplServer.out

java -classpath $CLASSPATH:$IPL_HOME/lib/* \
	-Dlog4j.configuration=file:$IPL_HOME/log4j.properties \
	-Dsmartsockets.external.manual=$IP_PUBLIC \
	-Xmx256M ibis.ipl.server.Server \
	--events --errors --stats  --port $port \
	2> $iplServerOutput &

test -s $iplServerOutput
while [ $? -ne 0 ]
do
	sleep 1
	test -s $iplServerOutput
done

address=""

while [ -z "$address" ]
do
    sleep 1
    address=$(grep "^Ibis server running on" $iplServerOutput | awk '{print $5}')
done

poolname="master_pool"

java -cp $BATS_HOME_LIB/*:$BATS_HOME/:$IPL_HOME/lib/* \
	-Dlog4j.configuration=log4j.properties:$IPL_HOME/log4j.properties \
	-Dibis.pool.name=$poolname \
	-Dibis.server.address=$address \
	-Dibis.server.port=$port \
	org.koala.runnersFramework.runners.bot.listener.BatsWrapper \
	1> $BATS_HOME/out.log 2> $BATS_HOME/err.log &
