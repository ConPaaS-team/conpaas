package org.koala.runnersFramework.runners.bot;


/**
 * This class contains metadata for a cluster, with some default values.
 */
public class ClusterMetadata {

    String className = "";
    String hostName = "localhost";
    String alias = "localhost";
    int port = 80;
    long timeUnit;
    int costUnit;
    int maxNodes;
    String instanceType = "";
    String speedFactor = "1";
    int image_id = 0;
    int network_id = 0;
    String keyPairName = "";
    String keyPairPath = "";
    String accessKey = "";
    String secretKey = "";
    String dns = "";
    String gateway = "";
    
}