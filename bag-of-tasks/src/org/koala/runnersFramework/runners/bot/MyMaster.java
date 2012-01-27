package org.koala.runnersFramework.runners.bot;

import org.koala.runnersFramework.runners.bot.BoTRunner;
import ibis.ipl.ConnectionFailedException;
import ibis.ipl.Ibis;
import ibis.ipl.IbisCapabilities;
import ibis.ipl.IbisFactory;
import ibis.ipl.IbisIdentifier;
import ibis.ipl.IbisProperties;
import ibis.ipl.PortType;
import ibis.ipl.ReadMessage;
import ibis.ipl.ReceivePort;
import ibis.ipl.ReceiveTimedOutException;
import ibis.ipl.SendPort;
import ibis.ipl.SendPortIdentifier;
import ibis.ipl.WriteMessage;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.Random;
import java.util.Set;
import org.koala.runnersFramework.runners.bot.Item;
import org.koala.runnersFramework.runners.bot.Job;
import org.koala.runnersFramework.runners.bot.JobRequest;
import org.koala.runnersFramework.runners.bot.JobResult;
import org.koala.runnersFramework.runners.bot.Knapsack;
import org.koala.runnersFramework.runners.bot.NoJob;
import org.koala.runnersFramework.runners.bot.WorkerStats;

public class MyMaster extends Master {
	
	
	protected HashMap<String, HashMap<Integer, HashMap<String, Job>>> categories;
	double va_old = 0;
	double ca_old = 0;
	double va = 0;
	double ca = 0;
	long timeOfLastSchedule;
	private long actualStartTime;
	
	MyMaster(BoTRunner aBot) throws Exception {
		super(aBot);
		
		double zeta_sq = bot.zeta * bot.zeta;
		bot.noSampleJobs = (int) Math.ceil(bot.tasks.size() * zeta_sq
				/ (zeta_sq + 2 * (bot.tasks.size() - 1) * bot.delta * bot.delta));
		
		System.out.println("Sample number is " + bot.noSampleJobs + " totalNumberTasks: " + totalNumberTasks);
		
		//bot.noInitialWorkers = bot.noSampleJobs ;
		//bot.noInitialWorkers = 1;
		bot.noInitialWorkers = (int) Math.min((0.1 * totalNumberTasks), bot.noSampleJobs);
		Collection<Cluster> clusters = bot.Clusters.values();		
		/*
		int minNumberNodes = Integer.MAX_VALUE;
		for (Cluster cluster : clusters) {
			minNumberNodes = Math.min(minNumberNodes, cluster.maxNodes);
		}
		bot.noInitialWorkers = (int) Math.min(minNumberNodes, bot.noSampleJobs);
		*/
		categories = new HashMap<String, HashMap<Integer, HashMap<String, Job>>>();
		
/*		if(bot.noSampleJobs*bot.Clusters.size() > 0.5 * totalNumberTasks)
		{
			System.out.println("Size of the BoT too small for the number of clusters");
			System.exit(0);
		}
	*/			
		for (Cluster cluster : clusters) {
			HashMap<Integer, HashMap<String, Job>> clusterCategories = new HashMap<Integer, HashMap<String, Job>>();
			clusterCategories.put(Integer.MAX_VALUE,
					new HashMap<String, Job>());
			categories.put(cluster.alias, clusterCategories);
			
			HashMap<String, WorkerStats> workersCluster = new HashMap<String, WorkerStats>();
			workers.put(cluster.alias, workersCluster);
			
			cluster.setCrtNodes(0);
			cluster.setPendingNodes(bot.noInitialWorkers);
			cluster.setNecNodes(bot.noInitialWorkers);
		}
	}

	protected void handleLostConnections() {
		String cluster;
		String node;
		for(SendPortIdentifier lost : masterRP.lostConnections()) {
			cluster = lost.ibisIdentifier().location().getParent().toString();		
			node = lost.ibisIdentifier().location().getLevel(0);
			if(! workers.get(cluster).get(node).isFinished()) {
			for(Job j : categories.get(cluster).get(Integer.MAX_VALUE).values())
				if (j.getNode().compareTo(node)==0) {
					categories.get(cluster).get(Integer.MAX_VALUE).remove(j.getJobID());	
					/*begin hpdc tests*/
					/*if (j.getNode().contains(bot.CLUSTER2)) {
						j.args[0] = new Long(3* Long.parseLong(j.args[0]) / 2).toString();
					}*/
					/*end hpdc tests*/
					bot.tasks.add(j);
					workers.get(cluster).get(j.getNode()).workerFinished(System.currentTimeMillis());
					bot.Clusters.get(cluster).setCrtNodes(bot.Clusters.get(cluster).getCrtNodes()-1);
					System.err.println("Node " + node + " in cluster " + cluster + 
							" failed during execution of job " + j.jobID);
					break;
				}
			}
		}
	}
	
	protected boolean areWeDone() {
		/*check whether we finished*/
		
		handleLostConnections();
		
		/*speed up*/
		if(bot.tasks.size() != 0) return false;
		
		int undoneJobs = 0;
		int doneJobs = 0;
		
		Collection<Cluster> clusters = bot.Clusters.values();
		for (Cluster cluster : clusters) {
			int undoneJobsCluster = categories.get(cluster.alias).get(Integer.MAX_VALUE).size();
			undoneJobs += undoneJobsCluster;
			HashMap<Integer, HashMap<String, Job>> categs = categories.get(cluster.alias);
			Collection<HashMap<String, Job>> jobs = categs.values();
			for(HashMap<String, Job> jobCategCls : jobs) {
				doneJobs += jobCategCls.size();
			}					
			doneJobs -= undoneJobsCluster;
		}
		if (undoneJobs == 0) {
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
				for (Cluster cluster : clusters) {
					Collection<WorkerStats> wss = workers.get(cluster.alias).values();					
					System.out.println("Cluster " + cluster.hostname + " stats =>");
					for (WorkerStats ws : wss) {
						ws.printStats();
						price += Math.ceil((double)ws.getUptime() / 60000 / cluster.timeUnit) * cluster.costUnit;
					}
					
					Set<Integer> durations = categories.get(cluster.alias).keySet();					
					for(Integer duration : durations) {			
						System.out.println("Category " + duration + " has " + categories.get(cluster.alias).get(duration).size());
					}	
				}
				System.out.println("Due amount " + price);
				long totalTime = (System.currentTimeMillis()-actualStartTime)/1000;
				System.out.println("Application took " + totalTime + " (sec), which is about " + totalTime/60 + "m" + totalTime%60 +"s");
				System.out.println("Hurray! I'm done with " + doneJobs + " jobs!!!");
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
	
	public void run() {
		// TODO Auto-generated method stub
		timeOfLastSchedule = System.currentTimeMillis();
		
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
				decide();
				System.err.println("I timed out!");
				undone = ! areWeDone();				
				
			} catch (ConnectionFailedException cfe) {
				/* !!! don't forget to decrease the number of crt nodes*/
				String cluster = cfe.ibisIdentifier().location().getParent().toString();		
				String node = cfe.ibisIdentifier().location().getLevel(0);
				for(Job j : categories.get(cluster).get(Integer.MAX_VALUE).values())
					if (j.getNode().compareTo(node)==0) {
						categories.get(cluster).get(Integer.MAX_VALUE).remove(j.getJobID());						
						/*begin hpdc tests*/
						/*if (j.getNode().contains(bot.CLUSTER2)) {
							j.args[0] = new Long(3* Long.parseLong(j.args[0]) / 2).toString();
						}*/
						/*end hpdc tests*/
						bot.tasks.add(j);
						workers.get(cluster).get(j.getNode()).workerFinished(System.currentTimeMillis());
						bot.Clusters.get(cluster).setCrtNodes(bot.Clusters.get(cluster).getCrtNodes()-1);
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
	
	
	private ArrayList<Item> updateClusterStats(boolean debug) {
		/*compute T_i*/
		Collection<Cluster> clusters = bot.Clusters.values();		
		ArrayList<Item> items = new ArrayList<Item>();		
		items.add(new Item(0,0,""));
		bot.minCostATU = Integer.MAX_VALUE;
		bot.maxCostATU = 0;
		bot.firstStats = false;
		for(Cluster cluster : clusters) {
			double t_i = 0;
			int N = 0;			
			/*DEBUG*/
			System.err.println("decide(): cluster " + cluster.alias);
			
			if(categories.get(cluster.alias) == null) continue;			
			Set<Integer> durations = categories.get(cluster.alias).keySet();			
			for(Integer duration : durations) {
				if(duration.compareTo(Integer.MAX_VALUE) != 0) {					
			
					/*DEBUG*/
					if(debug) System.err.println("decide(): categ " + duration + " has " + categories.get(cluster.alias).get(duration).size());
					
					t_i += duration.longValue() * cluster.timeUnit * categories.get(cluster.alias).get(duration).size();					
				} else {
					
					/*DEBUG*/
					if(debug) System.err.println("decide(): pending " + categories.get(cluster.alias).get(duration).size());
					Integer intermED;
					double intermET = 0.0;
					
					for(Job j : categories.get(cluster.alias).get(Integer.MAX_VALUE).values()) {
						/*deprecated - assume the duration of each unfinished job to be crtTime-startTime 
							 * and round up to next cost group*/
						intermET = (double) ((System.nanoTime() - j.startTime) / 60000000000L);						
						if((cluster.Ti>0) && (intermET > cluster.Ti)) {
							intermET = guessAvg(intermET,cluster.alias,cluster.timeUnit);
						}
						t_i += intermET;	
						if(debug) System.err.println("decide(): in pending, job in categ " + Math.ceil(intermET / bot.timeUnit));
					}
				}				
				N += categories.get(cluster.alias).get(duration).size();
			}	
			
			/*DEBUG*/
			System.err.println("decide(): in total " + N);
			
			/*if number of jobs seen so far is multiple of sample size i update the statistical props of 
			 * the cluster*/
			/*if the number of jobs seen is greater than the sample*/
			
			if(N > bot.noSampleJobs) {
				cluster.firstStats = true;
				
				/*save the previous values such that the estimate obtained for use in va and consumedBudget is the 
				 * same as the one above; a better impl would save the value computed above in the job and use it in the 
				 * through the worker => worker should keep reference to current job*/
				cluster.prevTi = cluster.Ti;
				
				cluster.Ti = t_i / N;
				
			
				System.out.println("cluster " + cluster.alias + " : \t Ti " + cluster.Ti);
			if(cluster.Ti != 0 ) {
				bot.minCostATU = (int) Math.min(bot.minCostATU, cluster.costUnit);
				bot.maxCostATU += cluster.maxNodes*cluster.costUnit;
				for(int i=0;i<cluster.maxNodes;i++) 
					/* worked with original knapsack limit budget/bot.totalNumberTasks
					items.add(new Item((double)cluster.timeUnit/(bot.totalNumberTasks*cluster.Ti),
							(double)cluster.costUnit/bot.totalNumberTasks,
							cluster.alias));
							*/
				items.add(new Item(1/cluster.Ti,
							(int) cluster.costUnit,
							cluster.alias));
				/*DEBUG*/
				if(debug) System.err.println("Added machines from cluster " + cluster.alias + "; Items has now " + items.size());
			}
			}
			bot.firstStats = bot.firstStats && cluster.firstStats;
		}
		return items;
	}
	
	
	private double guessAvg(double intermET, String alias, long timeUnit) {
		return guessAvgOverTail(intermET, alias, timeUnit);
	}
	
	/*returns result in minutes*/
	private double guessAvgOverTail(double intermET, String alias, long timeUnit) {
		Integer intermED = Integer.valueOf((int) Math.ceil(intermET / timeUnit));
		double guessedET = 0;		
		int N = 0;
		Set<Integer> durations = categories.get(alias).keySet();
		for(Integer duration : durations) {
			if(duration.compareTo(intermED) > 0) {
				if(duration.compareTo(Integer.MAX_VALUE) != 0) {			
					guessedET += duration.longValue() * timeUnit * categories.get(alias).get(duration).size();
					N += categories.get(alias).get(duration).size();
				} else {
					for(Job j : categories.get(alias).get(Integer.MAX_VALUE).values()) {
						double jcrtET = (double) ((System.nanoTime() - j.startTime) / 60000000000L);
						if( jcrtET > intermET) {
							guessedET += jcrtET;
							N ++;
						}
					}
				}
			}
		} 
		/*didn't find any previous job bigger than this*/
		if(N == 0) { return intermET; }
		return (double)(guessedET/N);		
	}

	private void decideWithMonitoringInterval() {
		// TODO Auto-generated method stub
		/*compute averages*/		
		Collection<Cluster> clusters = bot.Clusters.values();		
		va = 0;
		ca = 0;
		double consumedBudget = 0;
		int underExec = 0;
		int virtualJobsDone = 0;
		boolean dueTimeout = System.currentTimeMillis() - timeOfLastSchedule >= timeout;
		ArrayList<Item> items = updateClusterStats(dueTimeout);
		/*is it time to verify the configuration?*/
		if(dueTimeout || bot.firstStats) {
			if(dueTimeout) {System.out.println("Due timeout");}	
			for(Cluster cluster : clusters) {			
				/*compute the actual speed of this cluster using the worker stats*/
				for(WorkerStats ws : workers.get(cluster.alias).values()) {
					/*TODO change getRuntime to getUptime in consumedBudget after ensuring it's safe*/
				/*	if(ws.isFinished()) {
						va += (double) ws.getNoJobs()/
						((double)(ws.getRuntime())/60000000000L);
					} else {
						va += (double) (ws.getNoJobs()+1)/
						((double)(ws.getRuntime()+ (System.currentTimeMillis() * 1000000 - ws.getLatestJobStartTime() ) )/60000000000L);
					} */
					if(!ws.isFinished()) {				  
					/*	va += (double) (ws.getNoJobs()+1)*60000000000L/
						((double)(ws.getRuntime()+ (System.nanoTime() - ws.getLatestJobStartTime() ) ));
						*/ 
						/*worker is idle*/
						if(ws.getLatestJobStartTime() == 0) {
							va += (double) (ws.getNoJobs()*60000000000L)/((double)ws.getRuntime());
							consumedBudget +=
								Math.ceil((double)ws.getUptime()/ 60000L / cluster.timeUnit) * cluster.costUnit;
							long timeLeftATU = cluster.timeUnit*60000 - ws.getUptime()%(cluster.timeUnit*60000);
							virtualJobsDone += ((double)timeLeftATU/60000)*(double) (ws.getNoJobs()*60000000000L)/((double)ws.getRuntime());
						} else {
							//underExec ++;
							double intermET = (double) ((System.nanoTime() - ws.getLatestJobStartTime()) / 60000000000L);						
							if((cluster.prevTi>0) && (intermET > cluster.prevTi)) {
								intermET = guessAvg(intermET,cluster.alias,cluster.timeUnit);
							}
							va += (double) (ws.getNoJobs()+1)/(intermET + (double)ws.getRuntime()/60000000000L);
							consumedBudget += 
								Math.ceil((intermET + (double)ws.getUptime() / 60000) / cluster.timeUnit) * cluster.costUnit;
							long timeLeftATU = cluster.timeUnit*60000 - ws.getUptime()%(cluster.timeUnit*60000);
							virtualJobsDone += ((double)timeLeftATU/60000)*(double) (ws.getNoJobs()+1)/(intermET + (double)ws.getRuntime()/60000000000L);
						}
						ca += cluster.costUnit;						
					} else {
						consumedBudget += Math.ceil((double)ws.getUptime() / 60000 / cluster.timeUnit) * cluster.costUnit;
					}
				}
				//ca += (double) workers.get(cluster.alias).values().size() * cluster.costUnit;
			}
			
			double etLeft = (totalNumberTasks - jobsDone - virtualJobsDone/*underExec*/) / va;
			double ebLeft = Math.ceil(etLeft/bot.timeUnit) * ca;
			/*DEBUG*/
			System.out.println("ETT: " + etLeft + " ; ETB: " + ebLeft + " ; consumed budget: " + consumedBudget);
			
			if(/*(ett > bot.deadline) ||*/ (ebLeft > (bot.budget-consumedBudget))|| bot.firstStats) {					
				if(items.size() > 1) { 
					Knapsack moo = new Knapsack(items.toArray(new Item[0]),
							(long)bot.budget-(long)consumedBudget, totalNumberTasks-jobsDone-virtualJobsDone/*underExec*/, bot.minCostATU,
							bot.maxCostATU,(int)bot.timeUnit);
					System.out.println("budget available: " + ((long)bot.budget-(long)consumedBudget) + 
							" ; number of jobs to go: " + (totalNumberTasks-jobsDone-virtualJobsDone/*underExec*/) + 
							" ; minCostATU: " + bot.minCostATU + " ; maxCostATU: " + bot.maxCostATU);
					/*ItemType[] itemTypes = prepContKnap();
				ContKnap moo = new ContKnap(itemTypes, bot.budget, bot.timeUnit);*/
					HashMap<String, Integer> machinesPerCluster = moo.findSol();			

					for(Cluster cluster : clusters) {
						Integer Mi = machinesPerCluster.get(cluster.alias);
						int moreWorkers = 0; 
						if(Mi == null) {
							if(cluster.Ti!=0) {
								Mi = new Integer(0);
							} else {
								continue;
							}
						}					
						if(Mi.intValue() > cluster.necNodes) {
							if(Mi.intValue() > cluster.crtNodes) {
								moreWorkers = Math.min(cluster.maxNodes, Mi.intValue()) - cluster.crtNodes;
								cluster.startNodes("4:45:00", moreWorkers, bot.electionName, myIbis.properties().getProperty(
										IbisProperties.POOL_NAME), myIbis.properties().getProperty(
												IbisProperties.SERVER_ADDRESS));
								/*DEBUG*/
								System.out.println("Cluster " + cluster.alias + ": started " + moreWorkers + " more workers.");
							}
						}
						cluster.necNodes = Mi.intValue();
						/*DEBUG*/
						System.out.println("Total number of workers now " + cluster.necNodes);
					}
				} 
				else System.out.println("No cluster stats available yet");
			} 
			/*DEBUG*/
			else System.out.println("Nothing changed");
			if(bot.firstStats) bot.firstStats = false;
			timeOfLastSchedule = System.currentTimeMillis();
		}		
	}
	
	private void decide() {
		//decideWithPendingJobsRedistributed();
		//decideWithPendingJobsAssumedDeadline();
		decideWithMonitoringInterval();
	}

	protected Job handleJobResult(JobResult received, IbisIdentifier from) {
		// TODO Auto-generated method stub
		String cluster = from.location().getParent().toString();			
		
		System.err.println(from.location().toString() + " returned result of job " + received.getJobID() + " executed for (sec)" + received.getStats().getRuntime()/1000000000);
		
		//hpdc tests
		jobsDone ++;
		
		/* assumes jobs don't need to be replicated on the same cluster, except on failure */
		Job doneJob = categories.get(cluster).get(Integer.MAX_VALUE)
				.remove(received.getJobID());	
		
		workers.get(cluster).get(from.location().getLevel(0)).addJobStats(received.getStats().getRuntime());
		/*create category if it doesn't exist yet
		 * upper duration since we pay in discrete increments of priced time unit*/
		Integer duration = Integer.valueOf((int) Math.ceil((double) received.getStats().getRuntime() / (bot.timeUnit*60000000000L)));
		if (categories.get(cluster).get(duration) == null) {
			categories.get(cluster).put(duration, new HashMap<String, Job>());
		}
		categories.get(cluster).get(duration).put(doneJob.getJobID(), doneJob);
		
		System.err.println(from.location().toString() + " in cluster " + cluster + " did job in categ " + duration);
		
		decide();
		
		/*release unnecessary workers*/
		if (bot.Clusters.get(cluster).getCrtNodes() > bot.Clusters.get(cluster).getNecNodes()) {			
			return sayGB(from);
		}
		
		if(bot.tasks.size() == 0) return sayGB(from);
		 		
		return findNextJob(cluster,from);
	}

	protected Job handleJobRequest(IbisIdentifier from) {
		
		/*for now, when a new worker shows up, if there are no more jobs just return nojob
		 * should consider later addition of job replication*/		
		
		String cluster = from.location().getParent().toString();
		String node = from.location().getLevel(0);
		
		/*DEBUG*/
		System.err.println("job request from node " + from.location().toString() + " in cluster " + cluster);
		
		WorkerStats reacquiredMachine = workers.get(cluster).get(node);
		if(reacquiredMachine == null) {
			workers.get(cluster).put(node, new WorkerStats(node,System.currentTimeMillis()));
		} else {
			reacquiredMachine.reacquire(bot.Clusters.get(cluster).timeUnit, System.currentTimeMillis());
		}		
		
		bot.Clusters.get(cluster).setCrtNodes(bot.Clusters.get(cluster).getCrtNodes()+1);

		bot.Clusters.get(cluster).setPendingNodes(bot.Clusters.get(cluster).getPendingNodes()-1);
		
		/*release unnecessary workers*/
		if (bot.Clusters.get(cluster).getCrtNodes() > bot.Clusters.get(cluster).getNecNodes()) {			
			return sayGB(from);
		}
		
		if (bot.tasks.size() == 0) return sayGB(from);			
		
		return findNextJob(cluster,from);				
		
	}
	
	private Job findNextJob(String cluster, IbisIdentifier from) {
		Job nextJob = bot.tasks.remove(random.nextInt(bot.tasks.size()));
		
		/*the fact that pending jobs are timed from master side (hence including the latency to the worker) should 
		 * be mentioned and should also have some impact on the convergence speed of the histogram in those cases where 
		 * the job size is somewhat equal to this latency.
		 * */
		
		nextJob.startTime = System.nanoTime();
		workers.get(cluster).get(from.location().getLevel(0)).setLatestJobStartTime(nextJob.startTime);
		categories.get(cluster).get(Integer.MAX_VALUE).put(nextJob.jobID,
				nextJob);			
		/* might be the case that even here I return sayGB() */
		return nextJob;
	}
	
	private Job sayGB (IbisIdentifier to) {
		String cluster = to.location().getParent().toString();
		String node = to.location().getLevel(0);
		WorkerStats ws = workers.get(cluster).get(node);
		Cluster actualCluster = bot.Clusters.get(cluster);
		System.err.println("We say goodbye to " + to.location().toString());
		terminateWorker(actualCluster,ws, " scheduler decision");
		return new NoJob();
	}

	public void terminateWorker(Cluster cluster, WorkerStats ws, String reason) {
					
		ws.workerFinished(System.currentTimeMillis());
		ws.setLatestJobStartTime(0);
		cluster.setCrtNodes(bot.Clusters.get(cluster).getCrtNodes()-1);
	}
	
	@Override
	public void startInitWorkers() {
		
		System.err.println("BoTRunner has found " + bot.tasks.size() + " jobs; will distribute at first " + bot.noSampleJobs
				+ " over " + bot.noInitialWorkers + " initial workers on each participating cluster");
		
		Collection<Cluster> clusters = bot.Clusters.values();
		for (Cluster c : clusters) {
			Process p = c.startNodes(/*deadline2ResTime()*/"4:45:00", bot.noInitialWorkers, bot.electionName, 
                                                    bot.poolName, bot.serverAddress);
			//sshRunners.put(c.alias, p);
		}		
	}	
	
}