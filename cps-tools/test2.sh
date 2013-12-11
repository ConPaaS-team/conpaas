#!/bin/bash -xe

services=""
declare -A service

### PHP service
service[type]='php'
service[check_working]='php_check_working'

function php_check_working() {
    ## need an ip address....
    entry_ip=$1
}

services="$services $service"


## Galera service
service[type]='galera'
service[check_working]='galera_check_working'

function galera_check_working() {
    ## need an ip address....
    entry_ip=$1
}

services="$services $service"


for service in $services
do
    cps-tools create $service[type]

    sid=...

    cps-tools service start $sid

    cps-tools service add_nodes --$service[role][0] 1

    ${service[check_working]} $service_entry

    cps-tools sercice remove_nodes --$service[role][0] 1

    ${service[check_working]} $service_entry

    cps-tools service stop $sid
    
    cps-tools service delete $sid

done
