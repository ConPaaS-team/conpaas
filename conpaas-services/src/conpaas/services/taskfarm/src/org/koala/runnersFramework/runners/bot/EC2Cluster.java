package org.koala.runnersFramework.runners.bot;

import com.xerox.amazonws.ec2.EC2Exception;
import com.xerox.amazonws.ec2.InstanceType;
import com.xerox.amazonws.ec2.Jec2;
import com.xerox.amazonws.ec2.LaunchConfiguration;
import com.xerox.amazonws.ec2.ReservationDescription;
import com.xerox.amazonws.ec2.ReservationDescription.Instance;

import ibis.ipl.Ibis;
import ibis.ipl.IbisIdentifier;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * @author maricel
 */
public class EC2Cluster extends Cluster {

    /* Amazon Machine Image - pick one from the list */
    public String AMI; // = "ami-XXXXXXXX";
    public String SECURITY_GROUP = "default";
    /* Type of every instance of the cluster */
    public InstanceType INSTANCE_TYPE = InstanceType.LARGE;
    /* object which gives me control over the AWS */
    public transient Jec2 jec2;
    private String accessKey; // example: "AKIAIW6K6MC4R2RYGXJQ";
    private String secretKey; // example: "HCbSpehUvja7JrTDTclM1hG/LXE5QgDIyb/FMFzv";
    private String keyPairName; // das4
    /* keyPairPath is not used because I do not ssh to the machine.
    I just start it and the script passed as user-data does its job.*/
    private String keyPairPath;
    /* Information received after calling runInstances() */
    private ReservationDescription rd;
    /* Map used for shutting down the machines from the managerial level. 
    Maps location to VM id. */
    public HashMap<String, String> map = new HashMap<String, String>();

    /*no CPUs in the VM*/
    public String speedFactor;
    
    public EC2Cluster(String hostname, int port, String alias, long timeUnit,
            double costUnit, int maxNodes, String speedFactor,
            String AMI,
            String keyPairName, String keyPairPath,
            String accessKey, String secretKey) {
        super(hostname, alias, timeUnit, costUnit, maxNodes);

        this.speedFactor = speedFactor;
        
        this.AMI = AMI;
        this.keyPairName = keyPairName;
        this.keyPairPath = keyPairPath;

        this.accessKey = accessKey;
        this.secretKey = secretKey;
    }

    private void setJec2() {
        if (jec2 == null) {
            /* initialize the ec2 service with AWS login information */
            jec2 = new Jec2(this.accessKey, this.secretKey);
        }
    }

    @Override
    public Process startNodes(String time, int noWorkers,
            String electionName, String poolName, String serverAddress) {

        setJec2();

        LaunchConfiguration launchConfig;
        String script;
        System.out.print("Starting " + noWorkers + " Eucalyptus instances...");

        if (noWorkers == 0) {
            return null;
        }

        /* Create a Launch Configuration */
        launchConfig = new LaunchConfiguration(AMI, noWorkers, noWorkers);

        /* Specify the type of the instance - m1.small */
        launchConfig.setInstanceType(INSTANCE_TYPE);

        /* Specify the keyName that will be used */
        launchConfig.setKeyName(keyPairName);

        /* Specify the Security Groups to be used */
        ArrayList<String> securityGroup = new ArrayList<String>();
        securityGroup.add(SECURITY_GROUP);
        launchConfig.setSecurityGroup(securityGroup);

        /* Specify the user data - a script */
        script = this.createScript(electionName, poolName, serverAddress);
        launchConfig.setUserData(script.getBytes());
        try {
            /* Start an instance */
            rd = jec2.runInstances(launchConfig);
        } catch (EC2Exception ex) {
            Logger.getLogger(EC2Cluster.class.getName()).log(Level.SEVERE, null, ex);
            throw new RuntimeException("FAILED to start Amazon workers");
        }

        /* Gather information about the virtual machines and place it in 
        the hash map*/
        for (Instance instance : rd.getInstances()) {
            map.put(instance.getIpAddress(), instance.getInstanceId());
        }
        System.out.print("done!\n");

        return null;
    }

    private String createScript(String electionName,
            String poolName, String serverAddress) {
        String script;
        script = "#!/bin/bash\n";
        script += "export BATS_HOME=/root/BoT\n";
        script += "export IPL_HOME=$BATS_HOME/ibis\n";
        script += "IP=`ip addr show eth0 | grep eth0 | grep inet | awk '{print $2;}' | sed -e 's!/24!!'`\n";
        script += "java "
                + "-classpath $BATS_HOME/lib/*:$IPL_HOME/lib/* "
                + "-Dibis.location=$IP@ec2 "
                + "org.koala.runnersFramework.runners.bot.VMWorker "
                + electionName + " " + poolName + " "
                + serverAddress + " " + speedFactor
                + " &> /root/worker.log";
        return script;
    }

    @Override
    public void terminateNode(IbisIdentifier node, Ibis myIbis) throws IOException {
        myIbis.registry().signal("die", node);

        String VM_ID = map.get(node.location().toString());
        try {
            jec2.terminateInstances(new String[]{VM_ID});
        } catch (EC2Exception ex) {
            throw new RuntimeException(
                    "Exception when shutting down VM from managerial level:"
                    + "ibisLocation=" + node.location() + "; VM_ID=" + VM_ID
                    + "Error msg:\n" + ex);
        }
    }
}
