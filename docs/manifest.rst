==============
Manifest Guide
==============

What is a manifest file
=======================

When a user wants to create new services in ConPaaS_ there are two
options available: the first one is to create every single service using
the ConPaaS frontend or the ConPaaS client, while the second one is to
upload a manifest file that describes which services the application
needs. Using the ConPaaS frontend and the ConPaaS client is possible to
upload the manifest file to the director which will automatically parse
the file and create all the desired services.
In this guide we are going to describe all the options available in the
manifest file.

How to structure a manifest file
================================

A manifest file is a plain json file where users need to fill all the
necessary information to start the services.
In the next section we are going to describe how to setup a manifest file
for the sudoku example in the ConPaaS website.

Manifest file for Sudoku
========================

The sudoku application needs to have just one PHP service and the
following is the simplest manifest file::

   {
    "Application" : "Sudoku example",

    "Services" : [
     {
      "ServiceName" : "PHP sudoku backend",
      "Type" : "php",
      "Start" : 0,
      "Archive" : "http://www.conpaas.eu/wp-content/uploads/2011/09/sudoku.tar.gz"
     }
    ]
   }

The understanding of the file is quite straightforward. First of all the
user needs to specify a description of the application because if more
applications are running on ConPaaS it is easier to differentiate between
them.
Then all the services are specified. In this case the sudoku needs only
one service: PHP, so we setup a PHP service.
To setup a PHP service the user needs to provide few informations: the
service name shown in the frontend (otherwise the default will be just
"New PHP service"), the cloud where the service needs to run and
optionally the URL of the archive containing the application.
One more field that can be specified is the *Start* field, where the
user can specify if the service only needs to be created or if it should
also be started automatically.
The ConPaaS director will then automatically create all the needed
instances and start the service.

Manifest file for a MediaWiki
=============================

On the ConPaaS website there is a short video
(http://www.youtube.com/watch?v=kMzx8sgr96I) that shows how to setup a
MediaWiki installation using the ConPaaS frontend.
In this section we are going to create a manifest file that replicates
exactly the same MediaWiki application shown in the video::


   {
    "Application" : "Wiki in the Cloud",

    "Services" : [
     {
      "ServiceName" : "Wiki-Webserver",
      "Type" : "java",
      "Archive" : "http://mywebsite.com/scalaris-wiki.war",
      "StartupInstances" : {
       "proxy" : "1",
       "web" : "1",
       "backend" : "5"
      },
      "Start" : 1
     },
     {
      "ServiceName" : "Wiki-Database",
      "Type" : "scalaris",
      "Archive" : "http://mywebsite.com/wikipediadump",
      "Start" : 1
     }
    ]
   }

Even if the application is more complicated than the sudoku, the
manifest file is not very different.
In this case the file specifies two different services: Java and
Scalaris (which is a NoSQL database). Also, given that the service might
receive lots of traffic, 5 instances of the java backend are started.
In the presentation the java instances are added later, but in this
example to show how the *StartupInstances* works, 5 Java virtual
machines are started from the beginning.
Unfortunately the option of choosing a static ip for the database is not
yet available, so we can not specify it in the java service at startup.

Complete description of the manifest fields
===========================================

In this section we present a complete description of all the possible
fields that can be used in the manifest. We will also distinguish
between required and optional fields.
Currently, the available service types are:

-  php

-  java

-  mysql

-  scalaris

-  hadoop

-  selenium

-  xtreemfs

-  taskfarm

These are the required fields for each service

-  *Type*: Specify which type of service you want to create

If nothing else is specified in the manifest the service will have the
default name and it will not be started.

The following fields are optional and are available in all the services.

-  *Cloud*: Specify which cloud your service needs to run on

-  *Start*: Specify if the service should be started or not (0 or 1)

-  *ServiceName*: Specify the name of the service displayed in the
   frontend

-  *StartupScript*: Specify an URL of a script that will be executed at
   the startup of the agents

It is not required to define how many instances the service needs. By
default if the user starts a service 1 instance will be created. If the
user wants to create more instances this option in the manifest needs to
be used.

-  *StartupInstances*: Specify how many instances of each type needs to
   be created at startup.

This will be an object that can contain different fields.
All the possible fields that can be specified for each service are
described in the following table:

+----------+---------------------+
| Service  | Type                |
+==========+=====================+
| php      | proxy, web, backend |
+----------+---------------------+
| java     | proxy, web, backend |
+----------+---------------------+
| mysql    | slaves              |
+----------+---------------------+
| scalaris | scalaris            |
+----------+---------------------+
| hadoop   | workers             |
+----------+---------------------+
| selenium | node                |
+----------+---------------------+
| xtreemfs | osd                 |
+----------+---------------------+

Next, I'll show all the manifest fields that are specific for each
service.

php
---

-  *Archive*: Specify an URL where the service should fetch the source
   archive.

java
----

-  *Archive*: Specify an URL where the service should fetch the source
   archive.

mysql
-----

-  *Dump*: Specify an URL where the service should fetch the dump

xtreemfs
--------

-  *VolumeStartup*: Specify a volume that should be created at startup.
   This needs to be an object with the following fields inside

   -  *volumeName*: Name of the volume

   -  *owner*: Owner of the volume

Other fields are optional and are not service-specific, but
manifest-specific instead, so they need to be specified on top of the
file (see the full example in the end) are the following:

-  *Description*: This is just a description of the manifest. It is not
   parsed by ConPaaS, so it is needed just as a reminder for yourself

-  *Application*: Specify the application name on which your services
   will start. It can be a new application or an existing one. If it is
   omitted, the default application will be choose.

Full specification file
=======================

This example is a full specification file with all the possible options
available::

  {
   "Description" : "Description of the project",
   "Application" : "New full application"

   "Services" : [
    {
     "ServiceName" : "Meaningful PHP service name",
     "Type" : "php",
     "Cloud" : "default",
     "Start" : 0,
     "Archive" : "http://mywebsite.com/archive.tar.gz",
     "StartupInstances" : {
      "proxy" : "1",
      "web" : "1",
      "backend" : "1"
     }
    },
    {
     "ServiceName" : "Meaningful Java service name",
     "Type" : "java",
     "Cloud" : "default",
     "Start" : 0,
     "Archive" : "http://mywebsite.com/project.war",
     "StartupInstances" : {
      "proxy" : "1",
      "web" : "1",
      "backend" : "1"
     }
    },
    {
     "ServiceName" : "Meaningful MySQL service name",
     "Type" : "mysql",
     "Cloud" : "default",
     "Start" : 0,
     "Dump" : "http://mywebsite.com/dump.sql",
     "StartupInstances" : {
      "slaves" : "1"
     }
    },
    {
     "ServiceName" : "Meaningful Scalaris service name",
     "Type" : "scalaris",
     "Cloud" : "default",
     "Start" : 0,
     "StartupInstances" : {
      "scalaris" : "1"
     }
    },
    {
     "ServiceName" : "Meaningful Hadoop service name",
     "Type" : "hadoop",
     "Cloud" : "default",
     "Start" : 0,
     "StartupInstances" : {
      "workers" : "1"
     }
    },
    {
     "ServiceName" : "Meaningful Selenium service name",
     "Type" : "selenium",
     "Cloud" : "default",
     "Start" : 0,
     "StartupInstances" : {
      "node" : "1"
     }
    },
    {
     "ServiceName" : "Meaningful XtreemFS service name",
     "Type" : "xtreemfs",
     "Cloud" : "default",
     "Start" : 0,
     "VolumeStartup" : {
      "volumeName" : "Meaningful volume name",
      "owner" : "volumeowner"
     },
     "StartupInstances" : {
      "osd" : "1"
     }
    }
   ]
  }
