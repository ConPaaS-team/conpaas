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
	String alias;
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
 	
	public Cluster(String hostname, String alias, long timeUnit, double costUnit,
			int maxNodes) {
		
		this.hostname = hostname;
		this.alias = alias;
		this.costUnit = costUnit;
		this.timeUnit = timeUnit;
		this.maxNodes = maxNodes;
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


	public abstract Process startNodes(String time, int noNodes, 
			String electionName, String poolName, String serverAddress);

	public abstract void terminateNode(IbisIdentifier from, Ibis myIbis)
            throws IOException;
	
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

    // return phi(x) = standard Gaussian pdf
    private double phi(double x) {
        return Math.exp(-x*x / 2) / Math.sqrt(2 * Math.PI);
    }
    
    // return Phi(z) = standard Gaussian cdf using Taylor approximation
    private double Phi(double z) {
        if (z < -8.0) return 0.0;
        if (z >  8.0) return 1.0;
        double sum = 0.0, term = z;
        for (int i = 3; sum + term != sum; i += 2) {
            sum  = sum + term;
            term = term * z * z / i;
        }
        return 0.5 + sum * phi(z);
    }
    
    private double erfc(double x) {
    	return 2*Phi(-Math.sqrt(2)*x);
    }
    
    private double logGamma(double x) {
        double tmp = (x - 0.5) * Math.log(x + 4.5) - (x + 4.5);
        double ser = 1.0 + 76.18009173    / (x + 0)   - 86.50532033    / (x + 1)
                         + 24.01409822    / (x + 2)   -  1.231739516   / (x + 3)
                         +  0.00120858003 / (x + 4)   -  0.00000536382 / (x + 5);
        return tmp + Math.log(ser * Math.sqrt(2 * Math.PI));
     }
    
    private double gamma(double x) { return Math.exp(logGamma(x)); }
    
    public double estimateExecutionTime(long sofar) {
    	
    	int whichD = 2;  
    	if(whichD==0)
    		return estimateExecutionTimeND(sofar);
    	else if(whichD == 1)
    		return estimateExecutionTimeSD(sofar);
    	else if(whichD == 2)
    		return estimateExecutionTimeSDLT(sofar);
    	else if(whichD == 3)
    		return estimateExecutionTimeLN(sofar);
    	else return 0;
    }
    
    private double estimateExecutionTimeND(long sofar) {    	
    	double theta = (double)sofar/1000000000L;
    	double estimate = 0;
    	/*bebe's formula*/
    	System.out.println("Predict ND: Elapsed time: " + theta);
    	/*should always use the theta formula*/
    	/*if(theta < meanX) estimate=meanX;
    	else {*/
    		estimate = meanX + 
    		Math.sqrt(varXsq/(2*Math.PI))*
    		Math.exp(-(theta-meanX)*(theta-meanX)/(2*varXsq))/
    		(1-Phi((theta-meanX)/Math.sqrt(varXsq)));
    	//}
    	return estimate;
    }

    private double estimateExecutionTimeSD(long sofar) {    	
    	double alpha = 1.5; /*should be computed through MLE, just like varXsq*/
    	double estimate = 0;
    	double theta = (double)sofar/1000000000L;
    	/*bebe's formula*/
    	System.out.println("Predict SD: Elapsed time: " + theta);
    	/*should use a different formula for theta<meanX*/
    	if(theta < meanX) estimate=meanX;
    	else {
    		estimate = meanX + 2*Math.sqrt(varXsq) / (alpha*gamma(1+1/alpha)*Math.sin(Math.PI/alpha));
    	}
    	return estimate;
    }
    
    private double estimateExecutionTimeSDLT(long sofar) {    	
    	//double alpha = 0.5; /*should be computed through MLE, just like varXsq*/
    	double estimate = 0;
    	double theta = (double)sofar/1000000000L;
    	/*bebe's formula*/
    	System.out.println("Predict SD-LT: Elapsed time: " + theta);
    	/*should use a different formula for theta<meanX*/
    	double xmax = 2700; //should be updated by observations during high-throughput
    						//or read from user in conpaas
    	
    	double A = meanX/2/xmax; 
    	
    	double t0 = 0.366;
    	double sigma = 2*t0*t0*xmax;
    	estimate = (Math.sqrt(2*xmax*sigma)*Math.exp(-sigma/(2*xmax))-Math.sqrt(2*theta*sigma)*Math.exp(-sigma/(2*theta)))/
    				(Math.sqrt(Math.PI)*(erfc(Math.sqrt(sigma/(2*xmax)))-erfc(Math.sqrt(sigma/(2*theta))))) 
    				- sigma;
    	
    	return estimate;
    }
    
    private double estimateExecutionTimeLN(long sofar) {
    	double estimate = 0;
    	double theta = (double)sofar/1000000000L;
    	double mu = Math.log(meanX)-0.5*Math.log(1+varXsq/(meanX*meanX));
    	double sigmaSq = Math.log(1+varXsq/(meanX*meanX)); 
    	System.out.println("Predict LN: Elapsed time: " + theta);
    	estimate = Math.pow(1-Phi((Math.log(theta)-mu)/Math.sqrt(sigmaSq)), -1)*
    		Phi((mu+sigmaSq-Math.log(theta))/Math.sqrt(sigmaSq))*Math.exp(mu+0.5*sigmaSq);
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
}


