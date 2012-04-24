package org.koala.runnersFramework.runners.bot;

import ibis.ipl.IbisIdentifier;
import java.util.logging.Level;
import java.util.logging.Logger;

public class VMWorker extends Worker {

    VMWorker(String masterID, String poolName, String serverAddress, String speedFactor)
            throws Exception {
        super(masterID, poolName, serverAddress, speedFactor);
    }

    public static void main(String[] args) {
        System.out.println("Command received...");
        try {
            VMWorker vmWorker = new VMWorker(args[0], args[1], args[2], args[3]);
            vmWorker.oneSelfShutdown();
        } catch (Exception ex) {
            Logger.getLogger(VMWorker.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    @Override
    public void gotSignal(String arg0, IbisIdentifier arg1) {
    	
        System.err.println("Lease expired! Closing ibis and shutting down VM...");
        try {
            super.closePorts();
            myIbis.end();
        } catch (Exception ex) {
            System.err.println(ex.getMessage());
        }

        oneSelfShutdown();
        System.err.println("Lease expired! Exiting computation ...");
    }
    
    public void oneSelfShutdown() {
        try {
            Runtime runtime = Runtime.getRuntime();
            Process proc = runtime.exec("shutdown -n -t 0");
        } catch (Exception ex) {
            System.err.println(ex.getMessage());
        }

    }
    
}
