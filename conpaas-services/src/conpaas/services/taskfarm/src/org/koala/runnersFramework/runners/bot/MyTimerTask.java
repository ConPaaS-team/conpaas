package org.koala.runnersFramework.runners.bot;

import ibis.ipl.Ibis;
import ibis.ipl.IbisIdentifier;

import java.io.IOException;
import java.util.TimerTask;

public class MyTimerTask extends TimerTask {


	private Ibis myIbis;
	private IbisIdentifier who;
	private Cluster cluster;

	public MyTimerTask(Cluster cluster, IbisIdentifier who, Ibis myIbis) {
		super();
		this.cluster = cluster;		
		this.who = who;		
		this.myIbis = myIbis;
	}

	public void run() {
		
		//try {
			//cluster.terminateNode(who, myIbis);
			System.err.println("Skipped terminateNode in MyTimerTask");
			//myIbis.registry().signal("die", from);
		//} catch (IOException e) {
			// TODO Auto-generated catch block
		//	e.printStackTrace();
		//}
	}


	
}
