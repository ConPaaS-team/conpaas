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
 *
 * @author maricel
 */
public class EucalyptusCluster extends Cluster {

    /* Home-made image for BoTS. */
    public String EMI; // = "emi-XXXXXXX";
    public String SECURITY_GROUP = "default";
    /* Type of every instance of the cluster */
    public InstanceType INSTANCE_TYPE = InstanceType.DEFAULT;
    /* object which gives me control over the Eucalyptus service */
    public Jec2 euca;
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

    public EucalyptusCluster(String hostname, int port, String alias, long timeUnit,
            double costUnit, int maxNodes, String speedFactor,
            String EMI,
            String keyPairName, String keyPairPath,
            String accessKey, String secretKey) {
        super(hostname, alias, timeUnit, costUnit, maxNodes, speedFactor);

        this.EMI = EMI;
        this.keyPairName = keyPairName;
        this.keyPairPath = keyPairPath;

        this.accessKey = accessKey;
        this.secretKey = secretKey;

        /* initialize the ec2 service with Eucalyptus login information */
        euca = new Jec2(this.accessKey, this.secretKey, false, hostname, port);
        euca.setResourcePrefix("/services/Eucalyptus");
        euca.setSignatureVersion(1);
    }

    @Override
    public Process startWorkers(String time, int noWorkers,
            String electionName, String poolName, String serverAddress) {

        LaunchConfiguration launchConfig;
        String script;
        System.out.print("Starting " + noWorkers + " Eucalyptus instances...");

        if (noWorkers == 0) {
            return null;
        }

        /* Create a Launch Configuration */
        launchConfig = new LaunchConfiguration(EMI, noWorkers, noWorkers);

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
            rd = euca.runInstances(launchConfig);
        } catch (EC2Exception ex) {
            Logger.getLogger(EC2Cluster.class.getName()).log(Level.SEVERE, null, ex);
            throw new RuntimeException("FAILED to start Eucalyptus workers");
        }

        /* Gather information about the virtual machines and place it in 
        the hash map*/
        for (Instance instance : rd.getInstances()) {
            map.put(instance.getIpAddress() + "@" + super.alias,
                    instance.getInstanceId());
        }
        System.out.print("done!\n");

        return null;
    }

    private String createScript(String electionName,
            String poolName, String serverAddress) {
        String script;
        script = "#!/bin/bash\n";
        script += "java "
                + "-classpath /root/BoT/*:/root/BoT/ipl-2.2/lib/* "
                + "-Dibis.location=`/root/getIP`@" + alias + " "
                + "org.koala.runnersFramework.runners.bot.VMWorker "
                + electionName + " " + poolName + " "
                + serverAddress + " " + speedFactor;
        // + " &> /root/w.log";
        return script;
    }

    @Override
    public void terminateWorker(IbisIdentifier node, Ibis myIbis) throws IOException {
        myIbis.registry().signal("die", node);

        String vmId = map.get(node.location().toString());
        try {
            euca.terminateInstances(new String[]{vmId});
        } catch (EC2Exception ex) {
            // it throws a null exception, but it still shutdowns the machine
            // bug!
        }

    }
}
