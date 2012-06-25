package org.koala.runnersFramework.runners.bot.listener;

import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;
import java.util.Timer;
import java.util.TimerTask;
import org.koala.runnersFramework.runners.bot.BagOfTasks;
import org.koala.runnersFramework.runners.bot.Job;

class DemoWrapper {

    private final State serviceState;
    private final Object lock;
    private final Timer t;
    private long samplingStartTime, samplingFinishTime;
    private long executionStartTime, executionFinishTime;
    private double samplingPhaseTime = 10000; // ms
    private double samplingPercentage = 0.2;
    private double pricePerTaskExecutionPhase = 0;
    private int atu = 200;
    private int N = 5;
    private double costPerAtu = 3;
    private double timePerTask;
    private boolean samplingDone = false;
    private boolean samplingReturned = false;
    private List<SamplingResult> schedList = null;

    public DemoWrapper() {
        serviceState = new State(State.RUNNING);
        lock = new Object();
        t = new Timer();
        schedList = new ArrayList<SamplingResult>();
    }

    class SamplingTask extends TimerTask {

        @Override
        public void run() {
            synchronized (lock) {
                samplingFinishTime = System.currentTimeMillis();
                serviceState.state = org.koala.runnersFramework.runners.bot.listener.State.RUNNING;
            }
        }
    }

    class ExecutionTask extends TimerTask {

        @Override
        public void run() {
            synchronized (lock) {
                executionFinishTime = System.currentTimeMillis();
                serviceState.state = org.koala.runnersFramework.runners.bot.listener.State.RUNNING;
            }
        }
    }

    MethodReport start_sampling(String inputFile) {
        synchronized (lock) {
            if (State.ADAPTING.equals(serviceState.state)) {
                return new MethodReportError("Sampling failed! Service already running.");
            }
            serviceState.state = State.ADAPTING;
        }
        // reusing some old code.
        BagOfTasks bot = new BagOfTasks(inputFile);
        ArrayList<Job> list = bot.getBoT();
        if (list == null || list.isEmpty()) {
            synchronized (lock) {
                serviceState.state = org.koala.runnersFramework.runners.bot.listener.State.RUNNING;
                return new MethodReportError("No tasks found.");
            }
        }

        serviceState.noTotalTasks = list.size();
        timePerTask = samplingPhaseTime / (samplingPercentage * serviceState.noTotalTasks);
        samplingStartTime = System.currentTimeMillis();
        samplingFinishTime = 0;

        t.schedule(new SamplingTask(), (long) samplingPhaseTime);
        return new MethodReportSuccess("Sampling started.");
    }

    MethodReport start_execution(int scheduleNum) {
        synchronized (lock) {
            if (State.ADAPTING.equals(serviceState.state)) {
                return new MethodReportError("Sampling failed! Service already running.");
            }
            serviceState.state = State.ADAPTING;
        }
        executionStartTime = System.currentTimeMillis();
        executionFinishTime = 0;
        
        double execCost = get_execution_cost(scheduleNum);
	pricePerTaskExecutionPhase = execCost / ((1 - samplingPercentage) * serviceState.noTotalTasks);
        
        double executionPhaseTime = timePerTask * (1 - samplingPercentage)
                * serviceState.noTotalTasks;
        t.schedule(new ExecutionTask(), (long) executionPhaseTime);
        return new MethodReportSuccess("Execution started.");
    }

    private double get_execution_cost(int scheduleNum) {
    	
    	String s;
    	
    	if(schedList == null)
    	{
    		return 0;
    	}
    	List<String> scheds = schedList.get(0).schedules;
    	try {
    		s = scheds.get(scheduleNum);
    	}
    	catch(Exception E)
    	{
    		return 0;
    	}

    	StringTokenizer st = new StringTokenizer(s, " \t");
    	st.nextToken(); // first one is budget and we don't care about that
		return Double.parseDouble(st.nextToken());
	}

	MethodReport get_log() {
        // demo version can live without this implementation.
        return new MethodReportSuccess("");
    }

    MethodReport terminate_workers() {
        //nothing required over here, since no workers are actually started.
        return new MethodReportSuccess("Ok.");
    }

    State get_service_info() {
        long currTime = System.currentTimeMillis();
        synchronized (lock) {
            if (State.ADAPTING.equals(serviceState.state)) {
                // service is either in sampling or execution phase
                if (samplingFinishTime == 0) {
                    serviceState.noCompletedTasks = (int) ((double) (currTime
                            - samplingStartTime) / timePerTask);
                } else {
                    serviceState.noCompletedTasks = (int) (samplingPercentage
                            * serviceState.noTotalTasks + (currTime - executionStartTime) / timePerTask);
                }
            } else {
                // service is idle
                if (samplingFinishTime == 0) {
                    serviceState.noCompletedTasks = 0;
                } else if (executionFinishTime == 0) {
                    serviceState.noCompletedTasks = (int) (samplingPercentage
                            * serviceState.noTotalTasks);
                } else {
                    serviceState.noCompletedTasks = serviceState.noTotalTasks;
                }
            }

            int samplingPhaseNumTasks = (int) (serviceState.noTotalTasks * 
                    samplingPercentage);
            if ((serviceState.noCompletedTasks >= samplingPhaseNumTasks) && (serviceState.noCompletedTasks != 0)) {
            	this.samplingDone = true;
            	
                // sampling phase expired
                
		serviceState.moneySpent =  Math.ceil(serviceState.moneySpentSampling +
            	pricePerTaskExecutionPhase * (serviceState.noCompletedTasks - samplingPhaseNumTasks));
            } else if((serviceState.noCompletedTasks != 0)){
            	// sampling
            	
                serviceState.moneySpent = Math.ceil(serviceState.noCompletedTasks
                    * timePerTask / N / atu) * costPerAtu * N;
                serviceState.moneySpentSampling = serviceState.moneySpent;
            }

            return serviceState;
        }
    }

    Object get_sampling_result() {
    	
        if(this.samplingDone && !this.samplingReturned) {
        	
        	schedList = new ArrayList<SamplingResult>();
        	List<String> sched = new ArrayList<String>();

        	// Meaningful schedules to be used later in the DEMO version.
        	
            int atuForSampling = (int)Math.ceil(samplingPhaseTime / atu);
            int normalRateATU = (int)(atuForSampling * (1/(samplingPercentage))) - atuForSampling;
            int normalRateCost = (int)((serviceState.moneySpent  * (1/(samplingPercentage))) - serviceState.moneySpent);
            
        	sched.add("\t" + 0 + "\t" + (int)(normalRateCost*2) + "\t" + (int)(normalRateATU*0.7));
        	sched.add("\t" + 1 + "\t" + (int)(normalRateCost*1.5) + "\t" + (int)(normalRateATU*0.8));
        	sched.add("\t" + 2 + "\t" + normalRateCost + "\t" + normalRateATU + "\t");
        	sched.add("\t" + 3 + "\t" + (int)(normalRateCost*1.1) + "\t" + (int)(normalRateATU*1.1));
        	sched.add("\t" + 4 + "\t" + (int)(normalRateCost*0.8) + "\t" + (int)(normalRateATU*2));
        	
        	SamplingResult sr = new SamplingResult("1873477324884", sched);
        	schedList.add(sr);
        	samplingReturned = true;
        }
        return schedList;
    }
}
