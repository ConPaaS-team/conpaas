package org.koala.runnersFramework.runners.bot;

import java.io.Serializable;

public class JobStats implements Serializable {
	/*runtime expressed in nanoseconds*/
	private long runtime;
	
	public JobStats(long l) {
		// TODO Auto-generated constructor stub
		runtime = l;
	}

	public long getRuntime() {
		return runtime;
	}

	public void setRuntime(long runtime) {
		this.runtime = runtime;
	}
}
