package org.koala.runnersFramework.runners.bot;

import ibis.ipl.Ibis;
import ibis.ipl.IbisIdentifier;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public class OpenNebulaCluster extends Cluster {

    int currentNoNodes = 0;
    public String image;

    public OpenNebulaCluster(String hostname, int port, String alias, long timeUnit,
			     double costUnit, int maxNodes, String speedFactor, 
			     String image, String b, String c, String d, String e
            ) {
        super(hostname, alias, timeUnit, costUnit, maxNodes, speedFactor);
	this.image=image;
    }

    @Override
    public Process startWorkers(String time, int noWorkers,
            String electionName, String poolName, String serverAddress) {

        String templateName;

        if (noWorkers == 0 || (currentNoNodes + noWorkers >= maxNodes)) {
            return null;
        }

	//        List<String> cmdList = new ArrayList<String>();

	/*        cmdList.add("ssh");
        cmdList.add(hostname);
        cmdList.add("<<'EOF'");
	*/
	Process p = null;
        for (int i = 0; i < noWorkers; i++) {
            List<String> cmdList = new ArrayList<String>(); 
	    try {
                // create a template in the OpenNebulaCluster directory
                // return the name of the created template
                templateName = createVMTemplate(electionName, poolName, serverAddress,
                        speedFactor, i);
            } catch (IOException ex) {
                throw new RuntimeException("Couldn't create VM template.\n" + ex);
            }
            System.out.println("templateName = " + templateName);

            // run the script which will start a VM with the specified template.
            cmdList.add(BoTRunner.path + "/OpenNebulaCluster/startVM");
	    cmdList.add(templateName);
            System.out.println(BoTRunner.path + "/OpenNebulaCluster/startVM " + templateName);
            
            //cmdList.add("&>" + templateName + ".log");
            //cmdList.add(";");
	    
	    String[] cmdarray = cmdList.toArray(new String[0]);
	    try {
		p = Runtime.getRuntime().exec(cmdarray);
	    } catch (IOException ex) {
		Logger.getLogger(OpenNebulaCluster.class.getName()).log(Level.SEVERE, null, ex);
	    }
	}
        //cmdList.add("\nEOF");

        currentNoNodes += noWorkers;
	/*
        String[] cmdarray = cmdList.toArray(new String[0]);
        try {
            return Runtime.getRuntime().exec(cmdarray);
        } catch (IOException ex) {
            Logger.getLogger(OpenNebulaCluster.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
	*/
	return p;
    }

    private String createVMTemplate(String electionName, String poolName,
            String serverAddress, String speedFactor, int i) throws IOException {
        // alias is das4@cs@vu@nl@fs0
        String location = "node" + (currentNoNodes + i) + "@" + alias;
        String templateName = BoTRunner.path + "/OpenNebulaCluster/" + location + ".one";
        BufferedWriter out = new BufferedWriter(new FileWriter(
                templateName));

        String content =
                "NAME = BoTSVM\n"
                + "CPU = 1\n"
                + "MEMORY = 400\n\n"
                + "OS     = [\n"
                + "arch = x86_64\n"
                + "]\n\n"
                + "DISK   = [\n"
                + "image   = \""+image+"\",\n"
	        + "target  = \"sda\"\n"
                + "]\n\n"
                + "NIC    = [\n"
                + "NETWORK = \"Private LAN\"\n"
                + "]\n\n"
                + "GRAPHICS = [\n"
                + "TYPE    = \"vnc\",\n"
                + "LISTEN  = \"0.0.0.0\"\n"
                + "]\n\n"
                + "FEATURES = [\n"
                + "acpi=\"yes\"\n"
                + "]\n\n"
                + "RAW = [\n"
                + "type = \"kvm\",\n"
                + "data = \" <serial type='pty'> <source path='/dev/pts/3'/> <target port='1'/> </serial>\"\n"
                + "]\n\n"
                + "CONTEXT = [\n"
                + "hostname   = \"$NAME\",\n"
	    /*+ "dns        = \"$NETWORK[DNS, NAME=\\\"Small network\\\"]\",\n"*/
	        + "dns        = 130.73.121.1,\n"
            /*    + "gateway    = \"$NETWORK[GATEWAY, NAME=\\\"Small network\\\"]\",\n"*/
	        + "gateway    = 10.0.0.1,\n"
	        + "ip_public  = \"$NIC[IP, NETWORK=\\\"Private LAN\\\"]\",\n"
                + "# variables required by a BoT worker\n"
                + "LOCATION=" + location + ",\n"
                + "ELECTIONNAME=" + electionName + ",\n"
                + "POOLNAME=" + poolName + ",\n"
                + "SERVERADDRESS=" + serverAddress + ",\n"
                + "SPEEDFACTOR=" + speedFactor + ",\n"
                + "# end.\n"
                + "files = \"" + BoTRunner.path + "/OpenNebulaCluster/init.sh " 
                    + BoTRunner.path + "/OpenNebulaCluster/id_rsa.pub\",\n"
                + "target = \"sdb\",\n"
                + "root_pubkey = \"id_rsa.pub\",\n"
                + "username = \"opennebula\",\n"
                + "user_pubkey = \"id_rsa.pub\"\n"
                + "]\n";

        out.write(content);
        out.close();

        return templateName;
    }

    @Override
    public void terminateWorker(IbisIdentifier from, Ibis myIbis) throws IOException {
        System.out.println("No further actions taken to shut down workers.");
    }
}
