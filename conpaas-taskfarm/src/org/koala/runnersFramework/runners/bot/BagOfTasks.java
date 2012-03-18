package org.koala.runnersFramework.runners.bot;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.Scanner;

/**
 * This class creates/reads a bag of tasks.
 * @author Maricel
 */
public class BagOfTasks implements Serializable {

	private static final long serialVersionUID = -8150549529128640252L;
		
	private ArrayList<Job> tasks;
	private String inputFile;
	
	BagOfTasks(String inputFile) {
		tasks = new ArrayList<Job>();
		this.inputFile = inputFile;
		
		File file = new File(this.inputFile);
        if (!file.exists()) {
            this.inputFile = BoTRunner.path + "/" + this.inputFile;
        }
	}

	BagOfTasks() {
		tasks = new ArrayList<Job>();
	}
	
	String getInputFile() {
		return inputFile;
	}
	
	public void setBotFile(String inputFile) {
        this.inputFile = inputFile;
    }
	
	/**
	 * BoT generator.
	 * @param size
	 * @param mean
	 * @param variance
	 * @param memEffect
	 * @return
	 */
	public ArrayList<Job> getBoT(long size, double mean, double stDev, boolean memEffect) {
		Random random = new Random(999999999);
		long et;

		try {
			FileWriter fstream = new FileWriter(inputFile);
			BufferedWriter out = new BufferedWriter(fstream);

			for (int i = 0; i < size; i++) {
				et = (long) (random.nextGaussian() * stDev + mean);	//in seconds, for accuracy
				while (et <= 0) {
					et = (long) (random.nextGaussian() * stDev + mean);	//in seconds, for accuracy
				}
				//List<String> args = new ArrayList<String>();
				String arg = "" + et;
				if (memEffect) {
					if (et > mean) {
						arg = "" + 2 * et;
					}
				}
				ArrayList<String> argsList = new ArrayList<String>();
				argsList.add(arg);
				tasks.add(new Job(argsList, "/bin/sleep", "" + i));

				out.write("/bin/sleep " + arg + "\n");
			}
			out.close();
		} catch (Exception e) {
			System.err.println("Failed at writing tasks...");
			System.exit(1);
		}

		System.out.println("tasks size: " + tasks.size());// + "; totalNumberTasks: " + totalNumberTasks);
		return tasks;
	}

	public ArrayList<Job> generateStableDistributionBoT (long size, double mean, double dispersion) {
		Random u = new Random(999999999);
		Random z = new Random(999999990);

		long et;

		double alpha = 1.5;
		double beta = 0;
		double nu = dispersion;
		double delta = mean;

		double v, w;

		double Bab, Sab;
		double X;

		try {
			FileWriter fstream = new FileWriter(inputFile);
			BufferedWriter out = new BufferedWriter(fstream);

			for(int i=0 ; i<size ; i++) {
				v = Math.PI*(u.nextDouble()-0.5);
				w = -Math.log(z.nextDouble());

				Bab = Math.atan(beta*Math.tan(Math.PI*alpha*0.5))/alpha;
				Sab = Math.pow(1+beta*beta*Math.pow(Math.tan(Math.PI*alpha*0.5), 2), Math.pow(2*alpha,-1));
				X = Sab * Math.sin(alpha*(v+Bab))/Math.pow(Math.cos(v), Math.pow(alpha,-1))*
				Math.pow(Math.cos(v-alpha*(v+Bab))/w, (1-alpha)/alpha);

				et = (long) (X*dispersion/Math.sqrt(2)+mean);	//in seconds, for accuracy
				while((et<=0) || (et>delta+8*nu)) {
					v = Math.PI*(u.nextDouble()-0.5);
					w = -Math.log(z.nextDouble());

					Bab = Math.atan(beta*Math.tan(Math.PI*alpha*0.5))/alpha;
					Sab = Math.pow(1+beta*beta*Math.pow(Math.tan(Math.PI*alpha*0.5), 2), Math.pow(2*alpha,-1));
					X = Sab * Math.sin(alpha*(v+Bab))/Math.pow(Math.cos(v), Math.pow(alpha,-1))*
					Math.pow(Math.cos(v-alpha*(v+Bab))/w, (1-alpha)/alpha);

					et = (long) (X*dispersion/Math.sqrt(2)+mean);	//in seconds, for accuracy
				}
				//List<String> args = new ArrayList<String>();
				String arg = "" + et;
				String printC1 = et/60 + "m" + et%60 + "s";


				System.out.println("Generated job " + i + " with runtime for slow: " + printC1);

				ArrayList<String> argsList = new ArrayList<String>();
				argsList.add(arg);
				tasks.add(new Job(argsList, "/bin/sleep", "" + i));

				out.write("/bin/sleep " + arg + "\n");
			}
			out.close();
		} catch (Exception e) {
			System.err.println("Failed at writing tasks...");
			System.exit(1);
		}

		System.out.println("stable distribution tasks size: " + tasks.size());// + "; totalNumberTasks: " + totalNumberTasks);
		return tasks;

	}


	public ArrayList<Job> generateStableDistributionLevyTruncatedBoT (long size, double t0, double Xmax) {
		Random u = new Random(999999999);

		long et;
		double nu = 2*Xmax*t0*t0;

		double v;

		double X;

		int negativeETCount = 0;
		try {
			FileWriter fstream = new FileWriter(inputFile);
			BufferedWriter out = new BufferedWriter(fstream);

			for(int i=0 ; i<size ; i++) {
				v = u.nextGaussian();
				X = nu/(v*v);
				et = (long) X;
				while(et>Xmax) {
					negativeETCount ++;
					v = u.nextGaussian();
					X = nu/(v*v);
					et = (long) X;
				}

				String arg = "" + et;
				String printC1 = et/60 + "m" + et%60 + "s";


				System.out.println("Generated job " + i + " with runtime for slow: " + printC1);
				ArrayList<String> argsList = new ArrayList<String>();
				argsList.add(arg);
				tasks.add(new Job(argsList, "/bin/sleep", "" + i));

				out.write("/bin/sleep " + arg + "\n");
			}
			out.close();
		} catch (Exception e) {
			System.err.println("Failed at writing tasks...");
			System.exit(1);
		}

		System.out.println("stable distribution Levy truncated tasks size: " + tasks.size());// + "; totalNumberTasks: " + totalNumberTasks);
		return tasks;
	}


	/**
	 * Gets the BoT from the inputFile - default or specified in constructor.
	 */
	public ArrayList<Job> getBoT() {
		List<String> argsTask;
		String[] argsArray;
		String execTask;
		try {
			Scanner in = new Scanner(new File(inputFile));
			int i = 0;
			while (in.hasNext()) {
				argsArray = in.nextLine().split(" ");
				if (argsArray.length == 0) {
					continue;
				}
				execTask = argsArray[0];

				argsTask = new ArrayList<String>();
				for (int j = 1; j < argsArray.length; j++) {
					argsTask.add(argsArray[j]);
				}

				tasks.add(new Job(argsTask, execTask, "" + (i++)));
			}
		} catch (FileNotFoundException ex) {
			System.err.println("Failed to open input file for real tasks.\n" + ex);
			return null;
		}
		return tasks;
	}

	/**
	 * Cleans the tasks array.
	 */
	public void cleanup() {
		tasks.clear();
	}
}
