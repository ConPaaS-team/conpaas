package org.koala.runnersFramework.runners.bot;

import org.koala.runnersFramework.runners.bot.BagOfTasks;

import ibis.ipl.IbisProperties;

import java.io.File;

import java.io.IOException;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;


import org.koala.runnersFramework.runners.bot.DummyMaster;
import org.koala.runnersFramework.runners.bot.Job;
import org.koala.runnersFramework.runners.bot.MinMaxMaster;
import org.koala.runnersFramework.runners.bot.MinMinMaster;
import org.koala.runnersFramework.runners.bot.NaiveMaster;

public class BoTRunner implements Serializable {

	/*change static fields to allow more bags run in the same jvm*/
	public static String path;
    /* the URL which is to be mounted by the workers */
    public static String filesLocationUrl;
    /* file from where to read cluster configuration*/
    public String clusterConfigurationFile =
            "ClusterConfiguration/clusterConf.xml";
    /* file from where to read tasks, with default value*/
    public String inputFile = "BagOfTasks/bagOfTasks.bot";
    /* file in which to deposit schedules after sampling phase */
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
    public ArrayList<Job> finishedTasks;
    
    /* time unit expressed in minutes, it represents the accountable time unit */
    long timeUnit;    
    /* deadline expressed in minutes */
    long deadline;
    /* budget expressed in U.S. dollars */
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
    public int maxCostATU = 0;
    public int minCostATU = 0;
    public boolean firstTimeAllStatsReady = false;
    public boolean allStatsReady = false;
    
    public boolean firstStats; /*deprecated*/
    
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
        myIbisProps.put("ibis.election.name",electionName);
                
        
        /* NEW CODE */
        /* this is still for control tasks */
//         bag = new BagOfTasks();
//         double stDev = Double.parseDouble(System.getProperty("stDev", "" + Math.sqrt(5)));
//         tasks = bag.getBoT(sizeBoT, 5 * 60, stDev * 60, false);
//
        if (!"".equals(inputFile)) {
            this.inputFile = inputFile;
        }
        if ( !"".equals(clusterConfigurationFile)) {
            this.clusterConfigurationFile = clusterConfigurationFile;
        }
        
        bag = new BagOfTasks(inputFile);
         
        //bag = new BagOfTasks("./bags/bot-LT-t0-0.366-xmax2700");
        tasks = bag.getBoT();
        
         /*
         bag = new BagOfTasks();// no param means default inputFile;
         tasks = bag.getBoT(1000,15*60,Math.sqrt(5)*60, false); //arguments are sent in seconds         
         */
         
         /*
            bag = new BagOfTasks();// no param means default inputFile;
         	double t0 = 0.366;
         	double	Xmax = 45*60;
         	double	sigma = 2*Xmax*t0*t0;
         tasks = bag.generateStableDistributionLevyTruncatedBoT(1000, t0, Xmax);
         
        System.out.println("Generating bag with SD Levy Truncated, parameters: " + 
					"t0=" + t0 + "; Xmax=" + Xmax + "; stDev=" + sigma);
       */ 
         
         
        Clusters = new HashMap<String, Cluster>();
		
        readClustersFromFile();

        aggregateBoTTimeUnit();
        
        this.masterImpl = masterImpl;
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

            System.out.println("Master instantied as: " + master.getClass().getName());
        } catch (Exception ex) {
            Logger.getLogger(BoTRunner.class.getName()).log(Level.SEVERE, null, ex);
            System.exit(1);
        }

        try {
            master.initMasterComm();
        } catch (IOException ex) {
            Logger.getLogger(BoTRunner.class.getName()).log(Level.SEVERE, null, ex);
            System.err.println("master.initMasterComm() failed...");
            System.exit(1);
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
        Cluster cluster;
        File file = new File(clusterConfigurationFile);
        if (!file.exists()) {
            clusterConfigurationFile = path + "/" + clusterConfigurationFile;
        }

        ClusterXmlFileParser xmlParser = new ClusterXmlFileParser();
        List<ClusterMetadata> listClustersMetadata =
                xmlParser.readConfig(clusterConfigurationFile);

        for (ClusterMetadata cm : listClustersMetadata) {
            if (!"".equals(cm.image)) {
                cluster = (Cluster) getClusterInstance(cm.className, cm.hostName, cm.port,
                        cm.alias, cm.timeUnit, cm.costUnit, cm.maxNodes, "" + cm.speedFactor,
                        cm.image, cm.keyPairName, cm.keyPairPath, cm.accessKey, cm.secretKey);
            } else {
                cluster = (Cluster) getClusterInstance(cm.className, cm.hostName,
                        cm.alias, cm.timeUnit, cm.costUnit, cm.maxNodes, cm.speedFactor);
            }
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
    	for(Cluster c : Clusters.values()) {
    		if(c.timeUnit < this.timeUnit) {
    			this.timeUnit = c.timeUnit;
    		}
    	}
    	
    	System.out.println("BoT time unit set to: " + this.timeUnit);
    }
   
 /*   private void readClustersFromPlainFile() {
        String[] clusterInfo;
        Cluster cluster = null;
        String className, clusterName, alias;
        long timeUnit;
        int costUnit, maxNodes;
        double speedFactor;

        try {
            Scanner in = new Scanner(new File("cluster.config"));
            while (in.hasNext()) {
                clusterInfo = in.nextLine().split(" ");

                if (clusterInfo.length != 7) {
                    System.err.println("Skipped one line from cluster.config file");
                    continue;
                }

                className   = clusterInfo[0];
                clusterName = clusterInfo[1];
                alias       = clusterInfo[2];
                timeUnit    = Long.parseLong(clusterInfo[3]);
                costUnit    = Integer.parseInt(clusterInfo[4]);
                maxNodes    = Integer.parseInt(clusterInfo[5]);
                speedFactor = Double.parseDouble(clusterInfo[6]);

                cluster = (Cluster) getClusterInstance(className, clusterName, alias,
                        timeUnit, costUnit, maxNodes, speedFactor);

                if (cluster != null) {
                    Clusters.put(cluster.alias, cluster);
                }
            }
            in.close();
            System.out.println("Read: " + Clusters.size() + " clusters.");
        } catch (FileNotFoundException ex) {
            System.err.println("Failed to open cluster.config file.");
            System.err.println(ex);
            return;
        }
    }
/*
    /**
     * Creates an instance of the class specified in the 1st parameter
     * with the rest of the parameters as arguments.
     */
    /*physical hosts cluster*/
    private Object getClusterInstance(String className, String hostname,
            String alias, long timeUnit, double costUnit, int maxNodes, String speedFactor) {
        try {
            Class cl = Class.forName(className);
            Class[] cloudClusterClass = new Class[6];
            cloudClusterClass[0] = String.class;
            cloudClusterClass[1] = String.class;
            cloudClusterClass[2] = long.class;
            cloudClusterClass[3] = double.class;
            cloudClusterClass[4] = int.class;
            cloudClusterClass[5] = String.class;

            java.lang.reflect.Constructor constructor = cl.getConstructor(cloudClusterClass);
            Object invoker = constructor.newInstance(new Object[]{
                        hostname, alias, timeUnit, costUnit, maxNodes,
                        speedFactor});
            if (!(invoker instanceof Cluster)) {
                System.out.println("The class " + className + " is not a subclass of class Cluster.");
                return null;
            }
            return invoker;
        } catch (Exception ex) {
            Logger.getLogger(BoTRunner.class.getName()).log(Level.SEVERE, null, ex);
            return null;
        }
    }
    
    /*VM hosts cluster*/
    private Object getClusterInstance(String className, String hostname, int port,
            String alias, long timeUnit, double costUnit, int maxNodes, String speedFactor,
            String machineImage, String keyPairName, String keyPairPath,
            String accessKey, String secretKey) {
        try {
            Class cl = Class.forName(className);
            Class[] cloudClusterClass = new Class[12];
            cloudClusterClass[0] = String.class;
            cloudClusterClass[1] = int.class;
            cloudClusterClass[2] = String.class;
            cloudClusterClass[3] = long.class;
            cloudClusterClass[4] = double.class;
            cloudClusterClass[5] = int.class;
            cloudClusterClass[6] = String.class;
            cloudClusterClass[7] = String.class;
            cloudClusterClass[8] = String.class;
            cloudClusterClass[9] = String.class;
            cloudClusterClass[10] = String.class;
            cloudClusterClass[11] = String.class;

            java.lang.reflect.Constructor constructor = cl.getConstructor(cloudClusterClass);
            Object invoker = constructor.newInstance(new Object[]{
                        hostname, port, alias, timeUnit, costUnit, maxNodes,
                        speedFactor, machineImage,
                        keyPairName, keyPairPath,
                        accessKey, secretKey});
            if (!(invoker instanceof Cluster)) {
                System.out.println("The class " + className + " is not a subclass of class Cluster.");
                return null;
            }
            return invoker;
        } catch (Exception ex) {
            Logger.getLogger(BoTRunner.class.getName()).log(Level.SEVERE, null, ex);
            return null;
        }
    }
    /*private Object getClusterInstance(String className, String hostname, String alias,
            long timeUnit, int costUnit, int maxNodes, double speedFactor){
        try {
            Class cl = Class.forName(className);
            java.lang.reflect.Constructor constructor = cl.getConstructor(new Class[]{String.class, String.class, long.class, double.class, int.class, double.class});
            Object invoker = constructor.newInstance(new Object[]{hostname, alias, timeUnit, costUnit, maxNodes, speedFactor});
            if (!(invoker instanceof Cluster)) {
                System.out.println("The class " + className + " is not a subclass of class Cluster.");
                return null;
            }
            return invoker;
        } catch (Exception ex) {
            Logger.getLogger(BoTRunner.class.getName()).log(Level.SEVERE, null, ex);
            return null;
        }
    }*/

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
        budget = args.length < 3 ? 400 : Long.parseLong(args[2]);
        size = args.length < 4 ? 1000 : Integer.parseInt(args[3]); // required for control tests.
        schedulesFile = args.length < 5 ? "SchedulesDump/schedules.ser" : args[4];

        System.out.println("Master of type: " + masterType);
        BoTRunner runner = new BoTRunner(masterType, size, 60, deadline, budget, "", "");

        runner.run();
    }

	public int terminate() throws IOException {
		
		return master.terminateAllWorkers();
				
	}
}
