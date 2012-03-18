package org.koala.runnersFramework.runners.bot;

import ibis.ipl.IbisIdentifier;

import java.util.logging.Level;
import java.util.logging.Logger;

import org.opennebula.client.Client;
import org.opennebula.client.OneResponse;
import org.opennebula.client.vm.VirtualMachine;

import org.opennebula.client.Client;
import org.opennebula.client.OneResponse;
import org.opennebula.client.vm.VirtualMachine;

public class OneVMWorker extends VMWorker {

	OneVMWorker(String masterID, String poolName, String serverAddress, String speedFactor)
            throws Exception {
        super(masterID, poolName, serverAddress, speedFactor);
    }

    public static void main(String[] args) {
        System.out.println("Command received...");
        try {
            OneVMWorker vmWorker = new OneVMWorker(args[0], args[1], args[2], args[3]);
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
            /*
             * in order for this constructor to succeed,
             * the following env vars need to be properly set:
             * $ONE_AUTH=~/.one/one_auth
             * $ONE_XMLRPC=http://localhost:2633/RPC2
             */
            Client oneClient = new Client();
            int vmId = Integer.parseInt(System.getenv("VM_ID"));
            VirtualMachine vm = new VirtualMachine(vmId, oneClient);
            OneResponse oneResponse = vm.finalizeVM();
            if (oneResponse.isError()) {
                System.err.println("Failed to finalize VM:\n"
                        + oneResponse.getMessage());
            } else {
                System.err.println("All went fine...");
            }
        } catch (Exception ex) {
            System.err.println(ex.getMessage());
        }

    }

}
