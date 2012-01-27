package org.koala.runnersFramework.runners.bot.listener;

import ibis.ipl.IbisProperties;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.logging.FileHandler;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;
import org.koala.runnersFramework.runners.bot.BoTRunner;
import org.koala.runnersFramework.runners.bot.Executor;
import org.koala.runnersFramework.runners.bot.Schedule;

class BatsServiceApiImpl implements BatsServiceApi {

    private final String schedulesFolderString;
    private final File schedulesFolder;
    private final Object lock;
    private volatile State serviceState;
    private final String logFile = "exceptions.log";
    private static final Logger exceptionsLogger =
            Logger.getAnonymousLogger();

    public BatsServiceApiImpl() {
        serviceState = new State(State.RUNNING);
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
        /* Create, if non-existing, the schedules dump folder */
        schedulesFolder.mkdirs();
    }

    @Override
    public MethodReport start_sampling(String filesLocationUrl,
            String inputFile, String clusterConfigurationFile) {
        try {
            synchronized (lock) {
                if (State.ADAPTING.equals(serviceState.state)) {
                    return new MethodReportError("Sampling failed! Service already running.");
                }
                serviceState.state = State.ADAPTING;
            }

            final BoTRunner bot = new BoTRunner(5, 0, 60, 24, 400,
                    inputFile, clusterConfigurationFile);

            BoTRunner.schedulesFile = schedulesFolderString + File.separator
                     + System.currentTimeMillis();
//            old code:
//            BoTRunner.schedulesFile = schedulesFile;
            
            BoTRunner.filesLocationUrl = filesLocationUrl;

            Thread thread = new Thread() {

                @Override
                public void run() {
                    try {
                        bot.run();
                    } catch (Exception ex) {
                        exceptionsLogger.log(Level.SEVERE,
                                "Sampling failed because of:\n{0}\n",
                                ex.getLocalizedMessage());
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

    @Override
    public Object get_sampling_results() {
        /**
         * FAKE
         *
        List<SamplingResult> list = new ArrayList<SamplingResult>();
        List<String> sched = new ArrayList<String>();
        sched.add("\t" + 323 + "\t" + 100 + "\t" + 1000);
        sched.add("\t" + 421233 + "\t" + 100 + "\t" + 1000);
        sched.add("\t" + 323 + "\t" + 20 + "\t" + 30);
        sched.add("\t" + 32123 + "\t" + 100 + "\t" + 1000);
        sched.add("\t" + 3123 + "\t" + 1400 + "\t" + 10);
        SamplingResult sr = new SamplingResult("1873477324884", sched);
        list.add(sr);
        return list;
        **
         * END FAKE
         */
        List<SamplingResult> list = new ArrayList<SamplingResult>();
        
        for (File file : schedulesFolder.listFiles()) {
            if (file.length() <= 0) {
                continue;
            }
            
            List<Schedule> schedules = null;
            try {
                FileInputStream fis = new FileInputStream(file);
                ObjectInputStream ois = new ObjectInputStream(fis);

                // read the BoT, but no need to store it
                ois.readObject();
                schedules = (List<Schedule>) ois.readObject();

                ois.close();
            } catch (Exception ex) {
                Logger.getLogger(BatsServiceApiImpl_Later.class.getName()).log(Level.SEVERE, null, ex);
            }

            if (schedules == null) {
                continue;
            }
            
            /**
             * Return an array of schedules files names with their corresponding schedules.
             * Element of the array format:
             * [schedule time stamp] [sched0] [sched1] ...
             * 
             * Schedule format:
             * budget   cost    atus
             */ 
            
            List<String> schedulesString = new ArrayList<String>(schedules.size());
            for (int i = 0; i < schedules.size(); i++) {
                schedulesString.add(schedules.get(i).toString());
            }
            
            list.add(new SamplingResult(file.getName(), schedulesString));
        }

        if(list.isEmpty()) {
            return new MethodReportError("No schedules files available.");
        }
        
        return list;
    }    

    @Override
    public State get_service_info() {
        return serviceState;
    }

    @Override
    public MethodReport start_execution(long schedulesFileTimeStamp, int scheduleNo) {    
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

            /*work-around such that the "Sampling&Execution-in-the-same-VM" works well*/
            
            Properties initialIbisProps = execute.bot.myIbisProps;      
            execute.bot.poolName = initialIbisProps.get(IbisProperties.POOL_NAME)+"-executionPhase";
            execute.bot.myIbisProps.setProperty(IbisProperties.POOL_NAME, 
            		execute.bot.poolName);
            execute.bot.electionName = initialIbisProps.get("ibis.election.name")+"-executionPhase";
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
            }
            return new MethodReportError(ex.getLocalizedMessage());
        }
        return new MethodReportSuccess("Ok.");
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
}
