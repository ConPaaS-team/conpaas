package org.koala.runnersFramework.runners.bot.listener;

public class MethodReportError implements MethodReport {

    public StringBuilder error;

    MethodReportError() {
        this.error = new StringBuilder();
    }

    MethodReportError(String msg) {
        this.error = new StringBuilder(msg);
    }

    @Override
    public void append(String msg) {
        this.error.append(msg);
    }

    @Override
    public void clear() {
        this.error.delete(0, error.length());
    }

    @Override
    public String toString() {
        return this.error.toString();
    }
}
