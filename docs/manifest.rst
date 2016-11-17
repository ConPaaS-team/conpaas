==============
Manifest Guide
==============

A manifest is a JSON file that describes a ConPaaS application. It can be
written with your favorite text editor.

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
the path to the PHP program that will be uploaded to the newly created PHP service.

To create an application from a manifest, you can use either the web client or
the command line client.

 * On the web client, after login, press button "deploy application from manifest",
   then press button "Browse..." and select your ``sudoku.mnf``. A popup will
   appear to confirm that the creation of the application has started.

 * On the command line, you can simply run:
   ::
     cps-application manifest sudoku.mnf

In this example, once the application has been created, you will have to start
the PHP service either with the web client (button start on the PHP service
page) or with the command line client
(``cps-service start <app_id> <php_serv_id>``).


MediaWiki example
-----------------

The ConPaaS frontend offers the option to deploy two ready-made applications
from predefined manifest files: one WordPress and one MediaWiki installation.
In this section we are going to list the manifest file that creates the same
MediaWiki application as the one provided by the ConPaaS system::

   {
       "Application": "New MediaWiki application",
       "Services": [
           {
               "Type": "php",
               "ServiceName": "PHP service",
               "Start": 1,
               "Archive": "https://online.conpaas.eu/mediawiki/mediawiki.tar.gz",
               "StartupScript": "https://online.conpaas.eu/mediawiki/mediawiki.sh"
           },
           {
               "Type": "mysql",
               "ServiceName": "MySQL service",
               "Start": 1,
               "Dump": "https://online.conpaas.eu/mediawiki/mediawiki.sql",
               "Password": "contrail123"
           },
           {
               "Type": "xtreemfs",
               "ServiceName": "XtreemFS service",
               "Start": 1,
               "VolumeStartup": {
                   "volumeName": "data",
                   "owner": "www-data"
               }
           }
       ]
   }

Even if the application is more complicated than the sudoku, the manifest
file is not very different. In this case, the file specifies three different
services: PHP, MySQL, and XtreemFS.


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

-  xtreemfs

-  flink

-  generic

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
default, if the user starts a service, one instance will be created. If the
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
| mysql    | mysql, glb          |
+----------+---------------------+
| xtreemfs | osd                 |
+----------+---------------------+
| flink    | master, worker      |
+----------+---------------------+
| generic  | master, node        |
+----------+---------------------+

Next, I'll show all the manifest fields that are specific for each
service.

php
---

-  *Archive*: Specify a URL where the service should fetch the source
   archive.

java
----

-  *Archive*: Specify a URL where the service should fetch the source
   archive.

mysql
-----

-  *Dump*: Specify a URL where the service should fetch the dump

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
   parsed by ConPaaS, so it is needed just as a reminder for yourself.

-  *Application*: Specify the application name on which your services
   will start. It can be a new application or an existing one. If it is
   omitted, a default application name will be chosen.

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
      "mysql" : "1"
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
    },
    {
     "ServiceName" : "Meaningful Flink service name",
     "Type" : "flink",
     "Cloud" : "default",
     "Start" : 0,
     "StartupInstances" : {
      "master" : "1"
     }
    },
    {
     "ServiceName" : "Meaningful Generic service name",
     "Type" : "generic",
     "Cloud" : "default",
     "Start" : 0,
     "StartupInstances" : {
      "master" : "1"
     }
    }
   ]
  }
