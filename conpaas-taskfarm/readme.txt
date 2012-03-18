$BATS_HOME=absolute path to your BaTS installation, where the lib directory containing the necessary libraries can be found.

====================================================================================
SOLVED!
MAJOR unresolved issue: hard-coded path:

- in OpenNebulaOcaCluster:createVmTemplate():
		- modified the value of the "files" attribute from the template. See code:

	String path = "/home/vumaricel/batsManager";
        
        String pathToInitSh = path +"/OpenNebulaCluster/init.sh";
        String pathToIdRsaPub = path + "/OpenNebulaCluster/id_rsa.pub";

because:
- BoTRunner.path is relative to the VMMaster, so on a VM it would be: /home/opennebula/BoT/
- but the "onevm create" command is executed by the ONE admin (bzcmaier) on the frontend, thus the path is treated relative to the front-end
- also, the files need to be accessible by bzcmaier;
- I have tried: files = root@10.200.0.92:/home/.../init.sh but the user bzcmaier cannot access the machine in order to get the files, and his public key is not available to contextualize the workers with his public key.

==============================================================================
Protocol:
- once the service is running, it listens on port 8475 for incomming requests
- only POST requests are allowed
- once a request comes in, it is parsed and handled as a jsonrpc call. 
The available APIs are clearly written and documented in the file org/koala/runnersFramework/runners/bot/listener/BatsServiceApi.java
- for each request, a corresponding verbose json response is provided.
- any exception/error on run-time is logged in the exceptions.log file, 
and for any non-valid calls, proper error messages are returned

==============================================================================
All the new implementations for the listener are in the sub-package: org.koala.runnersFramework.runners.bot.listener.

Modifications:
- the init.sh file for workers (found in OpenNebulaCluster):
		- copies from a predetermined mounting point the (latest) conpaas-bot.jar
		- modified to mount a received url: $MOUNTURL
- refactored the BoTRunner constructor: also takes in bagOfTasksDescription filename and clusterConfig filename.
- replaced every System.exit() with throw new RuntimeException("some_message") , because it would kill the JVM that listens on the port
======================================================================================
Scripts, images and other files:

- in $BATS_HOME/manager you will find a template for the BaTS manager and the init.sh script.

-DEPRECATED: in OpenNebulaCluster folder there are the public key and init.sh for the workers.

- lib contains all the jars required by the jvm to function properly 
and the conpaas-bot.jar which it generates after calling ./compile. 
Note: after a recompilation, copy the new conpaas-bot.jar to $MOUNTURL.
 

