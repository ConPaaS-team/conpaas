package org.koala.runnersFramework.runners.bot;

/**
 * This class contains metadata for a cluster, with some default values.
 */
public class ClusterMetadata {

    String className;
    String hostName = "localhost";
    String alias = "localhost";
    int port = 80;
    long timeUnit;
    int costUnit;
    int maxNodes;
    String speedFactor = "1";
    String image;
    String keyPairName;
    String keyPairPath;
    String accessKey;
    String secretKey;
}