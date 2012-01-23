package org.koala.runnersFramework.runners.bot;

import ibis.ipl.Ibis;
import ibis.ipl.IbisIdentifier;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.opennebula.client.Client;
import org.opennebula.client.OneResponse;
import org.opennebula.client.vm.VirtualMachine;

public class OpenNebulaOcaCluster extends Cluster {

    transient int currentNoNodes = 0;
    public String image;
    /**
     * Map used for shutting down the machines from the managerial level. 
     * Maps location to VM id. 
     */
    public HashMap<String, String> map = new HashMap<String, String>();
    /**
     * Object used to execute ONE commands.
     */
    public transient Client oneClient = null;
    public static final String dns = "130.73.121.1";
    public static final String gateway = "10.0.0.1";

    public OpenNebulaOcaCluster(String hostname, int port, String alias, long timeUnit,
            double costUnit, int maxNodes, String speedFactor,
            String image, String b, String c, String d, String e) {
        super(hostname, alias, timeUnit, costUnit, maxNodes, speedFactor);
        this.image = image;
    }

    private void setOneClient() {
        if (oneClient == null) {
            try {
                /*
                 * First of all, a Client object has to be created.
                 * Here the client will try to connect to OpenNebula using the default 
                 * options: the auth file is assumed to be at $ONE_AUTH, and the 
                 * endpoint will be set to the environment variable $ONE_XMLRPC.
                 * 
                 * $ONE_AUTH=~/.one/one_auth
                 * $ONE_XMLRPC=http://localhost:2633/RPC2
                 */
                String auth, xmlrpc;
                auth = System.getenv().get("ONE_AUTH");
                xmlrpc = System.getenv().get("ONE_XMLRPC");
                System.out.println("Initializing ONE client with one_auth=" + auth + "  and one_xmlrpc=" + xmlrpc);
                oneClient = new Client();
                System.out.println("ONE client initialized...");
            } catch (Exception ex) {
                Logger.getLogger(OpenNebulaOcaCluster.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }

    @Override
    public Process startWorkers(String time, int noWorkers,
            String electionName, String poolName, String serverAddress) {

        System.out.println("Starting " + noWorkers + " workers with ONE...");

        // place here and not in constructor, because client is not serializable,
        // so when the deserializing at the Executor occurs, oneClient will be null.
        setOneClient();

        String vmTemplate, vmId, location;
        OneResponse rc;

        /*
         * I understand this caused you trouble, so I commented it out
        if (noWorkers == 0 || (currentNoNodes + noWorkers >= maxNodes)) {
        return null;
        }
         */

        int noWorkersNotStarted = 0, currentNo;

        for (int i = 0; i < noWorkers; i++) {
            currentNo = currentNoNodes + i - noWorkersNotStarted;
            location = "node" + currentNo + "@" + alias;

            // create a VM template
            vmTemplate = createVMTemplate(electionName, poolName, serverAddress,
                    speedFactor, location);

            rc = VirtualMachine.allocate(oneClient, vmTemplate);
            if (rc.isError()) {
                System.err.println("Failed starting the "
                        + currentNo + "-th worker!\nError msg: "
                        + rc.getErrorMessage()
                        + "\nONE template:\n"
                        + vmTemplate);
                System.err.flush();
                noWorkersNotStarted++;
                continue;
            }

            // The response message is the new VM's ID
            vmId = rc.getMessage();
            System.out.println("ONE worker with id " + vmId + " started ...");

            // Gather information about the virtual machines and place it in the hash map
            map.put(location, vmId);
        }
        currentNoNodes += noWorkers - noWorkersNotStarted;

        return null;
    }

    private String createVMTemplate(String electionName, String poolName,
            String serverAddress, String speedFactor, String location) {
        /**
         * TO DO:
         * HORRIBLE ISSUE:
         * The paths to init.sh and id_rsa.pub need to be accessible 
         * by the ONE admin (bzcmaier) - for a successful onevm create command.
         * Thus, on a VM, where BoTRunner.path is relative to that machine,
         * it is useless.
         * 
         * POSSIBLE SOLUTION:
         * just put these 2 files on the front-end somewhere accessible to anyone,
         * irrespective of the user.
         */
//        String pathToInitSh = BoTRunner.path + "/OpenNebulaCluster/init.sh";
//        String pathToIdRsaPub = BoTRunner.path + "/OpenNebulaCluster/id_rsa.pub";
        String path = "/home/vumaricel/batsManager";

        String pathToInitSh = path + "/OpenNebulaCluster/init.sh";
        String pathToIdRsaPub = path + "/OpenNebulaCluster/id_rsa.pub";

        String vmTemplate =
                "NAME = BoTSVM\n"
                + "CPU = 1\n"
                + "MEMORY = 400\n\n"
                + "OS     = [\n"
                + "arch = x86_64\n"
                + "]\n\n"
                + "DISK   = [\n"
                + "image   = \"" + image + "\",\n"
                + "target  = \"sda\"\n"
                + "]\n\n"
                + "NIC    = [\n"
                + "NETWORK = \"Private LAN\"\n"
                + "]\n\n"
                + "GRAPHICS = [\n"
                + "TYPE    = \"vnc\",\n"
                + "LISTEN  = \"0.0.0.0\"\n"
                + "]\n\n"
                + "FEATURES = [\n"
                + "acpi=\"yes\"\n"
                + "]\n\n"
                + "RAW = [\n"
                + "type = \"kvm\",\n"
                + "data = \" <serial type='pty'> <source path='/dev/pts/3'/> <target port='1'/> </serial>\"\n"
                + "]\n\n"
                + "CONTEXT = [\n"
                + "hostname   = \"$NAME\",\n"
                /*+ "dns        = \"$NETWORK[DNS, NAME=\\\"Small network\\\"]\",\n"*/
                + "dns        = " + dns + ",\n"
                /*    + "gateway    = \"$NETWORK[GATEWAY, NAME=\\\"Small network\\\"]\",\n"*/
                + "gateway    = " + gateway + ",\n"
                + "ip_public  = \"$NIC[IP, NETWORK=\\\"Private LAN\\\"]\",\n"
                /* variables required by a BoT worker */
                + "LOCATION=\"" + location + "\",\n"
                + "ELECTIONNAME=\"" + electionName + "\",\n"
                + "POOLNAME=\"" + poolName + "\",\n"
                + "SERVERADDRESS=\"" + serverAddress + "\",\n"
                + "SPEEDFACTOR=\"" + speedFactor + "\",\n"
                + "MOUNTURL=\"" + BoTRunner.filesLocationUrl + "\",\n"
                /* end of vars req by a BoT worker */
                /* variables required for calling the ONE service */
                + "ONE_XMLRPC=\"" + System.getenv().get("ONE_XMLRPC") + "\",\n"
                + "ONE_AUTH_CONTENT=\"" + 
                    getOneAuthContent(System.getenv().get("ONE_AUTH")) + "\",\n"
                + "VM_ID = \"$VMID\",\n"
                /* end - ONE service vars */
                + "files = \"" + pathToInitSh + " " + pathToIdRsaPub + "\",\n"
                + "target = \"sdb\",\n"
                + "root_pubkey = \"id_rsa.pub\",\n"
                + "username = \"opennebula\",\n"
                + "user_pubkey = \"id_rsa.pub\"\n"
                + "]\n";

        return vmTemplate;
    }
    
    private String getOneAuthContent(String oneAuthFile) {
        try {
            BufferedReader br = new BufferedReader(new FileReader(oneAuthFile));
            String retVal = br.readLine();
            br.close();            
            return retVal;
        } catch (Exception ex) {
            return "";
        }
    }

    @Override
    public void terminateWorker(IbisIdentifier node, Ibis myIbis)
            throws IOException {
        myIbis.registry().signal("die", node);
    }
}
