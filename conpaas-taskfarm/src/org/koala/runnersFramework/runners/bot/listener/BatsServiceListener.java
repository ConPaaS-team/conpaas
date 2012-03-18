package org.koala.runnersFramework.runners.bot.listener;

import com.googlecode.jsonrpc4j.JsonRpcServer;
import java.io.IOException;
import java.net.ServerSocket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.logging.Level;
import java.util.logging.Logger;

class BatsServiceListener extends Thread {

    public final static int SERVER_PORT = 8475;
    public final static int MAX_THREADS = 128;
    private JsonRpcServer jsonRpcServer;
    private BatsServiceApiImpl apiCalls;

    BatsServiceListener() {
        apiCalls = new BatsServiceApiImpl();
        jsonRpcServer = new JsonRpcServer(apiCalls, BatsServiceApi.class);
    }

    @Override
    public void run() {
        ServerSocket socket;
        ExecutorService execServ = Executors.newFixedThreadPool(MAX_THREADS);

        try {
            socket = new ServerSocket(SERVER_PORT);
        } catch (IOException ex) {
            Logger.getLogger(this.getClass().getName()).log(Level.SEVERE, null, ex);
            throw new RuntimeException("Could not initialize socket! Quiting...");
        }

        while (true) {
            try {
                /* block until a new connection arrives.
                Pass the new socket to a thread so that he can deal with it.*/
                execServ.execute(new ThreadHandler(socket.accept(), jsonRpcServer));
            } catch (IOException ex) {
                Logger.getLogger(this.getClass().getName()).log(Level.SEVERE, null, ex);
            }
        }
    }
}
