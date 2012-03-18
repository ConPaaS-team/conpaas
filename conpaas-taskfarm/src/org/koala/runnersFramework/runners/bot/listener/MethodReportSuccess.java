package org.koala.runnersFramework.runners.bot.listener;

public class MethodReportSuccess implements MethodReport {

    public StringBuilder message;

    MethodReportSuccess() {
        this.message = new StringBuilder();
    }

    MethodReportSuccess(String msg) {
        this.message = new StringBuilder(msg);
    }

    @Override
    public void append(String msg) {
        this.message.append(msg);
    }

    @Override
    public void clear() {
        this.message.delete(0, message.length());
    }

    @Override
    public String toString() {
        return this.message.toString();
    }
}
