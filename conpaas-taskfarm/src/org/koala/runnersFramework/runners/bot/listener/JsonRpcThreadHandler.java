package org.koala.runnersFramework.runners.bot.listener;

import com.googlecode.jsonrpc4j.JsonRpcServer;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.codehaus.jackson.map.JsonMappingException;

class JsonRpcThreadHandler extends Thread {

    JsonRpcThreadHandler(Socket socket, JsonRpcServer jsonRpcServer) {
        try {

            InputStream ips = transformToByteArrayInputStream(
                    socket.getInputStream());
            OutputStream ops = socket.getOutputStream();

            String jsonString = getJsonString(ips);
            InputStream baips = new ByteArrayInputStream(jsonString.getBytes());

            writeHeader(ops);

            jsonRpcServer.handle(baips, ops);

        } catch (JsonMappingException ex) {
            Logger.getLogger(BatsWrapper.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger(BatsWrapper.class.getName()).log(Level.SEVERE, null, ex);
        }

        try {
            socket.close();
        } catch (IOException ex) {
            Logger.getLogger(BatsWrapper.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    private String getJsonString(InputStream ips) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(ips));
        while (!("".equals(br.readLine()))) {
        }

        String retValue = br.readLine();
        return retValue != null ? retValue : "";
    }

    private void writeHeader(OutputStream ops) throws IOException {
        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(ops));
        bw.write("HTTP/1.1 200 OK");
        bw.newLine();
        bw.newLine();
    }

    private InputStream transformToByteArrayInputStream(InputStream ips)
            throws IOException {
        int counter = 0, read = 0, size = 256;
        byte[] buf = new byte[size];

        do {
            read = ips.read(buf, counter, size - counter);

            if (counter + read == size) {
                // reallocate
                size <<= 1;
                if (size <= 0) {
                    throw new RuntimeException("Input too big to handle");
                }
                byte[] temp = new byte[size];
                System.arraycopy(buf, 0, temp, 0, size >> 1);
                buf = temp;
            }
            counter += read;
        } while (ips.available() > 0);

        return new ByteArrayInputStream(buf, 0, counter);
    }
}
