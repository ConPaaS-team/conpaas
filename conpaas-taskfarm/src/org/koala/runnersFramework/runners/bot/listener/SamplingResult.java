package org.koala.runnersFramework.runners.bot.listener;

import java.util.List;

public class SamplingResult {
    public String timestamp;
    public List<String> schedules;
    
    SamplingResult(String ts, List<String> sched) {
        this.timestamp = ts;
        this.schedules = sched;
    }
}
