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

    /**
     * author Ana
     * BoT generator.
     * @param size
     * @param mean
     * @param variance
     * @param memEffect
     * @return
     */
    public ArrayList<Job> getBoT(long size, double mean, double variance, boolean memEffect) {
        Random random = new Random(999999999);
        long et;

        try {
            FileWriter fstream = new FileWriter(this.inputFile);
            BufferedWriter out = new BufferedWriter(fstream);

            for (int i = 0; i < size; i++) {
                et = (long) (random.nextGaussian() * variance + mean);	//in seconds, for accuracy
                while (et <= 0) {
                    et = (long) (random.nextGaussian() * variance + mean);	//in seconds, for accuracy
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
            throw new RuntimeException("Failed writing generated tasks.");
        }

        System.out.println("tasks size: " + tasks.size());// + "; totalNumberTasks: " + totalNumberTasks);
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
            File file = new File(this.inputFile);
            Scanner in = new Scanner(file);
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
            throw new RuntimeException("Failed to open input file for real tasks.\n" + ex);
        }
        return tasks;
    }

    /**
     * Cleanes the tasks array.
     */
    public void cleanup() {
        tasks.clear();
    }
}
