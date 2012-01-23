package org.koala.runnersFramework.runners.bot;

import java.io.File;
import java.io.IOException;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public class BoTRunner implements Serializable {

    public static String path;
    /* the URL which is to be mounted by the workers */
    public static String filesLocationUrl;
    /* file from where to read cluster configuration*/
    public String clusterConfigurationFile =
            "ClusterConfiguration/clusterConf.xml";
    /* file from where to read tasks */
    public String inputFile = "BagOfTasks/bagOfTasks.bot";
    /* file in which to deposit schedules after sampling phase */
    public static String schedulesFile;
    
    static double INITIAL_TIMEOUT_PERCENT = 0.1;
    static final String electionName = "BoT";
    private static final int MINE = 0;
    private static final int RR = 1;
    private static final int MINMIN = 2;
    private static final int MINMAX = 3;
    private static final int DUMMY = 4;
    private static final int SAMPLING = 5;
    private static final int SAMPLEFREE = 6;
    /*begin for hpdc tests*/
    private static String CLUSTER1;
    protected static String CLUSTER2;
    /*end for hpdc tests*/
    String poolName, serverAddress;
    public ArrayList<Job> tasks;
    public ArrayList<Job> finishedTasks;
    /* time unit expressed in minutes, it represents the accountable time unit */
    long timeUnit;
    /* price per time unit, expressed in U.S. dollars*/
    //double priceTimeUnit;
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
    public boolean firstStats;
    //the bag of tasks
    public BagOfTasks bag;

    public BoTRunner() {
    }
    
    public BoTRunner(int masterImpl, int sizeBoT,
            long timeUnit, long deadline, long budget,
            String inputFile, String clusterConfigurationFile) {
        this.timeUnit = timeUnit;
        //this.priceTimeUnit = priceTimeUnit;
        this.deadline = deadline;
        this.budget = budget;
        //getComponentsDescription(Utils.readFile(jdfFile));

        zeta = Double.parseDouble(System.getProperty("zeta", "1.96"));
        delta = Double.parseDouble(System.getProperty("delta", "0.25"));

        if (!"".equals(inputFile)) {
            this.inputFile = inputFile;
        }
        if ( !"".equals(clusterConfigurationFile)) {
            this.clusterConfigurationFile = clusterConfigurationFile;
        }
        
        bag = new BagOfTasks(inputFile);
        tasks = bag.getBoT();
        
        Clusters = new HashMap<String, Cluster>();

        readClustersFromFile();

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
        Master master = null;

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
            } else if (masterImpl == SAMPLING) {
                master = new SamplingPhaseMaster(this);
            } 

            System.out.println("Master instantied as: " + master.getClass().getName());
        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }

        try {
            master.initMasterComm();
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }

        //start workers, assuming format for reservation time interval "dd:hh:mm:00"
        master.startInitWorkers();

        master.run();
    }

    /**
     * Read the clusters and the required extra information from the file
     * clusterConfiguration/cluster.config
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

    /**
     * Creates an instance of the class specified in the 1st parameter
     * with the rest of the parameters as arguments.
     */
    private Object getClusterInstance(String className, String hostname,
            String alias, long timeUnit, int costUnit, int maxNodes, String speedFactor) {
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

    private Object getClusterInstance(String className, String hostname, int port,
            String alias, long timeUnit, int costUnit, int maxNodes, String speedFactor,
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
}
