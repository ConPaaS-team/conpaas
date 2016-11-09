=========
Internals
=========

Introduction
============

A ConPaaS service may consist of three main entities: the manager, the
agent and the frontend. The (primary) manager resides in the first VM
that is started by the frontend when the service is created and its role
is to manage the service by providing supporting agents, maintaining a
stable configuration at any time and by permanently monitoring the
service’s performance. An agent resides on each of the other VMs that
are started by the manager. The agent is the one that does all the work.
Note that a service may contain one manager and multiple agents, or
multiple managers that also act as agents.

To implement a new ConPaaS service, you must provide a new manager
service, a new agent service and a new frontend service (we assume that
each ConPaaS service can be mapped on the three entities architecture).
To ease the process of adding a new ConPaaS service, we propose a
framework which implements common functionality of the ConPaaS services.
So far, the framework provides abstraction for the IaaS layer (adding
support for a new cloud provider should not require modifications in any
ConPaaS service implementation) and it also provides abstraction for the
HTTP communication (we assume that HTTP is the preferred protocol for
the communication between the three entities).

ConPaaS directory structure
---------------------------

You can see below the directory structure of the ConPaaS software. The
*core* folder under *src* contains the ConPaaS framework. Any service
should make use of this code. It contains the manager http server, which
instantiates the python manager class that implements the required
service; the agent http server that instantiates the python agent class
(if the service requires agents); the IaaS abstractions and other useful
code.

A new service should be added in a new python module under the
*ConPaaS/src/conpaas/services* folder:

::

    ConPaaS/  (conpaas/conpaas-services/)
    │── src
    │   │── conpaas
    │   │   │── core
    │   │   │   │── clouds
    │   │   │   │   │── base.py
    │   │   │   │   │── dummy.py
    │   │   │   │   │── ec2.py
    │   │   │   │   │── federation.py
    │   │   │   │   │── openstack.py
    │   │   │   │── agent.py
    │   │   │   │── controller.py
    │   │   │   │── expose.py
    │   │   │   │── file.py
    │   │   │   │── ganglia.py
    │   │   │   │── git.py
    │   │   │   │── https
    │   │   │   │── iaas.py
    │   │   │   │── ipop.py
    │   │   │   │── log.py
    │   │   │   │── manager.py
    │   │   │   │── manager.py.generic_add_nodes
    │   │   │   │── misc.py
    │   │   │   │── node.py
    │   │   │   │── services.py
    │   │   │── services
    │   │       │── cds/
    │   │       │── mysql/
    │   │       │── helloworld/
    │   │       │── htc/
    │   │       │── htcondor/
    │   │       │── mapreduce/
    │   │       │── scalaris/
    │   │       │── selenium/
    │   │       │── taskfarm/
    │   │       │── webservers/
    │   │       │── xtreemfs/
    │   │── dist
    │   │── libcloud -> ../contrib/libcloud/
    │   │── setup.py
    │   │── tests
    │       │── core
    │       │── run_tests.py
    │       │── services
    │       │── unit-tests.sh
    │── config
    │── contrib
    │── misc
    │── sbin
    │── scripts

In the next paragraphs we describe how to add the new ConPaaS service.

Service Organization
====================

Service’s name
--------------

The first step in adding a new ConPaaS service is to choose a name for
it. This name will be used to construct, in a standardized manner, the
file names of the scripts required by this service (see below).
Therefore, the names should not contain spaces, nor unaccepted
characters.

Scripts
-------

To function properly, ConPaaS uses a series of configuration files and
scripts. Some of them must be modified by the administrator, i.e. the
ones concerning the cloud infrastructure, and the others are used,
ideally unchanged, by the manager and/or the agent. A newly added
service would ideally function with the default scripts. If, however,
the default scripts are not satisfactory (for example the new service
would need to start something on the VM, like a memcache server) then
the developers must supply a new script/config file, that would be used
instead of the default one. This new script’s name must be preceded by
the service’s chosen name (as described above) and will be selected by
the frontend at run time to generate the contextualization file for the
manager VM. (If the frontend doesn’t find such a script/config file for
a given service, then it will use the default script). **Note that some
scripts provided for a service do not replace the default ones, instead
they will be concatenated to them (see below the agent and manager
configuration scripts).**

Below we give an explanation of the scripts and configuration files used
by a ConPaaS service (there are other configuration files used by the
frontend but these are not relevant to the ConPaaS service). Basically
there are two scripts that a service uses to boot itself up - the
manager contextualization script, which is executed after the manager VM
booted, and the agent contextualization script, which is executed after
the agent VM booted. These scripts are composed of several parts, some
of which are customizable to the needs of the new service.

In the ConPaaS home folder (CONPAAS\_HOME) there is the *config* folder
that contains configuration files in the INI format and the *scripts*
folder that contains executable bash scripts. Some of these files are
specific to the cloud, other to the manager and the rest to the agent.
These files will be concatenated in a single contextualization script,
as described below.

-  Files specific to the Cloud:

   (1) CONPAAS\_HOME/config/cloud/\ *cloud\_name*.cfg, where
   *cloud\_name* refers to the clouds supported by the system (for now
   OpenStack and EC2). So there is one such file for each cloud the
   system supports. These files are filled in by the administrator. They
   contain information such as the username and password to access the
   cloud, the OS image to be used with the VMs, etc. These files are
   used by the frontend and the manager, as both need to ask the cloud
   to start VMs.

   (2) CONPAAS\_HOME/scripts/cloud/\ *cloud\_name*, where *cloud\_name*
   refers to the clouds supported by the system (for now OpenStack and
   EC2). So, as above, there is one such file for each cloud the system
   supports. These scripts will be included in the contextualization
   files. For example, for OpenStack, this file sets up the network.

-  Files specific to the Manager:

   (3) CONPAAS\_HOME/scripts/manager/manager-setup, which prepares the
   environment by copying the ConPaaS source code on the VM, unpacking
   it, and setting up the PYTHONPATH environment variable.

   (4) CONPAAS\_HOME/config/manager/\ *service\_name*-manager.cfg, which
   contains configuration variables specific to the service manager (in
   INI format). If the new service needs any other variables (like a
   path to a file in the source code), it should provide an annex to the
   default manager config file. This annex must be named
   *service\_name*-manager.cfg and will be concatenated to
   default-manager.cfg

   (5) CONPAAS\_HOME/scripts/manager/\ *service\_name*-manager-start,
   which starts the server manager and any other programs the service
   manager might use.

   (6) CONPAAS\_HOME/sbin/manager/\ *service\_name*-cpsmanager (will be
   started by the *service\_name*-manager-start script), which starts
   the manager server, which in turn will start the requested manager
   service.

   Scripts (1), (2), (3), (4) and (5) will be used by the frontend to
   generate the contextualization script for the manager VM. After this
   scripts executes, a configuration file containing the concatenation
   of (1) and (4) will be put in ROOT\_DIR/config.cfg and then (6) is
   started with the config.cfg file as a parameter that will be
   forwarded to the new service.

   Examples:

.. |lst:ec2cfg| replace:: Listing 1

.. centered:: |lst:ec2cfg|: Script (1) ConPaaS/config/cloud/ec2.cfg

.. literalinclude:: ../conpaas-services/config/cloud/ec2.cfg
    :language: cfg


.. |lst:ec2| replace:: Listing 2

.. centered:: |lst:ec2|: Script (2) ConPaaS/scripts/cloud/ec2

.. literalinclude:: ../conpaas-services/scripts/cloud/ec2
    :language: sh


.. |lst:managersetup| replace:: Listing 3

.. centered:: |lst:managersetup|: Script (3) ConPaaS/scripts/manager/manager-setup

.. literalinclude:: ../conpaas-services/scripts/manager/manager-setup
    :language: sh


.. |lst:defaultmanagercfg| replace:: Listing 4

.. centered:: |lst:defaultmanagercfg|: Script (4) ConPaaS/config/manager/default-manager.cfg

.. literalinclude:: ../conpaas-services/config/manager/default-manager.cfg
    :language: cfg


.. |lst:defaultmanagerstart| replace:: Listing 5

.. centered:: |lst:defaultmanagerstart|: Script (5) ConPaaS/scripts/manager/default-manager-start

.. literalinclude:: ../conpaas-services/scripts/manager/default-manager-start
    :language: sh


.. |lst:defaultcpsmanager| replace:: Listing 6

.. centered:: |lst:defaultcpsmanager|: Script (6) ConPaaS/sbin/manager/default-cpsmanager

.. literalinclude:: ../conpaas-services/sbin/manager/default-cpsmanager
    :language: python


-  Files specific to the Agent

   They are similar to the files described above for the manager, but
   this time the contextualization file is generated by the manager.


Scripts and config files directory structure
--------------------------------------------

Below you can find the directory structure of the scripts and
configuration files described above.

::

    ConPaaS/  (conpaas/conpaas-services/)
    │── config
    │   │── agent
    │   │   │── default-agent.cfg
    │   │   │── mysql-agent.cfg
    │   │   │── helloworld-agent.cfg
    │   │   │── htc-agent.cfg
    │   │   │── htcondor.cfg
    │   │   │── mapreduce-agent.cfg
    │   │   │── scalaris-agent.cfg
    │   │   │── web-agent.cfg
    │   │   │── xtreemfs-agent.cfg
    │   │── cloud
    │   │   │── clouds-template.cfg
    │   │   │── ec2.cfg
    │   │   │── ec2.cfg.example
    │   │── ganglia
    │   │   │── ganglia_frontend.tmpl
    │   │   │── ganglia-gmetad.tmpl
    │   │   │── ganglia-gmond.tmpl
    │   │── ipop
    │   │   │── bootstrap.config.tmpl
    │   │   │── dhcp.config.tmpl
    │   │   │── ipop.config.tmpl
    │   │   │── ipop.vpn.config.tmpl
    │   │   │── node.config.tmpl
    │   │── manager
    │       │── default-manager.cfg
    │       │── htc-manager.cfg
    │       │── htcondor.cfg
    │       │── java-manager.cfg
    │       │── php-manager.cfg
    │── sbin
    │   │── agent
    │   │   │── default-cpsagent
    │   │   │── web-cpsagent
    │   │── manager
    │       │── default-cpsmanager
    │       │── php-cpsmanager
    │       │── taskfarm-cpsmanager
    │── scripts
        │── agent
        │   │── agent-setup
        │   │── default-agent-start
        │   │── htc-agent-start
        │   │── htcondor-agent-start
        │   │── mapreduce-agent-start
        │   │── scalaris-agent-start
        │   │── selenium-agent-start
        │   │── taskfarm-agent-start
        │   │── web-agent-start
        │   │── xtreemfs-agent-start
        │── cloud
        │   │── dummy
        │   │── ec2
        │   │── federation
        │   │── openstack
        │── create_vm
        │   │── 40_custom
        │   │── create-img-conpaas.sh
        │   │── create-img-script.cfg
        │   │── create-img-script.py
        │   │── README
        │   │── register-image-ec2-ebs.sh
        │   │── register-image-ec2-s3.sh
        │   │── scripts
        │       │── 000-head
        │       │── 003-create-image
        │       │── 004-conpaas-core
        │       │── 501-php
        │       │── 502-mysql
        │       │── 503-condor
        │       │── 504-selenium
        │       │── 505-hadoop
        │       │── 506-scalaris
        │       │── 507-xtreemfs
        │       │── 508-cds
        │       │── 995-rm-unused-pkgs
        │       │── 996-user
        │       │── 997-tail
        │       │── 998-ec2
        │       │── 999-resize-image
        │── manager
            │── cds-manager-start
            │── default-git-deploy-hook
            │── default-manager-start
            │── htc-manager-start
            │── htcondor-manager-start
            │── java-manager-start
            │── manager-setup
            │── notify_git_push.py
            │── php-manager-start
            │── taskfarm-manager-start


Implementing a new ConPaaS service using blueprints
===================================================

Blueprints are service templates you can use to speed up the creation
of a new service.  You can use this blueprinting mechanism with
:file:`create-new-service-from-blueprints.sh`.

The :file:`conpaas-blueprints` tree contains the following files::

    conpaas-blueprints
    │── conpaas-client
    │   │── cps
    │       │── blueprint.py
    │── conpaas-frontend
    │   │── www
    │       │── images
    │       │   │── blueprint.png
    │       │── js
    │       │   │── blueprint.js
    │       │── lib
    │           │── service
    │           │   │── blueprint
    │           │       │── __init__.php
    │           │── ui
    │               │── instance
    │               │   │── blueprint
    │               │       │── __init__.php
    │               │── page
    │                   │── blueprint
    │                       │── __init__.php
    │── conpaas-services
        │── scripts
        │   │── create_vm
        │       │── scripts
        │           │── 5xx-blueprint
        │── src
            │── conpaas
                │── services
                    │── blueprint
                        │── agent
                        │   │── agent.py
                        │   │── client.py
                        │   │── __init__.py
                        │── __init__.py
                        │── manager
                            │── client.py
                            │── __init__.py
                            │── manager.py

Edit :file:`create-new-service-from-blueprints.sh`
and change the following lines to set up the script::

    BP_lc_name=foobar                  # Lowercase service name in the tree
    BP_mc_name=FooBar                  # Mixedcase service name in the tree
    BP_uc_name=FOOBAR                  # Uppercase service name in the tree
    BP_bp_name='Foo Bar'               # Selection name as shown on the frontend  create.php  page
    BP_bp_desc='My new FooBar Service' # Description as shown on the frontend  create.php  page
    BP_bp_num=511                      # Service sequence number for 
                                       # conpaas-services/scripts/create_vm/create-img-script.cfg
                                       # Please look in conpaas-services/scripts/create_vm/scripts 
                                       # for the first available number

Running the script in the ConPaaS root will copy the files from the 
tree above to the appropriate places in the :file:`conpaas-client`, 
:file:`conpaas-frontend` and :file:`conpaas-services` trees.  In the 
process of copying, the above keywords will be replaced by the values
you entered, and files and directories named :file:`*blueprint*` will be 
replaced by the new service name.  Furthermore, the following files 
will be adjusted similarly::

    conpaas-services/src/conpaas/core/services.py
    conpaas-frontend/www/create.php
    conpaas-frontend/www/lib/ui/page/PageFactory.php
    conpaas-frontend/www/lib/service/factory/__init__.php

Now you are ready to set up the specifics for your service. In most newly created files you will find the following comment 

::

    *TODO: as this file was created from a BLUEPRINT file, you may want to 
    change ports, paths and/or methods (e.g. for hub) to meet your specific 
    service/server needs*.

So it's a good idea to do just that.


Implementing a new ConPaaS service by hand
==========================================

In this section we describe how to implement a new ConPaaS service by
providing an example which can be used as a starting point. The new
service is called *helloworld* and will just generate helloworld
strings. Thus, the manager will provide a method, called get\_helloworld
which will ask all the agents to return a ’helloworld’ string (or
another string chosen by the manager).

We will start by implementing the agent. We will create a class, called
HelloWorldAgent, which implements the required method - get\_helloworld,
and put it in *conpaas/services/helloworld/agent/agent.py* (Note: make
the directory structure as needed and providing empty \_\_init\_\_.py to
make the directory be recognized as a module path). As you can see in
|lst:helloworldagent|, this class uses some functionality
provided in the conpaas.core package. The conpaas.core.expose module
provides a python decorator (@expose) that can be used to expose the
http methods that the agent server dispatches. By using this decorator,
a dictionary containing methods for http requests GET, POST or UPLOAD is
filled in behind the scenes. This dictionary is used by the built-in
server in the conpaas.core package to dispatch the HTTP requests. The
module conpaas.core.http contains some useful methods, like
HttpJsonResponse and HttpErrorResponse that are used to respond to the
HTTP request dispatched to the corresponding method. In this class we
also implemented a method called startup, which only changes the state
of the agent. This method could be used, for example, to make some
initializations in the agent. We will describe later the use of the
other method, check\_agent\_process.

.. |lst:helloworldagent| replace:: Listing 7

.. centered:: |lst:helloworldagent|: conpaas/services/helloworld/agent/agent.py

.. literalinclude:: ../conpaas-services/src/conpaas/services/helloworld/agent/agent.py

Let’s assume that the manager wants each agent to generate a different
string. The agent should be informed about the string that it has to
generate. To do this, we could either implement a method inside the
agent, that will receive the required string, or specify this string in
the configuration file with which the agent is started. We opted for the
second method just to illustrate how a service could make use of the
config files and also, maybe some service agents/managers need some
information before having been started.

Therefore, we will provide the *helloworld-agent.cfg* file (see
|lst:helloworldcfg|) that will be concatenated to the
default-manager.cfg file. It contains a variable ($STRING) which will be
replaced by the manager.

.. |lst:helloworldcfg| replace:: Listing 8

.. centered:: |lst:helloworldcfg|: ConPaaS/config/agent/helloworld-agent.cfg 

.. literalinclude:: ../conpaas-services/config/agent/helloworld-agent.cfg
    :language: cfg

Now let’s implement an http client for this new agent server. See
|lst:helloworldagentclient|. This client will be used by the
manager as a wrapper to easily send requests to the agent. We used some
useful methods from conpaas.core.http, to send json objects to the agent
server.

.. |lst:helloworldagentclient| replace:: Listing 9

.. centered:: |lst:helloworldagentclient|: conpaas/services/helloworld/agent/client.py

.. literalinclude:: ../conpaas-services/src/conpaas/services/helloworld/agent/client.py

Next, we will implement the manager in the same manner: we will write
the *HelloWorldManager* class and place it in the file
*conpaas/services/helloworld/manager/manager.py*.
(See |lst:helloworldmanagermanager|) To make use of the
IaaS abstractions, we need to instantiate a Controller which controls
all the requests to the clouds on which ConPaaS is running. Note the
lines:

::

    1: self.controller = Controller( config_parser)
    2: self.controller.generate_context('helloworld')

The first line instantiates a Controller. The controller maintains a
list of cloud objects generated from the *config\_parser* file. There
are several functions provided by the controller which are documented in
the doxygen documentation of file *controller.py*. The most important
ones, which are also used in the Hello World service implementation,
are: *generate\_context* (which generates a template of the
contextualization file); *update\_context* (which takes the
contextualization template and replaces the variables with the supplied
values); *create\_nodes* (which asks for additional nodes from the
specified cloud or the default one) and *delete\_nodes* (which deletes
the specified nodes).

Note that the *create\_nodes* function accepts as a parameter a function
(in our case *check\_agent\_process*) that tests if the agent process
started correctly in the agent VM. If an exception is generated during
the calls to this function for a given period of time, then the manager
assumes that the agent process didn’t start correctly and tries to start
the agent process on a different agent VM.

.. |lst:helloworldmanagermanager| replace:: Listing 10

.. centered:: |lst:helloworldmanagermanager|: conpaas/services/helloworld/manager/manager.py

.. literalinclude:: ../conpaas-services/src/conpaas/services/helloworld/manager/manager.py

We can also implement a client for the manager server (see
|lst:helloworldmanagerclient|). This will allow us to use the
command line interface to send requests to the manager, if the frontend
integration is not available.

.. |lst:helloworldmanagerclient| replace:: Listing 11

.. centered:: |lst:helloworldmanagerclient|: conpaas/services/helloworld/manager/client.py

.. literalinclude:: ../conpaas-services/src/conpaas/services/helloworld/manager/client.py

The last step is to register the new service to the conpaas core. One
entry must be added to file *conpaas/core/services.py*, as it is
indicated in |lst:helloworldservices|. Because the Java and PHP
services use the same code for the agent, there is only one entry in the
agent services, called *web* which is used by both webservices.

.. |lst:helloworldservices| replace:: Listing 12

.. centered:: |lst:helloworldservices|: conpaas/core/services.py

.. literalinclude:: ../conpaas-services/src/conpaas/core/services.py

Integrating the new service with the frontend
=============================================

So far there is no easy way to add a new frontend service. Each service
may require distinct graphical elements. In this section we explain how
the Hello World frontend service has been created.

Manager states
--------------

As you have noticed in the Hello World manager implementation, we used
some standard states, e.g. INIT, ADAPTING, etc. By calling the
*get\_service\_info* function, the frontend knows in which state the
manager is. Why do we need these standardized stated? As an example, if
the manager is in the ADAPTING state, the frontend would know to draw a
loading icon on the interface and keep polling the manager.

Files to be modified
--------------------

::

    frontend
    │── www
        │── create.php
        │── lib
            │── service
                │── factory
                    │── __init__.php

Several lines of code must be added to the two files above for the new
service to be recognized. If you look inside these files, you’ll see
that knowing where to add the lines and what lines to add is
self-explanatory.

Files to be added
-----------------
.. role:: red

::

    frontend
    │── www
        │── lib
        |   │── service
        |   |   │── helloworld
        |   |       │── __init__.php
        |   │── ui
        |       │── instance
        |           │── helloworld
        |               │── __init__.php
        │── images
            │── helloworld.png


.. _image-creation:

Creating A ConPaaS Services VM Image
====================================
Various services require certain packages and configurations to be present in
the VM image. ConPaaS provides facilities for creating specialized VM images
that contain these dependencies. Furthermore, for the convenience of users,
there are prebuilt images that contain the dependencies for *all* available
services. If you intend to use these images and do not need a specialized VM
image, then you can skip this section.

Configuring your VM image
-------------------------
The configuration file for customizing your VM image is located at
``conpaas-services/scripts/create_vm/create-img-script.cfg``.

In the **CUSTOMIZABLE** section of the configuration file, you can define
whether you plan to run ConPaaS on Amazon EC2 or OpenStack. Depending
on the virtualization technology that your target cloud uses, you should choose
either KVM or Xen for the hypervisor. Note that for Amazon EC2 this variable
needs to be set to Xen. Please do not make the recommended size for the image
file smaller than the default. The *optimize* flag enables certain optimizations
to reduce the necessary packages and disk size. These optimizations allow for
smaller VM images and faster VM startup.

In the **SERVICES** section of the configuration file, you have the opportunity
to disable any service that you do not need in your VM image. If a service is
disabled, its package dependencies are not installed in the VM image. Paired
with the *optimize* flag, the end result will be a minimal VM image that runs
only what you need.

Note that te configuration file contains also a **NUTSHELL** section. The
settings in this section are explained in details in :ref:`conpaas-in-a-nutshell`.
However, in order to generate a regular customized VM image, make sure that both
*container* and *nutshell* flags in this section are set to *false*.

Once you are done with the configuration, you should run this command in the
``create_vm`` directory::

    $ python create-img-script.py

This program generates a script file named ``create-img-conpaas.sh``. This script
is based on your specific configurations.

Creating your VM image
----------------------
To create the image you can execute ``create-img-conpaas.sh`` in any 64-bit
Debian or Ubuntu machine. Please note that you will need to have root
privileges on such a system. In case you do not have root access to a Debian or
Ubuntu machine please consider installing a virtual machine using your favorite
virtualization technology, or running a Debian/Ubuntu instance in the cloud.

#. Make sure your system has the following executables installed (they
   are usually located in ``/sbin`` or ``/usr/sbin``, so make sure these
   directories are in your ``$PATH``): **dd parted losetup kpartx
   mkfs.ext3 tune2fs mount debootstrap chroot umount grub-install**

#. It is particularly important that you use Grub version 2. To install
   it::

         sudo apt-get install grub2

#. Execute ``create-img-conpaas.sh`` as root.


The last step can take a very long time. If all goes well, the final VM image
is stored as ``conpaas.img``. This file is later registered to your target IaaS
cloud as your ConPaaS services image.

If things go wrong
------------------
Note that if anything fails during the image file creation, the script
will stop and it will try to revert any change it has done. However, it
might not always reset your system to its original state. To undo
everything the script has done, follow these instructions:

#. The image has been mounted as a separate file system. Find the
   mounted directory using command ``df -h``. The directory should be in
   the form of ``/tmp/tmp.X``.

#. There may be a ``dev`` and a ``proc`` directories mounted inside it.
   Unmount everything using::

           sudo umount /tmp/tmp.X/dev /tmp/tmp.X/proc /tmp/tmp.X
         

#. Find which loop device you are using::

           sudo losetup -a
         

#. Remove the device mapping::

           sudo kpartx -d /dev/loopX
         

#. Remove the binding of the loop device::

           sudo losetup -d /dev/loopX


#. Delete the image file

#. Your system should be back to its original state.


.. _creating-a-nutshell:

Creating a Nutshell image
=========================

Starting with the release 1.4.1, ConPaaS is shipped together with a VirtualBox
appliance containing the Nutshell VM image. This section explains how to create
a similar image that can be deployed on a different virtualization technology
(such as the other clouds supported by ConPaaS). The next section describes the
procedure for recreating the VirtualBox image. If you are interested only in
installing the standard VirtualBox image that is shipped with ConPaaS, you may
skip this chapter entirely and only read the installation guide available here:
:ref:`conpaas-in-a-nutshell`.

The procedure for creating a Nutshell image is very similar to the one for 
creating a standard customized image described in section :ref:`image-creation`.
However, there are a few settings in the configuration file which need 
to be considered.

Most importantly, there are two flags in the **Nutshell** section of the 
configuration file, *nutshell* and *container* which control the kind of image
that is going to be generated. Since these two flags can take either value
*true* of *false*, we distinguish four cases:

#. *nutshell = false*, *container = false*: In this case a standard ConPaaS VM
   image is generated and the nutshell configurations are not taken into
   consideration. This is the default configuration which should be used when
   ConPaaS is deployed on a standard cloud.

#. *nutshell = false*, *container = true*: In this case the user indicates that
   the image that will be generated will be a LXC container image. This image
   is similar to a standard VM one, but it does not contain a kernel installation. 

#. *nutshell = true*, *container = false*. In this case a Nutshell image is
   generated and a standard ConPaaS VM image will be embedded in it. This
   configuration should be used for deploying ConPaaS in nested standard VMs
   within a single VM.

#. *nutshell = true*, *container = true*. Similar to the previous case, a Nutshell
   image is generated but this time a container image is embedded in it instead
   of a VM one. Therefore, in order to generate a Nutshell based on LXC containers,
   make sure to set these flags to this configuration. This is the default
   configuration for our distribution of the Nutshell.

Another important setting for generating the Nutshell image is also the path to
a directory containing the ConPaaS tarballs (cps*.tar.gz files). The rest of the
settings specify the distro and kernel versions that the Nutshell VM would have.
For the moment we have tested it only for Ubuntu 12.04 with kernel 3.5.0.

In order to run the image generating script, the procedure is almost the same
as for a standard image. From the ``create_vm`` directory run::

    $ python create-img-script.py
    $ sudo ./create-img-nutshell.sh

Note that if the *nutshell* flag is enabled the generated script file is called
``create-img-nutshell.sh``. Otherwise, the generated script file is called
``create-img-conpaas.sh`` as indicated previously.

Creating a Nutshell image for VirtualBox
----------------------------------------

As mentioned earlier the Nutshell VM can also run on VirtualBox. In order to
generate a Nutshell image compatible with VirtualBox, you have to set the
*cloud* value to *vbox* in the **Customizable** section of the configuration
file. The rest of the procedure is the same as for other clouds. The result
of the image generation script would be a ``nutshell.vdi`` image file which
can be used as a virtual hard drive when creating a new appliance on VirtualBox.

The procedure for creating a new appliance on VirtualBox is quite standard:

#. Name and OS: You choose a custom name for the appliance but use *Linux* and
   *Ubuntu (64 bit)* for the type and version.

#. Memory size: Since the Nutshell runs a significant number of services and
   also requires some memory for the containers, we suggest to choose at least
   3 GB of RAM.

#. Hard drive: Select "User an existing virtual hard drive file", browse to the
   location of the ``nutshell.vdi`` file generated earlier and press *create*.


.. _preinstall-app-in-conpaas-image:

Preinstalling an application into a ConPaaS Services Image
==========================================================

A ConPaaS Services Image contains all the necessary components needed in order
to run the ConPaaS services. For deploying arbitrary applications using ConPaaS,
the :ref:`the-generic-service` provides a mechanism to install and run the application,
along with its dependencies. The installation, however, has to happen during the
initialization of every new node that is started, for example in the ``init.sh``
script of the Generic Service. If installing the application with its dependencies
takes a long time or, in general, is not desired to happen during every deployment
of a new node, another option is available: preinstalling the application inside the
ConPaaS Services Image. The current section describes this process.

#. Download a ConPaaS Services Image appropriate for your computer architecture
   and virtualization technology. Here are the download links for the latest images:
   
   **ConPaaS VM image for Amazon EC2 (x86_64):**
     | http://www.conpaas.eu/dl/conpaas-amazon.img
     | MD5: f883943fa01c5b1c094d6dddeb64da86
     | size: 2.0 GB
   
   **ConPaaS VM image for OpenStack with KVM (x86_64):**
     | http://www.conpaas.eu/dl/conpaas-openstack-kvm.img
     | MD5: 28299ac49cc216dde57b107000078c4f
     | size: 1.8 GB
   
   **ConPaaS VM image for OpenStack with LXC (x86_64):**
     | http://www.conpaas.eu/dl/conpaas-openstack-lxc.img
     | MD5: 45296e4cfcd44325a13703dc67da1d0b
     | size: 1.8 GB
   
   **ConPaaS VM image for OpenStack with LXC for the Raspberry Pi (arm):**
     | http://www.conpaas.eu/dl/ConPaaS-RPI/conpaas-rpi.img
     | MD5: c29cd086e8e0ebe7f0793e7d54304da4
     | size: 2.0 GB
   
   .. warning::
     If you choose to use one of the images above, it is always a good idea to check
     its integrity before continuing to the next step. A corrupt image may result in
     unexpected behaviour which may be hard to trace. You can check the integrity by
     verifying the MD5 hash with the ``md5sum`` command.
   
   Alternatively, you can also create one such image using the instructions provided
   in the section :ref:`image-creation`.
   
   The following steps will use as an example the image for the Raspberry PI.
   For other architecture or virtualization technologies, the commands are the
   same.
   
   .. warning::
     The following steps need to be performed on a machine with the same architecture
     and a similar operating system. For the regular images, this means the 64 bit
     version of a Debian or Ubuntu system. For the Raspberry PI image, the steps need
     to be performed on the Raspberry PI itself (with a Raspbian installation, arm
     architecture). Trying to customize the Raspberry PI image on a x86 system will not
     work!

#. Log in as **root** and change to the directory where you downloaded the image.

#. (Optional) If you need to expand the size of the image, you can do it right now.
   As the image is in the raw format, expanding the size can be done by increasing
   the size of the image file. For example, to increase the size with 1 GB::
   
     root@raspberrypi:/home/pi# dd if=/dev/zero bs=4M count=256 >> conpaas-rpi.img
     256+0 records in
     256+0 records out
     1073741824 bytes (1.1 GB) copied, 56.05551 s, 19 MB/s
   
   If you have the package ``qemu-utils`` installed, you can also use ``qemu-img``
   instead::
   
     root@raspberrypi:/home/pi# qemu-img resize conpaas-rpi.img +1G
     Image resized.

#. Map a loop device to the ConPaaS image::
   
     root@raspberrypi:/home/pi# losetup -fv conpaas-rpi.img
     Loop device is /dev/loop0
   
   .. warning::
     If you already have other loop devices in use, the output of this command may
     contain a different loop device. Take a note of it and replace *loop0* with the
     correct device in the following commands.

#. If you increased the size of the image in step 3, you now need to also expand the
   file system. First, check the integrity of the file system with the following
   command::
   
     root@raspberrypi:/home/pi# e2fsck -f /dev/loop0
     e2fsck 1.42.9 (4-Feb-2014)
     Pass 1: Checking inodes, blocks, and sizes
     Pass 2: Checking directory structure
     Pass 3: Checking directory connectivity
     Pass 4: Checking reference counts
     Pass 5: Checking group summary information
     root: 44283/117840 files (9.1% non-contiguous), 409442/470528 blocks
   
   You can now expand the file system::
   
     root@raspberrypi:/home/pi# resize2fs /dev/loop0
     resize2fs 1.42.9 (4-Feb-2014)
     Resizing the filesystem on /dev/loop0 to 732672 (4k) blocks.
     The filesystem on /dev/loop0 is now 732672 blocks long.

#. Create a new directory and mount the image to it::
   
     root@raspberrypi:/home/pi# mkdir conpaas-img
     root@raspberrypi:/home/pi# mount /dev/loop0 conpaas-img/
   
   Now you can access the contents of the image inside the ``conpaas-img`` directory.

#. Copy your application's binaries and any other static content that you want to
   include in the image somewhere under the ``conpaas-img`` directory.

#. To install any prerequisites, you may want to change the root directory to
   ``conpaas-img``. But first, you will need to mount ``/dev``, ``/dev/pts`` and ``/proc``
   in the ``conpaas-img`` directory (which will become the new root directory), or
   else the installation of some packages may fail::
   
     root@raspberrypi:/home/pi# mount -obind /dev conpaas-img/dev
     root@raspberrypi:/home/pi# mount -obind /dev/pts conpaas-img/dev/pts
     root@raspberrypi:/home/pi# mount -t proc proc conpaas-img/proc

#. You can now execute the chroot::
   
     root@raspberrypi:/home/pi# chroot conpaas-img
   
   Your root directory is now the root of the image.

#. To use *apt-get*, you need to set a working DNS server::
   
     root@raspberrypi:/# echo "nameserver 8.8.8.8" > /etc/resolv.conf
   
   This example uses the Google Public DNS, you may however use any DNS server you
   prefer.
   
   Check that the Internet works in this new environment::
   
     root@raspberrypi:/# ping www.conpaas.eu
     PING carambolier.irisa.fr (131.254.150.34) 56(84) bytes of data.
     64 bytes from carambolier.irisa.fr (131.254.150.34): icmp_seq=1 ttl=50 time=35.8 ms
     [... output omitted ...]

#. Use *apt-get* to install any packages that your application requires::
   
     root@raspberrypi:/# apt-get update
     Hit http://archive.raspbian.org wheezy Release.gpg
     Hit http://archive.raspbian.org wheezy Release
     [... output omitted ...]
     
     root@raspberrypi:/# apt-get install <...>

#. Make the final configurations (if needed) and make sure that everything works.

#. Clean-up:
   
   Exit the chroot::
   
     root@raspberrypi:/# exit
     exit
     root@raspberrypi:/home/pi#
   
   Unmount ``/dev``, ``/dev/pts`` and ``/proc``::
   
     root@raspberrypi:/home/pi# umount conpaas-img/proc
     root@raspberrypi:/home/pi# umount conpaas-img/dev/pts
     root@raspberrypi:/home/pi# umount conpaas-img/dev
    
   Unmount the image::
   
     root@raspberrypi:/home/pi# umount conpaas-img
   
   Remove the directory::
   
     root@raspberrypi:/home/pi# rm -r conpaas-img
   
   Delete the loop device mapping::
   
     root@raspberrypi:/home/pi# losetup -d /dev/loop0
   
   That's it! Now the file ``conpaas-rpi.img`` contains the new ConPaaS image
   with your application pre-installed.

You can now register the new image to the cloud of your choice and update the
ConPaaS Director's settings to use the new image. Instructions are available
in the Installation guide:

**For Amazon EC2:**
  :ref:`registering-image-on-ec2`

**For OpenStack:**
  :ref:`registering-image-on-openstack`
