package org.koala.runnersFramework.runners.bot.listener;

public class State {
    
    public String state;
    public String mode;
    public String phase;
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
        this.phase = PHASE_NA;
    }
    
    /**
     * System mode
     */
    public static String MODE_DEMO = "DEMO";
    public static String MODE_REAL = "REAL";
    public static String MODE_NA = "NA";
    
    /**
     * System phase
     */
    public static String PHASE_NA = "NA";
    public static String PHASE_SAMPLING = "SAMPLING";
    public static String PHASE_SAMPLING_READY = "SAMPLING_READY";
    public static String PHASE_FINISHED_WHILE_SAMPLING = "FINISHED_WHILE_SAMPLING";
    public static String PHASE_EXECUTING = "EXECUTING";
    public static String PHASE_FINISHED = "FINISHED";
    
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
