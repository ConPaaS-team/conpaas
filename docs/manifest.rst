==============
Manifest Guide
==============

A manifest is a JSON file that describes a ConPaaS application. It can be
written with your favourite text editor, or automatically generated from a
running ConPaaS application.

---------------------------------------
Creating an application from a manifest
---------------------------------------

Sudoku example
--------------

Here is manifest for an application that will run a simple PHP program (a free
sudoku PHP program). File ``sudoku.mnf``::

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

This simple example states the application name and the service list which is
here a single PHP service. It gives the name of the service, its type, whether
it should be automatically started (1 for autostart, 0 otherwise), and it gives
the path to the PHP program that will be uploaded into the created PHP service.

To create an application from a manifest, you can use either the web client or
the command line client.

 * On the web client, after login, press button "deploy ready-made application",
   then press button "Browse..." and select your ``sudoku.mnf``. A popup will
   appear to confirm that the creation of the application has started.

 * On the command line, you can simply run:
   ::
     cpsclient.py manifest sudoku.mnf

In this example, once the application has been created, you will have to start
the PHP service either with the web client (button start on the PHP service
page) or with command line client (``cpsclient.py start <php_serv_id>``).



MediaWiki example
-----------------

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
      "StartupInstances" :
       {
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
receive lots of traffic, 5 instances of the Java backend are started.
In the presentation the Java instances are added later, but in this
example to show how the *StartupInstances* works, 5 Java virtual
machines are started from the beginning.
Unfortunately the option of choosing a static IP for the database is not
yet available, so we cannot specify it in the Java service at startup.

------------------------------------------------
Generating a manifest from a created application
------------------------------------------------

You can generate a manifest from an existing ConPaaS application with command line client:
::
  cpsclient.py download_manifest appl_id > myappl.mnf

You can edit the generated manifest ``myappl.mnf`` to your liking.
Then you can create a new application with this manifest::
  cpslient.py manifest myappl.mnf


Note: in ConPaaS 1.3.1, you cannot get a manifest of an existing application
through the web client. It's only available through the command line client or
through the API.


-------------------------------------------
Complete description of the manifest fields
-------------------------------------------

In this section, we present the complete description of all the possible
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

-  *Start*: Specify if the service should be started or not (1 or 0)

-  *ServiceName*: Specify the name of the service

-  *StartupScript*: Specify a URL of a script that will be executed at
   the startup of the agents

It is not required to define how many instances the service needs. By
default if the user starts a service, one instance will be created. If the
user wants to create more instances, then the user can use this option in the manifest.

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
