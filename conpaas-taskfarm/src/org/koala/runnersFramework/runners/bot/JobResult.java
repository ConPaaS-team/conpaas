package org.koala.runnersFramework.runners.bot;

import java.io.Serializable;

public class JobResult implements Serializable {
	private JobStats stats;
	private String jobID;
	
	public JobResult(String jobID, JobStats jobStats) {
		super();
		this.stats = jobStats;
		this.jobID = jobID;
	}

	public JobStats getStats() {
		return stats;
	}

	public void setStats(JobStats stats) {
		this.stats = stats;
	}

	public String getJobID() {
		return jobID;
	}

	public void setJobID(String jobID) {
		this.jobID = jobID;
	}
	
	
}
