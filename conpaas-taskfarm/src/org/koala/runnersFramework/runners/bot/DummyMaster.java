package org.koala.runnersFramework.runners.bot;

import java.util.Collection;
import java.util.HashMap;

import ibis.ipl.IbisIdentifier;

public class DummyMaster extends Master {
	
	private HashMap<String,Job> doneJobs;
	private HashMap<String,Job> schedJobs;	
	private HashMap<String,Host> hosts;
	private int maxWorkers = 0;
	private long timeUnit;
	
	public DummyMaster(BoTRunner aBot) throws Exception {
		super(aBot);
	
		Collection<Cluster> clusters = bot.Clusters.values();
		hosts = new HashMap<String, Host>();
		for (Cluster cluster : clusters) {			
			maxWorkers += cluster.maxNodes;
			timeUnit = cluster.timeUnit;
			for(int i=0; i<cluster.maxNodes; i++) {
				hosts.put(i+"@"+cluster.alias, new Host(i+"@"+cluster.alias,cluster.costUnit));
			}
		}	
		
		doneJobs = new HashMap<String, Job>();
		schedJobs = new HashMap<String, Job>();
	}

	@Override
	protected boolean areWeDone() {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	protected Job handleJobRequest(IbisIdentifier from) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	protected Job handleJobResult(JobResult received, IbisIdentifier from) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	protected void handleLostConnections() {
		// TODO Auto-generated method stub

	}

	@Override
	public void run() {		
		
		while(!bot.tasks.isEmpty()) {
			long mct = Long.MIN_VALUE;
			String bestHost = "";
			//HPDCJob schedJob = null;
                        Job schedJob = null;
			for(Job job : bot.tasks) {
				// HPDCJob j = (HPDCJob) job;
				long mctj = Long.MAX_VALUE;
				String bestHostJ = "";
				long et = Long.parseLong(job.args[0]);//Long.parseLong(j.argC1);
				for(Host host : hosts.values()) {				
					if(host.node.contains("slow")) {
						if(mctj > host.EAT + 2* et /3) {
							mctj = host.EAT + 2* et /3;
							bestHostJ = host.node;
						}
					} else {
						if(mctj > host.EAT + et) {
							mctj = host.EAT + et;
							bestHostJ = host.node;
						}
					}			
				}
				if(mct < mctj) {
					mct = mctj;
					bestHost = bestHostJ;
					schedJob = job;
				}
			}			
			hosts.get(bestHost).addJob(schedJob);
			schedJobs.put(schedJob.jobID, schedJob);
			bot.tasks.remove(schedJob);
			System.out.println("Job " + schedJob.jobID + " with et: " + schedJob.args[0] + " was scheduled on machine " + bestHost + "; EAT is now " + hosts.get(bestHost).EAT);
		}
		
		long meat = Long.MIN_VALUE;
		double price = 0.0;
		for(Host host : hosts.values()) {			
			if(host.EAT > meat) meat = host.EAT;				
			price += Math.ceil((double)host.EAT / 60 / timeUnit) * host.cost;
			
		}		
		System.out.println("Longest run should be: " + meat/60 + "m" + meat%60 + "s with a total cost of " + price);
	}

	@Override
	public void startInitWorkers() {
		// TODO Auto-generated method stub

	}

	@Override
	public void terminateWorker(Cluster cluster, WorkerStats ws, String reason) {
		// TODO Auto-generated method stub
		
	}

}
