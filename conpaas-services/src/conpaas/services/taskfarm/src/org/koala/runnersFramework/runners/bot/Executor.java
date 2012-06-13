package org.koala.runnersFramework.runners.bot;

import java.io.File;
import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.util.ArrayList;
import java.util.Collection;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.koala.runnersFramework.runners.bot.listener.BatsServiceApiImpl;

/**
 * This class launches the execution based on already computed schedules.
 * [can also list schedules].
 * @author Maricel
 */
public class Executor {
    
    private ArrayList<Schedule> schedules;
    public BoTRunner bot;
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
            //BatsServiceApiImpl.serviceState.totalMoney = schedules.get(selectedSchedule).budget;
   }
        


    public void go() {
        if (run) {
            run();
        } else {
            list();
        }
    }

    void list() {
    	System.out.println("Solutions:\nNumber\tName\t\tBudget\tMakespan\tMachines");
        String[] schedNames=new String[]{"cheapest", "1.1*cheapest", "1.2*cheapest", "fastest ", "0.9*fastest", "0.8*fastest"};
	for (int i = 0; i < schedules.size(); i++) {
	    String machines = "";
	    for(String cl : schedules.get(i).machinesPerCluster.keySet()) {
		machines += schedules.get(i).machinesPerCluster.get(cl).intValue()==0 ? "" : schedules.get(i).machinesPerCluster.get(cl) + " * " + cl + " ; \n\t\t\t\t\t\t"; 
	    }
            System.out.println(i + ".\t" + schedNames[i] + "\t" + schedules.get(i).budget + "\t" + schedules.get(i).atus + " hours \t" + machines);
        }
    }

    void run() {
        Master master = null;
        
        /* this is still weird!? */
        int whichMaster = 1;
        try {
            if (whichMaster == 0) {
                master = new ExecutionPhaseRRMaster(bot, schedules.get(selectedSchedule));
            } else if (whichMaster == 1) {
                master = new ExecutionPhaseMaster(bot, schedules.get(selectedSchedule));
            } else if (whichMaster == 2) {
                master = new ExecutionTailPhaseMaster(bot, schedules.get(selectedSchedule));
            }
        } catch (Exception ex) {
            Logger.getLogger(Executor.class.getName()).log(Level.SEVERE, null, ex);
        }

        System.out.println("Executor type: " + whichMaster);      
        
        bot.master = master;
        
        try {
            master.initMasterComm();
            // start workers, assuming format for reservation time interval "dd:hh:mm:00"
            master.startInitWorkers();
            master.run();
        } catch (Exception ex) {
            Logger.getLogger(Executor.class.getName()).log(Level.SEVERE, null, ex);
            System.out.println("Master init/startInitWorkers/run failed.");
            throw new RuntimeException(ex.getMessage());
        }
    }

    private void deserializeSchedules() throws Exception {
        FileInputStream fis = new FileInputStream(schedulesFile);
        ObjectInputStream ois = new ObjectInputStream(fis);

        bot = (BoTRunner) ois.readObject();
        schedules = (ArrayList<Schedule>) ois.readObject();
        
        // Also update cache object progress information.
        BatsServiceApiImpl.serviceState.moneySpent = ois.readDouble();
        BatsServiceApiImpl.serviceState.noTotalTasks = bot.tasks.size();
        BatsServiceApiImpl.serviceState.noCompletedTasks = bot.finishedTasks.size();

        ois.close();

        // get the remaining tasks.
        bot.tasks = bot.bag.getBoT();

        System.out.println("Bag-of-Tasks file: " + bot.bag.getInputFile());

        System.out.println("Number of clusters: " + bot.Clusters.size());

        for(Cluster c : bot.Clusters.values()){           
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
     *      AND an optional parameter:
     *  - file : filename of schedules. this has a default value of: src\\schedules\\default.ser
     *
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        // it will survive the constructor only if the arguments are passed correctly.
        Executor execute = new Executor(args);
        execute.go();
    }
}
