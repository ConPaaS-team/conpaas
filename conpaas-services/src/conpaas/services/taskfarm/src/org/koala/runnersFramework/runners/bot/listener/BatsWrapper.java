package org.koala.runnersFramework.runners.bot.listener;

import org.koala.runnersFramework.runners.bot.BoTRunner;

public class BatsWrapper {

    public static void main(String[] args) {
        
        BoTRunner.path = System.getenv().get("BATS_HOME");
        if (BoTRunner.path == null) {
            throw new RuntimeException("You do not have BATS_HOME set!");
        }
        System.out.println("BATS_HOME=" + BoTRunner.path);
        Thread serviceListener = new BatsServiceListener();
        serviceListener.start();
    }
}
