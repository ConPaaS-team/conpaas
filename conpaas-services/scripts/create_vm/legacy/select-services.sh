#!/bin/bash
services="php mysql htcondor ipop git selenium hadoop scalaris xtreemfs cds"
SERVICES=`echo -n $services | tr '[a-z]' '[A-Z]'`
USAGE=`echo $services | sed 's/ / | /g'`
for uc in `echo $SERVICES`; do eval ${uc}_SERVICE=false ; done
nocasematch=true
# No service specified means: all
[ $# == 0 ] && set all
for i in $@
do
	uc=`echo -n $i | tr '[a-z]' '[A-Z]'`
	lc=`echo -n $i | tr '[A-Z]' '[a-z]'`
	case $lc in
	all) for ii in `echo $SERVICES`; do eval ${ii}_SERVICE=true ; done ;;
	php|mysql|htcondor|ipop|git|selenium|hadoop|scalaris|xtreemfs|cds) eval ${uc}_SERVICE=true ;;
	*)	echo "Unknown service \`$i'" ; echo "Usage: $0 [ $USAGE ]" ; exit 1 ;;
	esac
done
nocasematch=false

for i in $SERVICES
do
	name=${i}_SERVICE
	eval echo $name=\${$name}
done > services_config.cfg
cat services_config.cfg
