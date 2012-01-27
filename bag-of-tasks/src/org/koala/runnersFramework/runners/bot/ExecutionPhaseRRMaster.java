package org.koala.runnersFramework.runners.bot;

import ibis.ipl.ConnectionFailedException;
import ibis.ipl.IbisFactory;
import ibis.ipl.IbisIdentifier;
import ibis.ipl.IbisProperties;
import ibis.ipl.ReadMessage;
import ibis.ipl.ReceiveTimedOutException;
import ibis.ipl.SendPort;
import ibis.ipl.SendPortIdentifier;
import ibis.ipl.WriteMessage;

import java.io.IOException;
import java.util.Collection;
import java.util.HashMap;
import java.util.Set;


public class ExecutionPhaseRRMaster extends Master {

	private Schedule schedule;

	private HashMap<String,Job> doneJobs;
	private HashMap<String,Job> pendingJobs;
	private long actualStartTime;
	
	String electionName;
		
	protected ExecutionPhaseRRMaster(BoTRunner aBot, Schedule selectedSchedule) throws Exception {
		super(aBot);
		schedule = selectedSchedule;
		electionName=aBot.electionName;
		
		Collection<Cluster> clusters = bot.Clusters.values();
			for (Cluster cluster : clusters) {			
				HashMap<String, WorkerStats> workersCluster = new HashMap<String, WorkerStats>();
				workers.put(cluster.alias, workersCluster);
			}
			
			doneJobs = new HashMap<String, Job>();
			pendingJobs = new HashMap<String, Job>();
		}
		
		public void run() {
			// TODO Auto-generated method stub
			timeout = (long) (BoTRunner.INITIAL_TIMEOUT_PERCENT * bot.deadline * 60000);
			System.err.println("Timeout is now " + timeout);
			actualStartTime = System.currentTimeMillis();
			
			boolean undone = true;
			
			while (undone) {
				try {
					ReadMessage rm = masterRP.receive(timeout);

					Object received = rm.readObject();
					IbisIdentifier from = rm.origin().ibisIdentifier();
					rm.finish();
					Job nextJob = null;

					if (received instanceof JobRequest) {
						nextJob = handleJobRequest(from);
					} else if (received instanceof JobResult) {
						nextJob = handleJobResult((JobResult) received, from);
					} else {
						System.exit(1);
					}

					nextJob.setNode(from.location().getLevel(0));
		
					/*begin for hpdc tests
					if(! (nextJob instanceof NoJob)) {
						//long sleep = Long.parseLong(nextJob.args[0]);				
						if(from.location().getParent().toString().compareTo(bot.CLUSTER2) == 0) {
							//nextJob.args[0] = new Long(2* sleep / 3).toString();
							((HPDCJob)nextJob).setArg(2);
						} else ((HPDCJob)nextJob).setArg(1);
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
					for(Job j : pendingJobs.values())
						if (j.getNode().compareTo(node)==0) {
							pendingJobs.remove(j.getJobID());						
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
			if(bot.tasks.size() != 0) return false;
			
			if (pendingJobs.size() == 0) {
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
					long totalTime = (System.currentTimeMillis()-actualStartTime)/1000;
					System.out.println("Due amount " + price);				
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
			/*for now, when a new worker shows up, if there are no more jobs just return nojob
			 * should consider later addition of job replication*/		
			
			String cluster = from.location().getParent().toString();
			String node = from.location().getLevel(0);
			
			/*DEBUG*/
			System.err.println("job request from node " + from.location().toString() + " in cluster " + cluster);
			
			workers.get(cluster).put(node, new WorkerStats(node,System.currentTimeMillis()));
			
			/*release unnecessary workers*/
			
			if (bot.tasks.size() == 0) return sayGB(from);			
			
			Job nextJob = bot.tasks.remove(random.nextInt(bot.tasks.size()));
			//Job nextJob = bot.tasks.remove(0);
					
			/*the fact that pending jobs are timed from master side (hence including the latency to the worker) should 
			 * be mentioned and should also have some impact on the convergence speed of the histogram in those cases where 
			 * the job size is somewhat equal to this latency.
			 * */
			nextJob.startTime = System.nanoTime();
			pendingJobs.put(nextJob.jobID,
					nextJob);			
			/* might be the case that even here I return sayGB() */
			return nextJob;

		}

		@Override
		protected Job handleJobResult(JobResult received, IbisIdentifier from) {
			// TODO Auto-generated method stub
			String cluster = from.location().getParent().toString();			
			
			System.err.println(from.location().toString() + " returned result of job " + received.getJobID() + " executed for " + (received.getStats().getRuntime()/1000000000)/60 + "m" + (received.getStats().getRuntime()/1000000000)%60 + "s");	
			/* assumes jobs don't need to be replicated on the same cluster, except on failure */
			Job doneJob = pendingJobs.remove(received.getJobID());	
			
			workers.get(cluster).get(from.location().getLevel(0)).addJobStats(received.getStats().getRuntime());
			/*create category if it doesn't exist yet
			 * upper duration since we pay in discrete increments of priced time unit*/
			
			doneJobs.put(doneJob.getJobID(), doneJob);
					
			if(bot.tasks.size() == 0) return sayGB(from);
			 		
			Job nextJob = bot.tasks.remove(random.nextInt(bot.tasks.size()));
			//Job nextJob = bot.tasks.remove(0);
			
			nextJob.startTime = System.nanoTime();
			pendingJobs.put(nextJob.jobID,
					nextJob);
			return nextJob;

		}

		private Job sayGB (IbisIdentifier to) {
			
			System.err.println("We say goodbye to " + to.location().toString());
			
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
				cluster = lost.ibisIdentifier().location().getParent().toString();		
				node = lost.ibisIdentifier().location().getLevel(0);
				if(! workers.get(cluster).get(node).isFinished()) {
				for(Job j : pendingJobs.values())
					if (j.getNode().compareTo(node)==0) {
						pendingJobs.remove(j.getJobID());	
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

		System.err
				.println("BoTRunner has found "
						+ bot.tasks.size()
						+ " jobs; will start scheduled number of workers on each participating cluster");

		Collection<Cluster> clusters = bot.Clusters.values();
		for (Cluster c : clusters) {
			System.err.println("on cluster " + c.alias
					+ " maximum number workers is " + c.maxNodes);
			if (schedule.machinesPerCluster.containsKey(c.alias)) {
				Process p = c.startNodes(/* deadline2ResTime() */"12:45:00",
						schedule.machinesPerCluster.get(c.alias), electionName,
						myIbis.properties().getProperty(
								IbisProperties.POOL_NAME), myIbis.properties()
								.getProperty(IbisProperties.SERVER_ADDRESS));
				// sshRunners.put(c.alias, p);
				System.err.println("; will start " + schedule.machinesPerCluster.get(c.alias));
			}
		}
	}

		@Override
		public void terminateWorker(Cluster cluster, WorkerStats ws,
				String reason) {
			// TODO Auto-generated method stub
			
		}
}
