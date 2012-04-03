package org.koala.runnersFramework.runners.bot;

import ibis.ipl.Ibis;
import ibis.ipl.IbisIdentifier;
import java.io.IOException;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;

public abstract class Cluster implements Serializable {
	String hostname;
	public String alias;
	double costUnit;
	long timeUnit;
	int maxNodes;	
	int crtNodes;
	int necNodes;
	int prevNecNodes;
	int pendingNodes;
	/*expressed in minutes*/
	double Ti;
	public boolean firstStats;
	public double prevTi;
	public int timestamp;
	
	public double profitability = 0.0;
	
	public HashMap<String,Job> regressionPoints;
	public int replicatedTasksCounter = 0;
	
	public HashMap<String,Job> samplingPoints;
	public int samplingPointsCounter = 0;
	public boolean isReferenceCluster = false;
	public HashMap<String,Job> extraPoints;
	
	/*regression and extrapolation*/
	double meanX, varXsq; /*expressed in seconds*/
	double beta0, beta1; /*a-dimensional*/
	
	/*moving average*/
	public HashMap<String,Job> subsetJobs;
	public ArrayList<JobResult> orderedSampleResultsSet;
	long totalRuntimeDoneJobs; //expressed in seconds
	long totalRuntimeSampleJobs; //expressed in seconds
	int noDoneJobs;
	double initialTi;
	int noATUPlan;
	protected int ni;
        
        /* variable for testing purposes */
        String speedFactor;
 	
	public Cluster(String hostname, String alias, long timeUnit, double costUnit,
			int maxNodes, String speedFactor) {
		
		this.hostname = hostname;
		this.alias = alias;
		this.costUnit = costUnit;
		this.timeUnit = timeUnit;
		this.maxNodes = maxNodes;
                this.speedFactor = speedFactor;
		this.Ti = 0.0;
		this.prevTi = 0.0;  
		timestamp=0;
		firstStats = false;
		regressionPoints = new HashMap<String,Job>();
		samplingPoints = new HashMap<String,Job>();
		extraPoints = new HashMap<String,Job>();
		subsetJobs = new HashMap<String,Job>();
		orderedSampleResultsSet = new ArrayList<JobResult>();
		noDoneJobs = 0;
		initialTi=0.0;
		this.totalRuntimeDoneJobs = 0;
		this.totalRuntimeSampleJobs = 0;
		System.out.println("time unit: " + timeUnit + "; cost per time unit: " + costUnit);
	}

	public int getPendingNodes() {
		return pendingNodes;
	}

	public void setPendingNodes(int pendingNodes) {
		this.pendingNodes = pendingNodes;
	}

	public int getMaxNodes() {
		return maxNodes;
	}

	public void setMaxNodes(int maxNodes) {
		this.maxNodes = maxNodes;
	}

	public int getCrtNodes() {
		return crtNodes;
	}

	public void setCrtNodes(int crtNodes) {
		this.crtNodes = crtNodes;
	}

	public int getNecNodes() {
		return necNodes;
	}

	public void setNecNodes(int necNodes) {
		this.necNodes = necNodes;
	}


	public abstract Process startWorkers(String time, int noWorkers, 
			String electionName, String poolName, String serverAddress);

	public void linearRegression(Cluster reference) {
		
		double sumX = 0.0;
		double sumY = 0.0;
		
		for (Job j : regressionPoints.values()) {
			sumY += j.runtimes.get(alias).doubleValue();
			sumX += reference.regressionPoints.get(j.jobID).runtimes.get(reference.alias).doubleValue();			
		}
		
		double xBar = sumX / regressionPoints.size();
		double yBar = sumY / regressionPoints.size();
		
		double sumProdVars = 0.0;
		double sumvarXsq = 0.0;
		
		for (Job j : regressionPoints.values()) {
			sumProdVars += (reference.regressionPoints.get(j.jobID).runtimes.get(reference.alias).doubleValue()	- xBar) 
							* (j.runtimes.get(alias).doubleValue() - yBar);
			sumvarXsq += Math.pow(reference.regressionPoints.get(j.jobID).runtimes.get(reference.alias).doubleValue() - xBar, 2);
		}
		
		beta1 = sumProdVars / sumvarXsq;
		beta0 = yBar - beta1*xBar;
	
	}
			
	public void estimateX() {
		
		double sumX = 0.0;
		double sumvarsq = 0.0;
		for (Job j : regressionPoints.values()) {
			sumX += j.runtimes.get(alias).doubleValue();
		}
		for (Job j : samplingPoints.values()) {
			sumX += j.runtimes.get(alias).doubleValue();
		}
		meanX = sumX / (regressionPoints.size() + samplingPoints.size());
		
		for (Job j : regressionPoints.values()) {
			sumvarsq += Math.pow(j.runtimes.get(alias).doubleValue()-meanX, 2);
		}		
		for (Job j : samplingPoints.values()) {
			sumvarsq += Math.pow(j.runtimes.get(alias).doubleValue()-meanX, 2);
		}
		varXsq = sumvarsq / (regressionPoints.size() + samplingPoints.size());
	}
	  
    public void estimateX(Cluster reference) {

    	meanX = beta0 + beta1 * reference.meanX;
		varXsq = beta1*beta1*reference.varXsq;

    }
    
    public void estimateTi() {
    	Ti = meanX/60;    	
    }
    
    public void estimateTi(Cluster reference) {
    	
    	Ti = (beta1*reference.meanX + beta0)/60;
    }
    
    public void computeProfitability(Cluster cheapest) {
		profitability = (cheapest.Ti * cheapest.costUnit) / (Ti * costUnit); 
	}
    
    public void computeJobsPerATU() {
    	ni = (int)Math.floor(timeUnit/Ti);
    }
    
    /*needed by SampleFreeMaster*/
    
    public void doneJob(JobResult jobRes) {
    	if(samplingPoints.containsKey(jobRes.getJobID())) {
    		samplingPointsCounter ++;
    		this.totalRuntimeSampleJobs += jobRes.getStats().getRuntime()/1000000000L;
    		orderedSampleResultsSet.add(jobRes);
    	}
    	subsetJobs.remove(jobRes.getJobID());
    	noDoneJobs ++;
    	this.totalRuntimeDoneJobs += jobRes.getStats().getRuntime()/1000000000L;
    }
    
    public void sampleSetDone() {    	
    	initialTi=(double)totalRuntimeSampleJobs/samplingPointsCounter/60;
    	Collections.sort(orderedSampleResultsSet, new Comparator<JobResult>(){
			public int compare(JobResult a, JobResult b) {
				long tmp = a.getStats().getRuntime() - b.getStats().getRuntime();
				if(tmp < 0) return -1;
				if(tmp==0) return 0;
				return 1;
			}
		});
    }
    
    public void updateTi() {
    	double avg = 0.0;
    	long crtTime = System.nanoTime();
    	for(Job j : subsetJobs.values()) {    		
    		avg += estimateIntermediary(crtTime - j.startTime);
    	}
    	avg /=1000000000L; 
    	prevTi = Ti;
    	Ti = ((double)avg + this.totalRuntimeDoneJobs)/(subsetJobs.size()+noDoneJobs)/60;
    	System.out.println("initialTi="+ initialTi +"; Ti=" + Ti + "; avg=" + avg);
    }
    
    public double estimateIntermediary(long interm) {
    	long estimate = 0;
    	int counter = 0;
    	/*very inefficient, why bother ordering if i still do a for each jobResult*/
    	for(JobResult jres : orderedSampleResultsSet) {
			if(jres.getStats().getRuntime()>interm) {
			  estimate += jres.getStats().getRuntime();
			  counter ++;
			}
		}
    	if(counter != 0) return (double)estimate/counter;
    	return 1.0*interm;
    }

    public double estimateExecutionTime(long sofar) {
    	double estimate = 0;
    	/*bebe's formula*/
    	if(sofar < meanX*1000000000L) estimate=meanX*1000000000L;
    	else {
    		estimate = meanX*1000000000L + Math.sqrt(2*varXsq/Math.PI);
    	}
    	return estimate;
    }

	public double convertExecutionTime(Cluster targetC,
			double estimatedTETSource) {
		/*transform using beta-s*/
		double estimate = 0;
		estimate = targetC.beta1 / this.beta1 * estimatedTETSource + targetC.beta0 - targetC.beta1 * this.beta0 / this.beta1;
		return estimate;
	}

	public Job getJob(JobResult received) {		
		Job result = subsetJobs.get(received.getJobID());
		return result;
	}
        
        abstract public void terminateWorker(IbisIdentifier from, Ibis myIbis)
                throws IOException;
}


