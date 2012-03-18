package org.koala.runnersFramework.runners.bot;

import org.koala.runnersFramework.runners.bot.BoTRunner;
import java.io.IOException;
import java.util.Collection;
import java.util.HashMap;
import java.util.Properties;
import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;

import ibis.ipl.Ibis;
import ibis.ipl.IbisCapabilities;
import ibis.ipl.IbisCreationFailedException;
import ibis.ipl.IbisFactory;
import ibis.ipl.IbisIdentifier;
import ibis.ipl.IbisProperties;
import ibis.ipl.PortType;
import ibis.ipl.ReceivePort;
import java.io.Serializable;
import org.koala.runnersFramework.runners.bot.Job;
import org.koala.runnersFramework.runners.bot.JobResult;
import org.koala.runnersFramework.runners.bot.WorkerStats;

public abstract class Master {

	protected static final PortType masterReplyPortType = new PortType(
			PortType.COMMUNICATION_RELIABLE, PortType.SERIALIZATION_OBJECT,
			PortType.RECEIVE_EXPLICIT, PortType.RECEIVE_TIMEOUT, PortType.CONNECTION_ONE_TO_ONE);
	protected static final PortType workerRequestPortType = new PortType(
			PortType.COMMUNICATION_RELIABLE, PortType.SERIALIZATION_OBJECT,
			PortType.RECEIVE_EXPLICIT, PortType.RECEIVE_TIMEOUT, PortType.CONNECTION_MANY_TO_ONE, PortType.CONNECTION_DOWNCALLS);
	protected static final IbisCapabilities ibisCapabilities = new IbisCapabilities(
			IbisCapabilities.MALLEABLE,
			IbisCapabilities.MEMBERSHIP_TOTALLY_ORDERED,
			IbisCapabilities.ELECTIONS_STRICT,
			/*for job preemption*/
			IbisCapabilities.SIGNALS);
	
	protected final BoTRunner bot;
	
	public final Ibis myIbis;
	protected ReceivePort masterRP;
	
	protected long timeout;
	protected long totalNumberTasks;
	protected long jobsDone;
		
	protected HashMap<String, HashMap<String, WorkerStats>> workers;
	
	Random random = new Random(1111111111L);
	
	protected Master(BoTRunner aBot) throws Exception {		
		bot = aBot;
        		
		myIbis = IbisFactory.createIbis(ibisCapabilities, bot.myIbisProps, true, 
										null,
										workerRequestPortType, masterReplyPortType);
		
                System.out.println("Master: IBIS CREATED");
                
		if (myIbis.identifier().compareTo(
				myIbis.registry().elect(bot.electionName)) != 0)
			System.exit(1);
		
		workers = new HashMap<String, HashMap<String, WorkerStats>>();
		
		totalNumberTasks = bot.tasks.size();	
		jobsDone = 0;
           
	}
	
	public void initMasterComm() throws IOException {
		masterRP = myIbis
				.createReceivePort(workerRequestPortType, "master");
		// enable connections
		masterRP.enableConnections();			
	}
	
	public String getMasterID() {
		return myIbis.identifier().name();
	}

	protected abstract void handleLostConnections();
	
	protected abstract boolean areWeDone();
	
	public abstract void run();
	
	protected abstract Job handleJobResult(JobResult received, IbisIdentifier from);
	
	protected abstract Job handleJobRequest(IbisIdentifier from);

	public abstract void startInitWorkers();
	
	public abstract void terminateWorker(Cluster cluster, WorkerStats ws, String reason);

	public int terminateAllWorkers() throws IOException {
		
		int noWorkerTerminatedNow = 0;
		
		for(Cluster c : bot.Clusters.values()) {
			for(WorkerStats ws : workers.get(c.alias).values()) {
				if(!ws.isFinished()) {
					c.terminateNode(ws.getIbisIdentifier(), myIbis);
					noWorkerTerminatedNow ++;
				}
			}
		}
		return noWorkerTerminatedNow;
	} 	
	
	
}
