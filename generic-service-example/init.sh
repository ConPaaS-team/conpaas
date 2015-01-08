#/bin/bash
echo " " >> /root/generic.out
date >> /root/generic.out
echo "Initializing Generic Service!" >> /root/generic.out
echo "My IP is $MY_IP" >> /root/generic.out
echo "My role is $MY_ROLE" >> /root/generic.out
echo "My master IP is $MASTER_IP" >> /root/generic.out
echo "Information about other agents is stored at /var/cache/cpsagent/agents.json" >> /root/generic.out
cat /var/cache/cpsagent/agents.json >> /root/generic.out
echo "" >> /root/generic.out
export PATH=$PATH:/var/cache/cpsagent/bin >> /root/generic.out 2>>/root/generic.err
init-2.sh >> /root/generic.out 2>>/root/generic.err
