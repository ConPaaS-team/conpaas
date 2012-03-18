package org.koala.runnersFramework.runners.bot;

import ibis.ipl.Ibis;
import ibis.ipl.IbisIdentifier;

import java.io.IOException;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class DAS3Cluster extends Cluster {

	String FS;
        // variable for testing purposes.
        String speedFactor;
	
	public DAS3Cluster(String hostname, String alias, long timeUnit, double costUnit, int maxNodes, double speedFactor) {
		super(hostname, alias, timeUnit, costUnit, maxNodes);
		this.FS = alias.substring(alias.lastIndexOf("@")+1);
                this.speedFactor = "" + speedFactor;
	}

	@Override
	public Process startNodes(String time, int noWorkers,
			String electionName, String poolName, String serverAddress) {

		if(noWorkers == 0) return null;
		
		List<String> cmdList = new ArrayList<String>();

		cmdList.add("ssh");
		cmdList.add(hostname);
		cmdList.add("prun");
		cmdList.add("-rsh");
		cmdList.add("ssh");
		cmdList.add("-asocial");
		cmdList.add("-v");
		cmdList.add("-t");
		cmdList.add(time);
		cmdList.add("-1");
		cmdList.add("-no-panda");		
		cmdList.add("/usr/local/package/jdk1.6.0-linux-amd64/bin/java");
		cmdList.add(noWorkers+"");
		cmdList.add("-classpath");
		cmdList.add("conpaas-worker.jar:/home/amo/ibis/lib/*");
		cmdList.add("-Dibis.location.postfix="+FS);
		cmdList.add("org.koala.runnersFramework.runners.bot.Worker");
		cmdList.add(electionName);
		cmdList.add(poolName);			
		cmdList.add(serverAddress);
                cmdList.add(speedFactor);
		
		String[] cmdarray = cmdList.toArray(new String[0]);
		
		try {
                    return Runtime.getRuntime().exec(cmdarray);			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}	
		return null;
	}

	@Override
	public void terminateNode(IbisIdentifier from, Ibis myIbis)
			throws IOException {
		// TODO Auto-generated method stub
		
	}

}
