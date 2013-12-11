#!/bin/bash -xe

#
# Testing whether PHP services are usable
#

APPL_NAME="Test PHP application"

cps-tools application $APPL_NAME
appl_id="$(cps-tools application list | grep $APPL_NAME | awk '{print $1}')"

cps-tools service create php --application $appl_id

sid="$(cps-tools service list | grep "^$appl_id" | awk '{print $3}')"

cps-tools php get_config $sid

cps-tools php start $sid

# Initially all roles are running on the same machine
appl_ip="$(cps-tools php list_nodes | head -n 1 | awk '{print $NF}')"

function check_appli() {
  appl_ip="$1"
  ## check appli_ip is available
  wget -q -O - "$appl_ip/index.php" | grep "..."
}

function check_list_nodes() {
  sid=$1
  # expected number of web nodes
  web=$2
  # expected number of backend nodes
  backend=$3
  # expected number of proxy nodes
  proxy=$4

  for line in $(cps-tools php list_nodes $sid)
  do
    roles can be shared on the same node!!!
  done
}

check_appli $appl_ip

cps-tools php add_nodes $sid --web 1 --backend 2


check_appli $appl_ip

cps-tools php remove_nodes $sid --backend 1

check_appli $appl_ip

cps-tools php remove_nodes $sid --backend 1 --web 1

check_appli $appl_ip




