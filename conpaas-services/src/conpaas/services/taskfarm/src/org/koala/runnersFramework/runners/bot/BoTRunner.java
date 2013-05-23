package org.koala.runnersFramework.runners.bot;

import org.koala.runnersFramework.runners.bot.BagOfTasks;

import ibis.ipl.IbisProperties;

import java.io.File;

import java.io.IOException;
import java.io.Serializable;
import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;


import org.koala.runnersFramework.runners.bot.DummyMaster;
import org.koala.runnersFramework.runners.bot.Job;
import org.koala.runnersFramework.runners.bot.MinMaxMaster;
import org.koala.runnersFramework.runners.bot.MinMinMaster;
import org.koala.runnersFramework.runners.bot.NaiveMaster;
import org.koala.runnersFramework.runners.bot.listener.BatsServiceApiImpl;

public class BoTRunner implements Serializable {

    /*
     * change static fields to allow more bags run in the same jvm
     */
    public static String path;
    /*
     * the URL which is to be mounted by the workers
     */
    public static String filesLocationUrl;
    /*
     * file from where to read cluster configuration
     */
    public String clusterConfigurationFile =
            "ClusterConfiguration/clusterConf.xml";
    /*
     * file from where to read tasks, with default value
     */
    public String inputFile = "BagOfTasks/bagOfTasks.bot";
    /*
     * file in which to deposit schedules after sampling phase
     */
    public static String schedulesFile;
    public Properties myIbisProps;
    static double INITIAL_TIMEOUT_PERCENT = 0.1;
    // static final String electionName = "BoT";
    private static final int MINE = 0;
    private static final int RR = 1;
    private static final int MINMIN = 2;
    private static final int MINMAX = 3;
    private static final int DUMMY = 4;
    private static final int SAMPLING = 5;
    private static final int SAMPLEFREE = 6;
    public String poolName, electionName, serverAddress;
    public ArrayList<Job> tasks;
    public Set<Job> finishedTasks;
    /*
     * time unit expressed in minutes, it represents the accountable time unit
     */
    long timeUnit;
    /*
     * deadline expressed in minutes
     */
    long deadline;
    /*
     * budget expressed in U.S. dollars
     */
    long budget;
    double zeta;
    double delta;
    int subsetLength;
    int noReplicatedJobs = 7;
    int noSampleJobs;
    int noInitialWorkers;
    HashMap<String, Cluster> Clusters;
    private int masterImpl;
    public int jobsDone = 0;
    public int jobsRemainingAfterSampling = 0;
    public int maxCostATU = 0;
    public int minCostATU = 0;
    public boolean firstTimeAllStatsReady = false;
    public boolean allStatsReady = false;
    public boolean firstStats; /*
     * deprecated
     */

    //the bag of tasks
    public BagOfTasks bag;
    //the master
    transient public Master master;

    public BoTRunner() {
    }

    public BoTRunner(int masterImpl, int sizeBoT,
            long timeUnit, long deadline, long budget,
            String inputFile, String clusterConfigurationFile) {
        // TODO Auto-generated method stub
        this.timeUnit = timeUnit;
        //this.priceTimeUnit = priceTimeUnit;
        this.deadline = deadline;
        this.budget = budget;
        //getComponentsDescription(Utils.readFile(jdfFile));

        zeta = Double.parseDouble(System.getProperty("zeta", "1.96"));
        delta = Double.parseDouble(System.getProperty("delta", "0.25"));

        electionName = System.getProperty("ibis.election.name", "TaskFarmServiceElection");
        poolName = System.getProperty(IbisProperties.POOL_NAME, "TaskFarmServicePool");
        serverAddress = System.getProperty(IbisProperties.SERVER_ADDRESS, "localhost");

        myIbisProps = new Properties();
        myIbisProps.put(IbisProperties.POOL_NAME, poolName);
        myIbisProps.put(IbisProperties.SERVER_ADDRESS, serverAddress);
        myIbisProps.put("ibis.election.name", electionName);


        /*
         * NEW CODE
         */
        /*
         * this is still for control tasks
         */
//         bag = new BagOfTasks();
//         double stDev = Double.parseDouble(System.getProperty("stDev", "" + Math.sqrt(5)));
//         tasks = bag.getBoT(sizeBoT, 5 * 60, stDev * 60, false);
//
        if (inputFile != null && !"".equals(inputFile)) {
            this.inputFile = inputFile;
        }
        if (clusterConfigurationFile != null && !"".equals(clusterConfigurationFile)) {
            this.clusterConfigurationFile = clusterConfigurationFile;
        }

        bag = new BagOfTasks(this.inputFile);

        //bag = new BagOfTasks("./bags/bot-LT-t0-0.366-xmax2700");
        tasks = bag.getBoT();

        BatsServiceApiImpl.serviceState.noTotalTasks = tasks.size();
        BatsServiceApiImpl.serviceState.noCompletedTasks = 0;

        /*
         * bag = new BagOfTasks();// no param means default inputFile; tasks =
         * bag.getBoT(1000,15*60,Math.sqrt(5)*60, false); //arguments are sent
         * in seconds
         */

        /*
         * bag = new BagOfTasks();// no param means default inputFile; double t0
         * = 0.366; double	Xmax = 45*60; double	sigma = 2*Xmax*t0*t0; tasks =
         * bag.generateStableDistributionLevyTruncatedBoT(1000, t0, Xmax);
         *
         * System.out.println("Generating bag with SD Levy Truncated,
         * parameters: " + "t0=" + t0 + "; Xmax=" + Xmax + "; stDev=" + sigma);
         */


        Clusters = new HashMap<String, Cluster>();

        readClustersFromFile();

        aggregateBoTTimeUnit();

        this.masterImpl = masterImpl;
    }

    public void decrementUserCredit(double price) {
       if (price > 0) {
               runShellCommand("/bin/bash /root/ConPaaS/src/conpaas/services/taskfarm/agent/callback.sh decrementUserCredit " + price);
       }
    }

    private void runShellCommand(String cmd) {
            try {
                // Run command
                System.err.println("RUN: " + cmd);
                System.out.println("RUN: " + cmd);
                Process process = Runtime.getRuntime().exec(cmd);
            } catch (Exception e) {
                e.printStackTrace(System.err);
            }
    }

    public void calculateSampleSize()
    {
    	double zeta_sq = this.zeta * this.zeta;
    	this.noSampleJobs = (int) Math.ceil(this.tasks.size() * zeta_sq
				/ (zeta_sq + 2 * (this.tasks.size() - 1) * this.delta * this.delta));
    }
    
    public boolean isBagBigEnoughForReplication()
    {
    	calculateSampleSize();
    	return this.noReplicatedJobs < this.noSampleJobs;
    }
    
    public boolean isBagBigEnoughForSampling()
    {
		Collection<Cluster> clusters = this.Clusters.values();		

		if(this.noSampleJobs*this.Clusters.size() > 0.5 * this.tasks.size())
		{
			return false;
		}
		return true;
    }
    
    private String deadline2ResTime() {

        String dd, hh, mm;
        mm = "" + deadline % 60;
        hh = "" + (deadline / 60) % 24;
        dd = "" + (deadline / 60) / 24;
        return dd + ":" + hh + ":" + mm + ":" + "00";
    }

    public void run() {

        // prepare ibis master
        master = null;

        System.out.println("Trying to instantiate master as: " + masterImpl);
        try {
            if (masterImpl == MINE) {
                master = new MyMaster(this);
            } else if (masterImpl == RR) {
                master = new NaiveMaster(this);
            } else if (masterImpl == MINMIN) {
                master = new MinMinMaster(this);
            } else if (masterImpl == MINMAX) {
                master = new MinMaxMaster(this);
            } else if (masterImpl == DUMMY) {
                master = new DummyMaster(this);
            } else if (masterImpl == SAMPLING) {
                master = new SamplingPhaseMaster(this);
            } else if (masterImpl == SAMPLEFREE) {
                master = new SampleFreeMaster(this);
            }

            System.out.println("Master instantiated as: " + master.getClass().getName());
        } catch (Exception ex) {
            Logger.getLogger(BoTRunner.class.getName()).log(Level.SEVERE, null, ex);
            throw new RuntimeException(ex.getMessage());
        }

        try {
            master.initMasterComm();
        } catch (IOException ex) {
            Logger.getLogger(BoTRunner.class.getName()).log(Level.SEVERE, null, ex);
            System.err.println("master.initMasterComm() failed...");
            throw new RuntimeException(ex.getMessage());
        }

        //start workers, assuming format for reservation time interval "dd:hh:mm:00"
        master.startInitWorkers();

        master.run();
    }

    /**
     * Read the clusters and the required extra information from the file
     * cluster.config
     */
    private void readClustersFromFile() {
        Cluster cluster = null;
        File file = new File(clusterConfigurationFile);
        if (!file.exists()) {
            clusterConfigurationFile = path + "/" + clusterConfigurationFile;
        }

        ClusterXmlFileParser xmlParser = new ClusterXmlFileParser();
        List<ClusterMetadata> listClustersMetadata =
                xmlParser.readConfig(clusterConfigurationFile);

        for (ClusterMetadata cm : listClustersMetadata) {
            cluster = (Cluster) getClusterInstance(cm);
            
	    if (cluster != null) {
                Clusters.put(cluster.alias, cluster);
            }
        }

        System.out.println("Read " + Clusters.size() + " clusters.");

        if (Clusters.isEmpty()) {
            throw new RuntimeException("Read 0 clusters. "
                    + "Need at least 1 cluster to run BoT");
        }
    }

    private void aggregateBoTTimeUnit() {
        this.timeUnit = Long.MAX_VALUE;
        for (Cluster c : Clusters.values()) {
            if (c.timeUnit < this.timeUnit) {
                this.timeUnit = c.timeUnit;
            }
        }

        System.out.println("BoT time unit set to: " + this.timeUnit);
    }

    /**
     * Simpler constructor.
     * @param cm
     * @return 
     */
    private Object getClusterInstance(ClusterMetadata cm) {
        try {
            Class cl = Class.forName(cm.className);
            Class[] cloudClusterClass = new Class[1];
            cloudClusterClass[0] = ClusterMetadata.class;

            java.lang.reflect.Constructor constructor = cl.getConstructor(cloudClusterClass);
            Object invoker = constructor.newInstance(new Object[]{cm});
            if (!(invoker instanceof Cluster)) {
                System.out.println("The class " + cm.className + " is not a subclass of class Cluster.");
                return null;
            }
            return invoker;
        } catch (Exception ex) {
            Logger.getLogger(BoTRunner.class.getName()).log(Level.SEVERE, null, ex);
            return null;
        }
    }

    public static void main(String[] args) {

        int size;
        int masterType;
        long deadline;
        long budget;

        BoTRunner.path = System.getenv().get("BATS_HOME");
        if (BoTRunner.path == null) {
            throw new RuntimeException("Env var BATS_HOME not set!");
        }
        System.out.println("Path to BATS set as:\t" + BoTRunner.path);

        masterType = args.length < 1 ? 5 : Integer.parseInt(args[0]);
        deadline = args.length < 2 ? 24 : Long.parseLong(args[1]);
        budget = args.length < 3 ? 0*400 : Long.parseLong(args[2]); //Bert
        size = args.length < 4 ? 1000 : Integer.parseInt(args[3]); // required for control tests.
        schedulesFile = args.length < 5 ? "SchedulesDump/schedules.ser" : args[4];

        System.out.println("Master of type: " + masterType);
        BoTRunner runner = new BoTRunner(masterType, size, 60, deadline, budget, "", "");

        runner.run();
    }

    public int terminate() throws IOException {
    	if(master != null)
    		return master.terminateAllWorkers();
    	else
    		return 0;
    }
}
