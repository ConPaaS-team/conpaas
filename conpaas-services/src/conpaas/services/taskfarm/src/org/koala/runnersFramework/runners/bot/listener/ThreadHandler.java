package org.koala.runnersFramework.runners.bot.listener;

import java.io.BufferedOutputStream;
import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.util.Enumeration;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.activation.DataSource;
import javax.mail.BodyPart;
import javax.mail.Header;
import javax.mail.MessagingException;
import javax.mail.internet.MimeMultipart;
import javax.mail.util.ByteArrayDataSource;

import com.googlecode.jsonrpc4j.JsonRpcServer;
import java.io.File;
import java.util.HashMap;
import org.koala.runnersFramework.runners.bot.BoTRunner;

class ThreadHandler extends Thread {

    ThreadHandler(Socket socket, JsonRpcServer jsonRpcServer) {
        OutputStream ops = null;
        try {
            InputStream ips = socket.getInputStream();
            ops = socket.getOutputStream();

            byte[] byteArray = transformToByteArray(ips);

            DataSource ds = new ByteArrayDataSource(byteArray,
                    "application/octet-stream");
            MimeMultipart mimeMultipart = new MimeMultipart(ds);

            try {
                String header = mimeMultipart.getPreamble();

                /* Refuse any other request than POST requests */
                if (!header.contains("POST")) {
                    writeJsonErrorAndClose(ops, "Can only handle POST requests!");
                    return;
                }

                handleMime(jsonRpcServer, mimeMultipart, ops);
            } catch (MessagingException ex) {
                handleJsonRpc(jsonRpcServer, byteArray, ops);
            }

            ops.close();
        } catch (Exception ex) {
            try {
                writeJsonErrorAndClose(ops, ex.getLocalizedMessage());
            } catch (IOException ex1) {
                Logger.getLogger(ThreadHandler.class.getName()).log(Level.SEVERE, null, ex1);
            }
            Logger.getLogger(ThreadHandler.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    private void handleJsonRpc(JsonRpcServer jsonRpcServer,
            byte[] byteArray, OutputStream ops) throws IOException {

        String header = new String(byteArray);
        
        /* Refuse any other request than POST requests */
        if (!header.contains("POST")) {
            writeJsonErrorAndClose(ops, "Can only handle POST requests!");
            return;
        }
                
        String jsonString = header.substring(header.lastIndexOf("\n") + 1);

        if (jsonString == null) {
            jsonString = "";
        }

        InputStream baipsContent = new ByteArrayInputStream(jsonString.getBytes());

        writeHeader(ops, "HTTP/1.1 200 OK");

        try {
            jsonRpcServer.handle(baipsContent, ops);
        } catch (Exception ex) {
            System.err.println("Caught exception:\n" + ex);
            System.err.println("Request was:\n" + header + "\n" + jsonString);
        }
    }

    private void handleMime(JsonRpcServer jsonRpcServer,
            MimeMultipart m, OutputStream ops) throws Exception {
        int bodyParts = m.getCount();
        BodyPart part;
        String name;

        HashMap<String, String> jsonrpcMap = new HashMap<String, String>();
        jsonrpcMap.put("jsonrpc", "2.0");
        jsonrpcMap.put("method", "");
        jsonrpcMap.put("uriLocation", "");
        jsonrpcMap.put("botFile", "");
//        jsonrpcMap.put("clusterFile", "");
        jsonrpcMap.put("id", "1");

        for (int idx = 0; idx < bodyParts; idx++) {
            part = m.getBodyPart(idx);
            name = null;

            Enumeration<Header> en = part.getMatchingHeaders(
                    new String[]{"Content-Disposition"});
            // should be just 1 Content-Disposition
            while (en != null && en.hasMoreElements()) {
                Header header = en.nextElement();
                name = parseNameFromHeaderLine(header.getValue());
                // found one valid name, get out
                if (name != null) {
                    break;
                }
            }

            if (name == null) {
                continue;
            }
            handleBodyPart(name, part, jsonrpcMap);
        }

        String jsonrpcString = createStringFromMap(jsonrpcMap);
        handleJsonRpc(jsonRpcServer, jsonrpcString.getBytes(), ops);
    }

    private byte[] transformToByteArray(InputStream ips)
            throws IOException {
        int counter = 0, read = 0, size = 256;
        byte[] buf = new byte[size], temp;

        do {
            read = ips.read(buf, counter, size - counter);
            if (read < 0) {
                continue;
            }

            if (counter + read == size) {
                // reallocate
                size <<= 1;
                if (size <= 0) {
                    throw new RuntimeException("Input too big to handle");
                }
                temp = new byte[size];
                System.arraycopy(buf, 0, temp, 0, size >> 1);
                buf = temp;
            }
            counter += read;
        } while (ips.available() > 0);

        byte[] headerBytes = new byte[counter];
        System.arraycopy(buf, 0, headerBytes, 0, counter);

        String header = new String(headerBytes);
        int i = header.indexOf("Content-Length: ") + 16;
        int j = header.indexOf("\r\n", i);
        int contentLength = 0;
        try {
            contentLength = Integer.parseInt(header.substring(i, j));
        } catch (Exception ex) {
            contentLength = 0;
        }

        // we have read everything from one swoop
        if (counter >= contentLength) {
            return headerBytes;
        }

        // we have read just the header; also need the content
        for (counter = 0; counter < contentLength; counter += read) {
            read = ips.read(buf, counter, size - counter);

            if (counter + read == size) {
                // reallocate
                size <<= 1;
                if (size <= 0) {
                    throw new RuntimeException("Input too big to handle");
                }
                temp = new byte[size];
                System.arraycopy(buf, 0, temp, 0, size >> 1);
                buf = temp;
            }
        }
        byte[] data = new byte[headerBytes.length + counter];
        System.arraycopy(headerBytes, 0, data, 0, headerBytes.length);
        System.arraycopy(buf, 0, data, headerBytes.length, counter);

        return data;
    }

    private void writeHeader(OutputStream ops, String msg) throws IOException {
        if (ops == null) {
            return;
        }
        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(ops));
        bw.write(msg);
        bw.newLine();
        bw.newLine();
    }

    private void writeJsonErrorAndClose(OutputStream ops, String errMsg) throws IOException {
        if (ops == null) {
            return;
        }
        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(ops));
        bw.write("HTTP/1.1 400 Bad Request");
        bw.newLine();
        bw.newLine();

        String jsonErr;
        jsonErr = "{\"jsonrpc\": \"2.0\", \"error\": {"
                + "\"message\": "
                + "\"" + errMsg + "\"}, \"id\": null}";
        bw.write(jsonErr);

        bw.close();
    }

    private String parseNameFromHeaderLine(String value) {
        int idxBeg = value.indexOf("name=\"") + 6;
        int idxEnd = value.indexOf("\"", idxBeg);

        if (0 <= idxBeg && idxBeg < idxEnd && idxEnd <= value.length()) {
            return value.substring(idxBeg, idxEnd);
        }

        return null;
    }

    private void handleBodyPart(String name, BodyPart part,
            HashMap<String, String> jsonrpcMap) throws Exception {
        if ("method".equals(name)) {
            jsonrpcMap.put("method", part.getContent().toString());
        } else if ("uriLocation".equals(name)) {
            jsonrpcMap.put("uriLocation", part.getContent().toString());
        } else if ("botFile".equals(name)) {
            String botFile = part.getFileName();
            if (botFile == null || "".equals(botFile)) {
                botFile = "botFile.bot";
            }
            writeToFile(part.getInputStream(), botFile);
            jsonrpcMap.put("botFile", botFile);
        }
//        else if ("clusterFile".equals(name)) {
//            String clusterFile = part.getFileName();
//            if (clusterFile == null || "".equals(clusterFile)) {
//                clusterFile = "clusterFile.xml";
//            }
//            writeToFile(part.getInputStream(), clusterFile);
//            jsonrpcMap.put("clusterFile", clusterFile);
//        }
    }

    private void writeToFile(InputStream ips, String fileName)
            throws IOException {
        int read, size = 1024;
        byte[] buf = new byte[size];

        String absFileName = BoTRunner.path + File.separator + fileName;
        int idx = absFileName.lastIndexOf(File.separator);
        if (idx > 0) {
            String parentName = absFileName.substring(0, idx);
            File parent = new File(parentName);
            parent.mkdirs();
        }

        BufferedOutputStream bos = new BufferedOutputStream(
                new FileOutputStream(absFileName));

        do {
            read = ips.read(buf, 0, size);
            if (read < 0) {
                continue;
            }
            bos.write(buf, 0, read);
        } while (ips.available() > 0);

        bos.close();
    }

    private String createStringFromMap(HashMap<String, String> map) {
        return "{\"jsonrpc\":\"" + map.get("jsonrpc") + "\", "
                + "\"method\":\"" + map.get("method") + "\", "
                + "\"params\":["
                + "\"" + map.get("uriLocation") + "\", "
                + "\"" + map.get("botFile") + "\"], "
//                + "\"" + map.get("clusterFile") + "\"], " // carefull with ]
                + "\"id\":" + map.get("id") + "}";
    }
}
