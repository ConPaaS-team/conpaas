package org.koala.runnersFramework.runners.bot;

public class ItemType {
	double cost;
	double speed;	
	int max;
	int needed;
	String cluster;
	
	public ItemType(double cost, double speed, int max, String alias) {
		super();
		this.cost = cost;
		this.speed = speed;
		this.max = max;
		this.needed = 0;
		this.cluster = alias;
	}
	
	
}
