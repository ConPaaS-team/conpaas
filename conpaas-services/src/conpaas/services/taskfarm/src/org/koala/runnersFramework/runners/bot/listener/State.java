package org.koala.runnersFramework.runners.bot.listener;

public class State {
    
    public String state;
    public String mode;
    /*
     * Progress fields.
     */
    public int noTotalTasks;
    public int noCompletedTasks;
    public double moneySpent;
    public double moneySpentSampling;

    State(String state) {
        this.state = state;
        this.mode = MODE_NA;
    }
    
    /**
     * System mode
     */
    public static String MODE_DEMO = "DEMO";
    public static String MODE_REAL = "REAL";
    public static String MODE_NA = "NA";
    
    /**
     * Stable states
     */
    public static String RUNNING = "RUNNING";
    public static String STOPPED = "STOPPED";
    public static String TERMINATED = "TERMINATED";
    public static String PREINIT = "PREINIT";
    public static String INIT = "INIT";
    public static String ERROR = "ERROR";
    
    /**
     * Transient states:
     */
    public static String PROLOGUE = "PROLOGUE";
    public static String EPILOGUE = "EPILOGUE";
    public static String ADAPTING = "ADAPTING";
    
}
