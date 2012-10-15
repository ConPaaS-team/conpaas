package org.koala.runnersFramework.runners.bot.listener;

/**
 * This interface supports just the last executed sampling. All sampling support
 * offered in BatsServiceApi_Later
 *
 * @author maricel
 */
public interface BatsServiceApi {
    
    /**
     * @param filesLocation Mounted folder containing files to be executed by
     * the bag
     * @param inputFile Bag of Tasks file description
     * @return
     */
    public MethodReport start_sampling(String filesLocation, String inputFile);

    public MethodReport start_execution(long schedulesFileTimeStamp, int scheduleNo);

    /**
     * In case the API was successful, it will return a String[] object with the
     * list of schedules; otherwise, it will return a MethodReport object
     * describing the exceptions which took place.
     *
     * @return
     */
    public Object get_sampling_results();

    public State get_service_info();

    public MethodReport get_log();

    public MethodReport terminate_workers();
    
    public MethodReport set_service_mode(String mode);
    
    public MethodReport execute_command(String command);
}