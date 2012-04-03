package org.koala.runnersFramework.runners.bot.listener;

public class MethodReport {
    public StringBuilder message;
    
    MethodReport() {
        this.message = new StringBuilder();
    }
    
    MethodReport(String msg) {
        this.message = new StringBuilder(msg);
    }
    
    public void append(String msg) {
        this.message.append(msg);
    }
    
    public void clear() {
        this.message.delete(0, message.length());
    }
    
    @Override
    public String toString() {
        return this.message.toString();
    }
}

