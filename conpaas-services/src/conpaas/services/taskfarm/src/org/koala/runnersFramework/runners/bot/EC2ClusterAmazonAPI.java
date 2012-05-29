package org.koala.runnersFramework.runners.bot;

import ibis.ipl.Ibis;
import ibis.ipl.IbisIdentifier;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.apache.commons.codec.binary.Base64;


import com.amazonaws.AmazonServiceException;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.ec2.model.Reservation;
import com.amazonaws.services.ec2.model.RunInstancesRequest;
import com.amazonaws.services.ec2.model.RunInstancesResult;
import com.amazonaws.services.ec2.model.TerminateInstancesRequest;
import com.amazonaws.services.ec2.AmazonEC2;
import com.amazonaws.services.ec2.AmazonEC2Client;
import com.amazonaws.services.ec2.model.Instance;

public class EC2ClusterAmazonAPI extends Cluster {

	/* EC2 main control class*/
	private transient AmazonEC2 ec2;
	
	/* Amazon AMI */
	private String AMI;
	
	/* Number of cores */
	private String speedFactor;
	
	/* Key-pair name */
	private String keyPairName;
		
	/* Instance type */
	private String instanceType;
	
	
    public EC2ClusterAmazonAPI(String hostname, int port, String alias, long timeUnit,
            double costUnit, int maxNodes, String speedFactor,
            String AMI, String instanceType,
            String keyPairName, String keyPairPath,
            String accessKey, String secretKey) {
		super(hostname, alias, timeUnit, costUnit, maxNodes);
		
		this.AMI = AMI;
		this.speedFactor = speedFactor;
		this.keyPairName = keyPairName;
		this.instanceType = instanceType;
		this.ec2 = new AmazonEC2Client(new BasicAWSCredentials(accessKey, secretKey));
		
	}

    public EC2ClusterAmazonAPI(ClusterMetadata cm) {
        super(cm.hostName, cm.alias, cm.timeUnit, cm.costUnit, cm.maxNodes);

        this.AMI = cm.image;
        this.speedFactor = cm.speedFactor;
        this.keyPairName = cm.keyPairName;
        this.instanceType = cm.instanceType;
        this.ec2 = new AmazonEC2Client(
                new BasicAWSCredentials(cm.accessKey, cm.secretKey));
    }
    
    private String getContent(String dataFile) {
        try {
            BufferedReader br = new BufferedReader(new FileReader(dataFile));
            StringBuilder retVal = new StringBuilder();
            String line;
            while( (line = br.readLine()) != null) {
                retVal.append(line).append("\n");
            }
            br.close();            
            return retVal.toString();
        } catch (Exception ex) {
            return "";
        }
    }

	@Override
	public Process startNodes(String time, int noNodes, String electionName,
			String poolName, String serverAddress) throws AmazonServiceException {
		
		if(noNodes == 0)
		{
			return null;
		}
		
		System.out.println("Starting " + noNodes + " EC2 workers");
		
		
		/* set the requested VM properties */
		RunInstancesRequest runInstancesRequest = new RunInstancesRequest()
	    .withInstanceType(this.instanceType)
	    .withImageId(this.AMI)
	    .withMinCount(noNodes)
	    .withMaxCount(noNodes)
	    .withKeyName(this.keyPairName)
	    .withUserData(Base64.encodeBase64String(createUserData(electionName, poolName).getBytes()));
		
		RunInstancesResult result;
		
		try {
			/* request the VM */
			result = ec2.runInstances(runInstancesRequest);
		} catch (AmazonServiceException e)
		{
            Logger.getLogger(EC2ClusterAmazonAPI.class.getName()).log(Level.SEVERE, null, e);
            throw new RuntimeException("FAILED to start Amazon workers.");
		}
		
		System.out.println("Successfully created " + noNodes + " EC2 instances");
		
		Reservation reservation = result.getReservation();
		
        for (Instance instance : reservation.getInstances()) {
            System.out.println("EC2 instance with InstanceID " + instance.getInstanceId());
        }
		return null;
	}

	/* This method needs the VM_ID (instance-id) and IP_PUBLIC environment variables */
	private String createUserData(String electionName, String poolName) {
		String script =  getContent(System.getenv().get("EC2_WORKER_INIT_SH")).
		replaceAll("\\$LOCATION", "\\$VM_ID@ec2").
		replaceAll("\\$ELECTIONNAME", electionName).
		replaceAll("\\$POOLNAME", poolName).
		replaceAll("\\$SERVERADDRESS", System.getenv().get("IP_PUBLIC") + ":8999").
		replaceAll("\\$SPEEDFACTOR", this.speedFactor);
		return script;
	}

	@Override
	public void terminateNode(IbisIdentifier from, Ibis myIbis)
			throws IOException {
        
		
		myIbis.registry().signal("die", from);
        String instanceIDWithLocation = from.location().toString();
        String instanceID[] = instanceIDWithLocation.split("@"); 
        
		/* set the instance ID of the VM to be terminated */
		TerminateInstancesRequest terminateInstancesRequest = new TerminateInstancesRequest()
	    .withInstanceIds(instanceID[0]);
		
		/* Terminating the VM */
        try {
            ec2.terminateInstances(terminateInstancesRequest);
        } catch (AmazonServiceException e) {
            throw new RuntimeException(
                    "Exception while terminating the EC2 VM. "
                    + "ibisLocation=" + from.location() + "; InstanceID=" + instanceID
                    + " Error msg:\n" + e);
        }
	}
}
