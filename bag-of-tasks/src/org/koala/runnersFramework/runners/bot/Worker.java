package org.koala.runnersFramework.runners.bot;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

import ibis.ipl.Ibis;
import ibis.ipl.IbisCapabilities;
import ibis.ipl.IbisFactory;
import ibis.ipl.IbisIdentifier;
import ibis.ipl.IbisProperties;
import ibis.ipl.PortType;
import ibis.ipl.ReadMessage;
import ibis.ipl.ReceivePort;
import ibis.ipl.RegistryEventHandler;
import ibis.ipl.SendPort;
import ibis.ipl.WriteMessage;

public class Worker implements RegistryEventHandler {

	private static final PortType masterReplyPortType = new PortType(
			PortType.COMMUNICATION_RELIABLE, PortType.SERIALIZATION_OBJECT,
			PortType.RECEIVE_EXPLICIT, PortType.RECEIVE_TIMEOUT, PortType.CONNECTION_ONE_TO_ONE);
	private static final PortType workerRequestPortType = new PortType(
			PortType.COMMUNICATION_RELIABLE, PortType.SERIALIZATION_OBJECT,
			PortType.RECEIVE_EXPLICIT, PortType.RECEIVE_TIMEOUT, PortType.CONNECTION_MANY_TO_ONE, PortType.CONNECTION_DOWNCALLS);
	private static final IbisCapabilities ibisCapabilities = new IbisCapabilities(
			IbisCapabilities.MALLEABLE,
			IbisCapabilities.MEMBERSHIP_TOTALLY_ORDERED,
			IbisCapabilities.ELECTIONS_STRICT,
			/*for job preemption*/
			IbisCapabilities.SIGNALS);

	protected final Ibis myIbis;
	protected SendPort workRequestPort;
    protected ReceivePort workReplyPort;

	Worker(String masterID, String poolName, String serverAddress, String speedFactor)
			throws Exception {
		Properties props = new Properties();
		props.setProperty(IbisProperties.POOL_NAME, poolName);
		props.setProperty(IbisProperties.SERVER_ADDRESS, serverAddress);
		myIbis = IbisFactory.createIbis(ibisCapabilities, props, true, this,
				workerRequestPortType, masterReplyPortType);

		IbisIdentifier master = myIbis.registry().getElectionResult(masterID);

		/*for job preemption*/
		myIbis.registry().enableEvents();
		
		workRequestPort = myIbis.createSendPort(workerRequestPortType);
		workRequestPort.connect(master, "master");
				
		workReplyPort = myIbis.createReceivePort(
				this.masterReplyPortType, "worker");
		workReplyPort.enableConnections();

		WriteMessage requestWork = workRequestPort.newMessage();
		requestWork.writeObject(new JobRequest());
		requestWork.finish();

		while (true) {
			ReadMessage reply = workReplyPort.receive();
			Object replyObj = reply.readObject();
			if (replyObj instanceof NoJob) {
				reply.finish();
				/* could print some worker stats? */				
				workRequestPort.close();
				workReplyPort.close();
				myIbis.end();
				System.exit(0);
			}

			Job job = (Job) replyObj;

			reply.finish();

			/*if this is a simulation mimic the speedFactor*/
			double factor = Double.parseDouble(speedFactor);
			if("/bin/sleep".equalsIgnoreCase(job.getExec())) {
				long et = (long)((double)Long.parseLong(job.args[0])/factor);
				job.args[0] = "" + et;
			}
			
			/*
			   	String[] cmdarray = new String[job.args.length + 1];
			   	cmdarray[0] = job.getExec();
			   	for (int i = 0; i < job.args.length; i++) {							
					cmdarray[i + 1] = job.args[i];				
				} 	
				long startTime = System.nanoTime();
            	Process runJob = Runtime.getRuntime().exec(cmdarray);
				runJob.waitFor();
				long endTime = System.nanoTime();			
		
			*/
			
			String cmd = job.getExec();
            for (int i = 0; i < job.args.length; i++) {
                cmd += " " + job.args[i];
            }
            
            System.out.println("Running job: " + cmd);
            
            long startTime = System.nanoTime();
            
            ProcessBuilder pb = new ProcessBuilder("bash", "-c", cmd);
            
            /* modify current working directory for the ProcessBuilder
             * so as to treat as relative path the mounted file system */
            try {
                String mountFolder = System.getenv("MOUNT_FOLDER");
                if (mountFolder != null && !"".equals(mountFolder)) {
                    pb.directory(new File(mountFolder));
                }
            } catch (Exception ex) {
                System.err.println(ex.getLocalizedMessage());
            }
            /* end */
            pb.redirectErrorStream(true);
            Process shell = pb.start();

            InputStream shellIn = shell.getInputStream();
            int c;
            while ((c = shellIn.read()) != -1) {
            	/*pull bytes from output stream of shell process
             	  to avoid blocking it*/
            }
            shell.waitFor();

    	    long endTime = System.nanoTime();

          /*              
                        long waitTimeNanos = (long) ((endTime - startTime) * (factor-1));
                        long waitTimeMillis = waitTimeNanos / 1000000;
                        waitTimeNanos -= waitTimeMillis * 1000000;
                        Thread.sleep(waitTimeMillis, (int) waitTimeNanos);

                        // new endTime.
			endTime = System.nanoTime();			
*/
    	    System.out.println("Runtime(ms) " + ((double)(endTime - startTime) / 1000000000));
			requestWork = workRequestPort.newMessage();
			requestWork.writeObject(new JobResult(job.jobID, new JobStats(
					endTime - startTime)));
			requestWork.finish();
		}
	}

	/**
	 * * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		try {
                    System.out.println("Command received...");
			Worker worker = new Worker(args[0], args[1], args[2], args[3]);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void died(IbisIdentifier arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void electionResult(String arg0, IbisIdentifier arg1) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void gotSignal(String arg0, IbisIdentifier arg1) {
		System.out.println("Lease expired! Closing ibis ...");
		try {
			myIbis.end();
			oneSelfShutdown();
		        } catch (IOException ex) {
		            Logger.getLogger(Worker.class.getName()).log(Level.SEVERE, null, ex);
		        }
		        System.out.println("Lease expired! Exiting computation ...");
		        System.exit(0);
	}

	@Override
	public void joined(IbisIdentifier arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void left(IbisIdentifier arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void poolClosed() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void poolTerminated(IbisIdentifier arg0) {
		// TODO Auto-generated method stub
		
	}
	
	protected void closePorts() throws IOException {
        workRequestPort.close();
        workReplyPort.close();
    }
	
	public void oneSelfShutdown() {      
            System.exit(0);
    }
}
