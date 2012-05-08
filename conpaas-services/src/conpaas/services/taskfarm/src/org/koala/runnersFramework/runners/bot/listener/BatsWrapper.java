package org.koala.runnersFramework.runners.bot.listener;

import org.koala.runnersFramework.runners.bot.BoTRunner;

public class BatsWrapper {

    public static void main(String[] args) {
        
        BoTRunner.path = System.getenv().get("BATS_HOME");
        if (BoTRunner.path == null) {
            throw new RuntimeException("You do not have BATS_HOME set!");
        }
        System.out.println("BATS_HOME=" + BoTRunner.path);
        
        String demoValue = System.getProperty("demo");
        if ("on".equals(demoValue)) {
            BatsServiceApiImpl.DEMO = true;
        } else {
            BatsServiceApiImpl.DEMO = false;
        }
        System.out.println("DEMO=" + BatsServiceApiImpl.DEMO);

        Thread serviceListener = new BatsServiceListener();
        serviceListener.start();
    }
}
