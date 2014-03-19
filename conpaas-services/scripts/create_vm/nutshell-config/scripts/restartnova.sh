#!/bin/bash

echo "Restarting api..."
screen -p 5 -X stuff $'\cc'
screen -p 5 -X stuff "cd /opt/stack/nova && /usr/local/bin/nova-api$(printf \\r)"
sleep 1

echo "Restarting conductor..."
screen -p 6 -X stuff $'\cc'
screen -p 6 -X stuff "cd /opt/stack/nova && /usr/local/bin/nova-conductor$(printf \\r)"
sleep 1

echo "Restarting compute..."
screen -p 7 -X stuff $'\cc'
screen -p 7 -X stuff "cd /opt/stack/nova && sg libvirtd /usr/local/bin/nova-compute$(printf \\r)"
sleep 1

echo "Restarting certificate..."
screen -p 8 -X stuff $'\cc'
screen -p 8 -X stuff "cd /opt/stack/nova && /usr/local/bin/nova-cert$(printf \\r)"
sleep 1

echo "Restarting network..."
screen -p 9 -X stuff $'\cc'
screen -p 9 -X stuff "cd /opt/stack/nova && /usr/local/bin/nova-network$(printf \\r)"
sleep 1

echo "Restarting scheduler..."
screen -p 10 -X stuff $'\cc'
screen -p 10 -X stuff "cd /opt/stack/nova && /usr/local/bin/nova-scheduler$(printf \\r)"

echo "Nova services started!"
