package org.koala.runnersFramework.runners.bot.listener;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.util.ArrayList;
import java.util.logging.FileHandler;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;
import org.koala.runnersFramework.runners.bot.BoTRunner;
import org.koala.runnersFramework.runners.bot.Executor;
import org.koala.runnersFramework.runners.bot.Schedule;

class BatsServiceApiImpl implements BatsServiceApi {

    private final String schedulesFile = "schedules.ser";
    private final Object lock;
    private volatile State serviceState;
    private final String logFile = "exceptions.log";
    private static final Logger exceptionsLogger =
            Logger.getAnonymousLogger();

    public BatsServiceApiImpl() {
        serviceState = new State(State.INIT);
        lock = new Object();
        try {
            Handler handler = new FileHandler(BoTRunner.path + "/" + logFile);
            handler.setFormatter(new SimpleFormatter());
            exceptionsLogger.addHandler(handler);
            exceptionsLogger.log(Level.INFO, "Service started\n");
        } catch (Exception ex) {
            Logger.getLogger(BatsServiceApiImpl.class.getName()).log(
                    Level.SEVERE, null, ex);
        }
    }

    @Override
    public MethodReport start_sampling(String filesLocationUrl,
            String inputFile, String clusterConfigurationFile) {
        MethodReport retVal = new MethodReport("Sampling: ");

        try {
            synchronized (lock) {
                if (State.RUNNING.equals(serviceState.state)) {
                    retVal.append("Failed! Service already running.");
                    return retVal;
                }
                serviceState.state = State.RUNNING;
            }

            final BoTRunner bot = new BoTRunner(5, 0, 60, 24, 400,
                    inputFile, clusterConfigurationFile);

            BoTRunner.schedulesFile = schedulesFile;
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
                        serviceState.state = org.koala.runnersFramework.runners.bot.listener.State.STOPPED;
                    }

                }
            };

            thread.setPriority(Thread.MAX_PRIORITY);
            thread.start();
        } catch (Exception ex) {
            synchronized (lock) {
                serviceState.state = State.STOPPED;
            }
            retVal.append(ex.getLocalizedMessage());
            return retVal;
        }
        retVal.append("Ok.");
        return retVal;
    }

    @Override
    public Object get_sampling_result() {
        MethodReport retVal = new MethodReport("Sampling result: ");
        File file = hasSamplingResult(schedulesFile);

        if (file == null) {
            retVal.append("No sampling result available.");
            return retVal;
        }

        String[] retValue = null;
        FileInputStream fis;
        ArrayList<Schedule> schedules = null;
        try {
            fis = new FileInputStream(file);
            ObjectInputStream ois = new ObjectInputStream(fis);

            // read the BoT, but no need to store it
            ois.readObject();
            schedules = (ArrayList<Schedule>) ois.readObject();

            ois.close();
        } catch (Exception ex) {
            Logger.getLogger(BatsServiceApiImpl_Later.class.getName()).log(Level.SEVERE, null, ex);
        }

        if (schedules == null) {
            retVal.append("File available, but failed to read from it.");
            return retVal;
        }

        retValue = new String[schedules.size() + 1];
        retValue[0] = "\tbudget\tcost\tatus";
        for (int i = 1; i <= schedules.size(); i++) {
            retValue[i] = schedules.get(i).toString();
        }

        return retValue;
    }

    private File hasSamplingResult(String schedulesFile) {
        if (schedulesFile == null) {
            return null;
        }
        String fileName = schedulesFile;

        File file = new File(fileName);
        if (file.exists()) {
            return file;
        }

        fileName = BoTRunner.path + "/" + schedulesFile;
        file = new File(fileName);
        if (file.exists()) {
            return file;
        }

        return null;
    }

    @Override
    public State get_service_info() {
        return serviceState;
    }

    @Override
    public MethodReport start_execution(int scheduleNo) {
        MethodReport retVal = new MethodReport("Execution: ");

        try {
            synchronized (lock) {
                if (schedulesFile == null) {
                    retVal.append("Failed! No schedules file present.");
                    return retVal;
                }
                if ("RUNNING".equals(serviceState.state)) {
                    retVal.append("Failed! Service already running.");
                    return retVal;
                }
                serviceState.state = State.RUNNING;
            }

            String[] args = {"" + scheduleNo, schedulesFile};

            final Executor execute = new Executor(args);

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
                        serviceState.state = org.koala.runnersFramework.runners.bot.listener.State.STOPPED;
                    }
                }
            };

            thread.setPriority(Thread.MAX_PRIORITY);
            thread.start();
        } catch (Exception ex) {
            synchronized (lock) {
                serviceState.state = State.STOPPED;
            }
            retVal.append(ex.getLocalizedMessage());
            return retVal;
        }
        retVal.append("Ok.");
        return retVal;
    }

    @Override
    public MethodReport get_log() {
        MethodReport retVal = new MethodReport("Log:\n");
        try {
            BufferedReader br = new BufferedReader(new InputStreamReader(
                    new FileInputStream(BoTRunner.path + "/" + logFile)));
            String line;
            while ((line = br.readLine()) != null) {
                retVal.append(line + "\n");
            }
            br.close();
        } catch (IOException ex) {
            retVal.append(ex.getLocalizedMessage());
        }
        return retVal;
    }
}
