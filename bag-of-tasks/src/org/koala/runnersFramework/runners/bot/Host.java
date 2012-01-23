package org.koala.runnersFramework.runners.bot;

import ibis.ipl.IbisIdentifier;

import java.util.ArrayList;

public class Host {
	String node;
	IbisIdentifier from;
	double cost;
	//earliest available time
	long EAT = 0;
	ArrayList<Job> schedJobs = new ArrayList<Job>();
	
	public Host(IbisIdentifier host) {
		from = host;
		node = from.location().toString();
	}
	
	public Host(String host, double d) {
		// TODO Auto-generated constructor stub
		node = host;
		cost = d;
	}

	public void addJob(Job j) {
		schedJobs.add(j);
		EAT += Long.parseLong(j.args[0]);
                        //node.contains(BoTRunner.CLUSTER2) ? Long.parseLong(((HPDCJob)j).argC2) :
			//Long.parseLong(((HPDCJob)j).argC1);
	}
} 
