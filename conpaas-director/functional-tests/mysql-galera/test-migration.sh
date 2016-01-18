#!/bin/bash -xe

mysql_dump=wordpress-db.sql

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

test_db_is_working() {

    ip_addr=$1
    passwd=$2

    test_error=1
    test_passed=0

    if [ "$mysql_dump" == "wordpress-db.sql" ]
    then
        sql_cmd="USE wordpress; SELECT * FROM wp_users;"
        output="$(echo "$sql_cmd" | mysql -u mysqldb -p$passwd -h $ip_addr -sN)"
	line_nb="$(echo "$output" | wc -l)"
        if [ $line_nb -ne 1 ]
        then
	    echo "ERROR: expected exactly one user, not $line_nb users."
            return $test_error
	fi
	user_name="$(echo "$output" | awk '{print $2}')"
	if [ "$user_name" != "admin" ]
	then
	    echo "ERROR: expected user 'admin' and not user '$user_name'."
	    return $test_error
	fi
    else
        echo "Unknown database '$mysql_dump' cannot test if it is OK."
        return $test_error
    fi
    return $test_passed
}

mysql_sid=$(start_service "mysql")

wait_for_running $mysql_sid

# getting information for first agent node
mysql_info=$(cpsclient.py info $mysql_sid | grep 'node:')
ip1=$(echo "$mysql_info" | grep ip= | sed 's/.*ip=\(.*\) cloud.*/\1/')
cloud1=$(echo "$mysql_info" | grep ip= | sed 's/.*cloud=\(.*\) vmid.*/\1/')
vmid1=$(echo "$mysql_info" | grep ip= | sed 's/.*vmid=\(.*\).*/\1/')

echo "MySQL server running on $ip1" | ts

mysql_password=`echo | mkpasswd -`
cpsclient.py set_password "$mysql_sid" "$mysql_password" > /dev/null

echo "Loading MySQL dump" | ts
mysql -u mysqldb -h $ip1 --password=$mysql_password < $mysql_dump
echo "MySQL dump loaded" | ts

test_db_is_working "$ip1" "$mysql_password"
if [ $? -ne 0 ]
then
    exit 1
fi

cpsclient.py migrate_nodes $mysql_sid $cloud1:$vmid1:$cloud1

wait_for_running $mysql_sid

# TODO: chek that the old node is not there and there is a new one

mysql_info=$(cpsclient.py info $mysql_sid | grep 'node:')
ip2=$(echo "$mysql_info" | grep ip= | sed 's/.*ip=\(.*\) cloud.*/\1/')
cloud2=$(echo "$mysql_info" | grep ip= | sed 's/.*cloud=\(.*\) vmid.*/\1/')
vmid2=$(echo "$mysql_info" | grep ip= | sed 's/.*vmid=\(.*\).*/\1/')

if [ "$ip2" == "$ip1" -o "$vmid1" == "$vmid2" ]
then
    echo "ERROR: failed to migrate node."
    exit 1
fi

test_db_is_working "$ip2" "$mysql_password"
if [ $? -ne 0 ]
then
    exit 1
fi

# Second migration to test that the previous migrated node was in a clean state

cpsclient.py migrate_nodes $mysql_sid $cloud2:$vmid2:$cloud2

wait_for_running $mysql_sid

# TODO: chek that the old node is not there and there is a new one

mysql_info=$(cpsclient.py info $mysql_sid | grep 'node:')
ip3=$(echo "$mysql_info" | grep ip= | sed 's/.*ip=\(.*\) cloud.*/\1/')
cloud3=$(echo "$mysql_info" | grep ip= | sed 's/.*cloud=\(.*\) vmid.*/\1/')
vmid3=$(echo "$mysql_info" | grep ip= | sed 's/.*vmid=\(.*\).*/\1/')

if [ "$ip3" == "$ip2" -o "$vmid2" == "$vmid3" ]
then
    echo "ERROR: failed to migrate node."
    exit 1
fi

test_db_is_working "$ip3" "$mysql_password"
if [ $? -ne 0 ]
then
    exit 1
fi
 

# adding one more node for a total of two nodes

cpsclient.py add_nodes $mysql_sid 1

wait_for_running $mysql_sid

mysql_info=$(cpsclient.py info $mysql_sid | grep 'node:')
ip3=$(echo "$mysql_info" | grep ip= | sed 's/.*ip=\(.*\) cloud.*/\1/')
nb_nodes=$(echo "$ip3" | wc -l)

if [ $nb_nodes -ne 2 ]
then
    echo "ERROR: expected to have 2 nodes instead of $nb_nodes nodes."
    exit 1
fi

ip31="$(echo "$ip3" | head -n 1)"
ip32="$(echo "$ip3" | tail -n 1)"

test_db_is_working "$ip31" "$mysql_password"
if [ $? -ne 0 ]
then
    exit 1
fi

test_db_is_working "$ip32" "$mysql_password"
if [ $? -ne 0 ]
then
    exit 1
fi

# Start migrating both nodes at the same time

migr_all=$(echo "$mysql_info" | grep ip= | sed 's/.*cloud=\(.*\) vmid=\(.*\)/\1:\2:\1/')
migr_all="$(echo "$migr_all" | tr '\n' ',' | sed 's/,$//')"

cpsclient.py migrate_nodes $mysql_sid $migr_all

wait_for_running $mysql_sid

mysql_info=$(cpsclient.py info $mysql_sid | grep 'node:')
ip4=$(echo "$mysql_info" | grep ip= | sed 's/.*ip=\(.*\) cloud.*/\1/')
cloud4=$(echo "$mysql_info" | grep ip= | sed 's/.*cloud=\(.*\) vmid.*/\1/')
vmid4=$(echo "$mysql_info" | grep ip= | sed 's/.*vmid=\(.*\).*/\1/')

nb_nodes=$(echo "$ip4" | wc -l)

if [ $nb_nodes -ne 2 ]
then
    echo "ERROR: expected to have 2 nodes instead of $nb_nodes nodes."
    exit 1
fi

ip41="$(echo "$ip4" | head -n 1)"
ip42="$(echo "$ip4" | tail -n 1)"

test_db_is_working "$ip41" "$mysql_password"
if [ $? -ne 0 ]
then
    exit 1
fi

test_db_is_working "$ip42" "$mysql_password"
if [ $? -ne 0 ]
then
    exit 1
fi

if [ "$ip41" == "$ip31" -o "$ip42" == "$ip31" -o "$ip41" == "$ip32" -o "$ip42" == "$ip32" ]
then
    echo "ERROR: at least one of the 2 nodes has not migrated. Before: $ip31 and $ip32. After: $ip41 and $ip42"
    exit 1
fi

# Remove a node

cpsclient.py remove_nodes $mysql_sid 1

wait_for_running $mysql_sid

mysql_info=$(cpsclient.py info $mysql_sid | grep 'node:')
ip5=$(echo "$mysql_info" | grep ip= | sed 's/.*ip=\(.*\) cloud.*/\1/')
nb_nodes=$(echo "$ip5" | wc -l)

if [ $nb_nodes -ne 1 ]
then
    echo "ERROR: expected to have 1 node instead of $nb_nodes nodes."
    exit 1
fi

test_db_is_working "$ip5" "$mysql_password"
if [ $? -ne 0 ]
then
    exit 1
fi


# Stop service

cpsclient.py stop $mysql_sid

wait_for_stopped $mysql_sid


# Delete service

cpsclient.py terminate $mysql_sid

cpsclient.py list | grep -v "mysql   $mysql_sid"
if [ $? -ne 0 ]
then
    echo "ERROR: could not delete MySQL service $mysql_sid."
    exit 1
fi
