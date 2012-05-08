package org.koala.runnersFramework.runners.bot;

import org.koala.runnersFramework.runners.bot.BoTRunner;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Set;
import java.util.Timer;
import java.util.TimerTask;

import ibis.ipl.ConnectionFailedException;
import ibis.ipl.IbisIdentifier;
import ibis.ipl.IbisProperties;
import ibis.ipl.ReadMessage;
import ibis.ipl.ReceiveTimedOutException;
import ibis.ipl.SendPort;
import ibis.ipl.SendPortIdentifier;
import ibis.ipl.WriteMessage;
import org.koala.runnersFramework.runners.bot.Item;
import org.koala.runnersFramework.runners.bot.Job;
import org.koala.runnersFramework.runners.bot.JobRequest;
import org.koala.runnersFramework.runners.bot.JobResult;
import org.koala.runnersFramework.runners.bot.Knapsack;
import org.koala.runnersFramework.runners.bot.MyTimerTask;
import org.koala.runnersFramework.runners.bot.NoJob;
import org.koala.runnersFramework.runners.bot.WorkerStats;

public class SampleFreeMaster extends Master {

	long timeOfLastSchedule;
	private long actualStartTime;
	private long lastReconfigTime;
	private double va;
	private double ca;
	
	private Timer timer;
		
	protected SampleFreeMaster(BoTRunner aBot) throws Exception {
		super(aBot);
	
		double zeta_sq = bot.zeta * bot.zeta;
		bot.subsetLength = (int) Math.ceil(bot.tasks.size() * zeta_sq
				/ (zeta_sq + 2 * (bot.tasks.size() - 1) * bot.delta * bot.delta));
		
		System.out.println("Subset length is " + bot.subsetLength + " totalNumberTasks: " + totalNumberTasks);
		
		//bot.noInitialWorkers = bot.noSampleJobs ;
		//bot.noInitialWorkers = 1;
		bot.noInitialWorkers = (int) Math.min((0.1 * totalNumberTasks), bot.subsetLength);
		
		Collection<Cluster> clusters = bot.Clusters.values();
		
		for (Cluster cluster : clusters) {
			
			HashMap<String, WorkerStats> workersCluster = new HashMap<String, WorkerStats>();
			workers.put(cluster.alias, workersCluster);
			
			cluster.setCrtNodes(0);
			cluster.setPendingNodes(0);
			cluster.setNecNodes(bot.noInitialWorkers);
			cluster.noATUPlan=1;
		}
		
		timer = new Timer();
	
	}


	@Override
	protected void handleLostConnections() {
		String cluster;
		String node;
		for(SendPortIdentifier lost : masterRP.lostConnections()) {
			cluster = lost.ibisIdentifier().location().getParent().toString();		
			node = lost.ibisIdentifier().location().getLevel(0);
			if(! workers.get(cluster).get(node).isFinished()) {
			for(Job j : bot.Clusters.get(cluster).subsetJobs.values())
				if (j.getNode().compareTo(node)==0) {
					bot.Clusters.get(cluster).subsetJobs.remove(j.getJobID());
					bot.tasks.add(j);
					
					workers.get(cluster).get(j.getNode()).workerFinished(System.currentTimeMillis());
					
					bot.Clusters.get(cluster).setCrtNodes(bot.Clusters.get(cluster).getCrtNodes()-1);
					System.err.println("Node " + node + " in cluster " + cluster + 
							" failed during execution of job " + j.jobID + 
							" ; cost: " 
 + (Math.ceil((double)workers.get(cluster).get(j.getNode()).getUptime() / 60000 / bot.Clusters.get(cluster).timeUnit)  
									* bot.Clusters.get(cluster).costUnit));
					break;
				}
			}
		}
	}
	
	@Override
	protected boolean areWeDone() {
    /*check whether we finished*/
		
		handleLostConnections();
		
		/*speed up*/
		if(bot.tasks.size() != 0) return false;
				
		Collection<Cluster> clusters = bot.Clusters.values();
		
		if (jobsDone == totalNumberTasks) {
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
				}
				System.out.println("Due amount " + price);
				long totalTime = (System.currentTimeMillis()-actualStartTime)/1000;
				System.out.println("Application took " + totalTime + " (sec), which is about " + totalTime/60 + "m" + totalTime%60 +"s");
				System.out.println("Hurray! I'm done with " + jobsDone + " jobs!!!");
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


	private ArrayList<Item> updateClusterStats(boolean debug) {
		/*compute T_i*/
		Collection<Cluster> clusters = bot.Clusters.values();		
		ArrayList<Item> items = new ArrayList<Item>();		
		items.add(new Item(0,0,""));
		bot.minCostATU = Integer.MAX_VALUE;
		bot.maxCostATU = 0;
		boolean tmp = true;
		for(Cluster cluster : clusters) {
			double t_i = 0;
			int N = 0;			
			/*DEBUG*/
			System.err.println("decide(): cluster " + cluster.alias);
				
						
			/*DEBUG*/
			System.err.println("decide(): in total " + (cluster.noDoneJobs + cluster.subsetJobs.size()));
			
			if(cluster.samplingPointsCounter >= bot.subsetLength) {
				if(cluster.samplingPointsCounter == bot.subsetLength) {
					cluster.sampleSetDone();
				}
				cluster.firstStats = true;
				cluster.updateTi();
				System.out.println("cluster " + cluster.alias + " : \t Ti " + cluster.Ti);
			}
			if(cluster.Ti != 0 ) {
				bot.minCostATU = (int) Math.min(bot.minCostATU, cluster.costUnit);
				bot.maxCostATU += cluster.maxNodes*cluster.costUnit;
				for (int i = 0; i < cluster.maxNodes; i++)
					/*
					 * worked with original knapsack limit
					 * budget/bot.totalNumberTasks items.add(new
					 * Item((double)cluster
					 * .timeUnit/(bot.totalNumberTaskscluster.Ti),
					 * (double)cluster.costUnit/bot.totalNumberTasks,
					 * cluster.alias));
					 */
					items.add(new Item(1 / cluster.Ti, (int) cluster.costUnit,
							cluster.alias));
				/*DEBUG*/
				if(debug) System.err.println("Added machines from cluster " + cluster.alias + "; Items has now " + items.size());
			}			
			if(tmp && cluster.firstStats)
				tmp = true;
			else tmp = false;
		}
		
		if (tmp) {
			if((!bot.allStatsReady) && (!bot.firstTimeAllStatsReady)) {		
				bot.firstTimeAllStatsReady=true;
				bot.allStatsReady=true;
			}
		    else if(bot.firstTimeAllStatsReady) {
		    	bot.allStatsReady=true;
		    	bot.firstTimeAllStatsReady=false;
		    }
		}
		return items;
	}

	
	private void decideWithMovingAverage(boolean socketTimeout) {
		// TODO Auto-generated method stub
		/*compute averages*/		
		boolean dueTimeout = System.currentTimeMillis() - timeOfLastSchedule >= timeout;
		
		if(socketTimeout && (!dueTimeout)) return;

		Collection<Cluster> clusters = bot.Clusters.values();		
		va = 0;
		ca = 0;
		double consumedBudget = 0;		
		int virtualJobsDone = 0;
		double virtualJobsDoneDouble = 0.0;
		double potentialJobsDone = 0.0;
		ArrayList<Item> items = updateClusterStats(dueTimeout);
		/*is it time to verify the configuration?*/
		if((dueTimeout && bot.allStatsReady) || bot.firstTimeAllStatsReady) {
			if(dueTimeout) {System.out.println("Due timeout");}	
			System.out.println("Last reconfiguration time=" + (double)lastReconfigTime/60000);
			for(Cluster cluster : clusters) {			
				/*compute the actual speed of this cluster using the worker stats*/
				for(WorkerStats ws : workers.get(cluster.alias).values()) {
					if(!ws.isFinished()) {				  
						/*worker is idle*/
						long crtUptime = ws.getUptime();
						double tmp1;
						int pottmp=0;
						int  atusBeforeReconfig = 0;
						double v;
						int tmp;
						int noATUsPaidFor;
						System.out.println("lastReconfigTime="+ lastReconfigTime + " ; startTime=" + ws.getStartTime());
						if(ws.getStartTime() <  lastReconfigTime) {
						    atusBeforeReconfig = (int) (Math.ceil((double)(lastReconfigTime-ws.getStartTime())/60000/cluster.timeUnit));						    
						}
						if(ws.getLatestJobStartTime() == 0) {
							v = (double) (ws.getNoJobs()*60000000000L)/((double)ws.getRuntime());
							
							noATUsPaidFor = (int) Math.ceil((double)crtUptime/ 60000L / cluster.timeUnit);
							
							if(!ws.isMarked()) {
								/*check if i should terminate this ATU*/
								if((cluster.noATUPlan-(noATUsPaidFor-atusBeforeReconfig)) == 0) {
									terminateWorker(cluster, ws, " current ATU is last");
									cluster.necNodes --;
									consumedBudget +=
										noATUsPaidFor * cluster.costUnit;
									long timeLeftATU = cluster.timeUnit*60000 - crtUptime%(cluster.timeUnit*60000);
									tmp1=((double)timeLeftATU/60000)*v;
									tmp = (int) Math.floor(((double)timeLeftATU/60000)*v);
																	
									System.out.println("(marked now) node " + ws.getIbisIdentifier().location().toString() +
											": currentPaidForATU=" + noATUsPaidFor +
											" ; timeLeftATU=" + timeLeftATU +
											" ; atusBeforeReconfig=" + atusBeforeReconfig +
											" ; virtualJobsDone="+tmp);
								} else {
									va += v;							
									consumedBudget += noATUsPaidFor * cluster.costUnit;
									long currentPosition = crtUptime%(cluster.timeUnit*60000);
									long timeLeftATU = cluster.timeUnit*60000 - currentPosition;
									tmp1= ((double)timeLeftATU/60000)*v;
									tmp = (int) Math.floor(((double)timeLeftATU/60000)*v);									
								    ws.setSpeed(v);
									ws.setFuturePoint((double)(cluster.timeUnit*60000 - currentPosition - (double)60000*tmp/v)/60000);
									pottmp = (int)Math.floor(((double)(cluster.noATUPlan-(noATUsPaidFor-atusBeforeReconfig))*cluster.timeUnit
											+ws.getFuturePoint())*v);
									ws.setLastEstimatedUptime(noATUsPaidFor*cluster.timeUnit - ws.getFuturePoint());
									System.out.println("node " + ws.getIbisIdentifier().location().toString() +
											": currentPaidForATU=" + noATUsPaidFor +
											" ; timeLeftATU=" + timeLeftATU + 
											" ; atusBeforeReconfig=" + atusBeforeReconfig +
											" ; virtualJobsDone="+tmp + 
											" ; potentialJobsDone="+pottmp+
											" ; futurePoint="+ws.getFuturePoint());									
								}
							} else {
								/*already marked*/
								consumedBudget +=
									noATUsPaidFor * cluster.costUnit;
								long timeLeftATU = cluster.timeUnit*60000 - crtUptime%(cluster.timeUnit*60000);
								tmp1=((double)timeLeftATU/60000)*v;
								tmp = (int) Math.floor(((double)timeLeftATU/60000)*v);
																
								System.out.println("(marked) node " + ws.getIbisIdentifier().location().toString() +
										": currentPaidForATU=" + noATUsPaidFor +
										" ; timeLeftATU=" + timeLeftATU + 
										" ; atusBeforeReconfig=" + atusBeforeReconfig +
										" ; virtualJobsDone="+tmp);
							}
							virtualJobsDone += tmp;
							virtualJobsDoneDouble += tmp1;
							potentialJobsDone += pottmp;
						} else {
							//underExec ++;
							long taui = System.nanoTime() - ws.getLatestJobStartTime();
							double tauiToMin = (double)taui/60000000000L;
							double intermET =  cluster.estimateIntermediary(taui) / 60000000000L;						
							v = (double) (ws.getNoJobs()+1)/(intermET + (double)ws.getRuntime()/60000000000L);
							long timeLeftATU;							
							long currentPosition;
							if(!ws.isMarked()) {								
								noATUsPaidFor = (int) Math.ceil(((double)crtUptime / 60000 + intermET - tauiToMin) 
										/ cluster.timeUnit);								
								/*check if i should terminate this ATU*/
								if((cluster.noATUPlan-((int) Math.ceil((double)crtUptime / 60000 / cluster.timeUnit)-atusBeforeReconfig)) == 0) {
									terminateWorker(cluster, ws, " current ATU is last");
									cluster.necNodes --;
									consumedBudget +=  (int)(Math.ceil((double)crtUptime / 60000 / cluster.timeUnit)) * cluster.costUnit;
																		
									if((int)(Math.ceil((double)crtUptime / 60000 / cluster.timeUnit)) < noATUsPaidFor) {
										timeLeftATU = 0;
										noATUsPaidFor = (int) Math.ceil((double)crtUptime / 60000L / cluster.timeUnit);
									} else {
										timeLeftATU = cluster.timeUnit*60000 - (crtUptime + (long)((intermET-tauiToMin)*60000))%(cluster.timeUnit*60000);										
									}
									tmp1=((double)timeLeftATU/60000)*(double) (ws.getNoJobs()+1)/(intermET + (double)ws.getRuntime()/60000000000L);
									tmp = (int) Math.floor(((double)timeLeftATU/60000)*(double) (ws.getNoJobs()+1)/(intermET + (double)ws.getRuntime()/60000000000L));
									System.out.println("(marked now) node " + ws.getIbisIdentifier().location().toString() +
											": currentPaidForATU=" + noATUsPaidFor +
											" ; timeLeftATU=" + timeLeftATU + 
											" ; atusBeforeReconfig=" + atusBeforeReconfig +
											" ; virtualJobsDone="+tmp);
								} else {
									va += v;
									consumedBudget += noATUsPaidFor * cluster.costUnit;
									currentPosition = (crtUptime + (long)((intermET-tauiToMin)*60000))%(cluster.timeUnit*60000);
									timeLeftATU = cluster.timeUnit*60000 - currentPosition;
									tmp1=((double)timeLeftATU/60000)*v;
									tmp = (int) Math.floor(((double)timeLeftATU/60000)*v);									
									ws.setSpeed(v);
									ws.setFuturePoint((double)(timeLeftATU - (double)60000*tmp/v)/60000);
									pottmp = (int)Math.floor(((double)(cluster.noATUPlan-(noATUsPaidFor-atusBeforeReconfig))*cluster.timeUnit
											+ws.getFuturePoint())*v);
									ws.setLastEstimatedUptime(noATUsPaidFor*cluster.timeUnit - ws.getFuturePoint());
									System.out.println("node " + ws.getIbisIdentifier().location().toString() +
											": currentPaidForATU=" + noATUsPaidFor +
											" ; timeLeftATU=" + timeLeftATU + 
											" ; atusBeforeReconfig=" + atusBeforeReconfig +
											" ; virtualJobsDone="+tmp +
											" ; potentialJobsDone="+pottmp+
											" ; futurePoint="+ws.getFuturePoint() + "; v="+v);
								}
							} else {
								/*already marked*/
								noATUsPaidFor = (int) Math.ceil((double)crtUptime/ 60000L / cluster.timeUnit);
								consumedBudget += noATUsPaidFor * cluster.costUnit;
								if(noATUsPaidFor < (int) Math.ceil(((double)crtUptime / 60000 + intermET - tauiToMin) 
										/ cluster.timeUnit)) {
									timeLeftATU = 0;
								} else {
									timeLeftATU = cluster.timeUnit*60000 - (crtUptime + (long)((intermET-tauiToMin)*60000))%(cluster.timeUnit*60000);
								}
								tmp1=((double)timeLeftATU/60000)*(double) (ws.getNoJobs()+1)/(intermET + (double)ws.getRuntime()/60000000000L);
								tmp = (int) Math.floor(((double)timeLeftATU/60000)*(double) (ws.getNoJobs()+1)/(intermET + (double)ws.getRuntime()/60000000000L));
								System.out.println("(marked) node " + ws.getIbisIdentifier().location().toString() +
										": currentPaidForATU=" + noATUsPaidFor +
										" ; timeLeftATU=" + timeLeftATU +
										" ; atusBeforeReconfig=" + atusBeforeReconfig +
										" ; virtualJobsDone="+tmp);
							}

							virtualJobsDone += tmp;
							virtualJobsDoneDouble += tmp1;
							potentialJobsDone += pottmp;
						}											
					} else {
						consumedBudget += Math.ceil((double)ws.getUptime() / 60000 / cluster.timeUnit) * cluster.costUnit;						
					}
				}
				System.out.println("cluster " + cluster.alias  + ": va=" + va + 
						"; virtualJobsDone=" + virtualJobsDone
						+"; virtualJobsDoneDouble=" + virtualJobsDoneDouble
						+"; potentialJobsDoneDouble=" + potentialJobsDone);		
				System.out.println("cluster " + cluster.alias 
						+ ": prevNecNodes=" + cluster.prevNecNodes 
						+ "; necNodes="+cluster.necNodes 
						+ "; crtNodes="+cluster.crtNodes
						+ "; pendingNodes="+cluster.pendingNodes);
			}
			
			/*how many more minutes*/	
			int jobsLeft = bot.tasks.size() - /*(int)Math.floor(virtualJobsDoneDouble)*/virtualJobsDone ;
			double minSinceLastReconfig = (double)(System.currentTimeMillis() - lastReconfigTime)/60000;
			double etLeft = jobsLeft / va;
			if(etLeft<0) etLeft=0;			
			/*how much more money*/
			double ebLeft = 0.0; /*Math.ceil(etLeft/bot.timeUnit) * ca;*/ 

			System.out.println("Total execution time since last reconfiguration: " + Math.ceil((minSinceLastReconfig+etLeft)/bot.timeUnit));
		/*	for(Cluster cluster : clusters) {			
				compute the actual speed of this cluster using the worker stats
				for(WorkerStats ws : workers.get(cluster.alias).values()) {
					if(!ws.isFinished()) { 
						if(!ws.isMarked()) {
								expressed in ATU
								int timeLeftWorker; etLeft - ws.getOffset();||cluster.Ti*ws.getSpeed()*jobsLeft/va;||etLeft-ws.getFuturePoint();
								int atusBeforeReconfig=0;
								!!!!might be better to subtract and then compute ceil								
								if(ws.getStartTime() <  lastReconfigTime) {
								    atusBeforeReconfig = (int) (Math.ceil((double)(lastReconfigTime-ws.getStartTime())/60000)/cluster.timeUnit);
								}
								timeLeftWorker = cluster.noATUPlan - ((int)(
										Math.ceil(ws.getLastEstimatedUptime()/cluster.timeUnit)) - 
									    atusBeforeReconfig);				

								double costWorker;
								if(timeLeftWorker <= 0) {
									costWorker = 0;
									terminateNode(cluster, ws, " current ATU is last");
									cluster.necNodes --;
									might need to deal with cluster.nec nodes and so on
								}
								else {
									costWorker = timeLeftWorker*cluster.costUnit;
								}
								ebLeft += costWorker;
								System.out.println("worker " + ws.getIbisIdentifier().location().toString()  
										+ ": ATUs before reconfig " + atusBeforeReconfig 
										+ "; estimated future cost= " + costWorker  
										+ "; timeLeftWorker " + timeLeftWorker);
						}
					}
				}				
			}
*/
			/*DEBUG*/
			System.out.println("estimated number of jobs left: " + jobsLeft 
					+ " ; estimated time needed: " + etLeft 
					//+ " ; estimated budget needed: " + ebLeft
					+ " ; estimated number of potential jobs: " + potentialJobsDone
					+ " ; consumed budget: " + consumedBudget);
			
			if(((jobsLeft>potentialJobsDone)/*(ebLeft > 1.0*(bot.budget-consumedBudget))*/ && bot.allStatsReady) || (bot.firstTimeAllStatsReady)) {					
				if(items.size() > 1) { 
					Knapsack moo = new Knapsack(items.toArray(new Item[0]),
							(long)bot.budget-(long)consumedBudget, jobsLeft, bot.minCostATU,
							bot.maxCostATU,(int)bot.timeUnit);
					System.out.println("budget available: " + (bot.budget-consumedBudget) + 
							" ; number of jobs to go: " + jobsLeft + 
							" ; minCostATU: " + bot.minCostATU + " ; maxCostATU: " + bot.maxCostATU);
					/*ItemType[] itemTypes = prepContKnap();
				ContKnap moo = new ContKnap(itemTypes, bot.budget, bot.timeUnit);*/
					HashMap<String, Integer> machinesPerCluster = moo.findSol();			
					System.out.println("NoATUsPlan=" + moo.noATUPlan);
					for(Cluster cluster : clusters) {
						Integer Mi = machinesPerCluster.get(cluster.alias);
						int moreWorkers = 0;
						cluster.noATUPlan = moo.noATUPlan;
						if(Mi == null) {
							if(cluster.Ti!=0) {
								Mi = new Integer(0);
							} else {
								continue;
							}
						} 
						lastReconfigTime = System.currentTimeMillis();
						cluster.prevNecNodes = cluster.necNodes;
						
						System.out.println("cluster " + cluster.alias 
								+ ": prevNecNodes=" + cluster.prevNecNodes 
								+ "; necNodes="+Mi.intValue() 
								+ "; crtNodes="+cluster.crtNodes
								+ "; pendingNodes="+cluster.pendingNodes);
						
						if(Mi.intValue() > cluster.prevNecNodes) {
							if(Mi.intValue() > cluster.crtNodes + cluster.pendingNodes) {
								moreWorkers = Math.min(cluster.maxNodes, Mi.intValue()) 
										- cluster.crtNodes - cluster.pendingNodes;
								cluster.startNodes("12:45:00", moreWorkers, bot.electionName, bot.poolName, bot.serverAddress);
								cluster.setPendingNodes(cluster.pendingNodes + moreWorkers);
								/*DEBUG*/
								System.out.println("Cluster " + cluster.alias + ": started " + moreWorkers + " more workers.");
							}
							/*!in testing!*/
							else {
								int keepWorkers = Mi.intValue() - cluster.prevNecNodes;
								ArrayList<WorkerStats> orderedByTimeLeftATU = new ArrayList<WorkerStats>(workers.get(cluster.alias).values());
								Collections.sort(orderedByTimeLeftATU, new Comparator<WorkerStats>(){
									public int compare(WorkerStats a, WorkerStats b) {
										return a.timestamp - b.timestamp;
									}
								});
								for(int i=orderedByTimeLeftATU.size()-1; i>=0; i--) {
									WorkerStats ws = orderedByTimeLeftATU.get(i);									
									if(ws.isMarked() && (!ws.isFinished()) && (ws.killingMe!=null)) {
										if(ws.killingMe.cancel()) {
											ws.unmarkTerminated();
											keepWorkers --;
											System.out.println("Will not terminate node: " 
													+ ws.getIbisIdentifier().location().toString());
											if(keepWorkers == 0) break;
										}
									}
								}
								if(keepWorkers != 0) {
									System.out.println("Trouble!!!!!! Could not resurect enough workers; should reacquire them!");
								}
							}
							cluster.necNodes = Mi.intValue();
						} else if(Mi.intValue() < cluster.prevNecNodes) {					
								cluster.necNodes = Mi.intValue();
								if(cluster.necNodes < cluster.crtNodes + cluster.pendingNodes) {
									System.out.println("Terminate nodes on cluster " + cluster.alias);
									selectTerminatedWorkers(cluster);								
								}
						}
						/*DEBUG*/
						System.out.println("cluster " + cluster.alias + 
								"-> new necessary number of workers: " + cluster.necNodes);
					}					
				} 
				else System.out.println("No cluster stats available yet");
			} 
			/*DEBUG*/
			else System.out.println("Nothing changed");
			
			timeOfLastSchedule = System.currentTimeMillis();
		}		
	}

	@SuppressWarnings("unchecked")
	private void selectTerminatedWorkers(Cluster cluster) {
		
		if(cluster.crtNodes <= cluster.necNodes) {
			/*i need to get rid of only extra pending nodes*/
			cluster.pendingNodes = cluster.necNodes - cluster.crtNodes;
			return;
		}
		int howManyCrtNodes = cluster.prevNecNodes - cluster.necNodes;
		ArrayList<WorkerStats> orderedByArrival = new ArrayList(workers.get(cluster.alias).values());
		Collections.sort(orderedByArrival, new Comparator<WorkerStats>(){
			public int compare(WorkerStats a, WorkerStats b) {
				return a.timestamp - b.timestamp;
			}
		});
		for(int i=orderedByArrival.size()-1; i>=0; i--) {
			WorkerStats ws = orderedByArrival.get(i);
			/*could select the terminated workers based on other criterion*/
			if((!ws.isFinished()) && (!ws.isMarked())) {
				/*5*60000 should be replaced by a function of Ti*/ 
				/*long timeLeftATU = cluster.timeUnit*60000 - ws.getUptime()%(cluster.timeUnit*60000) - 5*60000;
				if(timeLeftATU < 0) {
					try {						
						myIbis.registry().signal("die", ws.getIbisIdentifier());
					} catch (IOException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				} else {
					timer.schedule(new MyTimerTask(myIbis,ws.getIbisIdentifier()),timeLeftATU);
				}
				ws.markTerminated();
				System.out.println("Selected node " + ws.getIbisIdentifier().location().toString() + " for termination");
				*/
				terminateWorker(cluster, ws, " selected by scheduler");
				howManyCrtNodes --;
				if(howManyCrtNodes == 0) break;
			}
		}
		return;
	}
		
	public void terminateWorker(Cluster cluster, WorkerStats ws, String reason) {
		long crtTime=0;
		long timeLeftATU = cluster.timeUnit*60000 - ws.getUptime()%(cluster.timeUnit*60000) - 60000;
		TimerTask tt = null;
		if(timeLeftATU <= 0) {
			try {	
				crtTime= System.currentTimeMillis();
				cluster.terminateNode(ws.getIbisIdentifier(), myIbis);
				//myIbis.registry().signal("die", ws.getIbisIdentifier());
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		} else {
			crtTime= System.currentTimeMillis();
			tt = new MyTimerTask(cluster,ws.getIbisIdentifier(),myIbis);
			timer.schedule(tt,timeLeftATU);
		}
		ws.markTerminated(tt);
		ws.setTimeToDie(crtTime+timeLeftATU);
		System.out.println("Node " + ws.getIbisIdentifier().location().toString() + " will terminate after current ATU due to " 
				+ reason);		
	}
	
	private void decide(boolean socketTimeout) {
		decideWithMovingAverage(socketTimeout);
	}
	
	@Override
	protected Job handleJobRequest(IbisIdentifier from) {
		/*for now, when a new worker shows up, if there are no more jobs just return nojob
		 * should consider later addition of job replication*/		
		
		String cluster = from.location().getParent().toString();
		String node = from.location().getLevel(0);
		
		/*DEBUG*/
		System.err.println("job request from node " + from.location().toString() + " in cluster " + cluster);
		
		/*might be changed to allow execution for one ATU, since it has already started
		 * for now we do not consider it, and behave as if we do not pay*/
		
		if(bot.Clusters.get(cluster).pendingNodes == 0) {
			/*DEBUG*/
			System.err.println("node " + from.location().toString() + " in cluster " + cluster 
					+ " has been dismissed right after registration with master");
			
			return new NoJob();
		}
		
		WorkerStats reacquiredMachine = workers.get(cluster).get(node);
		long startTime = System.currentTimeMillis();
		if(reacquiredMachine == null) {
			workers.get(cluster).put(node, new WorkerStats(node,startTime, from));
			workers.get(cluster).get(node).setIbisIdentifier(from);
			bot.Clusters.get(cluster).timestamp++;
			
			if(bot.Clusters.get(cluster).timestamp > bot.noInitialWorkers)
				workers.get(cluster).get(node).setOffset((double)bot.Clusters.get(cluster).timeUnit-((startTime-this.actualStartTime)%(bot.Clusters.get(cluster).timeUnit*60000))/60000);
			else 
				workers.get(cluster).get(node).setInitialWorker(true);
			
			workers.get(cluster).get(node).timestamp = bot.Clusters.get(cluster).timestamp;
			workers.get(cluster).get(node).noATUPlan = bot.Clusters.get(cluster).noATUPlan;
		} else {
			reacquiredMachine.reacquire(bot.Clusters.get(cluster).timeUnit, startTime);
			reacquiredMachine.setIbisIdentifier(from);
			workers.get(cluster).get(node).setOffset((double)bot.Clusters.get(cluster).timeUnit-((startTime-this.actualStartTime)%(bot.Clusters.get(cluster).timeUnit*60000))/60000);
			bot.Clusters.get(cluster).timestamp++;
			workers.get(cluster).get(node).timestamp = bot.Clusters.get(cluster).timestamp;
			workers.get(cluster).get(node).noATUPlan = bot.Clusters.get(cluster).noATUPlan;
		}		
		
		bot.Clusters.get(cluster).setCrtNodes(bot.Clusters.get(cluster).getCrtNodes()+1);
		bot.Clusters.get(cluster).setPendingNodes(bot.Clusters.get(cluster).getPendingNodes()-1);
		
		/*release unnecessary workers*/
		if(releaseNow(cluster,from)) {
			return new NoJob();
		}
		
		return findNextJob(cluster,from);				
    }

	@Override
	protected Job handleJobResult(JobResult received, IbisIdentifier from) {
		// TODO Auto-generated method stub
		String cluster = from.location().getParent().toString();			
		
		System.err.println(from.location().toString() + " returned result of job " + received.getJobID() + " executed for (sec)" + received.getStats().getRuntime()/1000000000);
		
		/* assumes jobs don't need to be replicated on the same cluster, except on failure */
		
		jobsDone ++;
			
		workers.get(cluster).get(from.location().getLevel(0)).addJobStats(received.getStats().getRuntime());
		
		bot.Clusters.get(cluster).doneJob(received);	
		
		decide(false);
		
		/*release unnecessary workers*/
		if(releaseNow(cluster,from)) {
			return new NoJob();
		} /*else if(bot.tasks.size() == 0) {
			return new AskAgainJob();
		}*/
		 		
		return findNextJob(cluster,from);		
	}

	private boolean releaseNow(String cluster, IbisIdentifier to) {
		/*could check whether "black-listed" machine and, if too little of ATU is left
		 * get rid of it now and maybe even cancel the respective timer*/
		
		/*if enough of ATU is left could replicate jobs sent to other "dying" workers*/ 
		/*this.jobsDone == this.totalNumberTasks*/
		if(bot.tasks.size()==0) {
			System.err.println("We say goodbye to " + to.location().toString());
			
			String node = to.location().getLevel(0);
			workers.get(cluster).get(node).workerFinished(System.currentTimeMillis());
			workers.get(cluster).get(node).setLatestJobStartTime(0);
			bot.Clusters.get(cluster).setCrtNodes(bot.Clusters.get(cluster).getCrtNodes()-1);
			//bot.Clusters.get(cluster).setPendingNodes(bot.Clusters.get(cluster).getPendingNodes()-1);
			return true;
		} 
		return false;
	}

	
	private Job findNextJob(String cluster, IbisIdentifier from) {
		Job nextJob = bot.tasks.remove(random.nextInt(bot.tasks.size()));
		
		/*the fact that pending jobs are timed from master side (hence including the latency to the worker) should 
		 * be mentioned and should also have some impact on the convergence speed of the histogram in those cases where 
		 * the job size is somewhat equal to this latency.
		 * */
		
		nextJob.startTime = System.nanoTime();
		workers.get(cluster).get(from.location().getLevel(0)).setLatestJobStartTime(nextJob.startTime);
		bot.Clusters.get(cluster).subsetJobs.put(nextJob.jobID, nextJob);
		if(bot.Clusters.get(cluster).samplingPoints.size() < bot.subsetLength) {
			bot.Clusters.get(cluster).samplingPoints.put(nextJob.jobID, nextJob);
		}
		/* might be the case that even here I return sayGB() */
		return nextJob;
	}
		
	@Override
	public void run() {
		// TODO Auto-generated method stub
		timeOfLastSchedule = System.currentTimeMillis();
		
		timeout = (long) (BoTRunner.INITIAL_TIMEOUT_PERCENT * bot.deadline * 60000);
		System.err.println("Timeout is now " + timeout);		
		
		actualStartTime = System.currentTimeMillis();
		lastReconfigTime = Long.MAX_VALUE;
		
		boolean undone = true;
		boolean socketTimeout = false;
		
		while (undone) {
			try {
				socketTimeout = false;
				ReadMessage rm = masterRP.receive(30000);

				Object received = rm.readObject();
				IbisIdentifier from = rm.origin().ibisIdentifier();
				rm.finish();
				Job nextJob = null;

				if (received instanceof JobRequest) {
					nextJob = handleJobRequest(from);
				} else if (received instanceof JobResult) {
					nextJob = handleJobResult((JobResult) received, from);
				} else {
					throw new RuntimeException("received "
                                                        + "an object which is not JobRequest or JobResult:" + received);
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
				
				System.err.println("I timed out on socket!");
				socketTimeout = true;
				
				undone = ! areWeDone();
				
				decide(socketTimeout);
											
				
			} catch (ConnectionFailedException cfe) {
				/* !!! don't forget to decrease the number of crt nodes*/
				String cluster = cfe.ibisIdentifier().location().getParent().toString();		
				String node = cfe.ibisIdentifier().location().getLevel(0);
				for(Job j : bot.Clusters.get(cluster).subsetJobs.values())
					if (j.getNode().compareTo(node)==0) {
						bot.Clusters.get(cluster).subsetJobs.remove(j.getJobID());
						bot.tasks.add(j);
						
						workers.get(cluster).get(j.getNode()).workerFinished(System.currentTimeMillis());
						
						bot.Clusters.get(cluster).setCrtNodes(bot.Clusters.get(cluster).getCrtNodes()-1);
						System.err.println("Node " + cfe.ibisIdentifier().location().toString() + 
								" failed before receiving job " + j.jobID + 
								" ; cost: " 
+ (Math.ceil((double)workers.get(cluster).get(j.getNode()).getUptime() / 60000 / bot.Clusters.get(cluster).timeUnit)  
																	* bot.Clusters.get(cluster).costUnit));
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
	public void startInitWorkers() {
		
		System.err.println("BoTRunner has found " + bot.tasks.size() + " jobs; will distribute at first " + bot.subsetLength
				+ " over " + bot.noInitialWorkers + " initial workers on each participating cluster");
		
		Collection<Cluster> clusters = bot.Clusters.values();
		for (Cluster c : clusters) {
			Process p = c.startNodes(/*deadline2ResTime()*/"12:45:00", c.necNodes, bot.electionName,
                                                     bot.poolName, bot.serverAddress);
			//sshRunners.put(c.alias, p);
			c.setPendingNodes(c.necNodes);
		}		
	}

}
