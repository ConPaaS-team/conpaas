package org.koala.runnersFramework.runners.bot.listener;

/**
 * This interface supports all samplings
 * @author maricel
 */
public interface BatsServiceApi_Later {

    /**
     * @param filesLocation Mounted folder containing files to be executed by the bag
     * @param inputFile Bag of Tasks file description
     * @param clusterConfigurationFile Cluster file description
     * @return 
     */
    public MethodReport start_sampling(String filesLocation,
            String inputFile, String clusterConfigurationFile);

    /**
     * In case the API was successful, it will return a 
     * String[] object with the list of schedules;
     * otherwise, it will return a 
     * MethodReport object describing the exceptions which took place.
     * @return 
     */
    public Object get_sampling_result(String filesLocation,
            String inputFile, String clusterConfigurationFile);

    /**
     * Requires the same first 3 params as in the sampling in order to get
     * the corresponding output from the sampling phase.
     * It will also require the schedule number.
     * @param filesLocationUrl
     * @param inputFile
     * @param clusterConfigurationFile
     * @param scheduleNo
     * @return 
     */
    public MethodReport start_execution(String filesLocationUrl,
            String inputFile, String clusterConfigurationFile,
            int scheduleNo);

    /**
     * Possible states:
     * Idle, Sampling, Executing, Failed
     * @return 
     */
    public State get_service_info();

    public MethodReport get_log();
}
