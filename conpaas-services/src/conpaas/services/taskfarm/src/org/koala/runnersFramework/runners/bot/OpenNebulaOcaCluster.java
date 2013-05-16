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

	private static final long serialVersionUID = -3283811123364250109L;
    public transient int currentNoNodes = 0;
    public int image_id, network_id;
    public String mem;
    public String dns, gateway, netmask;
    public String diskTarget, contextTarget, OSArch;
    /*number of CPUs for the VM*/
    public String speedFactor;
    /**
     * Map used for shutting down the machines from the managerial level. 
     * Maps location to VM id. 
     */
    public HashMap<String, String> map = new HashMap<String, String>();
    /**
     * Object used to execute ONE commands.
     */
    public transient Client oneClient = null;
    /**
     * irrelevant dns and gateway default values.
     */
    public static final String DEF_MEM = "1024";
    
    
    public OpenNebulaOcaCluster(ClusterMetadata cm) {
        super(cm.hostName, cm.alias, cm.timeUnit, cm.costUnit, cm.maxNodes);
        
	this.image_id = cm.image_id;        
        this.network_id = cm.network_id;
        this.speedFactor = cm.speedFactor;
        this.diskTarget = cm.disk_target;
        this.contextTarget = cm.contex_target;
        this.OSArch = cm.os_arch;
     	this.dns = cm.dns;
	this.netmask = cm.netmask;
        this.mem = DEF_MEM;

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
    public Process startNodes(String time, int noWorkers,
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
            System.out.println("Ibis node with location " + location);
            
        }
        currentNoNodes += noWorkers - noWorkersNotStarted;

        return null;
    }

    private String createVMTemplate(String electionName, String poolName,
            String serverAddress, String speedFactor, String location) {

        String vmTemplate =
                "NAME = taskfarm\n"
                + "CPU = " + speedFactor  + "\n"
                + "MEMORY = " + mem + "\n\n"
                + "OS     = [\n"
                + "arch = " + this.OSArch + "\n"
                + "]\n\n"
                + "DISK   = [\n"
                + "IMAGE_ID  = " + image_id + ",\n"
                + "target  = \"" + diskTarget + "\"\n"
                + "]\n\n"
                + "NIC    = [\n"
                + "NETWORK_ID = " + network_id +"\n"
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
                + "nameserver        = " + dns + ",\n"
                + "ip_gateway    = " + gateway + ",\n"
                + "netmask    = " + netmask + ",\n"
                + "ip_public  = \"$NIC[IP]\",\n"
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
               /*ISSUE: + "files = \"" + pathToInitSh + " " + pathToIdRsaPub + "\",\n"*/
				/* PAY ATTENTION: this will work only if the worker's image is set to run $USERDATA*/
                + "USERDATA = \"" + getHexContent(System.getenv("HEX_FILE")) + "\",\n"
                + "target = \""+ contextTarget + "\"\n"
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

    private String getHexContent(String hexFile) {
        try {
            BufferedReader br = new BufferedReader(new FileReader(hexFile));
            StringBuilder retVal = new StringBuilder();
            String line;
            while( (line = br.readLine()) != null) {
                retVal.append(line).append("\n");
            }
            br.close();            
            return retVal.toString();
        } catch (Exception ex) {
            return "";
        }
    }

    @Override
    public void terminateNode(IbisIdentifier node, Ibis myIbis)
            throws IOException {
		// XXX Another deletion method which can be used when self-VM
		// Deletion causes OpenNebula to crash.
    	try {
                String loc = node.location().toString();
                Integer vm_id = Integer.parseInt(map.get(loc));
                System.err.println("Deleting with loc: " + loc + ", ID: " + vm_id );
                VirtualMachine vm = new VirtualMachine(vm_id, oneClient);
                OneResponse oneResponse = vm.finalizeVM();
                map.remove(loc);
                if (oneResponse.isError()) {
                    System.err.println(this.getClass() + ": Failed to finalize VM:\n"
                            + oneResponse.getMessage());
                } else {
                    System.err.println("All went fine...");
                }
    	}
     	catch(Exception E)
    	{
    		E.printStackTrace();
    	}
		
       // myIbis.registry().signal("die", node);
    }
}
