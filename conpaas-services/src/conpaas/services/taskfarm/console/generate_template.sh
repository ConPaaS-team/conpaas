#!/bin/bash
# To create a vm template out of the contents of init.sh to pass to manager VM.

###############################################################################
# If you are using a secure XtreemFS drive, you need to uncomment and update
# the following lines by changing your_certificate.p12 and grid-mapfile.
###############################################################################
#XTFS_CERT_RAW=`xxd -p your_certificate.p12`
#XTFS_CERT=`echo $XTFS_CERT_RAW | sed 's/ //g'`

#GRID_MAP_RAW=`xxd -p grid-mapfile`
#GRID_MAP=`echo $GRID_MAP_RAW | sed 's/ //g'`

#sed 's|all variables accordingly:|all variables accordingly:\
#export XTFS_CERT=\"'"$XTFS_CERT"'\"\
#export GRID_MAP=\"'"$GRID_MAP"'\"|' < init.sh > final_init.sh
###############################################################################


HEXRAW=`xxd -p final_init.sh`
HEX=`echo $HEXRAW | sed 's/ //g'`
sed 's|CONTEXT\ =\ \[|CONTEXT\ =\ \[\
\ \ USERDATA\ =\ \"'"$HEX"'\",|' < template.vm > final_template.vm

cp bagMountTest.bot ~/TaskFarmPublic/config
cp clusterConf.xml ~/TaskFarmPublic/config
