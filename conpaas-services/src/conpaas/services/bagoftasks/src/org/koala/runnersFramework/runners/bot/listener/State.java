package org.koala.runnersFramework.runners.bot.listener;

public class State {
    
    public String state;

    State(String state) {
        this.state = state;
    }
    
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
