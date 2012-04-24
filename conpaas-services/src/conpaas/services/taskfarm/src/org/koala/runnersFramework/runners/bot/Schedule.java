package org.koala.runnersFramework.runners.bot;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Iterator;

public class Schedule implements Serializable {

    long budget;
    long cost;
    int atus;
    HashMap<String, Integer> machinesPerCluster;
    public boolean extraBudget = false;
    long bDeltaN;
    public int deltaN;

    public Schedule(long budget, long cost, int atus,
            HashMap<String, Integer> machinesPerCluster) {
        super();
        this.budget = budget;
        this.cost = cost;
        this.atus = atus;
        this.machinesPerCluster = machinesPerCluster;
    }

    public Schedule(long bmakespanMin, long bdeltaN, int deltaN, long costPlan,
            int noATUPlan, HashMap<String, Integer> fastestSol) {
        super();
        this.budget = bmakespanMin;
        this.bDeltaN = bdeltaN;
        this.deltaN = deltaN;
        this.cost = costPlan;
        this.atus = noATUPlan;
        this.machinesPerCluster = fastestSol;
        extraBudget = true;
    }

    @Override
    public String toString() {
    	String machines = "";
    	Iterator sols = machinesPerCluster.entrySet().iterator();
    	while(sols.hasNext()) {
    		machines += sols.next() + "\t";
    	}
        return "\t" + budget + "\t" + cost + "\t" + atus + "\t" + machines;
    }
}
