#!/bin/bash

[ -z "$BATS_HOME" ] && echo "Need to set BATS_HOME" && exit 1
[ -z "$IPL_HOME" ] && echo "Need to set IPL_HOME" && exit 1

mkdir $BATS_HOME/temp 

javac -cp $BATS_HOME/lib/*:$IPL_HOME/lib/* \
	$BATS_HOME/src/org/koala/runnersFramework/runners/bot/*.java \
	$BATS_HOME/src/org/koala/runnersFramework/runners/bot/listener/*.java \
	-d $BATS_HOME/temp/

cd $BATS_HOME/temp
jar cf $BATS_HOME/lib/conpaas-bot.jar *
cd $1

rm -r $BATS_HOME/temp
