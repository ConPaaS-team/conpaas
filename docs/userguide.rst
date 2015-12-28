==========
User Guide
==========

ConPaaS currently contains the following services:

-  **Two Web hosting services** respectively specialized for hosting PHP
   and JSP applications;

-  **MySQL** offering a multi-master replicated load-balanced database service;

-  **Scalarix service** offering a scalable in-memory key-value store;

-  **MapReduce service** providing the well-known high-performance
   computation framework;

-  **TaskFarming service** high-performance batch processing;

-  **Selenium service** for functional testing of web applications;

-  **XtreemFS service** offering a distributed and replicated file
   system;

-  **HTC service** providing a throughput-oriented scheduler for bags of tasks
   submitted on demand;

-  **Generic service** allowing the execution of arbitrary applications.

ConPaaS applications can be composed of any number of services. For
example, a bio-informatics application may make use of a PHP and a MySQL
service to host a Web-based frontend, and link this frontend to a
MapReduce backend service for conducting high-performance genomic
computations on demand.

Usage overview
==============

Web-based interface
-------------------

Most operations in ConPaaS can be done using the ConPaaS frontend, which
gives a Web-based interface to the system. The front-end allows users to
register (directly with ConPaaS or through an external Identification 
Provider at Contrail), create services, upload code and data to the 
services, and configure each service.

-  The Dashboard page displays the list of services currently active in
   the system.

-  Each service comes with a separate page which allows one to configure
   it, upload code and data, and scale it up and down.


Command line interfaces
-----------------------

All the functionalities of the frontend are also available using a
command-line interface. This allows one to script commands for ConPaaS.
The command-line interface also features additional advanced
functionalities, which are not available using the front-end.
(The use of external Identification Provider at Contrail is not yet 
available from the command-line interface.)

It exists two command line clients: ``cpsclient.py`` and ``cps-tools``.

``cpsclient.py``
    Installation and configuration:
    see :ref:`cpsclient-installation`.

    Command arguments::

        $ cpsclient.py usage

    Available service types::

        $ cpsclient.py available

    Service command specific arguments::

        $ cpsclient.py usage <service_type>

    Create a service::

        $ cpsclient.py create <service_type>

    List services::

        $ cpsclient.py list

``cps-tools``
    Installation and configuration:
        see :ref:`cpstools-installation`.

    Command arguments::

        $ cps-tools --help

    Available service types::

        $ cps-tools service get_types
        $ cps-service get-types

    Service command specific arguments::

        $ cps-tools <service_type> --help
        $ cps-<service_type> --help

    Create a service::

        $ cps-tools service create <service_type>
        $ cps-tools <service_type> create
        $ cps-<service_type> create

    List services::

        $ cps-tools service list
        $ cps-service list

    List applications::

        $ cps-tools application list
        $ cps-application list

    List clouds::

       $ cps-tools cloud list
       $ cps-cloud list


Controlling services using the front-end
----------------------------------------

The ConPaaS front-end provides a simple and intuitive interface for
controlling services. We discuss here the features that are common to
all services, and refer to the next sections for service-specific
functionality.

Create a service.
    Click on “add new service”, then select the service you want to
    add. This operation adds extra functionalities to the 
    application manager which are specific to a certain service.
    These functionalities enable the application manager to be 
    charge of taking care of the service, but it does not host applications itself. 
    Other instances in charge
    of running the actual application are called “agent” instances.

Start a service.
    Click on “start”, this will create a new virtual machine which can
    host applications, depending on the type of service.

Rename the service.
    By default all new services are named “New service”. To give a
    meaningful name to a service, click on this name in the
    service-specific page and enter a new name.

Check the list of virtual instances.
    A service can run using one or more virtual machine instances. The
    service-specific page shows the list of instances, their respective
    IP addresses, and the role each instance is currently having in the
    service. Certain services use a single role for all instances, while
    other services specialize different instances to take different
    roles. For example, the PHP Web hosting service distinguishes three
    roles: load balancers, web servers, and PHP servers.

Scale the service up and down.
    When a service is started it uses a single “agent” instance. To add
    more capacity, or to later reduce capacity you can vary the number
    of instances used by the service. Click the numbers below the list
    of instances to request adding or removing servers. The system
    reconfigures itself without any service interruption.

Stop the service.
    When you do not need to run the application any more, click “stop”
    to stop the service. This stops all instances except the manager
    which keeps on running.

Terminate the service.
    Click “terminate” to terminate the service. At this point all the
    state of the service manager will be lost.

Controlling services using the command-line interfaces
------------------------------------------------------

Command-line interfaces allow one to control services without using the
graphical interface. The command-line interfaces also offer additional
functionalities for advanced usage of the services.
See :ref:`cpsclient-installation` to install it.

List all options of the command-line tool.
     

    ::

        $ cpsclient.py help 

Create a service.
     

    ::

        $ cpsclient.py create php

List available services.
     

    ::

        $ cpsclient.py list

List service-specific options.
     

    ::

        # in this example the id of our service is 1
        $ cpsclient.py usage 1 

Scale the service up and down.
     

    ::

        $ cpsclient.py usage 1
        $ cpsclient.py add_nodes 1 1 1 0 
        $ cpsclient.py remove_nodes 1 1 1 0 

The credit system
-----------------

In Cloud computing, resources come at a cost. ConPaaS reflects this
reality in the form of a credit system. Each user is given a number of
credits that she can use as she wishes. One credit corresponds to one
hour of execution of one virtual machine. The number of available
credits is always mentioned in the top-right corner of the front-end.
Once credits are exhausted, your running instances will be stopped and
you will not be able to use the system until the administrator decides
to give additional credit.

Note that every service consumes credit, even if it is in “stopped”
state. The reason is that stopped services still have one “manager”
instance running. To stop using credits you must completely terminate
your services.

Tutorial: hosting WordPress in ConPaaS
======================================

This short tutorial illustrates the way to use ConPaaS to install and
host WordPress (http://www.wordpress.org), a well-known third-party Web
application. WordPress is implemented in PHP using a MySQL database so
we will need a PHP and a MySQL service in ConPaaS.

#. Open the ConPaaS front-end in your Web browser and log in. If
   necessary, create yourself a user account and make sure that you have
   at least 5 credits. Your credits are always shown in the top-right
   corner of the front-end. One credit corresponds to one hour of
   execution of one virtual machine instance.

#. Create a MySQL service, start it, reset its password. Copy the IP
   address of the master node somewhere, we will need it in step 5.

#. Create a PHP service, start it.

#. Download a WordPress tarball from http://www.wordpress.org, and
   expand it in your computer.

#. Copy file ``wordpress/wp-config-sample.php`` to
   ``wordpress/wp-config.php`` and edit the ``DB_NAME``, ``DB_USER``,
   ``DB_PASSWORD`` and ``DB_HOST`` variables to point to the database
   service. You can choose any database name for the ``DB_NAME``
   variable as long as it does not contain any special character. We
   will reuse the same name in step 7.

#. Rebuild a tarball of the directory such that it will expand in the
   current directory rather than in a ``wordpress`` subdirectory. Upload
   this tarball to the PHP service, and make the new version active.

#. Connect to the database using the command proposed by the frontend.
   Create a database of the same name as in step 5 using command
   "``CREATE DATABASE databasename;``\ "

#. Open the page of the PHP service, and click “access application.”
   Your browser will display nothing because the application is not
   fully installed yet. Visit the same site at URL
   ``http://xxx.yyy.zzz.ttt/wp-admin/install.php`` and fill in the
   requested information (site name etc).

#. That’s it! The system works, and can be scaled up and down.

Note that, for this simple example, the “file upload” functionality of WordPress will not work if
you scale the system up. This is because WordPress stores files in the
local file system of the PHP server where the upload has been processed.
If a subsequent request for this file is processed by another PHP server
then the file will not be found.
The solution to that issue consists in using the shared file-system
service called XtreemFS to store the uploaded files.

The PHP Web hosting service
===========================

The PHP Web hosting service is dedicated to hosting Web applications
written in PHP. It can also host static Web content.


.. _code_upload:

Uploading application code
--------------------------

PHP applications can be uploaded as an archive or via the Git version
control system.

Archives can be either in the ``tar``, ``zip``, ``gzip`` or ``bzip2`` format.

.. warning::
  the archive must expand **in the current directory** rather than in a
  subdirectory.

The service does not immediately use new applications when
they are uploaded. The frontend shows the list of versions that have
been uploaded; choose one version and click “set active” to activate
it.

Note that the frontend only allows uploading archives smaller than a
certain size. To upload large archives, you must use the command-line
tools or Git.

The following example illustrates how to upload an archive to the
service with id 1 using the ``cpsclient.py`` command line tool:

::

    $ cpsclient.py upload_code 1 path/to/archive.zip

To enable Git-based code uploads you first need to upload your SSH
public key. This can be done either using the command line tool:

::

    $ cpsclient.py upload_key serviceid filename

An SSH public key can also be uploaded using the ConPaaS frontend by
choosing the “checking out repository” option in the “Code management”
section of your PHP service. Once the key is uploaded the frontend will
show the ``git`` command to be executed in order to obtain a copy of the
repository. The repository itself can then be used as usual. A new
version of your application can be uploaded with ``git push``.

::

    user@host:~/code$ git add index.php
    user@host:~/code$ git commit -am "New index.php version"
    user@host:~/code$ git push origin master

Access the application
----------------------

The frontend gives a link to the running application. This URL will
remain valid as long as you do not stop the service.

Using PHP sessions
------------------

PHP normally stores session state in its main memory. When scaling up
the PHP service, this creates problems because multiple PHP servers
running in different VM instances cannot share their memory. To support
PHP sessions the PHP service features a key-value store where session
states can be transparently stored. To overwrite PHP session functions
such that they make use of the shared key-value store, the PHP service
includes a standard “phpsession.php” file at the beginning of every .php
file of your application that uses sessions, i.e. in which function
*session\_start()* is encountered. This file overwrites the session
handlers using the *session\_set\_save\_handler()* function.

This modification is transparent to your application so no particular
action is necessary to use PHP sessions in ConPaaS.

Debug mode
----------

By default the PHP service does not display anything in case PHP errors
occur while executing the application. This setting is useful for
production, when you do not want to reveal internal information to
external users. While developing an application it is however useful to
let PHP display errors.

::

    $ cpsclient.py toggle_debug serviceid

Adding and removing nodes
-------------------------

Like all ConPaaS services, the PHP service is elastic:
service owner can add or remove nodes.
The PHP service (like the Java service) belongs to a class of web services
that deals with three types of nodes:

proxy
  a node that is used as an entry point for the web application and as a load balancer
web
  a node that deals with static pages only
backend
  a node that deals with PHP requests only

When a proxy node receives a request, it redirects it to 
a web node if it is a request for a static page,
or a backend node if it is a request for a PHP page.

If your PHP service has a slow response time, increase the number of backend nodes.

On command line, you can use ``cpsclient.py`` to add nodes.
The ``add_nodes`` sub-command takes 4 arguments in that order: the PHP service identifier,
the number of backend nodes, the number of web nodes and the number of proxy nodes to add.
It also take a 5th optional argument that specify in which cloud nodes will be created.
For example, adding two backend nodes to PHP service id 1::

  $ cpsclient.py add_nodes 1 2 0 0

Adding one backend node and one web node in a cloud provider called ``mycloud``::

  $ cpsclient.py add_nodes 1 1 1 0 mycloud

You can also remove nodes using ``cpsclient.py``.
For example, the following command will remove one backend node::

  $ cpsclient.py remove_nodes 1 1 0 0


.. warning::
  Initially, an instance of each node is running on one single VM.
  Then, when adding a backend node, ConPaaS will move the backend
  node running on the first VM to a new VM.
  So, actually, it will *not* add a new backend node the first time.
  Requesting for one more backend node will create a new VM that will
  run an additional backend.

Autoscaling
-----------

One of the worries of a service owner is the trade-off between the performance
of the service and the cost of running it. The service owner can add nodes to
improve the performance of the service, which will have more nodes to balance the
load, or remove nodes from the service to decrease the cost per hour, but
increase the load per node.

Adding and removing nodes as described above is interactive: the service owner
has to run a command line or push some buttons on the web frontend GUI. However,
the service owner is not always watching for the performance of his Web service.

Autoscaling for the PHP service will add or remove nodes according to the load
on the Web service. If the load on nodes running a Web service exceeds a given
threshold and the autoscaling mechanism estimates that it will last, then the
autoscaling mechanism will automatically add nodes for the service to balance
the load. If the load on nodes running a Web service is low and the autoscaling
mechanism estimates that it will last and that removing some nodes will not
increase the load on nodes beyond the given threshold, then the autoscaling
mechanism will automatically remove nodes from the service to decrease the cost
per hour of the service.

Autoscaling for the PHP service will also take into account the different kind
of nodes that the cloud providers propose. They usually propose small instances,
middle range instances and large instances. So, the autoscaling mechanism will
select different kind of nodes depending on the service owner strategy choice.

To enable autoscaling for the PHP service, run the command::

    $ cpsclient.py on_autoscaling <sid> <adapt_interval> <response_time_threshold> <strategy>
    
where:
  * <sid> is the service identifier
  * <adapt_interval> is the time in minutes between automatic adaptation point
  * <response_time_threshold> is the desired response time in milliseconds
  * <strategy> is the policy used to select instance type when adding nodes, it must be one of:

    - "low": will always select the smallest (and cheapest) instance proposed by the cloud provider
    - "medium_down"
    - "medium"
    - "medium_up"
    - "high"

For example::

    $ cpsclient.py on_autoscaling 1 5 2000 low

enables autoscaling for PHP service 1, with an adaptation every 5 minutes, a
response time threshold of 2000 milliseconds (2 seconds), and using the strategy
low. This means that every 5 minutes, autoscaling will determine if it will add
nodes, remove nodes, or do nothing, by looking at the history of the Web service
response time and comparing it to the desired 2000 milliseconds. According the
specified "low" strategy, if it decides to create nodes, it will always select the
smallest instance from the cloud provider.

Any time, the service owner may re-run the "on_autoscaling" command to tune autoscaling with different parameters::

    $ cpsclient.py on_autoscaling 1 10 1500 low

this command updates the previous call to "on_autoscaling" and changes the
adaptation interval to 10 minutes, and setting a lower threshold to 15000
milliseconds.

Autoscaling may be disabled by running command::

    $ cpsclient.py off_autoscaling <sid>


The Java Web hosting service
============================

The Java Web hosting service is dedicated to hosting Web applications
written in Java using JSP or servlets. It can also host static Web
content.

Uploading application code
--------------------------

Applications in the Java Web hosting service can be uploaded in the form
of a ``war`` file or via the Git version control system. The service
does not immediately use new applications when they are uploaded. The
frontend shows the list of versions that have been uploaded; choose one
version and click “set active” to activate it.

Note that the frontend only allows uploading archives smaller than a
certain size. To upload large archives, you must use the command-line
tools or Git.

The following example illustrates how to upload an archive with the
``cpsclient.py`` command line tool::

    $ cpsclient.py upload_code serviceid archivename

To upload new versions of your application via Git, please refer to
section :ref:`code_upload`.

Access the application
----------------------

The frontend gives a link to the running application. This URL will
remain valid as long as you do not stop the service.

The MySQL Database Service
===============================================

The MySQL service is a true multi-master database cluster based on
MySQL-5.5 and the Galera synchronous replication system. It is an
easy-to-use, high-availability solution, which provides high system
uptime, no data loss and scalability for future growth. It provides
exactly the same look and feel as a regular MySQL database.
 
Summarizing, its advanced features are:

-  Synchronous replication
-  Active-active multi-master topology
-  Read and write to any cluster node
-  Automatic membership control, failed nodes drop from the cluster
-  Automatic node joining
-  True parallel replication, on row level
-  Both read and write scalability
-  Direct client connections, native MySQL look & feel

The Database Nodes and Load Balancer Nodes
-------------------------------------------

The MySQL service offers the capability to instantiate multiple
instances of database nodes, which can be used to increase the
throughput and to improve features of fault tolerance through
replication. The multi-master structure allows any database node to
process incoming updates, because the replication system is
responsible for propagating the data modifications made by each member
to the rest of the group and resolving any conflicts that might arise
between concurrent changes made by different members. These features
can be used to increase the throughput of the cluster. 

To obtain the better performances from a cluster, it is a best
practice to use it in balanced fashion, so that each node has
approximatively the same load of the others. To achieve this, the
service allows users to allocate special load balancer nodes
(``glb_nodes``) which implement load balancing. Load balancer nodes
are designed to receive all incoming database queries and
automatically schedule them between the database nodes, making sure
they all process equivalent workload.

Resetting the User Password
---------------------------

When a MySQL service is started, a new user "``mysqldb``" is created
with a randomly-generated password. To gain access to the database you
must first reset this password. Click "Reset Password" in the
front-end, and choose the new password.

Note that the user password is not kept by the ConPaaS frontend. If
you forget the password the only thing you can do is reset the
password again to a new value.

Accessing the database
----------------------

The frontend provides the command-line to access the database cluster.
Copy-paste this command in a terminal. You will be asked for the user
password, after which you can use the database as you wish. Note
that, in case the service has instantiated a load balancer, the command
refers to the load balancer IP and its specific port, so the load
balancer can receive all the queries and distributes them across the
ordinary nodes. Note, again, that the *mysqldb* user has extended
privileges. It can create new databases, new users etc.

Uploading a Database Dump
-------------------------

The ConPaaS frontend allows users to easily upload database dumps to a
MySQL service. Note that this functionality is restricted to dumps of
a relatively small size. To upload larger dumps you can always use the
regular mysql command for this::

    $ mysql mysql-ip-address -u mysqldb -p < dumpfile.sql

Performance Monitoring
----------------------

The MySQL service interface provides a sophisticated mechanism to monitor the
service. The user interface, in the frontend, shows a monitoring control,
called "Performance Monitor", that can be used to monitor a large cluster's
behaviour. It interacts with "Ganglia", "Galera" and "MySQL" to obtain various
kinds of information. Thus, "Performance Monitor" provides a solution for
maintaining control and visibility of all nodes, with a monitoring dynamic data
every few seconds. 

It consists of three main components.

- "Cluster usage" monitors the number of incoming SQL queries. This
  will let you know in advance about any overload of the resources.
  You will also be able to spot usage trends over time so as to get
  insights on when you need to add new nodes, serving the MySQL
  database.

- The second control highlights the cluster’s performance, with a
  table detailing the load, memory usage, CPU utilization, and network
  traffic for each node of the cluster.  Users can use these
  informations in order to detect problems in their applications. The
  table displays the resource utilization across all nodes, and
  highlight the parameters which suggest an abnormality. For example
  if CPU utilization is high, or free memory is very low this is shown
  clearly. This may mean that processes on this node will start to
  slow down, and that it may be time to add additional nodes to the
  cluster. On the other hand this may indicate a malfunction of the
  specific node.

  In this latter case, in a multimaster system, it may be a good idea to
  kill the node and replace it with another one. The monitoring
  system also simplifies this kind of operations through buttons which
  allow to directly kill a specific node. Keep in mind, however,
  that high CPU utilization may not necessarily affect application
  performance.

- "Galera Mean Misalignment" draws a real-time measure of the mean
  misalignment across the nodes. This information is derived by
  Galera metrics about the average length of the receive queue since
  the most recent status query. If this value is noticeably larger
  than zero, the nodes are likely to be overloaded, and cannot apply
  the writesets as quickly as they arrive, resulting in replication
  throttling.

The Scalarix key-value store service
====================================

The Scalarix service provides an in-memory key-value store. It is highly
scalable and fault-tolerant. This service deviates slightly from the
organization of other services in that it does not have a separate
manager virtual machine instance. Scalarix is fully symmetric so any
Scalarix node can act as a service manager.

Accessing the key-value store
-----------------------------

Clients of the Scalarix service need the IP address of (at least) one
node to connect to the service. Copy-paste the address of any of the
running instances in the client. A good choice is the first instance in
the list: when scaling the service up and down, other instances may be
created or removed. The first instance will however remain across these
reconfigurations, until the service is terminated.

Managing the key-value store
----------------------------

Scalarix provides its own Web-based interface to monitor the state and
performance of the key-value store, manually add or query key-value
pairs, etc. For convenience reasons the ConPaaS front-end provides a
link to this interface.

The MapReduce service
=====================

The MapReduce service provides the well-known Apache Hadoop framework in
ConPaaS. Once the MapReduce service is created and started, the
front-end provides useful links to the Hadoop namenode, the job tracker,
and to a graphical interface which allows to upload/download data
to/from the service and issue MapReduce jobs. 

.. warning::
  This service requires virtual machines with **at least** 384 MB of RAM to
  function properly.

The TaskFarming service
====================

The TaskFarming service provides a bag of tasks scheduler for ConPaaS. The
user needs to provide a list of independent tasks to be executed on the
cloud and a file system location where the tasks can read input data
and/or write output data to it. The service first enters a sampling
phase, where its agents sample the runtime of the given tasks on
different cloud instances. The service then based on the sampled
runtimes, provides the user with a list of schedules. Schedules are
presented in a graph and the user can choose between cost/makespan of
different schedules for the given set of tasks. After the choice is made,
the service enters the execution phase and completes the execution of
the rest of the tasks according to the user’s choice.

Preparing the ConPaaS services image
------------------------------------

By default, the TaskFarming service can execute the user code that is
supported by the default ConPaaS services image. If user’s tasks depend
on specific libraries and/or applications that do not ship with the
default ConPaaS services image, the user needs to configure the ConPaaS
services image accordingly and use the customized image ID in ConPaaS
configuration files.

The bag of tasks file
---------------------

The bag of tasks file is a simple plain text file that contains the list
of tasks along with their arguments to be executed. The tasks are
separated by new lines. This file needs to be uploaded to the service,
before the service can start sampling. Below is an example of a simple
bag of tasks file containing three tasks::

    /bin/sleep 1 && echo "slept for 1 seconds" >> /mnt/xtreemfs/log
    /bin/sleep 2 && echo "slept for 2 seconds" >> /mnt/xtreemfs/log
    /bin/sleep 3 && echo "slept for 3 seconds" >> /mnt/xtreemfs/log

The minimum number of tasks required by the service to start sampling is
depending on the number of tasks itself, but a bag with more than thirty
tasks is large enough.

The filesystem location
-----------------------

The TaskFarming service uses XtreemFS for data input/output. The actual task
code can also reside in the XtreemFS. The user can optionally provide an
XtreemFS location which is then mounted on TaskFarming agents.

The demo mode
-------------

With large bags of tasks and/or with long running tasks, the TaskFarming
service can take a long time to execute the given bag. The service
provides its users with a progress bar and reports the amount of money
spent so far. The TaskFarming service also provides a “demo” mode where the
users can try the service with custom bags without spending time and
money.

The XtreemFS service
====================

The XtreemFS service provides POSIX compatible storage for ConPaaS. Users can
create volumes that can be mounted remotely or used by other ConPaaS services,
or inside applications. An XtreemFS instance consists of multiple DIR, MRC and 
OSD servers. The OSDs contain the actual storage, while the DIR is a directory 
service and the MRC contains meta data. By default, one instance of each runs 
inside the first agent virtual machine and the service can be scaled up and 
down by adding and removing additional OSD nodes. The XtreemFS documentation 
can be found at http://xtreemfs.org/userguide.php.


SSL Certificates
----------------

The XtreemFS service uses SSL certificates for authorization and authentication.
There are two types of certificates, user-certificates and client-certificates.
Both certificates can additionally be flagged as administrator certificates which
allows performing administrative file-systems tasks when using them to access
XtreemFS. Certificates are only valid for the service that was used to create them.
The generated certificates are in P12-format.

The difference between client- and user-certificates is how POSIX users and
groups are handled when accessing volumes and their content. Client-certificates
take the user and group with whom an XtreemFS command is called, or a mounted XtreemFS
volume is accessed. So multiple users might share a single client-certificate.
On the other hand, user-certificates contain a user and group inside the certificate.
So usually, each user has her personal user-certificate. Both kinds of certificate can
be used in parallel. Client-certificates are less secure, since the user and group with
whom files are accessed can be arbitrarily changed if the mounting user has local
superuser rights. So client-certificates should only be used in trusted environments.

Using the command line client, certificates can be created like this, where <adminflag>
can be "true", "yes", or "1" to grant administrator rights::

    $ cpsclient.py get_client_cert <service-id> <passphrase> <adminflag> <filename.p12>
    $ cpsclient.py get_user_cert <service-id> <user> <group> <passphrase> <adminflag> <filename.p12>

Accessing volumes directly
--------------------------

Once a volume has been created, it can be directly mounted on a remote site by
using the mount.xtreemfs command. A mounted volume can be used like any local
POSIX-compatible filesystem. You need a certificate for mounting (see last section).
The command looks like this, where <address> is the IP of an agent running
an XtreemFS directory service (usually the first agent)::

    $ mount.xtreemfs <address>/<volume> <mount-point> --pkcs12-file-path <filename.p12> --pkcs12-passphrase <passphrase> 

The volume can be unmounted with the following command::

    $ fusermount -u <mount-point>

Please refer to the XtreemFS user guide (http://xtreemfs.org/userguide.php) for further details.

Policies
--------

Different aspects of XtreemFS (e.g. replica- and OSD-selection) can be 
customised by setting certain policies. Those policies can be set via the 
ConPaaS command line client (recommended) or directly via xtfsutil (see the
XtreemFS user guide). The commands are like follows, were <policy_type> is
"osd_sel", "replica_sel", or "replication"::

   $ cpsclient.py list_policies <service-id> <policy_type>
   $ cpsclient.py set_policy <service-id> <policy_type> <volume> <policy> [factor]

Persistency
-----------

If the XtreemFS service is shut down, all its data is permanently lost. If 
persistency beyond the service runtime is needed, the XtreemFS service can be
moved into a snapshot by using the download_manifest operation of the command
line client.

.. warning::
  This operation will automatically shut down the service and its application.

The whole application containing the service and all of its stored volumes 
with their data can be moved back into a running ConPaaS application by using
the manifest operation.

The commands are::

    $ cpsclient.py download_manifest <application-id> > <filename>
    $ cpsclient.py manifest <filename>


Important notes
---------------

When a service is scaled down by removing OSDs, the data of those OSDs is
migrated to the remaining OSDs. Always make sure there is enough free space 
for this operation to succeed. Otherwise you risk data loss.
The download_manifest operation of the XtreemFS service will also shut the 
service down. This behaviour might differ from other ConPaaS services, but is 
necessary to avoid copying the whole filesystem (which would be a very 
expensive operation). This might change in future releases.

The HTC service
===============
The HTC service provides a throughput-oriented scheduler for bags of tasks
submitted on demand for ConPaaS. An initial bag of tasks is sampled generating a
throughput = f(cost) function.  The user is allowed at any point, including
upon new tasks submission, to request the latest throughput = f(cost) function
and insert his target throughput.  After the first bag is sampled and submitted
for execution the user is allowed to add tasks to the job with the
corresponding identifier. The user is allowed at any point, including upon new
tasks submission, to request the latest throughput = f(cost) function and adjust
his target throughput.  All tasks that are added are immediately submitted for
execution using the latest configuration requested by the user, corresponding
to the target throughput.

Available commands
------------------
``start service_id``: prompts the user to specify a mode (’real’ or ’demo’) and
type (’batch’, ’online’ or ’workflow’) for the service. Starts the service
under the selected context and initializes all the internal data structures for
running the service.

``stop service_id``: stops and releases all running VMs that exist in the pool
of workers regardless of the tasks running.

``terminate service_id``: stops and releases the manager VM along with the
running algorithm and existing data structures.

``create_worker service_id type count``: adds count workers to the pool returns
the worker_ids. The worker is added to the table. The manager starts the worker
on a VM requested of the selected type.

``remove_worker service_id worker_id``: removes a worker from the condor pool.
The worker_id is removed from the table.

``create_job service_id .bot_file``: creates a new job on the manager and
returns a job_id. It uploads the .bot_file on the manager and assign a queue to
the job which will contain the path of all .bot_files submitted to this job_id.

``sample service_id job_id``: samples the job on all available machine types in
the cloud according to the HTC model.

``throughput service_id``: prompts the user to select a target throughput
within [0,TMAX] and returns the cost for that throughput.

``configuration service_id``: prompts the user to select a target throughput
within [0,TMAX] and returns the machine configuration required for that
throughput. At this point the user can manually create the pool of workers
using create_worker and remove_worker.

``select service_id``: prompts the user to select a target throughput within
[0,TMAX] and creates the pool of workers needed to obtain that throughput. 

``submit service_id job_id``: submits all the bags in this job_id for execution
with the current configuration of workers.

``add service_id job_id .bot_file``: submits a .bot_file for execution on
demand.  The bag is executed with the existing configuration.


.. _the-generic-service:

The Generic service
===================

The Generic service facilitates the deployment of arbitrary server-side
applications in the cloud. A Generic service may contain multiple Generic
agents, each of them running an instance of the application.

The users can control the application's life cycle by installing or removing
code versions, running or interrupting the execution of the application or
checking the status of each of the Generic agents. New Generic agents can be
added or old ones removed at any time, based on the needs of the application.
Moreover, additional storage volumes can be attached to agents if additional
storage space is needed.

To package an application for the Generic service, the user has to provide
simple scripts that guide the process of installing, running, scaling up
and down, interrupting or removing an application to/form a Generic agent.

Agent roles
-----------
Generic agents assume two roles: the first agent started is always a “master”
and all the other agents assume the role of regular “nodes”. This distinction
is purely informational: there is no real difference between the two agent
types, both run the same version of the application's code and are treated by
the ConPaaS system in exactly the same way. This distinction may be useful,
however, when implementing some distributed algorithms in which one node must
assume a specific role, such as leader or coordinator.

It is guaranteed that, as long as the Generic service is running, there will
always be exactly one agent with the “master” role and the same agent will
assume this role until the Generic service is stopped. Adding or removing nodes
will only affect the number of regular nodes.

Packaging an application
------------------------
To package an application for the Generic service, one needs to write various
scripts which are automatically called inside agents whenever the corresponding
events happen. The following scripts may be used:

``init.sh`` – called whenever a new code version is activated. The script is
automatically called for each agent as soon as the corresponding code version
becomes active. The script should contain commands that initialize the
environment and prepare it for the execution of the application. It is guaranteed
that this script is is called before any other scripts in a specific code version.

``notify.sh`` – called whenever a new agent is added or removed. The script
is automatically called whenever a new agent is added and becomes active or
is removed from the Generic service. The script may configure the application
to take into account the addition or removal of a specific node or group of
nodes. In order to retrieve the updated list of nodes along with their IP
addresses, the script may check the content of the following file, which always
contains the current list of nodes in JSON format: ``/var/cache/cpsagent/agents.json``.
Note that when multiple nodes are added or removed in a single operation, the
script will be called only once for each of the remaining nodes.

``run.sh`` – called whenever the user requests to start the application. 
The script should start executing the application and after the execution
completes, it may return an error code that will be shown to the user. It is
guaranteed that the ``init.sh`` script already finished execution before ``run.sh``
is called.

``interrupt.sh`` – called whenever the user requests that the application is
interrupted. The script should notify the application that the interruption was
requested and allow it to gracefully terminate execution. It is guaranteed that
``interrupt.sh`` is only called when the application is actually running.

``cleanup.sh`` – called whenever the user requests that the application's code
is removed from the agent. The script should remove any files that the
application generated during execution and are not longer needed. After the
script completes execution, a new version of the code may be activated and the
``init.sh`` script called again, so the agent needs to be reverted to a clean
state.

To create an application's package, all the previous scripts must be added to
an archive in the ``tar``, ``zip``, ``gzip`` or ``bzip2`` format. If there is
no need to execute any tasks when a specific type of event happens, some of
the previous scripts may be left empty or may even be missing completely from
the application's archive.

.. warning::
  the archive must expand **in the current directory** rather than in a subdirectory.

The application's binaries can be included in the archive only if they are small
enough.

.. warning::
  the archive is stored on the service manager instance and its contents are extracted in each
  agent's root file system which usually has a very limited amount of free
  space (usually a little more than 100 MB), so application's binaries can
  be included only if they are really small (a few MBs).

A better idea would be to attach an additional storage volume where the ``init.sh``
script can download the application's binaries from an external location for each
Generic agent. This will render the archive very small as it only contains a few
scripts. This is the recommended approach.

Uploading the archive
---------------------
An application's package can be uploaded to the Generic service either as an
archive or via the Git version control system. Either way, the code does not
immediately become active and must be activated first.

Using the web frontend, the “Code management” section offers the possibility
to upload a new archive to the Generic service. After the upload succeeds,
the interface shows the list of versions that have been uploaded; choose one
version and click “set active” to activate it. Note that the frontend only
allows uploading archives smaller than a certain size. To upload large archives,
you must use the command-line tools or Git. The web frontend also allows
downloading or deleting a specific code version. Note that the active code
version cannot be deleted.

Using the command-line interface, uploading and enabling a new code version
is just as simple. The following example illustrates how to upload and activate
an archive to the service with id 1 using the ``cpsclient.py`` command line tool::

  $ cpsclient.py upload_code 1 test-code.tar.gz
  Code version code-pw1LKs uploaded
  $ cpsclient.py enable_code 1 code-pw1LKs
  code-pw1LKs enabled
  $ cpsclient.py list_uploads 1
  current codeVersionId filename         description
  ------------------------------------------------------
        * code-pw1LKs   test-code.tar.gz
          code-default  code-default.tar Initial version

To download a specific code version, the following command may be used::

  $ cpsclient.py download_code <serviceid> <code-version>

The archive will be downloaded using the original name in the current directory.

.. warning::
  if another file with the same name is present in the current directory,
  it will be overwritten.

The command-line client also allows deleting a code version, with the exception
of the currently active version::

  $ cpsclient.py delete_code <serviceid> <code-version>

It is a good idea to delete the code versions which are not needed anymore, as
all the available code versions are stored in the Generic manager's file system,
which has a very limited amount of available space. In contrast to the manager,
the agents only store the active code version, which is replaced every time a new
version becomes active.

Uploading the code using git
----------------------------
As an alternative to uploading the application's package as stated above, the
Generic service also supports uploading the package's content using Git.

To enable Git-based code uploads, you first need to upload your SSH public key.
This can be done either using the web frontend, in the “Code management” section,
after selecting “checking out repository” or using the command-line client::

  $ cpsclient.py upload_key <serviceid> <filename>

You can check that the key was successfully uploaded by listing the trusted
SSH keys::

  $ cpsclient.py list_keys <serviceid>

Once the key is uploaded, the following command has to be executed in order to
obtain a copy of the repository::

  $ git clone git@<generic-manager-ip>:code

The repository itself can then be used as usual. A new version of your
application can be uploaded with ``git push``::

  $ cd code
  $ git add {init,notify,run,interrupt,cleanup}.sh
  $ git commit -m "New code version"
  $ git push origin master

The ``git push`` command will trigger the updating of the available code versions.
To activate the new code version, the same procedure as before must be followed.
Note that, when using the web frontend, you may need to refresh the page in
order to see the new code version.

To download a code version uploaded using Git, you must clone the repository
and checkout a specific commit. The version number represents the first part
of the commit hash, so you can use that as a parameter for the ``git checkout``
command::

  $ cpsclient.py list_uploads 1
  current codeVersionId filename            description
  ---------------------------------------------------------
          git-7235de9   7235de9             Git upload
        * code-default  code-default.tar    Initial version
  $ git clone git@192.168.56.10:code
  $ cd code
  $ git checkout 7235de9

Deleting a specific code version uploaded using Git is not possible.

Managing storage volumes
------------------------
Storage volumes of arbitrary size can be attached to any Generic agent.
Note that, for some clouds such as Amazon EC2 and OpenStack, the volume
size must be a multiple of  1 GB. In this case, if the requested size does
not satisfy this constraint, it will be rounded up to the smallest size
multiple of 1 GB that is greater than the requested size.

The attach or detach operations are permitted only if there are no scripts
running inside the agents. This guarantees that a volume is never in use when
it is detached.

To create and attach a storage volume using the web frontend, you must click
the “+ add volume” link below the instance name of the agent that should have
this volume attached to. A small form will expand where you can enter the
volume name and the requested size. Note that the volume name must be unique,
or else the volume will not be created. The volume is created and attached
after pressing the “create volume” button. Depending on the cloud in use and
the volume size, this operation may take a little while. Additional volumes
can be attached later to the same agent if more storage space is needed.

The list of volumes attached to a specific agent is shown in the instance
view of the agent, right under the instance name. For each volume, the name
of the volume and the requested size is shown. To detach and delete a volume,
you can press the red X icon after the volume's size.

.. warning::
  after a volume is detached, all data contained within it is lost forever.

Using the command-line client, a volume can be created and attached to a
specific agent with the following command::

  $ cpsclient.py create_volume <serviceid> <vol_name> <size> <agent_id>

Size must always be specified in MB. To find out the *agent_id* of a specific
instance, you may issue the following command::

  $ cpsclient.py list_nodes <serviceid>

The list of all storage volumes can be retrieved with::

  $ cpsclient.py list_volumes <serviceid>

This command detaches and deletes a storage volume::

  $ cpsclient.py delete_volume <serviceid> <agent_id>

Controlling the application's life cycle
----------------------------------------
A newly started Generic service contains only one agent with the role
“master”.  As in the case of other ConPaaS services, nodes can be added
to the service (or removed from the service) at any point in time.

In the web frontend, new Generic nodes can be added by entering the number
of new nodes (in a small cell below the list of instances) and pressing
the “submit” button. Entering a negative number of nodes will lead to the
removal of the specified number of nodes.

On the command-line, nodes can be added with the following command::

  $ cpsclient.py add_nodes <serviceid> <number_of_nodes>

Immediately after the new nodes are ready, the active code version is copied
to the new nodes and the ``init.sh`` script is executed in each of the new
nodes. All the other nodes which were already up before the execution of the
command will be notified about the addition of the new nodes to the service,
so ``notify.sh`` is executed in their case. The ``init.sh`` script is never
executed twice for the same agent and the same code version.

Nodes can be removed with::

  $ cpsclient.py remove_nodes <serviceid> <number_of_nodes>

After the command completes and the specified number of nodes are terminated,
the ``notify.sh`` script is executed for all the remaining nodes to notify
them of the change.

The Generic service also offers an easy way to run the application on every
agent, interrupt a running application or cleanup the agents after the
execution is completed.

In the web frontend, the ``run``, ``interrupt`` and ``cleanup`` buttons
are conveniently located on the top of the page, above the instances view.
Pressing such a button will execute the corresponding script in all the agents.
Above the buttons there is also a parameters field which allow the user to
specify parameters which will be forwarded to the script during the execution.

On the command line, the following commands may be used::

  $ cpsclient.py run <serviceid> [parameters]
  $ cpsclient.py interrupt <serviceid> [parameters]
  $ cpsclient.py cleanup <serviceid> [parameters]

The parameters are optional and, if not present, will be replaced by an empty
list.

The ``run`` and ``cleanup`` commands cannot be issued if any scripts are
still running inside at least one agent. In this case, if it is not desired
to wait for them to complete execution, ``interrupt`` may be called first.

In turn, ``interrupt`` cannot be called if no scripts are running (there is
nothing to interrupt). The ``interrupt`` command will execute the ``interrupt.sh``
script that tries to cleanly shut down the application. If the ``interrupt.sh``
completes execution and the application is still running, the application will
be automatically killed. When ``interrupt.sh`` itself has to be
killed, the ``interrupt`` command can be issued again. In this case, it will
kill all the running scripts (including ``interrupt.sh``). In the web frontend,
this is highlighted by renaiming the ``interrupt`` button to ``kill``.

.. warning::
  issuing the ``interrupt`` command twice kills all the running
  scripts, including the child processes started by them!

Enabling a new code version is allowed only when no script from the current
code version is currently running. If it is not desired to wait for them
to complete execution, ``interrupt`` may be called first. When enabling a
new code version, immediately after copying the new code to the agents,
the new ``init.sh`` script is called.

Checking the status of the agents
---------------------------------
The running status of the various scripts for each agent can easily be
checked in both the web frontend and using the command-line interface.

In the web frontend, the instance view of each agent contains a table with
the 5 scripts and each script's running status, along with a led that codes
the status using colors: *light blue* when the current version of the script
was never executed, *blinking green* when the script is currently running
and *red* when the script finished execution. In the latter case, hovering
the mouse pointer over the led will indicate the return code in  a tool-tip
text.

With the command-line interface, the status of the scripts for each agent
can be listed using the following command::

  $ cpsclient.py get_script_status <serviceid>

The Generic service also facilitates retrieving the agent's log file and
the contents of standard output and error streams. In the web frontend,
three links are present in the instance's view of each agent. Using the
command line, the logs can be retrieved with the following command::

  $ cpsclient.py get_script_status <serviceid> <agent_id>

To find out the agent_id of a specific instance, you may issue the following command::

  $ cpsclient.py list_nodes <serviceid>


.. _nutshell-guide:

ConPaaS in a VirtualBox Nutshell
================================

ConPaaS in a Nutshell is a version of ConPaaS which runs inside a
single VirtualBox VM. It is the recommended way to test the system
and/or to run it in a single physical machine.

Starting the Nutshell
---------------------

In this section, we assume that the Nutshell is already installed into VirtualBox
according to the instructions in the Installation guide. If this is not the case,
you may want to check these instructions first: :ref:`conpaas-in-a-nutshell`.

#. Open VirtualBox and start the Nutshell by selecting it from the list on the left
   side and then clicking the *Start* button. Wait a few seconds until you see a
   login prompt. Any messages that may appear in the VM window at this stage are
   usually harmless debug messages which can be ignored.

#. Once the Nutshell is started and the login prompt appears, you can log into it.
   The login credentials are::
   
    Username: stack
    Password: contrail

#. One important piece of information which you may want to note down is
   the IP address assigned to the Nutshell VM. This can be used to access
   the web frontend directly from your host machine or to SSH into the Nutshell
   VM in order to execute command-line interface commands or to copy files.
   To find it, type the following command::
   
     $ ifconfig br200
   
   The IP address will appear in the second line of text.


Using the Nutshell via the graphical frontend
---------------------------------------------

You can access the ConPaaS frontend by inserting the IP address of the
Nutshell VM in your Web browser, **making sure to add https:// in front of it**::

  https://192.168.56.xxx 

.. warning::
  The first time you access the web frontend, a security warning will appear,
  stating that the SSL certificate of the website is invalid. This is normal, as
  the certificate is self-signed and the server name is usually different from the
  IP address you are using to access it. To proceed further, you need to confirm
  that you want to continue anyway. The procedure is different depending on your
  web browser.

Note that the frontend is accessible only from your local
machine. Other machines will not be able to access it. A default user
is available for you, its credentials are::

  ConPaaS
  Username: test
  Password: password

You can now use the frontend in the same way as any ConPaaS system,
creating applications, services etc. Note that the services are also
only accessible from your local machine.

Note that also *Horizon* (the Openstack dashboard) is running on it as
well. In case you are curious and want to have a look under the hood,
Horizon can be reached (using HTTP, not HTTPS) at the same IP address::

  http://192.168.56.xxx

The credentials for Horizon are::

  Openstack
  Username: admin
  Password: password


Using the Nutshell via the command-line interface
-------------------------------------------------

You can also use the command-line to control your Nutshell installation.
You need to log in as the *stack* user directly in the VirtualBox window
or using SSH to connect to the Nutshell VM's IP address (the preferred method).

On login, both the ConPaaS and OpenStack users will already be authenticated.
You should be able to execute ConPaaS commands, for example starting a
*helloworld* service can be done with::

  $ cpsclient.py create helloworld

or::

  $ cps-tools service create helloworld

OpenStack commands are also available. For example::

  $ nova list

lists all the active instances and::

  $ cinder list

lists all the existing volumes.

The Nutshell contains a *Devstack* installation of Openstack,
therefore different services run and log on different tabs of a
*screen* session. In order to stop, start or consult the logs of these
services, connect to the screen session by executing::

  $ /opt/stack/devstack/rejoin-stack.sh

Every tab in the screen session is labeled with the name of the
service it belongs to. For more information on how to navigate between
tabs and scroll up and down the logs, please consult the manual page
for the *screen* command.


.. _changing-the-ips-of-the-nutshell:

Changing the IP address space used by the Nutshell
--------------------------------------------------

The Nutshell VM uses an IP address assigned by the DHCP server of the
host-only network of VirtualBox. In the default settings, the DHCP server
uses a range from ``192.168.56.101`` to ``192.168.56.254``. If you want to change
this IP range, you can do this in the VirtualBox window by going to *File* >
*Preferences* > *Network* > *Host-only Networks*. Select the *vboxnet0* network
and click on the *Edit host-only network* button and then *DHCP server*.

Note that ConPaaS services running inside the Nutshell VM also need to have
IP addresses assigned. This is done using OpenStack's floating IP mechanism.
The default configuration uses an IP range from ``192.168.56.10`` to ``192.168.56.99``,
which does not overlap with the default one used by the DHCP server of the
host-only network in VirtualBox. If you want to modify this IP range, execute
the following commands on the Nutshell as the *stack* user::

  $ nova floating-ip-bulk-delete 192.168.56.0/25
  $ nova floating-ip-bulk-create --pool public --interface br200 <new_range>

The first command removes the default IP range for floating IPs and the
second adds the new range. After executing these two commands, do not
forget to restart the Nutshell so the changes take effect::

  $ sudo reboot


Using the Nutshell to host a publicly accessible ConPaaS installation
---------------------------------------------------------------------

The Nutshell can also be configured to host services which are accessible from
the public Internet. In this case, the floating IP pool in use by OpenStack
needs to be configured with an IP range that contains public IP addresses.
The procedure for using such an IP range is the same as the one described
above. Care must be taken so that these public IP addresses are not in use by
other machines in the network and routing for this range is correctly implemented.

If the ConPaaS frontend itself needs to be publicly accessible, the host-only
network of VirtualBox can be replaced with a bridged network connected to a
physical network interface that provides Internet access. Note that this
bridge network must use a DHCP server that assigns a public IP address to the
Nutshell or, alternatively, the Nutshell can be configured to use a static IP
address (for example by editing the file ``/etc/network/interfaces``). If the
Nutshell is publicly accessible, you may want to make sure that tighter security
is implemented: the default user for the ConPaaS frontend is removed and access
to SSH and OpenStack dashboard is blocked.


.. _raspberrypi-guide:

ConPaaS on Raspberry PI
=======================

The following ConPaaS services are supported on the Raspberry PI version of ConPaaS:

-  **php**: PHP version 5.3 with Nginx

-  **java**: Apache Tomcat 6.0 servlet container

-  **xtreemfs**: XtreemFS-1.5 distributed file system

-  **generic**: deployment of arbitrary server-side applications

For instructions on how to install the Raspberry PI version of ConPaaS, please refer
to the relevant section in the Installation guide: :ref:`conpaas-on-raspberrypi`.


Access credentials
------------------

**Backend VM**::

  IP address: 172.16.0.1
  user: stack
  password: raspberry

For OpenStack's dashboard (Horizon)::

  URL: http://172.16.0.1/
  user: admin
  password: password

For the ConPaaS web frontend::

  URL: https://172.16.0.1/
  user: test
  password: password


**Raspberry PI**::

  IP address: 172.16.0.11
  user: pi
  password: raspberry


**Containers deployed on the Raspberry PI**::

  IP addresses (public): between 172.16.0.225 and 172.16.0.254
  IP addresses (private): between 172.16.0.32 and 172.16.0.61
  user: root
  password: contrail


Networking setup
----------------

IP addresses on the Raspberry PI and backend VM are already configured, all in the
``172.16.0.0/24`` range. The Raspberry PI is also configured to accept a secondary IP address
using DHCP. If this is available, it will use it for Internet access. If not, it will
route the Internet traffic through the backend VM. Everything is already configured, no other
configurations are needed. In principle there is no need to have Internet access on the PI
(if the hosted application does not require it), however note that in this case you will
need to manually set the correct time on the Raspberry PI after every reboot, or else the
SSL certificates-based authentication in ConPaaS will fail.

If another device has to take part in this local network (for example to allow it to easily
ssh into the different components of the system, or for the clients of the application hosted
on the Raspberry PIs), you can use any IP in that range that does not collide with the ones
used by the components listed above. For example, additional servers can have IP addresses
between ``172.16.0.2`` and ``172.16.0.10``, additional Raspberry PIs can use IPs between
``172.16.0.12`` and ``172.16.0.31``, clients can use IPs between ``172.16.0.200`` and
``172.16.0.223``. The ranges ``172.16.0.64/26``, ``172.16.0.128/26`` are also completely free.

The system was designed to allow connecting the components using an already-existing local
network that you may have, without interfering too much with it. That's why it does not run
by default a DHCP server to automatically allocate IPs to other machines that get connected
to this network. On the other hand, this means that you will need to manually add an IP address
to any other machine that needs to take part in this network. This address can be added as
a secondary IP address, besides the usual address that your device has, if using an
already-existing network. For example, in order to access the system from the laptop that
hosts the backend VM, another IP address from the ``172.16.0.0/24`` range needs to be assigned
as the secondary address to the *eth0* interface of this laptop.


Usage example
-------------

Here follows an usage example in which we create and start a new Generic Service using the
command line tools. The same outcome can also be achieved using the graphical frontend, which
can be accessed using the backend VM's IP address (note that the protocol should be
**HTTPS**, not HTTP): https://172.16.0.1/

1. Start the Backend VM. Start the Raspberry PI. Allow them some time to finish booting.

2. Make sure the time is synchronized between the Raspberry PI and the Backend VM. This step
   is crucial in order to allow the SSL certificates-based authentication in ConPaaS to succeed. 
   As the Raspberry PI does not have an internal battery to keep the time when powered off, it
   relies on the NTP protocol to set its time. If there is no Internet connectivity or updating
   the time through NTP fails, the correct time will have to be set manually using the ``date``
   command after every reboot.

3. Check that the OpenStack services are up and running. On the backend server, run the
   following command::
   
     stack@nutshell:~$ nova-manage service list
     [... debugging output omitted ...]
     Binary           Host                                 Zone             Status     State Updated_At
     nova-conductor   nutshell                             internal         enabled    :-)   2015-11-08 15:48:07
     nova-cert        nutshell                             internal         enabled    :-)   2015-11-08 15:48:08
     nova-scheduler   nutshell                             internal         enabled    :-)   2015-11-08 15:48:07
     nova-consoleauth nutshell                             internal         enabled    :-)   2015-11-08 15:48:07
     nova-compute     raspberrypi                          nova             enabled    :-)   2015-11-08 15:48:04
     nova-network     nutshell                             internal         enabled    :-)   2015-11-08 15:48:05
   
   As in the example above, you should see 6 ``nova`` services running, all of them should be
   up (smiley faces). Pay extra attention to the ``nova-compute`` service, which is running on
   the Raspberry PI, and may become ready a little later than the others.
   
   Do not proceed further if any service is down.

4. Create a new Generic Service using ConPaaS. This will start a new container for the
   ConPaaS Manager::
   
     stack@nutshell:~$ time cps-tools service create generic
     Creating new manager on 172.16.0.225...  done.
     
     real	2m04.515s
     user	0m0.704s
     sys	0m0.152s
   
   This step should take around 2-3 minutes. During this time, the first container is created
   and the ConPaaS Manager is started and initialized.
   
   Check that the container is up and running with ``nova list``::
   
     stack@nutshell:~$ nova list
     +--------------------------------------+---------------------------------------------+--------+------------+-------------+-----------------------------------+
     | ID                                   | Name                                        | Status | Task State | Power State | Networks                          |
     +--------------------------------------+---------------------------------------------+--------+------------+-------------+-----------------------------------+
     | 3c5c3375-1e73-4e0a-b6cc-223460c726e0 | Server 3c5c3375-1e73-4e0a-b6cc-223460c726e0 | ACTIVE | -          | Running     | private=172.16.0.42, 172.16.0.225 |
     +--------------------------------------+---------------------------------------------+--------+------------+-------------+-----------------------------------+

5. Start the newly created service. This will start the second container on the Raspberry PI
   in which the first ConPaaS agent can host an application::
   
     stack@nutshell:~$ time cps-tools service start 1
     Service 1 is starting...
     
     real	1m02.043s
     user	0m4.948s
     sys	0m1.384s
   
   This step should take around 1-2 minutes. During this time, the second container is created
   and the ConPaaS Agent is started and initialized.

6. Find out the IP address of the newly started container::
   
     stack@nutshell:~$ cps-tools generic list_nodes 1
     master: node iaasi-00000012 with IP address 172.16.0.226
   
   You can also determine the IP addresses of the containers with ``nova list``::
   
     stack@nutshell:~$ nova list
     +--------------------------------------+---------------------------------------------+--------+------------+-------------+-----------------------------------+
     | ID                                   | Name                                        | Status | Task State | Power State | Networks                          |
     +--------------------------------------+---------------------------------------------+--------+------------+-------------+-----------------------------------+
     | 2a1d758d-5300-4d7f-8ba2-4f1499838a7d | Server 2a1d758d-5300-4d7f-8ba2-4f1499838a7d | ACTIVE | -          | Running     | private=172.16.0.43, 172.16.0.226 |
     | 3c5c3375-1e73-4e0a-b6cc-223460c726e0 | Server 3c5c3375-1e73-4e0a-b6cc-223460c726e0 | ACTIVE | -          | Running     | private=172.16.0.42, 172.16.0.225 |
     +--------------------------------------+---------------------------------------------+--------+------------+-------------+-----------------------------------+

7. Log on to the container and check that the ConPaaS Agent is running correctly (the default
   script just prints some information)::
   
     stack@nutshell:~$ ssh root@172.16.0.226
     root@172.16.0.226's password: [contrail]
     Linux conpaas 4.1.12-v7+ #824 SMP PREEMPT Wed Oct 28 16:46:35 GMT 2015 armv7l
     [... welcome message omitted ...]
     root@server-2a1d758d-5300-4d7f-8ba2-4f1499838a7d:~# cat generic.out
     Sun Nov  8 16:21:21 UTC 2015
     Executing script init.sh
     Parameters (0): 
     My IP is 172.16.0.226
     My role is master
     My master IP is 172.16.0.226
     Information about other agents is stored at /var/cache/cpsagent/agents.json
     [{"ip": "172.16.0.226", "role": "master", "id": "iaasi-00000012"}]
   
   If the output looks like in the example above, everything is running smoothly!
   
   For more information on ConPaaS, please refer to section :ref:`the-generic-service`.

8. Do not forget to delete the service after you're done with it::
   
     stack@nutshell:~$ cps-tools service delete 1
     Deleting service... 
     Service 1 has been deleted.
