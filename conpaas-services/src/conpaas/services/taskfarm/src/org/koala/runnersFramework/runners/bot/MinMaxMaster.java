package org.koala.runnersFramework.runners.bot;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;

import ibis.ipl.ConnectionFailedException;
import ibis.ipl.IbisIdentifier;
import ibis.ipl.IbisProperties;
import ibis.ipl.ReadMessage;
import ibis.ipl.ReceiveTimedOutException;
import ibis.ipl.SendPort;
import ibis.ipl.SendPortIdentifier;
import ibis.ipl.WriteMessage;

public class MinMaxMaster extends Master {


	private HashMap<String,Job> doneJobs;
	private HashMap<String,Job> schedJobs;	
	private HashMap<String,Host> hosts;
	private int maxWorkers = 0;
	private long actualStartTime;
	
	public MinMaxMaster(BoTRunner aBot) throws Exception {
		super(aBot);
		
		Collection<Cluster> clusters = bot.Clusters.values();
		for (Cluster cluster : clusters) {			
			HashMap<String, WorkerStats> workersCluster = new HashMap<String, WorkerStats>();
			workers.put(cluster.alias, workersCluster);
			maxWorkers += cluster.maxNodes;
		}
		
		hosts = new HashMap<String, Host>();
		doneJobs = new HashMap<String, Job>();
		schedJobs = new HashMap<String, Job>();
	}
	
	public void run() {
		// TODO Auto-generated method stub
		timeout = (long) (BoTRunner.INITIAL_TIMEOUT_PERCENT * bot.deadline * 60000);
		System.err.println("Timeout is now " + timeout);

		/*first receive requests from all workers*/
		while(hosts.size()!= maxWorkers) {
			ReadMessage rm;
			try {
			
			rm = masterRP.receive(timeout);
		
			Object received = rm.readObject();
			IbisIdentifier from = rm.origin().ibisIdentifier();
			rm.finish();
						
			hosts.put(from.location().toString(), new Host(from));
			
			String cluster = from.location().getParent().toString();			
			
			/*DEBUG*/
			System.err.println("job request from node " + from.location().toString() + " in cluster " + cluster + "; number of hosts is now " + hosts.size());
			
			
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (ClassNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}

		/*then precompute schedule*/
		while(bot.tasks.size() != 0) {
			long mct = Long.MIN_VALUE;
			String bestHost = "";
			Job schedJob = null;
			for(Job j : bot.tasks) {
				long mctj = Long.MAX_VALUE;
				String bestHostJ = "";
				long et = Long.parseLong(j.args[0]);
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
					schedJob = j;
				}
			}			
			hosts.get(bestHost).addJob(schedJob);
			schedJobs.put(schedJob.jobID, schedJob);
			bot.tasks.remove(schedJob);
			System.out.println("Job " + schedJob.jobID + " with et: " + schedJob.args[0] + " was scheduled on machine " + bestHost + "; EAT is now " + hosts.get(bestHost).EAT);
		}
		
		long meat = Long.MIN_VALUE;
		for(Host host : hosts.values()) {			
			if(host.EAT > meat) meat = host.EAT;
		}		
		System.out.println("Longest run should be: " + meat/60 + "m" + meat%60 + "s");
		
		actualStartTime = System.currentTimeMillis();
		
		/*send first job to each worker*/
		for(Host host : hosts.values()) {
			/*begin for hpdc tests*/

			Job nextJob = handleJobRequest(host.from);
			
			nextJob.setNode(host.from.location().getLevel(0));
			
			if((! (nextJob instanceof NoJob)) && (nextJob.submitted != true)) {
				long sleep = Long.parseLong(nextJob.args[0]);				
				if(host.from.location().getParent().toString().compareTo("slow") == 0) {
					nextJob.args[0] = new Long(2* sleep / 3).toString();
				}
				nextJob.submitted = true;
				}
				/*end for hpdc tests*/
				
				SendPort workReplyPort;
				try {
					workReplyPort = myIbis
							.createSendPort(masterReplyPortType);
				
				workReplyPort.connect(host.from, "worker");

				WriteMessage wm = workReplyPort.newMessage();
				wm.writeObject(nextJob);
				wm.finish();
				workReplyPort.close();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
		}
			
		boolean undone = true;	
			
		while (undone) {
			try {
				
				ReadMessage rm = masterRP.receive(timeout);

				Object received = rm.readObject();
				IbisIdentifier from = rm.origin().ibisIdentifier();
				rm.finish();

				Job nextJob = null;

				if (received instanceof JobResult) {
					nextJob = handleJobResult((JobResult) received, from);
				} else {
					throw new RuntimeException("received "
                                                        + "an object which is not JobResult:" + received);
				}

				nextJob.setNode(from.location().getLevel(0));
	
				/*begin for hpdc tests*/
				if(! (nextJob instanceof NoJob)) {
					long sleep = Long.parseLong(nextJob.args[0]);				
					if(from.location().getParent().toString().compareTo("slow") == 0) {
						nextJob.args[0] = new Long(2* sleep / 3).toString();
					}				
				}
				/*end for hpdc tests*/
				
				SendPort workReplyPort = myIbis
						.createSendPort(masterReplyPortType);
				workReplyPort.connect(from, "worker");

				WriteMessage wm = workReplyPort.newMessage();
				wm.writeObject(nextJob);
				wm.finish();
				workReplyPort.close();
				
				undone = ! areWeDone();					
				
			} catch (ReceiveTimedOutException rtoe) {				
				System.err.println("I timed out!");
				undone = ! areWeDone();				
				
			} catch (ConnectionFailedException cfe) {
				String cluster = cfe.ibisIdentifier().location().getParent().toString();		
				String node = cfe.ibisIdentifier().location().getLevel(0);
				for(Job j : schedJobs.values())
					if (j.getNode().compareTo(node)==0) {
						schedJobs.remove(j.getJobID());						
						/*begin hpdc tests*/
						if (j.getNode().contains("slow")) {
							j.args[0] = new Long(3* Long.parseLong(j.args[0]) / 2).toString();
						}
						/*end hpdc tests*/
						bot.tasks.add(j);
						workers.get(cluster).get(j.getNode()).workerFinished(System.currentTimeMillis());
						
						System.err.println("Node " + cfe.ibisIdentifier().location().toString() + 
								" failed before receiving job " + j.jobID);
						break;
					}
			} catch (IOException ioe) {									
				ioe.printStackTrace();	
				undone = ! areWeDone();
			} catch (ClassNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
	

	@Override
	protected boolean areWeDone() {
/*check whether we finished*/
		
		handleLostConnections();
		
		/*speed up*/
		//if(bot.tasks.size() != 0) return false;
		
		if (schedJobs.size() == 0) {
			/*disable connections*/
			masterRP.disableConnections();
			/*first check whether more workers are connected*/
			for (SendPortIdentifier spi : masterRP.connectedTo()) {
				String node = spi.ibisIdentifier().location().getLevel(0);
				String cl = spi.ibisIdentifier().location().getParent().toString();
				/*node connected but didn't manage to send a job request, either because it died or because it 
				 * was slower than the other nodes*/
				if ((workers.get(cl).get(node) == null) ||
						/*node did not report job result back yet*/
					(workers.get(cl).get(node).isFinished() == false)) {						
						timeout = 1;
						return false;
				}
			}
			try {
				/*for(Process p : sshRunners.values())
					if(p !=null) p.destroy();*/
				double price = 0;
				Collection<Cluster> clusters = bot.Clusters.values();
				for (Cluster cluster : clusters) {
					Collection<WorkerStats> wss = workers.get(cluster.alias).values();					
					System.out.println("Cluster " + cluster.hostname + " stats =>");
					for (WorkerStats ws : wss) {
						ws.printStats();
						price += Math.ceil((double)ws.getUptime() / 60000 / cluster.timeUnit) * cluster.costUnit; 
					}						
				}
				System.out.println("Due amount " + price);
				long totalTime = (System.currentTimeMillis()-actualStartTime)/1000;
				System.out.println("Application took " + totalTime + " (sec), which is about " + totalTime/60 + "m" + totalTime%60 +"s");
				System.out.println("Hurray! I'm done with " + doneJobs.size() + " jobs!!!");
				masterRP.close();
				System.out.println("Hurray! I shut down masterRP!!!");
				myIbis.end();
				System.out.println("Hurray! I shut down ibis!!!");					
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}				
			System.out.println("Good bye!");
			return true;								
		} return false;
	}

	@Override
	protected Job handleJobRequest(IbisIdentifier from) {
		String cluster = from.location().getParent().toString();
		String node = from.location().getLevel(0);
		
		/*DEBUG*/
		System.err.println("served first job request from node " + from.location().toString() + " in cluster " + cluster);
		
		workers.get(cluster).put(node, new WorkerStats(node,System.currentTimeMillis(), from));
		
		/*release unnecessary workers*/
		
		if (hosts.get(from.location().toString()).schedJobs.size() == 0) return sayGB(from);			
		
		Job nextJob = hosts.get(from.location().toString()).schedJobs.remove(0);
				
		/*the fact that pending jobs are timed from master side (hence including the latency to the worker) should 
		 * be mentioned and should also have some impact on the convergence speed of the histogram in those cases where 
		 * the job size is somewhat equal to this latency.
		 * */
		nextJob.startTime = System.nanoTime();
		//sJobs.put(nextJob.jobID, nextJob);			
		/* might be the case that even here I return sayGB() */
		return nextJob;
	}

	@Override
	protected Job handleJobResult(JobResult received, IbisIdentifier from) {
		// TODO Auto-generated method stub
		String cluster = from.location().getParent().toString();			
		
		System.err.println(from.location().toString() + " " + received.getStats().getRuntime());
		
		/* assumes jobs don't need to be replicated on the same cluster, except on failure */
		Job doneJob = schedJobs.remove(received.getJobID());	
		
		workers.get(cluster).get(from.location().getLevel(0)).addJobStats(received.getStats().getRuntime());
		/*create category if it doesn't exist yet
		 * upper duration since we pay in discrete increments of priced time unit*/
		
		doneJobs.put(doneJob.getJobID(), doneJob);
				
		if(hosts.get(from.location().toString()).schedJobs.size() == 0) return sayGB(from);
		 		
		Job nextJob = hosts.get(from.location().toString()).schedJobs.remove(0);
		nextJob.startTime = System.nanoTime();
		
		return nextJob;

	}

	private Job sayGB (IbisIdentifier to) {
		
		System.err.println("We say goodbye to " + to.location().toString() + " from " + this.getClass().getName());
		
		String cluster = to.location().getParent().toString();
		String node = to.location().getLevel(0);
		workers.get(cluster).get(node).workerFinished(System.currentTimeMillis());
		return new NoJob();
	}
	
	@Override
	protected void handleLostConnections() {
		String cluster;
		String node;
		for(SendPortIdentifier lost : masterRP.lostConnections()) {
			System.out.println("lost connection with " + lost.ibisIdentifier().location().toString());
			cluster = lost.ibisIdentifier().location().getParent().toString();		
			node = lost.ibisIdentifier().location().getLevel(0);
			
			if(! workers.get(cluster).get(node).isFinished()) {
			for(Job j : schedJobs.values())
				if (j.getNode().compareTo(node)==0) {
					schedJobs.remove(j.getJobID());	
					/*begin hpdc tests*/
					if (j.getNode().contains("slow")) {
						j.args[0] = new Long(3* Long.parseLong(j.args[0]) / 2).toString();
					}
					/*end hpdc tests*/
					bot.tasks.add(j);
					workers.get(cluster).get(j.getNode()).workerFinished(System.currentTimeMillis());
					
					System.err.println("Node " + node + " in cluster " + cluster + 
							" failed during execution of job " + j.jobID);
					break;
				}
			}
		}
		
	}

	@Override
	public void startInitWorkers() {
		
		System.err.println("BoTRunner has found " + bot.tasks.size() + " jobs; will start maximum number of workers on each participating cluster"); 
		
		Collection<Cluster> clusters = bot.Clusters.values();
		for (Cluster c : clusters) {
			System.err.println("on cluster " + c.alias + " maximmum number workers is " + c.maxNodes);
			Process p = c.startNodes(/*deadline2ResTime()*/"4:45:00", c.maxNodes, bot.electionName,
                                                    bot.poolName, bot.serverAddress);
			//sshRunners.put(c.alias, p);
		}
		
	}

	@Override
	public void terminateWorker(Cluster cluster, WorkerStats ws, String reason) {
		// TODO Auto-generated method stub
		
	}
	
}
