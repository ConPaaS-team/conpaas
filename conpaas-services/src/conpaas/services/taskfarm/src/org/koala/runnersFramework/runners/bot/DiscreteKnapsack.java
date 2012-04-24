package org.koala.runnersFramework.runners.bot;

import java.util.HashMap;

public class DiscreteKnapsack {

	Item[] items;
	int N;
	int wmin;
	int W;
	private long size;
	private long budget;
	private int atu;
	public int noATUPlan;
	public long costPlan;
	public boolean debug = false;
	
	public DiscreteKnapsack(Item[] items, long budget, long size, int minCATU, int allCostATU, int atu) {
		this.items = items;
		wmin = minCATU;
		W = allCostATU;
		this.budget = budget;
		this.size = size;
		N = items.length - 1;
		this.atu = atu;
	}
	
	public HashMap<String, Integer> findSol() {
		
		//System.out.println(N + " items " + W + " sum of costs per ATU");
		
		HashMap<String, Integer> finalSol = new HashMap<String, Integer>();
		
		double[][] opt = new double[N+1][W+1];
        boolean[][] sol = new boolean[N+1][W+1];
        
        for (int n=0; n<=N; n++) {
        	for (int w=0; w<=wmin; w++) {
        		opt[n][w] = 0;
        		sol[n][w] = false;
        	}        		
        }
        
        for (int n = 1; n <= N; n++) {
            for (int w = wmin; w <= W; w++) {

                // don't take item n
                double option1 = opt[n-1][w];

                // take item n
                double option2 = 0;
                if (items[n].weight <= w) {
                	//System.out.println("Might have option");
                	double tmp = opt[n-1][w-items[n].weight];
                	//if(w*Math.ceil((double)size/(atu*(items[n].profit + tmp))) < budget) {
                		option2 = items[n].profit + tmp;
          //      		System.out.println("[n-1][w-wn]=" + tmp + "; Does have option: " + n + ", " + w 
            //    				+ "; need to compare [n][w]" + option2 + " with [n-1][w]=" + option1);
                	//}
                }
                                
                // select better of two options
                opt[n][w] = Math.max(option1, option2);                
                sol[n][w] = (option2 > option1);
                /*
                if((w==81) && sol[n][w]) {
                	System.out.println("[" + n + "][" + w +"]=" + opt[n][w]);
                }*/
            }
        }

        // determine which items to take
        int w=W; int n=N; boolean stop = false;
        int wminATUs = 0; int nminATUs = 0; int minATUs = Integer.MAX_VALUE;
        
        for(; w>0; w--) {
        	for(int i=N; i>0; i--) {
        		if((sol[i][w]) && (w*Math.ceil((double)size/(atu*opt[i][w])) <= budget)){
        			/*  			if(minATUs>Math.ceil((double)size/(atu*opt[i][w]))) { */        				
        			nminATUs=i;
        			wminATUs=w;
        			minATUs=(int)Math.ceil((double)size/(atu*opt[i][w]));
        			System.out.println("Found sol at " + i + ", " + w + ", noATUs=" + minATUs);        				
        			costPlan = w * minATUs;        			
        			stop = true; break;
        		}
        	} if(stop) break;      	
        }
        noATUPlan = minATUs;
        w=wminATUs;
        for (n=nminATUs; n > 0; n--) {
            if (sol[n][w]) {                   	
             items[n].take = true;  w = (int) (w - items[n].weight); 
            	if(!finalSol.containsKey(items[n].cluster)) finalSol.put(items[n].cluster, new Integer(0));
            	finalSol.put(items[n].cluster, new Integer(finalSol.get(items[n].cluster).intValue()+1));
            }
            else           { items[n].take = false;                    }
        }
        
       
        for(String cluster : finalSol.keySet()) {
        	System.out.println("cluster " + cluster + " : " + finalSol.get(cluster) + " machines");
        }

        //print results
        if(debug ) {
        	System.out.println("item" + "\t" + "profit" + "\t" + "weight" + "\t" + "take");
        	for (int i = 1; i <= N; i++) {
        		System.out.println(i + "\t" + items[i].profit + "\t" + items[i].weight + "\t" + items[i].take);
        	}
        }
		return finalSol;		
	}
    
}
