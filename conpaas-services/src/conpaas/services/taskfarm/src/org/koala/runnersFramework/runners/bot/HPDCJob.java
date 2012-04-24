package org.koala.runnersFramework.runners.bot;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class HPDCJob extends Job {
	String argC1;
	String argC2;
	
	public HPDCJob(String argv1, String argv2, String executable, String jobID) {
		super();
		super.setExec(executable);
		super.setJobID(jobID);
		argC1=argv1;
		argC2=argv2;
		super.args = new String[1]; 
		super.runtimes = new HashMap<String, Double>();
		super.starttimes = new HashMap<String, Long>();
		super.replicaNodes = new HashMap<String, String>();
	}
	
	public void setArg(int i) {		
		if(i==1) {
			super.args[0] = argC1;
		} else {
			super.args[0] = argC2;
		}
	}
}
