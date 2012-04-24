package org.koala.runnersFramework.runners.bot;

import java.util.Properties;
import ibis.ipl.IbisProperties;

/*
 * This class is to setup the ibis environment before 
 * calling BaTS executer from console.
 */

public class ExecutorConsole {
	
	public static void main(String[] args) {
		final Executor execute = new Executor(args);
		Properties initialIbisProps = execute.bot.myIbisProps;      
		execute.bot.poolName = initialIbisProps.get(IbisProperties.POOL_NAME)+"-executionPhase";
		execute.bot.myIbisProps.setProperty(IbisProperties.POOL_NAME, 
				execute.bot.poolName);
		execute.bot.electionName = initialIbisProps.get("ibis.election.name")+"-executionPhase";
		execute.bot.myIbisProps.setProperty("ibis.election.name", 
				execute.bot.electionName);
		execute.go();
	}
	
}
