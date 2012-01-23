
package org.koala.runnersFramework.runners.bot;

import ibis.ipl.Ibis;
import ibis.ipl.IbisIdentifier;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class DAS3Cluster extends Cluster {

    String FS;

    public DAS3Cluster(String hostname, String alias, long timeUnit,
            double costUnit, int maxNodes, String speedFactor
            ) {
        super(hostname, alias, timeUnit, costUnit, maxNodes, speedFactor);
        this.FS = alias.substring(alias.lastIndexOf("@") + 1);
        // keyPairName, keyPathName, accessKey, secretKey = n/a.
    }

    @Override
    public Process startWorkers(String time, int noWorkers,
            String electionName, String poolName, String serverAddress) {

        if (noWorkers == 0) {
            return null;
        }

        List<String> cmdList = new ArrayList<String>();

        cmdList.add("ssh");
        cmdList.add(hostname);
        cmdList.add("prun");
        cmdList.add("-rsh");
        cmdList.add("ssh");
        cmdList.add("-asocial");
        cmdList.add("-v");
        cmdList.add("-t");
        cmdList.add(time);
        cmdList.add("-1");
        cmdList.add("-no-panda");
        cmdList.add("/usr/local/package/jdk1.6.0-linux-amd64/bin/java");
        cmdList.add(noWorkers + "");
        cmdList.add("-classpath");
        cmdList.add(BoTRunner.path + "/worker.jar:" + BoTRunner.path + "/ipl-2.2/lib/*");
        cmdList.add("-Dibis.location.postfix=" + FS);
        cmdList.add("org.koala.runnersFramework.runners.bot.Worker");
        cmdList.add(electionName);
        cmdList.add(poolName);
        cmdList.add(serverAddress);
        cmdList.add(speedFactor);

        String[] cmdarray = cmdList.toArray(new String[0]);

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

