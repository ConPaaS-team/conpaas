package org.koala.runnersFramework.runners.bot;


import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import javax.xml.stream.XMLEventReader;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.events.EndElement;
import javax.xml.stream.events.StartElement;
import javax.xml.stream.events.XMLEvent;


public class ClusterXmlFileParser {

    /**
     * Field names from the XML file.
     */
    static final String CLUSTER = "cluster";
    static final String CLASSNAME = "classname";
    static final String HOSTNAME = "hostname";
    static final String ALIAS = "alias";
    static final String PORT = "port";
    static final String TIMEUNIT = "timeunit";
    static final String COSTUNIT = "costunit";
    static final String MAXNODES = "maxnodes";
    static final String SPEEDFACTOR = "speedfactor";
    static final String IMAGE_ID = "imageid";
    static final String NETWORK_ID = "networkid";
    static final String INSTANCETYPE = "instancetype";
    static final String KEYPAIRNAME = "keypairname";
    static final String KEYPAIRPATH = "keypairpath";
    static final String ACCESSKEY = "accesskey";
    static final String SECRETKEY = "secretkey";
    static final String DNS = "nameserver";
    static final String GATEWAY = "gateway";
    

    public List<ClusterMetadata> readConfig(String configFile) {
        List<ClusterMetadata> listClustersMetadata = new ArrayList<ClusterMetadata>();
        try {
            // First create a new XMLInputFactory
            XMLInputFactory inputFactory = XMLInputFactory.newInstance();
            // Setup a new eventReader
            InputStream in = new FileInputStream(configFile);
            XMLEventReader eventReader = inputFactory.createXMLEventReader(in);
            // Read the XML document
            ClusterMetadata clusterMetadata = null;

            while (eventReader.hasNext()) {
                XMLEvent event = eventReader.nextEvent();

                if (event.isStartElement()) {
                    StartElement startElement = event.asStartElement();
                    // If we have a item element we create a new item
                    if (startElement.getName().getLocalPart().equals(CLUSTER)) {
                        clusterMetadata = new ClusterMetadata();
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(CLASSNAME)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.className = event.asCharacters().getData();
                        continue;
                    }
                    if (event.asStartElement().getName().getLocalPart().equals(HOSTNAME)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.hostName = event.asCharacters().getData();
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(ALIAS)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.alias = event.asCharacters().getData();
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(PORT)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.port = Integer.parseInt(event.asCharacters().getData());
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(TIMEUNIT)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.timeUnit = Long.parseLong(event.asCharacters().getData());
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(COSTUNIT)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.costUnit = Integer.parseInt(event.asCharacters().getData());
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(MAXNODES)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.maxNodes = Integer.parseInt(event.asCharacters().getData());
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(SPEEDFACTOR)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.speedFactor = event.asCharacters().getData();
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(IMAGE_ID)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.image_id = Integer.parseInt(event.asCharacters().getData());
                        continue;
                    }
                    
                    if (event.asStartElement().getName().getLocalPart().equals(NETWORK_ID)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.network_id = Integer.parseInt(event.asCharacters().getData());
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(INSTANCETYPE)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.instanceType = event.asCharacters().getData();
                        continue;
                    }
                    
                    if (event.asStartElement().getName().getLocalPart().equals(KEYPAIRNAME)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.keyPairName = event.asCharacters().getData();
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(KEYPAIRPATH)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.keyPairPath = event.asCharacters().getData();
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(ACCESSKEY)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.accessKey = event.asCharacters().getData();
                        continue;
                    }

                    if (event.asStartElement().getName().getLocalPart().equals(SECRETKEY)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.secretKey = event.asCharacters().getData();
                        continue;
                    }
                    
                    if (event.asStartElement().getName().getLocalPart().equals(DNS)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.dns = event.asCharacters().getData();
                        continue;
                    }
                    
                    if (event.asStartElement().getName().getLocalPart().equals(GATEWAY)) {
                        event = eventReader.nextEvent();
                        clusterMetadata.gateway = event.asCharacters().getData();
                        continue;
                    }
                }
                // If we reach the end of an item element we add it to the list
                if (event.isEndElement()) {
                    EndElement endElement = event.asEndElement();
                    if (endElement.getName().getLocalPart().equals(CLUSTER)) {
                        listClustersMetadata.add(clusterMetadata);
                    }
                }

            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (XMLStreamException e) {
            e.printStackTrace();
        }
        return listClustersMetadata;
    }
}
