package org.koala.runnersFramework.runners.bot;

import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;

public class ContKnap {
	
	ItemType[] types;
	double budget;
	private long atu;
	private double noJobs;
	private long size;
	
	public ContKnap(ItemType[] types, double budget, long atu, long size) {
		super();
		this.types = types;
		this.budget = budget;
		this.atu = atu;
		this.size = size;
	}
	
	class MyComp implements Comparator<ItemType> {

		@Override
		public int compare(ItemType arg0, ItemType arg1) {
			if(arg0.speed > arg1.speed) return -1;
			else if(arg0.speed < arg1.speed) return 1;
			return 0;
		}
		
	}
	
	public HashMap<String, Integer> findSol() {
		
		System.out.println(types.length + " item types " + budget + " budget");
		
		HashMap<String, Integer> finalSol = new HashMap<String, Integer>();
		int noATUs = 0;
		int minNoATUs = Integer.MAX_VALUE;
		
		if(size <= types[0].max+types[1].max) {
			for(int i = 0; i<=types[0].max; i++) {
				for(int j = 0; j <= types[1].max; j++) {	
						noATUs = (int) Math.ceil(size/(atu*(i*types[0].speed+j*types[1].speed)));				
						if((noATUs*(i*types[0].cost + j*types[1].cost) <= budget) && (noATUs <= minNoATUs) && 
								(size >= (i+j))) { 
							minNoATUs = noATUs;
							types[0].needed = i;
							types[1].needed = j;
					
						}
				}
			}
		} else {		
			for(int i = 0; i<=types[0].max; i++) {
				for(int j = 0; j <= types[1].max; j++) {
					for(int k = 0; k <= types[2].max; k++) {
					noATUs = (int) Math.ceil(size/(atu*(i*types[0].speed+j*types[1].speed + k*types[2].speed)));				
						if ((noATUs
								* (i * types[0].cost + j * types[1].cost + k
										* types[2].cost) <= budget)
								&& (noATUs <= minNoATUs)) {
							minNoATUs = noATUs;
							types[0].needed = i;
							types[1].needed = j;
							types[2].needed = k;
						}	
					}
				}
			}
		}
				
		finalSol.put(types[0].cluster, types[0].needed);
		finalSol.put(types[1].cluster, types[1].needed);
		finalSol.put(types[2].cluster, types[2].needed);
		
		System.out.println("Number ATUs: " + minNoATUs + " ; required budget: " 
				+ minNoATUs*(types[0].cost*types[0].needed+types[1].cost*types[1].needed
							+types[2].cost*types[2].needed));
		
	/*Under construction!!!!!!!!!!!*/		
		/*
		 * 
		Arrays.sort(types, new MyComp());
		double noATUs = Double.MAX_VALUE;
		double deadline = 0.0;
		for(int i=0; i<types.length; i++) {
			System.out.println("Inspecting type " + types[i].cluster);
			do{
				types[i].needed --;
				noATUs = Math.ceil(noJobs/(types[i].needed*atu*types[i].speed));
			} while((types[0].needed != 0) || 
				(deadline*types[0].needed*types[0].cost > budget));
		}
		
		do { 
			types[0].needed --;		
			deadline = Math.ceil(noJobs/(types[0].needed*atu*types[0].speed));
		} while((types[0].needed != 0) || 
				(deadline*types[0].needed*types[0].cost > budget));
		
		if(types[0].needed != 0) { finalSol.put(types[0].cluster, types[0].needed); }
		
		budget = budget - Math.ceil(noJobs/(types[0].needed*atu*types[0].speed))*types[0].needed*types[0].cost;
		
		
		for(int i=1; i<types.length; i++) {
			do{
				types[i].needed --;
				if(deadline == Double.MAX_VALUE) 
					deadline = Math.ceil(noJobs/(types[i].needed*atu*types[i].speed));
			}while((types[i].needed != 0) ||
					(deadline*types[i].needed*types[i].cost > budget));
			if(types[i].needed != 0) finalSol.put(types[i].cluster, types[i].needed);
			budget = budget - Math.ceil(noJobs/(types[i].needed*atu*types[i].speed))*types[i].needed*types[i].cost;
		}
		*/
		for(String cluster : finalSol.keySet()) {
        	System.out.println("cluster " + cluster + " : " + finalSol.get(cluster) + " machines");
        }
		return finalSol;
	}

}
