package org.koala.runnersFramework.runners.bot;

import java.io.Serializable;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

public class Job implements Serializable {

	private static final long serialVersionUID = 1L;
	private String exec;
	public String[] args;
	public String jobID;
	public String node;
	public long startTime;
	/*begin for hpdc tests*/
	public boolean submitted = false;
	public boolean done = false;	
	/*for replication on tail phase*/
	public boolean replicated = false;
	public double tau;
	/*end for hpdc tests*/
	
	/*expressed in seconds*/
	public HashMap<String,Double> runtimes;
	
	/*replication*/
	/*expressed in nanoseconds*/
	public HashMap<String,Long> starttimes;
	public HashMap<String,String> replicaNodes;
	public boolean notYetFinished = true;
	
	/*empty constructor for NoJob*/
	public Job() {}
	
	public Job(List<String> args2, String executable, String jobID) {
		// TODO Auto-generated constructor stub
		setExec(executable);
		setJobID(jobID);
		args = new String[args2.size()];
		args2.toArray(args);		
		runtimes = new HashMap<String, Double>();
		starttimes = new HashMap<String, Long>();
		replicaNodes = new HashMap<String, String>();
	}
		
	public String getNode() {
		return node;
	}
	
	public void setNode(String node) {		
		this.node = node;
	}
	
	public void setNode(String cluster, String node) {
		if(!replicated)
			this.node = node;
		else 
			replicaNodes.put(cluster, node);
	}
	
	public String getJobID() {
		return jobID;
	}

	public void setJobID(String jobID) {
		this.jobID = jobID;
	}
	
	public void setExec(String exec) {
		this.exec = exec;
	}

	public String getExec() {
		return exec;
	}
	
	public void setTau(double tau) {
		this.tau = tau;
	}
	
	public double getTau() {
		return tau;
	}

	/*assumes one degree of replication*/
	public void originalDied() {
		replicated = false;
		this.node = replicaNodes.values().iterator().next();
		replicaNodes = new HashMap<String, String>();
		this.startTime = starttimes.values().iterator().next().longValue();
		starttimes = new HashMap<String,Long>();
	}

	/*assumes one degree of replication*/
	public void replicaDied(String cluster) {
		replicated = false;
		replicaNodes = new HashMap<String, String>();
		starttimes = new HashMap<String,Long>();
	}

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (obj == this) {
            return true;
        }
        if (!(obj instanceof Job)) {
            return false;
        }
        Job job = (Job) obj;
        if (this.jobID == null || job.jobID == null) {
            return false;
        }
        return this.jobID.equals(job.jobID);
    }

    @Override
    public int hashCode() {
        int hash = 7;
        hash = 71 * hash + (this.exec != null ? this.exec.hashCode() : 0);
        hash = 71 * hash + Arrays.deepHashCode(this.args);
        hash = 71 * hash + (this.jobID != null ? this.jobID.hashCode() : 0);
        return hash;
    }
}
