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
    String image = "";
    int image_id = 0;
    int network_id = 0;
    String keyPairName = "";
    String keyPairPath = "";
    String accessKey = "";
    String secretKey = "";
    String dns = "";
    String gateway = "";
    String netmask = "255.255.255.0";
    String disk_target = "sda";
    String contex_target = "sdb";
    String os_arch = "i386";
    String security_group = "default";
    String region = "ec2.us-east-1.amazonaws.com";
}
