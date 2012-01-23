package org.koala.runnersFramework.runners.bot;

import ibis.ipl.Ibis;
import ibis.ipl.IbisIdentifier;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class G5KCluster extends Cluster {
    /*
    http://lists.gforge.inria.fr/pipermail/grudu-commits/2009-April/000035.html
     */

    String FS;
    String hubAddress;

    public G5KCluster(String hostname, int port, String alias, long timeUnit,
            double costUnit, int maxNodes, String speedFactor
            ) {
        super(hostname, alias, timeUnit, costUnit, maxNodes, speedFactor);
        FS = alias.substring(alias.lastIndexOf("@") + 1);
    }

    public String getHubAddress() {
        return hubAddress;
    }

    public void setHubAddress(String hubAddress) {
        this.hubAddress = hubAddress;
    }

    @Override
    public Process startWorkers(String time, int noWorkers,
            String electionName, String poolName, String serverAddress) {

        if (noWorkers == 0) {
            return null;
        }

        /*start the hub*/
        List<String> cmdList = new ArrayList<String>();
        cmdList.add("ssh");
        cmdList.add("aoprescu@" + hostname);
        cmdList.add("java");
        cmdList.add("-classpath");
        cmdList.add("/home/" + FS + "/aoprescu/ibis/lib/*");
        cmdList.add("-Dlog4j.configuration=file:/home/" + FS + "/aoprescu/ibis/log4j.properties");
        cmdList.add("-Xmx256M");
        cmdList.add("ibis.ipl.server.Server");
        cmdList.add("--hub-only");
        cmdList.add("--hub-addresses");
        cmdList.add(serverAddress);
        String[] cmdarray = cmdList.toArray(new String[0]);

        try {
            Runtime.getRuntime().exec(cmdarray);
        } catch (IOException e1) {
            // TODO Auto-generated catch block
            throw new RuntimeException("BoTRunner: Failed to start hub on " + hostname);
        }

        /*start workers*/
        List<String> workList = new ArrayList<String>();
        workList.add("ssh");
        cmdList.add("aoprescu@" + hostname);

        cmdList.add("prun");
        cmdList.add("-rsh");
        cmdList.add("ssh");
        cmdList.add("-v");
        cmdList.add("-t");
        cmdList.add(time);
        cmdList.add("-1");
        cmdList.add("-no-panda");
        cmdList.add("/usr/local/package/jdk1.6.0-linux-amd64/bin/java");
        cmdList.add(noWorkers + "");
        cmdList.add("-classpath");
        cmdList.add("worker.jar:/home/amo/ibis/lib/*");
        cmdList.add("-Dibis.location.postfix=" + FS);
        cmdList.add("org.koala.runnersFramework.runners.bot.Worker");
        cmdList.add(electionName);
        cmdList.add(poolName);
        cmdList.add(serverAddress);


        String[] workArray = cmdList.toArray(new String[0]);

        try {
            return Runtime.getRuntime().exec(cmdarray);

        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return null;
    }

    @Override
    public void terminateWorker(IbisIdentifier from, Ibis myIbis) {
        System.out.println("No further actions taken to shut down workers.");
    }
}
