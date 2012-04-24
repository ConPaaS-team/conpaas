package org.koala.runnersFramework.runners.bot;

import java.util.logging.Level;
import java.util.logging.Logger;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Random;
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

import java.io.File;
import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.util.HashSet;
import java.util.Iterator;


/**
 * This is the estimator.
 */
public class SamplingPhaseMaster extends Master {

	
	protected HashMap<String, HashMap<Integer, HashMap<String, Job>>> categories;
	private ArrayList<Job> replicatedTasks;

	Timer timer;

	private boolean selectedReferenceCluster = false;
	private int totalSamplingPointsCounter = 0;
	private int totalSamplingSubmittedCounter = 0;
	private double sampleCost;
	private long sampleMakespan; /*expressed in seconds*/
	public ArrayList<Schedule> schedules;

	protected SamplingPhaseMaster(BoTRunner bot) throws Exception {
		super(bot);
		schedules = new ArrayList<Schedule>();
		double zeta_sq = bot.zeta * bot.zeta;
		bot.noSampleJobs = (int) Math.ceil(bot.tasks.size() * zeta_sq
				/ (zeta_sq + 2 * (bot.tasks.size() - 1) * bot.delta * bot.delta));		

		System.out.println("Sample size is: " + bot.noSampleJobs);
	
		
		if(bot.noSampleJobs < bot.noReplicatedJobs) {
			System.out.println("Bag too small!");
			System.exit(0);
		}

		bot.finishedTasks = new ArrayList<Job>();

		replicatedTasks = new ArrayList<Job>();
		Random randomSample = new Random(1111111111L);
		
		
		for(int i = 0; i < bot.noReplicatedJobs; i++) {
			replicatedTasks.add(bot.tasks.remove(randomSample.nextInt(bot.tasks.size())));
		}

		Collection<Cluster> clusters = bot.Clusters.values();		

		if(bot.noSampleJobs*bot.Clusters.size() > 0.5 * totalNumberTasks)
		{
			throw new RuntimeException("Size of the BoT too small for the number of clusters");
		}

		bot.noInitialWorkers = 1;

		Cluster cheapest = findCheapest();

		bot.minCostATU = Integer.MAX_VALUE;
		bot.maxCostATU = 0;

		for (Cluster cluster : clusters) {

			HashMap<String, WorkerStats> workersCluster = new HashMap<String, WorkerStats>();
			workers.put(cluster.alias, workersCluster);

			cluster.setCrtNodes(0);
			cluster.setPendingNodes(computeRatio(cluster.costUnit,cheapest.costUnit,true));
			cluster.setNecNodes(bot.noInitialWorkers);

			bot.minCostATU = (int) Math.min(bot.minCostATU, cluster.costUnit);
			bot.maxCostATU += cluster.maxNodes*cluster.costUnit;
		}

		timer = new Timer();
	}

	private int computeRatio(double c_i, double cheapest, boolean uniform) {
		int initialWorkers = bot.noInitialWorkers;
		if(!uniform) {
			double ratio = c_i/cheapest;
			if(ratio > bot.noInitialWorkers) {
				ratio = bot.noInitialWorkers;
			}
			initialWorkers = (int) Math.floor(bot.noInitialWorkers / ratio);
		}
		return initialWorkers;
	}

	private Cluster findCheapest() {
		Cluster cheapestCluster = null;
		double cheapest = Double.MAX_VALUE;
		for (Cluster cluster : bot.Clusters.values()) {
			if(cluster.costUnit < cheapest) {
				cheapest = cluster.costUnit;
				cheapestCluster = cluster;
			} else if (cluster.costUnit == cheapest) {
				if(cluster.Ti < cheapestCluster.Ti) {
					cheapestCluster = cluster;
				}
			}
		}
		return cheapestCluster;
	}

	@Override
	protected boolean areWeDone() {

		handleLostConnections();

		for(Cluster cluster : bot.Clusters.values()) {
			if(cluster.replicatedTasksCounter != bot.noReplicatedJobs) { 
				return false;
				/* not used in all-compute-sample mode
				 * if(cluster.isReferenceCluster) {
					if(cluster.samplingPointsCounter + cluster.replicatedTasksCounter != bot.noSampleJobs) {
						return false;
					}
				   }*/	
			}	
		}		
		if((totalSamplingPointsCounter+bot.noReplicatedJobs) != bot.noSampleJobs) {
			return false;
		}

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
				return false;
			}
		}		
		return true;
	}

	@Override
	protected Job handleJobRequest(IbisIdentifier from) {
		String clusterName = from.location().getParent().toString();
		String node = from.location().getLevel(0);
		Cluster cluster = bot.Clusters.get(clusterName);

		/*DEBUG*/
		System.err.println("job request from node " + from.location().toString() + " in cluster " + clusterName);

		WorkerStats reacquiredMachine = workers.get(clusterName).get(node);
		if(reacquiredMachine == null) {
			workers.get(clusterName).put(node, new WorkerStats(node, System.currentTimeMillis(), from));
		} else {
			reacquiredMachine.reacquire(cluster.timeUnit, System.currentTimeMillis());
		}	

		cluster.setCrtNodes(cluster.getCrtNodes()+1);
		cluster.setPendingNodes(cluster.getPendingNodes()-1);

		//decideReferenceCluster();

		return findNextJob(cluster, from);
	}

	@Override
	protected Job handleJobResult(JobResult received, IbisIdentifier from) {

		String node = from.location().getLevel(0);
		String clusterName = from.location().getParent().toString();			
		Cluster cluster = bot.Clusters.get(clusterName);

		System.err.println(from.location().toString() + " returned result of job " + 
				received.getJobID() + " executed for (sec)" + received.getStats().getRuntime()/1000000000);

		/*find the job*/		
		Job doneJob = cluster.regressionPoints.get(received.getJobID()); 

		if(doneJob == null) {
			doneJob = cluster.samplingPoints.get(received.getJobID());
			if(doneJob == null) {
				doneJob = cluster.extraPoints.get(received.getJobID());
			} else {
				cluster.samplingPointsCounter ++;
				totalSamplingPointsCounter ++;
			}
		} else {
			cluster.replicatedTasksCounter ++;
		}

		doneJob.runtimes.put(clusterName, new Double(received.getStats().getRuntime()/1000000000)) ;
		doneJob.done = true;

		bot.finishedTasks.add(doneJob);

		workers.get(clusterName).get(node).addJobStats(received.getStats().getRuntime());

		//decideReferenceCluster();

		return findNextJob(cluster,from);		
	}

	private void decideReferenceCluster() {		
		if(selectedReferenceCluster == false) {	
			/*if this is the last regression point to be executed on this cluster
			 * this cluster should become reference
			 * replace later by better condition, since some clusters might start 
			 * somewhat later, though workers are faster, hence having a handicap
			 * which translates in selection of "wrong" reference cluster; also,
			 * if we do not have the same number of initial workers on each
			 * cluster, the current condition becomes wrong*/
			Double minRT = Double.MAX_VALUE;
			Cluster ref = null;
			for(Cluster cluster:bot.Clusters.values()) {
				if(cluster.replicatedTasksCounter != bot.noReplicatedJobs) {
					return;
				} else {
					if(replicatedTasks.get(0).runtimes.get(cluster.alias).doubleValue() < minRT) {
						minRT = replicatedTasks.get(0).runtimes.get(cluster.alias).doubleValue();
						ref = cluster;
					} else if(replicatedTasks.get(0).runtimes.get(cluster.alias).doubleValue() == minRT) {
						if(ref.costUnit > cluster.costUnit) {
							ref = cluster;
						}
					}
				}
			}

			ref.isReferenceCluster = true;
			selectedReferenceCluster = true; 
		}
	}

	private Job findNextJob(Cluster cluster, IbisIdentifier from) {
		String clusterName = cluster.alias;
		String node = from.location().getLevel(0);

		Job nextJob = null;
		if(cluster.regressionPoints.size() < bot.noReplicatedJobs) {
			/*should select next unsubmitted task, to deal with failed replicated jobs*/
			nextJob = replicatedTasks.get(cluster.regressionPoints.size());
			cluster.regressionPoints.put(nextJob.jobID, nextJob);			
		} else {
			/*	if(cluster.isReferenceCluster && 
		      (cluster.samplingPoints.size() < bot.noSampleJobs-bot.noReplicatedJobs)) {*/
			if(totalSamplingSubmittedCounter < bot.noSampleJobs-bot.noReplicatedJobs) {

				nextJob = bot.tasks.remove(random.nextInt(bot.tasks.size()));
				cluster.samplingPoints.put(nextJob.jobID, nextJob);
				totalSamplingSubmittedCounter ++;
			} else {
				WorkerStats ws = workers.get(clusterName).get(node);
				long timeLeftATU = cluster.timeUnit*60000 - ws.getUptime()%(cluster.timeUnit*60000) 
									- 60000;
				//System.out.println("timeLeftATU = " + timeLeftATU);
				if(timeLeftATU > 0) {
					try{
						nextJob = bot.tasks.remove(random.nextInt(bot.tasks.size()));
						cluster.extraPoints.put(nextJob.jobID, nextJob);
						ws.setTimeLeftATU(timeLeftATU);
						terminateWorker(cluster, ws, " sampling finished, end of current ATU");
					
					} catch(Exception e){
						if(bot.tasks.size() == 0) {
							System.out.println("Out of tasks");
							return sayGB(from);
						} else {
							System.err.println("Unknown error in sampling: ");
							e.getLocalizedMessage();
						}
					}
				} else {
					return sayGB(from);
				}
			}
		}
		return nextJob;
	}

	public void terminateWorker(Cluster cluster, WorkerStats ws, String reason) {
		long crtTime=0;		
		TimerTask tt = null;
		crtTime= System.currentTimeMillis();
		tt = new MyTimerTask(cluster, ws.getIbisIdentifier(), myIbis);
		timer.schedule(tt,ws.timeLeftATU);

	}
	
	
	private Job sayGB (IbisIdentifier to) {

		System.err.println("We say goodbye to " + to.location().toString());

		String cluster = to.location().getParent().toString();
		String node = to.location().getLevel(0);
		workers.get(cluster).get(node).workerFinished(System.currentTimeMillis());
		workers.get(cluster).get(node).setLatestJobStartTime(0);
		bot.Clusters.get(cluster).setCrtNodes(bot.Clusters.get(cluster).getCrtNodes()-1);
		return new NoJob();
	}

	@Override
	protected void handleLostConnections() {
		String clusterName;
		String node;
		Cluster cluster;  
		for(SendPortIdentifier lost : masterRP.lostConnections()) {

			cluster = bot.Clusters.get(lost.ibisIdentifier().location().getParent().toString());
			clusterName = cluster.alias;
			node = lost.ibisIdentifier().location().getLevel(0);
			if(! workers.get(clusterName).get(node).isFinished()) {
				String jobID = findFailedJob(clusterName,node);
				workers.get(clusterName).get(node).workerFinished(System.currentTimeMillis());
				cluster.setCrtNodes(cluster.getCrtNodes()-1);
			}
		}

	}

	@Override
	public void run() {

		boolean undone = true;
		timeout = (long) (BoTRunner.INITIAL_TIMEOUT_PERCENT * bot.deadline * 60000);
		System.err.println("Timeout is now " + timeout);

		long actualStartTime = System.currentTimeMillis();

		while (undone) {
			try {
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
				String clusterName = cfe.ibisIdentifier().location().getParent().toString();	
				Cluster cluster = bot.Clusters.get(clusterName);
				String node = cfe.ibisIdentifier().location().getLevel(0);
				String jobID = findFailedJob(clusterName,node); 
				workers.get(clusterName).get(node).workerFinished(System.currentTimeMillis());
				cluster.setCrtNodes(cluster.getCrtNodes()-1);
				System.err.println("Node " + cfe.ibisIdentifier().location().toString() + 
						" failed before receiving job " + jobID);	
			} catch (IOException ioe) {									
				ioe.printStackTrace();
				undone = ! areWeDone();
			} catch (ClassNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}

		//select last cluster as base for sampling points normalization,

		ArrayList<Cluster> clusterList = new ArrayList<Cluster>(bot.Clusters.values()); 
		int baseIndex = clusterList.size()-1;
		Cluster base = clusterList.get(baseIndex);
		base.isReferenceCluster = true;
		base.beta0 = 0;
		base.beta1 = 1;

		for(int i=0; i < baseIndex; i++) {						
			Cluster cluster = clusterList.get(i);
			cluster.linearRegression(base);
			for(Job j : cluster.samplingPoints.values()) {
				double t = j.runtimes.get(cluster.alias).doubleValue();
				double tbase = (t-cluster.beta0)/cluster.beta1;
				j.runtimes.put(base.alias,new Double(tbase));
				base.samplingPoints.put(j.jobID, j);
				base.samplingPointsCounter ++;
			}
			System.out.println("cluster " + cluster.alias + ": beta1=" + cluster.beta1
					+ ", beta0=" + cluster.beta0);
		}

		base.estimateX();
		base.estimateTi();

		for(Job j : base.samplingPoints.values()) {
			double tbase = j.runtimes.get(base.alias).doubleValue();			
			base.noDoneJobs ++;
			base.totalRuntimeSampleJobs += tbase;
			base.totalRuntimeDoneJobs += tbase;
			base.orderedSampleResultsSet.add(new JobResult(j.jobID,new JobStats((long)tbase*1000000000L)));
		}
		for(Job j : base.regressionPoints.values()) {
			double tbase = j.runtimes.get(base.alias).doubleValue();
			base.samplingPoints.put(j.jobID, j);
			base.samplingPointsCounter ++;
			base.noDoneJobs ++;
			base.totalRuntimeSampleJobs += tbase;
			base.totalRuntimeDoneJobs += tbase;
			base.orderedSampleResultsSet.add(new JobResult(j.jobID,new JobStats((long)tbase*1000000000L)));
		}
		for(Job j : base.extraPoints.values()) {
			double tbase = j.runtimes.get(base.alias).doubleValue();			
			base.noDoneJobs ++;    		
			base.totalRuntimeDoneJobs += tbase;    		
		}
		System.out.println("cluster " + base.alias + " has " + base.samplingPointsCounter + " samples;" 
				+ " size of sampling points array is " + base.samplingPoints.size());

		System.out.println("base cluster is " + base.alias + ": mean=" + base.meanX 
				+ ", variance=" + base.varXsq);

		for(Cluster cluster : bot.Clusters.values()) {	
			if(!cluster.isReferenceCluster) {				
				cluster.estimateX(base);
				cluster.estimateTi(base);
				for(Job j : base.samplingPoints.values()) {
					double tbase = j.runtimes.get(base.alias).doubleValue();
					double t = tbase*cluster.beta1 + cluster.beta0;
					j.runtimes.put(cluster.alias,new Double(t));
					if(cluster.samplingPoints.put(j.jobID, j) == null) 	cluster.samplingPointsCounter ++;
					cluster.noDoneJobs ++;
					cluster.totalRuntimeSampleJobs += t;
					cluster.totalRuntimeDoneJobs += t;
					cluster.orderedSampleResultsSet.add(new JobResult(j.jobID,new JobStats((long)t*1000000000L)));
				}
				for(Job j : cluster.extraPoints.values()) {
					double t = j.runtimes.get(cluster.alias).doubleValue();			
					cluster.noDoneJobs ++;    		
					cluster.totalRuntimeDoneJobs += t;    		
				}
				System.out.println("cluster " + cluster.alias + " has " + cluster.samplingPointsCounter + " samples;" 
						+ " size of sampling points array is " + cluster.samplingPoints.size());
				System.out.println("cluster " + cluster.alias + ": mean=" + cluster.meanX + ", variance=" + cluster.varXsq +
						", beta1=" + cluster.beta1 + ", beta0=" + cluster.beta0);
			}
		}

		double price = 0;
		for (Cluster cluster : bot.Clusters.values()) {
			Collection<WorkerStats> wss = workers.get(cluster.alias).values();					
			System.out.println("Cluster " + cluster.alias + " stats =>");
			for (WorkerStats ws : wss) {
				ws.printStats();
				price += Math.ceil((double)ws.getUptime() / 60000 / cluster.timeUnit) * cluster.costUnit;
				System.out.println("Unused fraction of ATU: " + 
						(Math.ceil((double)ws.getUptime() / 60000 / cluster.timeUnit)* cluster.timeUnit*60000 
						 - ws.getUptime()%(cluster.timeUnit*60000)));
			}			
		}

		System.out.println("Due amount sampling " + price);
		sampleCost = price;
		long totalTime = (System.currentTimeMillis()-actualStartTime)/1000;
		sampleMakespan = totalTime;
		System.out.println("Sampling phase took " + totalTime + " (sec), which is about " + totalTime/60 + "m" + totalTime%60 +"s");

		Cluster mostProfitable = selectMostProfitable();		

		System.out.println("Most profitable machine type: " + mostProfitable.alias 
				+ ", cost: " + mostProfitable.costUnit + ", Ti: " + mostProfitable.Ti + " minutes");

		for (Cluster cluster : bot.Clusters.values()) {
			cluster.computeJobsPerATU();
		}

		System.out.println(" Solutions follow ");
		System.out.println("\tB\tC\tM");

		int jobsLeft = bot.tasks.size();
		double makespanBmin = Math.ceil((jobsLeft*mostProfitable.Ti)/bot.timeUnit);
		double Bmin = makespanBmin*mostProfitable.costUnit;

		double maxSpeed = 0.0;
		long costMaxSpeed = 0;

		System.out.println("1.\t"+Bmin+"\t"+Bmin+"\t"+makespanBmin);

		ArrayList<Item> items = new ArrayList<Item>();
		items.add(new Item(0,0,""));
		for(Cluster cluster : bot.Clusters.values()) {
			for(int i=0;i<cluster.maxNodes;i++)		
				items.add(new Item(1/cluster.Ti,
						(int) cluster.costUnit,
						cluster.alias));
			maxSpeed += (double) (cluster.maxNodes / cluster.Ti);
			costMaxSpeed += cluster.maxNodes * cluster.costUnit;
		}

		double makespanMin = Math.ceil((jobsLeft/maxSpeed)/bot.timeUnit);
		double BmakespanMin = makespanMin * costMaxSpeed;

		System.out.println("---------------------");
		// selectedSchedule = 0;
		Knapsack mooCheapest = new Knapsack(items.toArray(new Item[0]),
				(long)Bmin, jobsLeft, bot.minCostATU,
				bot.maxCostATU,(int)bot.timeUnit);		
		HashMap<String, Integer> cheapestSol = mooCheapest.findSol();
		int aini = 0;
		for (Cluster cluster : bot.Clusters.values()) {
			if(cheapestSol.get(cluster.alias) != null) 
				aini += cheapestSol.get(cluster.alias).intValue()* Math.floor(mooCheapest.noATUPlan*bot.timeUnit/cluster.Ti);
		}
		int deltaN = jobsLeft - aini;
		int x = 0;		
		boolean success = true;

		while(deltaN > 0) {
			System.out.println("deltaN=" + deltaN);
			deltaN = 0;
			x ++;
			System.out.println("adding 1 procent extra, x=" + x);						

			mooCheapest = new Knapsack(items.toArray(new Item[0]),
					(long)Math.ceil(Bmin+(double)(x*Bmin/100)), jobsLeft, bot.minCostATU,					
					bot.maxCostATU,(int)bot.timeUnit);			
			cheapestSol = mooCheapest.findSol();
			aini = 0;
			for (Cluster cluster : bot.Clusters.values()) {
				if(cheapestSol.get(cluster.alias) != null)
					aini += cheapestSol.get(cluster.alias).intValue()* Math.floor(mooCheapest.noATUPlan*bot.timeUnit/cluster.Ti);
			}
			deltaN = jobsLeft - aini;
			if ((long)Math.ceil(Bmin+(double)(x*Bmin/100)) > BmakespanMin) {
				System.out.println("Can't find cheap schedule!");
				success = false;
				break;
			}
		}		

		System.out.println("deltaN=" + deltaN);

		double BminN = Math.ceil(Bmin+(double)(x*Bmin/100));
		schedules.add(new Schedule((long)BminN,mooCheapest.costPlan,mooCheapest.noATUPlan, cheapestSol));

		System.out.println("2.\t" + BminN + "\t" + mooCheapest.costPlan + "\t" + mooCheapest.noATUPlan);

		if(x < 10) {
			System.out.println("---------------------");
			// selectedSchedule=1;
			long BminPlus10 = (long)(Bmin*1.1); 
			Knapsack mooCheapestPlus10 = new Knapsack(items.toArray(new Item[0]),
					BminPlus10 , jobsLeft, bot.minCostATU,
					bot.maxCostATU,(int)bot.timeUnit);
			HashMap<String, Integer> cheapestPlus10Sol = mooCheapestPlus10.findSol();
			schedules.add(new Schedule(BminPlus10, mooCheapestPlus10.costPlan, mooCheapestPlus10.noATUPlan, cheapestPlus10Sol));
			System.out.println("3.\t" + BminPlus10 + "\t" + mooCheapestPlus10.costPlan + "\t" + mooCheapestPlus10.noATUPlan);
		}
		if (x < 20) {
			System.out.println("---------------------");
			// selectedSchedule=2
			long BminPlus20 = (long)(Bmin*1.2); 
			Knapsack mooCheapestPlus20 = new Knapsack(items.toArray(new Item[0]),
					BminPlus20 , jobsLeft, bot.minCostATU,
					bot.maxCostATU,(int)bot.timeUnit);
			HashMap<String, Integer> cheapestPlus20Sol = mooCheapestPlus20.findSol();
			schedules.add(new Schedule(BminPlus20, mooCheapestPlus20.costPlan, mooCheapestPlus20.noATUPlan, cheapestPlus20Sol));
			System.out.println("4.\t" + BminPlus20 + "\t" + mooCheapestPlus20.costPlan + "\t" + mooCheapestPlus20.noATUPlan);
		}


		System.out.println("---------------------");
		// selectedSchedule=3

		System.out.println("Initial BmakespanMin=" + BmakespanMin + "; initial makespanMin=" + makespanMin);

		Knapsack mooFastest = new Knapsack(items.toArray(new Item[0]),
				(long)BmakespanMin, jobsLeft, bot.minCostATU,
				bot.maxCostATU,(int)bot.timeUnit);
		HashMap<String, Integer> fastestSol = mooFastest.findSol();

		aini = 0;
		for (Cluster cluster : bot.Clusters.values()) {
			if(fastestSol.get(cluster.alias) != null) 
				aini += fastestSol.get(cluster.alias).intValue()* Math.floor(mooFastest.noATUPlan*bot.timeUnit/cluster.Ti);
		}
		deltaN = jobsLeft - aini;
		x = 0;		
		long BdeltaN = 0;
		if(deltaN > 0) {
			System.out.println("deltaN=" + deltaN);
			ArrayList<Cluster> orderedByJobsPerATU = new ArrayList<Cluster>(bot.Clusters.values());
			Collections.sort(orderedByJobsPerATU, new Comparator<Cluster>(){
				public int compare(Cluster a, Cluster b) {
					return a.ni - b.ni;
				}
			});

			int leftDeltaN = deltaN;			
			for(int i=orderedByJobsPerATU.size()-1; i>=0; i--) {
				if(leftDeltaN > orderedByJobsPerATU.get(i).maxNodes) {
					BdeltaN += (long) orderedByJobsPerATU.get(i).maxNodes*orderedByJobsPerATU.get(i).costUnit;
					leftDeltaN -= orderedByJobsPerATU.get(i).maxNodes;
				} else {
					BdeltaN += (long) leftDeltaN*orderedByJobsPerATU.get(i).costUnit;
					leftDeltaN=0;
					break;
				}
			}
		}		

		schedules.add(new Schedule((long)BmakespanMin, (long) BdeltaN, deltaN, mooFastest.costPlan, mooFastest.noATUPlan, fastestSol));
		System.out.println("5.\t" + BmakespanMin + "\t" + mooFastest.costPlan + "\t" + mooFastest.noATUPlan);	

		System.out.println("---------------------");

		//selectedSchedule=4
		long BmakespanMinMinus10 = (long) (BmakespanMin*0.9);
		Knapsack mooFastestMinus10 = new Knapsack(items.toArray(new Item[0]),
				BmakespanMinMinus10, jobsLeft, bot.minCostATU,
				bot.maxCostATU,(int)bot.timeUnit);
		HashMap<String, Integer> fastestMinus10Sol = mooFastestMinus10.findSol();
		schedules.add(new Schedule((long)BmakespanMinMinus10, mooFastestMinus10.costPlan, mooFastestMinus10.noATUPlan, fastestMinus10Sol));
		System.out.println("6.\t" + BmakespanMinMinus10 + "\t" + mooFastestMinus10.costPlan + "\t" + mooFastestMinus10.noATUPlan);

		System.out.println("---------------------");

		//selectedSchedule=5		

		double BmakespanMinMinus20 = BmakespanMin*0.8;

		Knapsack mooFastestMinus20 = new Knapsack(items.toArray(new Item[0]),
				(long)BmakespanMinMinus20, jobsLeft, bot.minCostATU,
				bot.maxCostATU,(int)bot.timeUnit);
		HashMap<String, Integer> fastestMinus20Sol = mooFastestMinus20.findSol();


		aini = 0;
		for (Cluster cluster : bot.Clusters.values()) {
			if(fastestMinus20Sol.get(cluster.alias) != null) 
				aini += fastestMinus20Sol.get(cluster.alias).intValue()* Math.floor(mooFastestMinus20.noATUPlan*bot.timeUnit/cluster.Ti);
		}
		deltaN = jobsLeft - aini;

		/*	
		long BdeltaNBmakespanMinMinus20 = 0;
		if(deltaN > 0) {
			System.out.println("deltaN=" + deltaN);
			ArrayList<Cluster> orderedByJobsPerATU = new ArrayList<Cluster>(bot.Clusters.values());
			Collections.sort(orderedByJobsPerATU, new Comparator<Cluster>(){
				public int compare(Cluster a, Cluster b) {
					return a.ni - b.ni;
				}
			});

			int leftDeltaN = deltaN;			
			for(int i=orderedByJobsPerATU.size()-1; i>=0; i--) {
				if(leftDeltaN > orderedByJobsPerATU.get(i).maxNodes) {
					BdeltaNBmakespanMinMinus20 += (long) orderedByJobsPerATU.get(i).maxNodes*orderedByJobsPerATU.get(i).costUnit;
					leftDeltaN -= orderedByJobsPerATU.get(i).maxNodes;
				} else {
					BdeltaNBmakespanMinMinus20 += (long) leftDeltaN*orderedByJobsPerATU.get(i).costUnit;
					leftDeltaN=0;
					break;
				}
			}
		}
		 */
		long Bthreshold = (long) (BmakespanMinMinus10);		
		success = true;
		x = 0;	
		while(deltaN > 0) {
			System.out.println("deltaN=" + deltaN);
			deltaN = 0;
			x ++;
			System.out.println("adding 1 procent extra, x=" + x);						

			mooFastestMinus20 = new Knapsack(items.toArray(new Item[0]),
					((long) Math.ceil(BmakespanMin*(0.8+(double)x/100))), jobsLeft, bot.minCostATU,							
					bot.maxCostATU,(int)bot.timeUnit);			
			fastestMinus20Sol = mooFastestMinus20.findSol();
			aini = 0;
			for (Cluster cluster : bot.Clusters.values()) {
				if(fastestMinus20Sol.get(cluster.alias) != null)
					aini += fastestMinus20Sol.get(cluster.alias).intValue()* Math.floor(mooFastestMinus20.noATUPlan*bot.timeUnit/cluster.Ti);
			}
			deltaN = jobsLeft - aini;
			if (((long) Math.ceil(BmakespanMin*(0.8+(double)x/100))) > Bthreshold) {
				System.out.println("Can't find 20% off fastest schedule by incrementing!");
				System.out.println("Schedule risky!");
				success = false;
				break;
			}
		}		

		if(success){
			BmakespanMinMinus20 =  Math.ceil(BmakespanMin*(0.8+(double)x/100));
		} else {
			mooFastestMinus20 = new Knapsack(items.toArray(new Item[0]),
					(long)BmakespanMinMinus20, jobsLeft, bot.minCostATU,
					bot.maxCostATU,(int)bot.timeUnit); 
			fastestMinus20Sol = mooFastestMinus20.findSol();
		}

		schedules.add(new Schedule((long)BmakespanMinMinus20, mooFastestMinus20.costPlan, mooFastestMinus20.noATUPlan, fastestMinus20Sol));
		System.out.println("7.\t" + BmakespanMinMinus20 + "\t" + mooFastestMinus20.costPlan + "\t" + mooFastestMinus20.noATUPlan);

		timer.cancel();

		try {
			masterRP.close();
			System.out.println("Hurray! I shut down masterRP!!!");
			myIbis.end();
			System.out.println("Hurray! I shut down ibis!!!");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		System.out.println("For me:");
		System.out.println("Finished tasks: " + bot.finishedTasks.size());
		System.out.println("Replicated tasks: " + this.replicatedTasks.size());
		System.out.println("Remaining tasks: " + bot.tasks.size());
		dumpSchedules();
		System.out.println("Shuting down...");

		// and now quit... is there something i should do?
		// some shutdowns?!?!

		/*      This is not required anymore.
		 *      It's implemented in the Executor class.
		 * 
            //Add user selection input

		int selectedSchedule = 3;

		Master master = null;
		int whichMaster = 2;
		try {
			if(whichMaster == 0) {
				master = new ExecutionPhaseRRMaster(bot, schedules.get(selectedSchedule));
			} else if (whichMaster == 1) {
				master = new ExecutionPhaseMaster(bot, schedules.get(selectedSchedule));
			} else if (whichMaster == 2) {
				master = new ExecutionTailPhaseMaster(bot, schedules.get(selectedSchedule));
			}
		} catch (Exception e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		try {
			master.initMasterComm();

			//start workers, assuming format for reservation time interval "dd:hh:mm:00"
			master.startInitWorkers();

			master.run();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		 */
	}

	/*
	 * Dumps the schedules in "dump.ser" file.
	 * further comments: should be put in Master.java
	 */
	private void dumpSchedules() {
		try {
            String fileName;
            if(new File(bot.schedulesFile).isAbsolute()) {
                fileName = bot.schedulesFile;
            } else {
                fileName = BoTRunner.path + "/" + bot.schedulesFile;
            }
            
            File dirs = new File(fileName.substring(0, fileName.lastIndexOf('/')));
            dirs.mkdirs();
            
            File file = new File(fileName);
            file.createNewFile();
            
            FileOutputStream fos = new FileOutputStream(file);
            ObjectOutputStream oos = new ObjectOutputStream(fos);
            // don't write all the tasks. just the ones completed.
            // they are already stored in bot.finishedTasks;
            // clear the bag full of remaining tasks
            bot.bag.cleanup();
            oos.writeObject(bot);
            oos.writeObject(schedules);
            fos.close();
            System.out.println("Schedules and BoT dumped to file: " + fileName);
        } catch (IOException ex) {
            throw new RuntimeException("Failed to save to file the computed schedules.\n" + ex);
        }
	}

	private Cluster orderFastestPerATU() {
		// TODO Auto-generated method stub
		return null;
	}

	private Cluster selectMostProfitable() {
		// TODO Auto-generated method stub
		Cluster mostProfitable = null;
		Cluster cheapest = findCheapest();
		double profitMax = Double.MIN_VALUE;
		for(Cluster cluster : bot.Clusters.values()) {
			cluster.computeProfitability(cheapest);
			if(cluster.profitability > profitMax) {
				profitMax = cluster.profitability;
				mostProfitable = cluster;
			}
		}
		return mostProfitable;
	}

	private void decide() {		

	}

	private String findFailedJob(String clusterName, String node) {

		Cluster cluster = bot.Clusters.get(clusterName);
		String jobId = null;
		for(Job j : cluster.extraPoints.values()) {
			if ((!j.done) && (j.getNode().compareTo(node)==0)) {
				jobId = j.getJobID();
				cluster.extraPoints.remove(j.getJobID());
				bot.tasks.add(j);
				System.err.println("Node " + node + " in cluster " + clusterName + 
						" failed to execute (extra point) job " + jobId);
				break;
			}
		}
		if(jobId == null) {
			for(Job j : cluster.samplingPoints.values()) {
				if ((!j.done) && (j.getNode().compareTo(node)==0)) {
					jobId = j.getJobID();
					cluster.samplingPoints.remove(j.getJobID());
					bot.tasks.add(j);
					System.err.println("Node " + node + " in cluster " + clusterName + 
							" failed to execute (sampling point) job " + jobId);
					break;
				}
			}
			if(jobId == null) {
				for(Job j : cluster.regressionPoints.values()) {
					if ((!j.done) && (j.getNode().compareTo(node)==0)) {
						jobId = j.getJobID();
						cluster.regressionPoints.remove(j.getJobID());
						System.err.println("Node " + node + " in cluster " + clusterName + 
								" failed to execute (regression point) job " + jobId);
						break;
					}
				}
			}
		}
		return jobId;
	}

	@Override
	public void startInitWorkers() {

		Collection<Cluster> clusters = bot.Clusters.values();
		for (Cluster c : clusters) {
			System.err
			.println("BoTRunner has found " + bot.tasks.size()
					+ " jobs; will send " + bot.noReplicatedJobs
					+ " to " + c.pendingNodes
					+ " initial workers on cluster " + c.alias);
			Process p = c.startNodes(/* deadline2ResTime() */"4:45:00",
					c.pendingNodes, bot.electionName,
					bot.poolName, bot.serverAddress);

			// sshRunners.put(c.alias, p);
		}
	}

	public double getSampleCost() {
		return sampleCost;
	}

	public long getSampleMakespan() {
		return sampleMakespan;
	}
}
