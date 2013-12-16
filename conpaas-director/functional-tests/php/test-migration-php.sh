#!/bin/bash

php_program=sudoku-php.tar.gz

start_service() {
    service_type=$1

    manager_ip=`cpsclient.py create $1 | awk '{ print $5 }' | sed s/...$//`
    sid=`cpsclient.py list | grep $manager_ip | awk '{ print $2 }'`

    cpsclient.py start $sid > /dev/null
    echo $sid
}

wait_for_running() {
    sid=$1

    while [ -z "`cpsclient.py info $sid | grep 'state: RUNNING'`" ]
    do
        sleep 10
    done
}


wait_for_stopped() {
    sid=$1

    while [ -z "`cpsclient.py info $sid | grep 'state: STOPPED'`" ]
    do
        sleep 10
    done
}

test_php_page_is_working() {
    site_ip=$1

    wget -q $site_ip -O - | grep -q 'Online Sudoku by Michael Jentsch'
    if [ $? -ne 0 ]
    then
	echo "ERROR: cannot find PHP page."
	exit 1
    fi
}

test_static_page_is_working() {
    site_ip=$1

    wget -q $site_ip -O - | grep -q 'Welcome to ConPaaS'
    if [ $? -ne 0 ]
    then
	echo "ERROR: cannot find static web page."
	exit 1
    fi
}



### MAIN

echo "Starting script that will tests PHP migration capabilities."
echo "(0) Create and start a PHP service ..."

php_sid=$(start_service "php")

wait_for_running $php_sid

proxy_ip=$(cpsclient.py info $php_sid | grep 'proxy ' | awk '{print $2}')

test_static_page_is_working $proxy_ip



echo "(1) Test migration of a web node with the default static web page"
echo "(1.1) add node that will be migrated later"
cpsclient.py add_nodes $php_sid 0 1 0

wait_for_running $php_sid

web_ip=$(cpsclient.py info $php_sid | grep 'web ' | awk '{print $2}')

test_static_page_is_working $proxy_ip

echo "(1.2) migrate added web node..."
vmid=$(echo $web_ip | tr '.' ' ' | awk '{print $4}')
vmid=$(($vmid - 1))

cpsclient.py migrate_nodes $php_sid iaas:$vmid:iaas

wait_for_running $php_sid

web_ip_migr=$(cpsclient.py info $php_sid | grep 'web ' | awk '{print $2}')

if [ "$web_ip_migr" == "$web_ip" ]
then
    echo "ERROR: failed to migrate web node."
    exit 1
fi

test_static_page_is_working $proxy_ip


echo "(2) Test migration of a backend with a PHP program"
echo "(2.1) upload PHP program"
code_version=$(cpsclient.py upload_code $php_sid $php_program)
code_version=$(echo $code_version | awk '{print $3}')

cpsclient.py enable_code $php_sid $code_version
if [ $? -ne 0 ]
then
    echo "ERROR: cannot enable code $code_version on service $php_sid"
    exit 1
fi

# wait a few seconds for the site to be installed
sleep 5

test_php_page_is_working $proxy_ip

echo "(2.2) add a new backend node"

cpsclient.py add_nodes $php_sid 1 0 0

wait_for_running $php_sid

backend_ip=$(cpsclient.py info $php_sid | grep 'backend ' | awk '{print $2}')

test_php_page_is_working $proxy_ip

echo "(2.3) migrate added backend node..."
vmid=$(echo $backend_ip | tr '.' ' ' | awk '{print $4}')
vmid=$(($vmid - 1))

cpsclient.py migrate_nodes $php_sid iaas:$vmid:iaas

wait_for_running $php_sid

backend_ip_migr=$(cpsclient.py info $php_sid | grep 'backend ' | awk '{print $2}')

if [ "$backend_ip_migr" == "$backend_ip" ]
then
    echo "ERROR: failed to migrate backend node."
    exit 1
fi

test_php_page_is_working $proxy_ip



echo "(3) Test migration of proxy"
proxy_ip=$(cpsclient.py info $php_sid | grep 'proxy ' | awk '{print $2}')

vmid=$(echo $proxy_ip | tr '.' ' ' | awk '{print $4}')
vmid=$(($vmid - 1))

cpsclient.py migrate_nodes $php_sid iaas:$vmid:iaas

wait_for_running $php_sid

proxy_ip_migr=$(cpsclient.py info $php_sid | grep 'proxy ' | awk '{print $2}')

if [ "$proxy_ip_migr" == "$proxy_ip" ]
then
    echo "ERROR: failed to migrate proxy node."
    exit 1
fi

proxy_ip=$proxy_ip_migr
test_php_page_is_working $proxy_ip


echo "(4) Pack back the backend node and migrate the proxy-backend packed node"
cpsclient.py remove_nodes $php_sid 1 0 0

wait_for_running $php_sid

test_php_page_is_working $proxy_ip

proxy_ip=$(cpsclient.py info $php_sid | grep 'proxy ' | awk '{print $2}')
vmid=$(echo $proxy_ip | tr '.' ' ' | awk '{print $4}')
vmid=$(($vmid - 1))

cpsclient.py migrate_nodes $php_sid iaas:$vmid:iaas

wait_for_running $php_sid

proxy_ip_migr=$(cpsclient.py info $php_sid | grep 'proxy ' | awk '{print $2}')

if [ "$proxy_ip_migr" == "$proxy_ip" ]
then
    echo "ERROR: failed to migrate proxy-backend node."
    exit 1
fi

proxy_ip=$proxy_ip_migr
test_php_page_is_working $proxy_ip

echo "(5) Pack back the web node and migrate the proxy-web-backend packed node"
cpsclient.py remove_nodes $php_sid 0 1 0

wait_for_running $php_sid

test_php_page_is_working $proxy_ip

proxy_ip=$(cpsclient.py info $php_sid | grep 'proxy ' | awk '{print $2}')
vmid=$(echo $proxy_ip | tr '.' ' ' | awk '{print $4}')
vmid=$(($vmid - 1))

cpsclient.py migrate_nodes $php_sid iaas:$vmid:iaas

wait_for_running $php_sid

proxy_ip_migr=$(cpsclient.py info $php_sid | grep 'proxy ' | awk '{print $2}')

if [ "$proxy_ip_migr" == "$proxy_ip" ]
then
    echo "ERROR: failed to migrate proxy-web-backend node."
    exit 1
fi

proxy_ip=$proxy_ip_migr
test_php_page_is_working $proxy_ip


echo "(6) Stop service and delete it"

cpsclient.py stop $php_sid

wait_for_stopped $php_sid

cpsclient.py terminate $php_sid

cpsclient.py list | grep -q "No running services"

echo "Congratulations! PHP migration test has PASSED!"
