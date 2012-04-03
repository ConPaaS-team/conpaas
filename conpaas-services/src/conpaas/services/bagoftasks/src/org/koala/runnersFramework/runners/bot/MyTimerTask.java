package org.koala.runnersFramework.runners.bot;

import ibis.ipl.Ibis;
import ibis.ipl.IbisIdentifier;

import java.io.IOException;
import java.util.TimerTask;
import java.util.logging.Level;
import java.util.logging.Logger;

public class MyTimerTask extends TimerTask {

    private Ibis myIbis;
    private IbisIdentifier from;
    private Cluster cluster;

    public MyTimerTask(Cluster cluster, Ibis myIbis, IbisIdentifier from) {
        super();
        this.cluster = cluster;
        this.myIbis = myIbis;
        this.from = from;
    }

    @Override
    public void run() {
        try {
            cluster.terminateWorker(from, myIbis);
        } catch (IOException ex) {
            Logger.getLogger(MyTimerTask.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
}
