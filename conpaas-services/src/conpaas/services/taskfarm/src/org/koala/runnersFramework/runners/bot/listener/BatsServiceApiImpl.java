package org.koala.runnersFramework.runners.bot.listener;

import ibis.ipl.IbisProperties;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.lang.Thread.UncaughtExceptionHandler;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Properties;
import java.util.StringTokenizer;
import java.util.logging.FileHandler;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;
import org.koala.runnersFramework.runners.bot.BoTRunner;
import org.koala.runnersFramework.runners.bot.Executor;
import org.koala.runnersFramework.runners.bot.Schedule;

public class BatsServiceApiImpl implements BatsServiceApi, UncaughtExceptionHandler {

    private final String schedulesFolderString;
    private final File schedulesFolder;
    private final Object lock;
    private final String logFile = "exceptions.log";
    private static final Logger exceptionsLogger =
            Logger.getAnonymousLogger();
    private BoTRunner serviceBoT;
    /**
     * Cache object. Read by this class, updated inside the service.
     */
    public static volatile State serviceState = new State(State.RUNNING);
    /**
     * Demo object.
     */
    private DemoWrapper demo;

    /**
     * XXX
     * For security reasons TaskFarm manager does not accept shell commands
     * by default. This can change in future once the communication between 
     * TaskFarm manager and the director is secured.
     */
    private static Boolean executeCommands = false;
    
    private String threadExceptionString = "";
    private Boolean threadExceptionHappened = false;
    
    public static long longestATU = 0;
    private int command_nr = 0;
	private static final int TMPSIZE = 2048;
	byte tmp[] = new byte[TMPSIZE];
    
    public BatsServiceApiImpl() {
        lock = new Object();
        try {
            Handler handler = new FileHandler(BoTRunner.path + File.separator + logFile);
            handler.setFormatter(new SimpleFormatter());
            exceptionsLogger.addHandler(handler);
            exceptionsLogger.log(Level.INFO, "Service started\n");
        } catch (Exception ex) {
            Logger.getLogger(BatsServiceApiImpl.class.getName()).log(
                    Level.SEVERE, null, ex);
        }
        schedulesFolderString = BoTRunner.path + File.separator + "schedules";
        schedulesFolder = new File(schedulesFolderString);
        /*
         * Create, if non-existing, the schedules dump folder
         */
        schedulesFolder.mkdirs();
        demo = new DemoWrapper();
        serviceState.moneySpent = 0;
        serviceState.moneySpentSampling = 0;
    }
   
    
	@Override
	public void uncaughtException(Thread t, Throwable e) {
		threadExceptionHappened = true;
		threadExceptionString = String.format("Sampling failed because of:\n%s\n",
                e.getLocalizedMessage());
	}
    
    @Override
    public MethodReport start_sampling(String filesLocationUrl, String inputFile) {
        
    	if (serviceState.mode.equals(State.MODE_DEMO)) {
    		return demo.start_sampling(inputFile);
    	}

    	try {
    		serviceBoT = new BoTRunner(5, 0, 60, 24, 400,
    				inputFile, ""); //clusterConfFile is set to default value.

    		if(!(serviceBoT.isBagBigEnoughForReplication() && 
    				serviceBoT.isBagBigEnoughForSampling()))
    		{
    			System.err.println("Error: BoT is too small");
    			return new MethodReportError("BoT is too small");
    		}

    		BoTRunner.schedulesFile = schedulesFolderString + File.separator
    		+ System.currentTimeMillis();
    		
    		BoTRunner.filesLocationUrl = filesLocationUrl;
    	}
    	catch (Exception Ex)
    	{
    		return new MethodReportError(Ex.getLocalizedMessage());
    	}
    	
        try {
            synchronized (lock) {
                if (State.ADAPTING.equals(serviceState.state)) {
                    return new MethodReportError("Sampling failed! Service already running.");
                }
                serviceState.state = State.ADAPTING;
            }
            
            Thread thread = new Thread() {

                @Override
                public void run() {
                    try {
                        serviceBoT.run();
                    } catch (Exception ex) {
                        exceptionsLogger.log(Level.SEVERE,
                                "Sampling failed because of:\n{0}\n",
                                ex.getLocalizedMessage());
                        synchronized (lock) {
                            serviceState.state = org.koala.runnersFramework.runners.bot.listener.State.RUNNING;
                        }
                    }
                    synchronized (lock) {
                        serviceState.state = org.koala.runnersFramework.runners.bot.listener.State.RUNNING;
                    }
                }
            };

            thread.setPriority(Thread.MAX_PRIORITY);
            thread.start();
        } catch (Exception ex) {
            synchronized (lock) {
                serviceState.state = State.RUNNING;   
            }
            return new MethodReportError(ex.getLocalizedMessage());
        }
        return new MethodReportSuccess("Sampling started.");
    }
    
    private String create_json_schedules(List<SamplingResult> list)
    {
       	String schedulesJson = "";
    	for (int i = 0; i < list.size(); i++) {
			SamplingResult samplingResult = list.get(i);
			schedulesJson += "{";

			schedulesJson += "\"timestamp\": " + samplingResult.timestamp + ",";
			schedulesJson += "\"schedules\": [";
			for(int j = 0; j < samplingResult.schedules.size(); j++)
			{
				
				String sched = samplingResult.schedules.get(j);
				StringTokenizer st = new StringTokenizer(sched, " \t");
				st.nextToken(); // first one is budget and we don't care about that
				int cost = (int)(Double.parseDouble(st.nextToken()));
				int time = (int)(Double.parseDouble(st.nextToken()));
				if(time > 1000)
				{
					// to prevent a bug in the optimization code when 
					// there are not enough schedule points
					if(j == (samplingResult.schedules.size() - 1))
					{
						schedulesJson = schedulesJson.substring(0, schedulesJson.length() - 2);
						schedulesJson += "}";
					}
					
					continue;
				}
				schedulesJson += "{";
				schedulesJson += "\"cost\": " + cost + ",";
				schedulesJson += "\"time\": " + time * longestATU ;
				
				if(j == (samplingResult.schedules.size() - 1))
				{
					schedulesJson += "}";
				}
				else
				{
					schedulesJson += "},";
				}
			}
			schedulesJson += "]";
			if(i == (list.size() - 1))
			{
				schedulesJson += "}";
			}
			else
			{
				schedulesJson += "},";
			}
		}
    	return schedulesJson;
    }

    @Override
    public Object get_sampling_results() {
        
        List<SamplingResult> list = new ArrayList<SamplingResult>();
        
    	if (serviceState.mode.equals(State.MODE_DEMO)) {
    		list = (List<SamplingResult>)demo.get_sampling_result();
    		return create_json_schedules(list);
        }

        for (File file : schedulesFolder.listFiles()) {
            if (file.length() <= 0) {
                continue;
            }

            List<Schedule> schedules = null;
            BoTRunner bot = null;
            try {
                FileInputStream fis = new FileInputStream(file);
                ObjectInputStream ois = new ObjectInputStream(fis);

                // read the (remainder) BoT, if empty, schedules are all 0,0,0
                bot = (BoTRunner) ois.readObject();
                schedules = (List<Schedule>) ois.readObject();

                ois.close();
            } catch (Exception ex) {
                Logger.getLogger(BatsServiceApiImpl.class.getName()).log(Level.SEVERE, null, ex);
            }

            if (schedules == null) {
                continue;
            }

            /**
             * Return an array of schedules files names with their corresponding
             * schedules. Element of the array format: [schedule time stamp]
             * [sched0] [sched1] ...
             *
             * Schedule format: budget cost atus
             */
            List<String> schedulesString = new ArrayList<String>(schedules.size());
            if (bot.jobsRemainingAfterSampling > 0) {
            	for (int i = 0; i < schedules.size(); i++) {
            		schedulesString.add(schedules.get(i).toString());
            	}
            }

            list.add(new SamplingResult(file.getName(), schedulesString));
        }
        if (list.isEmpty()) {
//            return new MethodReportError("No schedules files available.");
//            Claudiu asked for this method not to return an error, but an empty non-error message.
            return new MethodReportSuccess();
        }
        
        return create_json_schedules(list);
    }

    @Override
    public State get_service_info() {
        if (serviceState.mode.equals(State.MODE_DEMO)) {
            return demo.get_service_info();
        }
        return serviceState;
    }

    @Override
    public MethodReport start_execution(long schedulesFileTimeStamp, int scheduleNo) {
    	
    	if (serviceState.mode.equals(State.MODE_DEMO)) {
            return demo.start_execution(scheduleNo);
        }

    	if(serviceState.noCompletedTasks == serviceState.noTotalTasks)
    	{
    		return new MethodReportError("Execution failed! Service has already executed all tasks.");
    	}
    	
        File schedFile = null;
        try {
            synchronized (lock) {
                schedFile = getSchedulesFile(schedulesFileTimeStamp);
                if (schedFile == null) {
                    return new MethodReportError("Execution failed! No schedules file present.");
                }
                if (State.ADAPTING.equals(serviceState.state)) {
                    return new MethodReportError("Execution failed! Service already running.");
                }
                serviceState.state = State.ADAPTING;
            }

            String[] args = {"" + scheduleNo, schedFile.getPath()};

            final Executor execute = new Executor(args);
            serviceBoT = execute.bot;

            /*
             * work-around such that the "Sampling&Execution-in-the-same-VM"
             * works well
             */
            Properties initialIbisProps = execute.bot.myIbisProps;
            execute.bot.poolName = initialIbisProps.get(IbisProperties.POOL_NAME) + "-executionPhase";
            execute.bot.myIbisProps.setProperty(IbisProperties.POOL_NAME,
                    execute.bot.poolName);
            execute.bot.electionName = initialIbisProps.get("ibis.election.name") + "-executionPhase";
            execute.bot.myIbisProps.setProperty("ibis.election.name",
                    execute.bot.electionName);


            Thread thread = new Thread() {

                @Override
                public void run() {
                    try {
                        execute.go();
                    } catch (Exception ex) {
                        exceptionsLogger.log(Level.SEVERE,
                                "Execution failed because of:\n{0}\n", ex.getLocalizedMessage());
                    }
                    synchronized (lock) {
                        serviceState.state = org.koala.runnersFramework.runners.bot.listener.State.RUNNING;
                    }
                }
            };

            thread.setPriority(Thread.MAX_PRIORITY);
            thread.start();
        } catch (Exception ex) {
            synchronized (lock) {
                serviceState.state = State.STOPPED;
                return new MethodReportError(ex.getLocalizedMessage());
            }
        }
        return new MethodReportSuccess("Ok.");
    }

    @Override
    public MethodReport terminate_workers() {
        if (serviceState.mode.equals(State.MODE_DEMO)) {
            return demo.terminate_workers();
        }

        MethodReport retVal = new MethodReportSuccess();
        int totalNoWorkersTerminated = 0;
        try {
            synchronized (lock) {
                if (serviceBoT == null) {
                    serviceState.state = State.STOPPED;
                    retVal.append(totalNoWorkersTerminated + "\n");
                    retVal.append("Ok.");
                    return retVal;
                }
            }
            System.out.println("terminating workers!");
            totalNoWorkersTerminated = serviceBoT.terminate();
            retVal.append(totalNoWorkersTerminated + "\n");

            serviceState.state = State.STOPPED;
        } catch (IOException ioe) {
            return new MethodReportError(ioe.getLocalizedMessage());
        } catch (Exception e)
	{
	    // XXX when workers are already killed.
	    // This should be properly handled in the future.
	}

        retVal.append("Ok.");
        return retVal;
    }

    private File getSchedulesFile(long schedulesFileTimeStamp) {
        String schedulesFile = "" + schedulesFileTimeStamp;

        File file = new File(schedulesFile);
        if (file.exists()) {
            return file;
        }

        schedulesFile = schedulesFolder + File.separator + schedulesFile;
        file = new File(schedulesFile);
        if (file.exists()) {
            return file;
        }

        return null;
    }

    @Override
    public MethodReport get_log() {
        if (serviceState.mode.equals(State.MODE_DEMO)) {
            return demo.get_log();
        }

        MethodReport retVal = new MethodReportSuccess();
        try {
            BufferedReader br = new BufferedReader(new InputStreamReader(
                    new FileInputStream(BoTRunner.path + "/" + logFile)));
            String line;
            while ((line = br.readLine()) != null) {
                retVal.append(line + "\n");
            }
            br.close();
        } catch (IOException ex) {
            return new MethodReportError(ex.getLocalizedMessage());
        }
        return retVal;
    }

	@Override
	public MethodReport set_service_mode(String mode) {
		if(mode.equals(State.MODE_DEMO) || mode.equals(State.MODE_REAL))
		{
			serviceState.mode = mode;
		}
		else
		{
			return new MethodReportError("Invalid service mode");
		}
		return new MethodReportSuccess();
	}

	
	private static void dumpData(File file, byte data[], int len)
	{
		try {
		    FileOutputStream fs = new FileOutputStream(file, true);
		    fs.write(data, 0, len);
		    fs.flush();
		    fs.close();
		} catch (IOException e) {
			Logger.getLogger(BatsServiceApiImpl.class.getName()).log(Level.SEVERE, null, e);
		}
	}
	
	private static void dumpData(File file, String str)
	{
		try {
		    FileOutputStream fs = new FileOutputStream(file);
		    fs.write(str.getBytes());
		    fs.flush();
		    fs.close();
		} catch (IOException e) {
			Logger.getLogger(BatsServiceApiImpl.class.getName()).log(Level.SEVERE, null, e);
		}
	}

	
	private void executeShellCommand(final String command)
	{
		 Thread thread = new Thread() {

	            @Override
	            public void run() {
	        		long startTime = System.nanoTime();
	                
	                ProcessBuilder pb = new ProcessBuilder("bash", "-c", command);
	                
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
	                
	        		File jobPath = new File(System.getenv("MOUNT_FOLDER") + "/commands/" + command_nr);
	        		
	        		jobPath.mkdirs();
	        		
	        		File pathOut = new File(System.getenv("MOUNT_FOLDER") + "/commands/" + command_nr + "/out");
	        		File pathErr = new File(System.getenv("MOUNT_FOLDER") + "/commands/" + command_nr + "/err");
	        		File pathParam = new File(System.getenv("MOUNT_FOLDER") + "/commands/" + command_nr + "/param");
	        		
	        		// Update number for the next command 
	        		command_nr++;
	        		
	        		dumpData(pathParam, command);
	                
	                Process shell;
	        		try {
	        			shell = pb.start();
	        		} catch (IOException e) {
	        			e.printStackTrace();
	        			return;
	        		}

	        		
	                int len;
	                
	                InputStream is = shell.getInputStream();
	                InputStream es = shell.getErrorStream();
	                
	                // XXX might not be the best idea to first read Out and then Err.
	                
	                try {
	        			while ((len = is.read(tmp, 0, TMPSIZE)) != -1) {
	        				dumpData(pathOut, tmp, len);
	        			}
	                
	        			while ((len = es.read(tmp, 0, TMPSIZE)) != -1) {
	                		dumpData(pathErr, tmp, len);
	                	}
	        		} catch (IOException e) {
	        			e.printStackTrace();
	        			return;
	        		}
	                
	                try {
	        			shell.waitFor();
	        		} catch (InterruptedException e) {
	        			e.printStackTrace();
	        			return;
	        		}
	                
	        	    long endTime = System.nanoTime();
	        	    

	        	    System.out.println("Runtime(ms) " + ((double)(endTime - startTime) / 1000000000));
	        	    
	                synchronized (lock) {
	                    serviceState.state = org.koala.runnersFramework.runners.bot.listener.State.RUNNING;
	                }

	            }
	        };
	        thread.setPriority(Thread.MAX_PRIORITY);
            thread.start();
	}
	
	@Override
	public MethodReport execute_command(final String command) {
		
        if (serviceState.mode.equals(State.MODE_DEMO)) {
			return new MethodReportError(
					"No support for command execution in the DEMO mode.");
        }
		if(executeCommands == false)
		{
			return new MethodReportError(
					"Executing commands is disabled in this deployment.");
		}
        synchronized (lock) {
    		if (State.ADAPTING.equals(BatsServiceApiImpl.serviceState.state)) {
    			return new MethodReportError(
    					"Command execution failed! Service is busy.");
    		}
    		BatsServiceApiImpl.serviceState.state = State.ADAPTING;
        }
        executeShellCommand(command);
        
		return new MethodReportSuccess();
	}

}
