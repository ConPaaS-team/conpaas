package org.koala.runnersFramework.runners.bot;

public class Item {

	double profit;
	int weight;
	String cluster;
	boolean take;
	
	public Item(double profit, int costUnit, String cluster) {
		super();
		this.profit = profit;
		this.weight = costUnit;
		this.cluster = cluster;
	}	
}
