package org.koala.runnersFramework.runners.bot;

import java.io.File;
import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * This class launches the execution based on already computed schedules.
 * [can also list schedules].
 * @author Maricel
 */
public class Executor {

    private ArrayList<Schedule> schedules;
    private BoTRunner bot;
    // boolean to determine whether to print or run selected|default schedule
    private boolean run = true;
    private int selectedSchedule;
    private String schedulesFile;

    /*
     * This constructor takes as parameters: "<schedule_number>"
     * and an optional filename from which to take the schedules.
     * The default filename is BoTRunner.schedulesFile
     */
    public Executor(String[] args) {

        if (args.length != 2) {
            throw new RuntimeException("Usage: list|<number> file");
        }

        if (args[0].equals("list")) {
            run = false;
        }

        // the file from which to read the schedules is overriden
        schedulesFile = args[1];
        if (!(new File(schedulesFile).isAbsolute())) {
            schedulesFile = BoTRunner.path + "/"
                    + schedulesFile;
        }

        try {
            deserializeSchedules();
        } catch (Exception ex) {
            throw new RuntimeException("Unable to deserialize the schedules from file.\n" + ex);
        }

        if (run) {
            selectedSchedule = Integer.parseInt(args[0]);
            if (selectedSchedule < 0 || selectedSchedule >= schedules.size()) {
                throw new RuntimeException("Invalid schedule number. Schedules "
                        + "are from 0 to " + (schedules.size() - 1) +
                        "Usage: list|<number> file ");
            }
            System.out.println("You have chosen schedule no. " + selectedSchedule
                    + ":\n" + schedules.get(selectedSchedule).toString());
        }
    }

    public void go() {
        if (run) {
            run();
        } else {
            list();
        }
    }

    public void list() {
        System.out.println("Schedules:");
        for (int i = 0; i < schedules.size(); i++) {
            System.out.println(i + ".\t" + schedules.get(i).toString());
        }
    }

    public void run() {
        Master master = null;

        int whichMaster = 1;
        try {
            master = new ExecutionPhaseMaster(bot, schedules.get(selectedSchedule));            
        } catch (Exception ex) {
            Logger.getLogger(Executor.class.getName()).log(Level.SEVERE, null, ex);
        }

        try {
            master.initMasterComm();
            // start workers, assuming format for reservation time interval "dd:hh:mm:00"
            master.startInitWorkers();
            master.run();
        } catch (Exception ex) {
            throw new RuntimeException("Master init/startInitWorkers/run failed.\n" + ex);
        }
    }

    private void deserializeSchedules() throws Exception {
        FileInputStream fis = new FileInputStream(schedulesFile);
        ObjectInputStream ois = new ObjectInputStream(fis);

        bot = (BoTRunner) ois.readObject();
        schedules = (ArrayList<Schedule>) ois.readObject();
        ois.close();
        
        // no further use for this file, but just to know from where bot was deserialized
        bot.schedulesFile = schedulesFile;

        // get the remaining tasks.
        bot.tasks = bot.bag.getBoT();

        System.out.println("cluster size: " + bot.Clusters.size());

        for (Cluster c : bot.Clusters.values()) {
            System.out.println("Cluster alias: " + c.alias + ", hostname: " + c.hostname);
        }

        System.out.println("Number of initial tasks: " + bot.tasks.size());
        bot.tasks.removeAll(bot.finishedTasks);
        System.out.println("Number of remaining tasks: " + bot.tasks.size());
    }

    /**
     * This executor receives as parameter:
     *  - list : lists all available schedules.
     *      OR
     *  - <number> : loads the schedule with number <number>
     *
     *      AND:
     *  - file : filename of schedules.
     *
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        // it will survive the constructor only if the arguments are passed correctly.
        Executor execute = new Executor(args);
        execute.go();
    }
}
