==========
User Guide
==========

ConPaaS currently contains the following services:

-  **Two Web hosting services** respectively specialized for hosting PHP
   and JSP applications;

-  **MySQL** offering a multi-master replicated load-balanced database
   service;

-  **XtreemFS service** offering a distributed and replicated file
   system;

-  **Flink service** offering distributed stream and batch data processing;

-  **Generic service** allowing the execution of arbitrary applications.

ConPaaS applications can be composed of any number of services. For
example, an application can use a Web hosting service, a database
service to store the internal application state and a file storage
service to store access logs.


Usage overview
==============

Web-based interface
-------------------

Most operations in ConPaaS can be performed using the ConPaaS frontend, which
provides a Web-based interface to the system. The frontend allows users to
register, create and start applications, add and start services, upload
code and configure each service.

-  The Dashboard page displays the list of applications created by the
   current user.

-  Each application has a separate page which allows the user to add or
   remove services.
   
-  Each service has its own separate page which allows the user to
   configure it, upload code and data, and scale it up and down.

The ConPaaS front-end provides simple and intuitive interfaces for
controlling applications and services. We describe here the most common
features. Please refer to the next sections for service-specific
functionality.

Create an application.
    In the main ConPaaS Dashboard, click on “create new application”.
    Write the application's name and click on “OK”. The application's
    name must be unique.

Start an application.
    From the main ConPaaS Dashboard, click on the desired application.
    To start the application, click on the “start application” button.
    This will create a new virtual machine which hosts the Application's
    Manager, a ConPaaS component in charge of managing the entire application.

Add a service.
    Click on “add new service”, then select the service you want to
    add. This operation adds extra functionalities to the application
    manager which are specific to a certain service. These functionalities
    enable the application manager to be in charge of taking care of the
    service, but it does not host applications itself. Other instances in
    charge of running the actual application are called “agent” instances.

Start a service.
    Click on the newly created service, then click on the “start” button.
    This will create a new virtual machine which can host applications,
    depending on the type of service.

Rename the service.
    By default, all new services are named “New service”. To give a
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
    When you do not need to run the service anymore, click on the “stop”
    button to stop the service. This stops all instances of the service.

Remove the service.
    Click “remove” to delete the service. At this point, all the state of
    the service manager is lost.

Stop the application.
    Even when all the services from an application are stopped, the application's
    manager will keep on running. To stop it, in the application's page,
    click on the “stop application” button. The application will not use
    resources anymore.


Command line interface
----------------------

All the functionalities of the frontend are also available using a
command line interface. This allows one to script commands for ConPaaS.
The command line interface also features additional advanced
functionalities, which are not available using the frontend.

The new command line client for ConPaaS is called ``cps-tools``.

Installation and configuration:
    see :ref:`cpstools-installation`.

Command arguments::

    $ cps-tools --help

Create an application::

    $ cps-tools application create <appl_name>
    $ cps-application create <appl_name>

List applications::

    $ cps-tools application list
    $ cps-application list

Start an application::

    $ cps-tools application start <app_name_or_id>
    $ cps-application start <app_name_or_id>

Available service types::

    $ cps-tools service get_types
    $ cps-service get_types

Add a service to an application::

    $ cps-tools service add <service_type> <app_name_or_id>
    $ cps-tools <service_type> add <app_name_or_id>
    $ cps-<service_type> add <app_name_or_id>

List services::

    $ cps-tools service list
    $ cps-service list

Start a service::

    $ cps-tools <service_type> start <app_name_or_id> <serv_name_or_id>
    $ cps-service start <app_name_or_id> <serv_name_or_id>
    $ cps-<service_type> start <app_name_or_id> <serv_name_or_id>

Service command specific arguments::

    $ cps-tools <service_type> --help
    $ cps-<service_type> --help

Scale the service up and down::

    $ cps-service add_nodes <app_name_or_id> <serv_name_or_id>
    $ cps-service remove_nodes <app_name_or_id> <serv_name_or_id>

List the available clouds::

    $ cps-tools cloud list
    $ cps-cloud list


The credit system
-----------------

In Cloud computing, resources come at a cost. ConPaaS reflects this
reality in the form of a credit system. Each user is given a number of
credits that she can use as she wishes. One credit corresponds to one
hour of execution of one virtual machine. The number of available
credits is always mentioned in the top-right corner of the front-end.
Once credits are exhausted, your running instances will be stopped and
you will not be able to use the system until the administrator decides
to give you additional credit.

Note that every running application consumes credit, even if all its
services are in the “stopped” state. The reason is that the application
still has one “Application Manager” instance running. To stop using any
credits you must also stop all your applications.


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

Note that, for this simple example, the “file upload” functionality of
WordPress will not work if you scale the system up. This is because
WordPress stores files in the local file system of the PHP server where
the upload has been processed. If a subsequent request for this file is
processed by another PHP server then the file will not be found.
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
service with id 1 of application with id 1 using the command line tool:

::

    $ cps-php upload_code 1 1 path/to/archive.zip

To enable Git-based code uploads you first need to upload your SSH
public key. This can be done either using the command line tool:

::

    $ cps-php upload_key <app_name_or_id> <serv_name_or_id> <filename>

An SSH public key can also be uploaded using the ConPaaS frontend by
choosing the “checking out repository” option in the “Code management”
section of your PHP service. There is only one git repository per
application, so you only need to upload your SSH key once.

Below the area for entering the SSH key, the frontend will show the ``git``
command to be executed in order to obtain a copy of the repository. As there is
only a single repository for all the services running inside an application,
**the code that belongs to a specific service has to be placed in a directory
with the name identical to the service id**, which has to be created by the
user. The repository itself can then be used as usual. A new version of your
application can be uploaded with ``git push``.

::

    user@host:~/code$ mkdir 1
    user@host:~/code$ vi 1/index.php
    user@host:~/code$ git add 1/index.php
    user@host:~/code$ git commit -am "New index.php version for service 1"
    user@host:~/code$ git push origin master

.. warning::
  Do not forget to place the code belonging to a service in a directory
  with the name identical to the service id, or else the service will be
  unable to find the files.

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

By default, the PHP service does not display anything in case PHP errors
occur while executing the application. This setting is useful for
production, when you do not want to reveal internal information to
external users. While developing an application it is, however, useful to
let PHP display errors.

::

    $ cps-php debug <app_name_or_id> <serv_name_or_id> <on | off>

Adding and removing nodes
-------------------------

Like all ConPaaS services, the PHP service is elastic: service owner can
add or remove nodes. The PHP service (like the Java service) belongs to
a class of web services that deals with three types of nodes:

**proxy**
  a node that is used as an entry point for the web application and as a load balancer
**web**
  a node that deals with static pages only
**backend**
  a node that deals with PHP requests only

When a proxy node receives a request, it redirects it to  a web node if
it is a request for a static page, or a backend node if it is a request
for a PHP page.

If your PHP service has a slow response time, increase the number of backend nodes.

On the command line, the ``add_nodes`` subcommand can be used to add
additional nodes to a service. It takes as arguments the number of backend nodes,
web nodes and proxy nodes to add::

  $ cps-php add_nodes <app_name_or_id> <serv_name_or_id> --backend COUNT --proxy COUNT --web COUNT

For example, adding two backend nodes to PHP service id 1 of application 1::

  $ cps-php add_nodes 1 1 -- backend 2

Adding one backend node and one web node in a cloud provider called ``mycloud``::

  $ cps-php add_nodes 1 1 --backend 1 --web 1 --cloud mycloud

You can also remove nodes using the command line.
For example, the following command will remove one backend node::

  $ cps-php remove_nodes 1 1 --backend 1

.. warning::
  Initially, an instance of each node is running on one single VM.
  Then, when adding a backend node, ConPaaS will move the backend
  node running on the first VM to a new VM.
  So, actually, it will *not* add a new backend node the first time.
  Requesting for one more backend node will create a new VM that will
  run an additional backend.


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
command line tool::

    $ cps-java upload_code <app_name_or_id> <serv_name_or_id> <path/to/archive.war>

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
process incoming updates, the replication system being
responsible for propagating the data modifications made by each member
to the rest of the group and resolving any conflicts that might arise
between concurrent changes made by different members. These features
can be used to increase the throughput of the cluster. 

To obtain better performance from a cluster, it is a best
practice to use it in a balanced fashion, so that each node has
approximately the same load of the others. To achieve this, the
service allows users to allocate special load balancer nodes
(``glb``) which implement load balancing. Load balancer nodes
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

    $ mysql <mysql-ip-address> -u mysqldb -p < dumpfile.sql

Performance Monitoring
----------------------

The MySQL service interface provides a sophisticated mechanism to monitor the
service. The user interface, in the frontend, shows a monitoring control,
called "Performance Monitor", that can be used to monitor a large cluster's
behavior. It interacts with "Ganglia", "Galera" and "MySQL" to obtain various
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
  traffic for each node of the cluster.  Users can use this
  information in order to detect problems in their applications. The
  table displays the resource utilization across all nodes, and
  highlight the parameters which suggest an abnormality. For example,
  if CPU utilization is high or free memory is very low, this is shown
  clearly. This may mean that processes on this node will start to
  slow down and that it may be time to add additional nodes to the
  cluster. On the other hand, this may indicate a malfunction of the
  specific node.

- "Galera Mean Misalignment" draws a real-time measure of the mean
  misalignment across the nodes. This information is derived from
  Galera metrics about the average length of the receive queue since
  the most recent status query. If this value is noticeably larger
  than zero, the nodes are likely to be overloaded, and cannot apply
  the writesets as quickly as they arrive, resulting in replication
  throttling.


The XtreemFS service
====================

The XtreemFS service provides POSIX compatible storage for ConPaaS. Users can
create volumes that can be mounted remotely or used by other ConPaaS services,
or inside applications. An XtreemFS instance consists of multiple DIR, MRC and 
OSD servers. The OSDs contain the actual storage, while the DIR is a directory 
service and the MRC contains metadata. By default, one instance of each runs 
inside the first agent virtual machine and the service can be scaled up and 
down by adding and removing additional OSD nodes. The XtreemFS documentation 
can be found at http://xtreemfs.org/userguide.php.

SSL Certificates
----------------

The XtreemFS service uses SSL certificates for authorization and authentication.
There are two types of certificates, user-certificates and client-certificates.
Both certificates can additionally be flagged as administrator certificates which
allow performing administrative file-systems tasks when used to access
XtreemFS. Certificates are only valid for the service that was used to create them.
The generated certificates are in P12-format.

The difference between client- and user-certificates is how POSIX users and
groups are handled when accessing volumes and their content. Client-certificates
take the user and group with whom an XtreemFS command is called, or a mounted XtreemFS
volume is accessed. So multiple users might share a single client-certificate.
On the other hand, user-certificates contain a user and group inside the certificate.
So usually, each user has her personal user-certificate. Both kinds of certificate can
be used in parallel. Client-certificates are less secure since the user and group with
whom files are accessed can be arbitrarily changed if the mounting user has local
superuser rights. So client-certificates should only be used in trusted environments.

Using the command line client, certificates can be created like this, where <adminflag>
can be "true", "yes", or "1" to grant administrator rights::

    $ cps-xtreemfs get_client_cert <app_name_or_id> <serv_name_or_id> <passphrase> <adminflag> <filename.p12>
    $ cps-xtreemfs get_user_cert <app_name_or_id> <serv_name_or_id> <user> <group> <passphrase> <adminflag> <filename.p12>

Accessing volumes directly
--------------------------

Once a volume has been created, it can be directly mounted on a remote site by
using the ``mount.xtreemfs`` command. A mounted volume can be used like any local
POSIX-compatible filesystem. You need a certificate for mounting (see the last section).
The command looks like this, where <address> is the IP of an agent running
an XtreemFS directory service (usually the first agent)::

    $ mount.xtreemfs <address>/<volume> <mount-point> --pkcs12-file-path <filename.p12> --pkcs12-passphrase <passphrase> 

The volume can be unmounted with the following command::

    $ fusermount -u <mount-point>

Please refer to the XtreemFS user guide (http://xtreemfs.org/userguide.php) for further details.

Policies
--------

Different aspects of XtreemFS (e.g. replica- and OSD-selection) can be 
customized by setting certain policies. Those policies can be set via the
ConPaaS command line client (recommended) or directly via ``xtfsutil`` (see the
XtreemFS user guide). The commands are like follows, were <policy_type> is
``osd_sel``, ``replica_sel``, or ``replication``::

   $ cps-xtreemfs list_policies <app_name_or_id> <serv_name_or_id> <policy_type>
   $ cps-xtreemfs set_policy <app_name_or_id> <serv_name_or_id> <policy_type> <policy> <volume>

Important notes
---------------

When a service is scaled down by removing OSDs, the data of those OSDs is
migrated to the remaining OSDs. Always make sure there is enough free space 
for this operation to succeed. Otherwise, you risk data loss.


The Flink service
====================

The Flink service facilitates the deployment of applications that use the
Apache Flink platform for distributed stream and batch data processing.
Flink provides data distribution, communication, and fault tolerance for
distributed computations over data streams. Flink also supports batch
processing applications, treated as special cases of stream processing.

A Flink node can assume two possible roles: **master** or **worker**. A master
(also called *JobManager*) coordinates the distributed execution. It schedules
tasks, coordinates checkpoints and recovery on failures, etc. The workers
(also called *TaskManagers*) execute the tasks of a dataflow, and buffer
and exchange the data streams. A Flink service will always have exactly
one master and one or more workers. The first instance that is started by
the service will always assume both roles (master and worker). All the other
instances will be considered as worker nodes.

Running a Flink application
---------------------------

After a Flink service is started, the user can access the Flink Dashboard
using the link that appears in the upper-right corner of the service page.
From the dashboard, the Flink deployment can be used in the same way as
a regular installation.

As an example, we will illustrate how to upload and execute the WordCount
sample application. The **jar** containing the application can be found in
the *examples* directory inside the Flink binary package, which can be
downloaded from the official website:

http://www-eu.apache.org/dist/flink/flink-1.1.1/flink-1.1.1-bin-hadoop1-scala_2.10.tgz

Start a Flink service, wait for it to become ready and access the Flink
Dashboard using the link that appears in the upper-right corner of the
service page. Go to the "Submit new Job" page and click on the "Add new"
button. Select the *WordCount.jar* file and click on "Upload". Tick the
box in front of the job's name. To be able to see the output, redirect it
to the TaskManager's output file by entering the following text in the
"Program Arguments" field::

--output file:///var/cache/cpsagent/flink-taskmanager.log

To run the job, press the "Submit" button. You will be shown a page where
you can monitor the progress of your job. When the job finished execution,
you can check the output by accessing the "TaskManager out" link from the
Flink service's page.

For more information on using Flink, please consult the official documentation:
https://ci.apache.org/projects/flink/flink-docs-release-1.1/


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
an archive to the service with id 1 using the command line tool::

  $ cps-generic upload_code 1 1 test-code.tar.gz
  Code version code-pw1LKs uploaded
  $ cps-generic enable_code 1 1 code-pw1LKs
  code-pw1LKs enabled
  $ cps-generic list_codes 1 1
  current codeVersionId filename         description
  ------------------------------------------------------
        * code-pw1LKs   test-code.tar.gz
          code-default  code-default.tar Initial version

To download a specific code version, the following command may be used::

  $ cps-generic download_code <app_name_or_id> <serv_name_or_id> --version <code-version>

The archive will be downloaded using the original name in the current directory.

.. warning::
  if another file with the same name is present in the current directory,
  it will be overwritten.

The command-line client also allows deleting a code version, with the exception
of the currently active version::

  $ cps-generic delete_code <app_name_or_id> <serv_name_or_id> <code-version>

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

  $ cps-generic upload_key <app_name_or_id> <serv_name_or_id> <filename>

You can check that the key was successfully uploaded by listing the trusted
SSH keys::

  $ cps-generic list_keys <app_name_or_id> <serv_name_or_id>

There is only one git repository per application, so you only need to upload
your SSH key once.

After the key is uploaded, the following command has to be executed in order to
obtain a copy of the repository::

  $ git clone git@<generic-manager-ip>:code

As there is only a single repository for all the services running inside an
application, **the code that belongs to a specific service has to be placed
in a directory with the name identical to the service id**, which has to be
created by the user. The repository itself can then be used as usual. A new
version of your application can be uploaded with ``git push``::

  $ cd code
  $ mkdir 1
  $ <create the scripts in this directory>
  $ git add 1/{init,notify,run,interrupt,cleanup}.sh
  $ git commit -m "New code version"
  $ git push origin master

.. warning::
  Do not forget to place the code belonging to a service in a directory
  with the name identical to the service id, or else the service will be
  unable to find the files.

The ``git push`` command will trigger the updating of the available code versions.
To activate the new code version, the same procedure as before must be followed.
Note that, when using the web frontend, you may need to refresh the page in
order to see the new code version.

To download a code version uploaded using Git, you must clone the repository
and checkout a specific commit. The version number represents the first part
of the commit hash, so you can use that as a parameter for the ``git checkout``
command::

  $ cps-generic list_codes 1 1
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

  $ cps-generic create_volume <app_name_or_id> <vol_name> <vol_size> <agent_id>

Size must always be specified in MB. To find out the *agent_id* of a specific
instance, you may issue the following command::

  $ cps-generic list_nodes <app_name_or_id> <serv_name_or_id>

The list of all storage volumes can be retrieved with::

  $ cps-generic list_volumes <app_name_or_id> <serv_name_or_id>

This command detaches and deletes a storage volume::

  $ cps-generic delete_volume <app_name_or_id> <agent_id>

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

  $ cps-generic add_nodes <app_name_or_id> <serv_name_or_id> --count <number_of_nodes>

Immediately after the new nodes are ready, the active code version is copied
to the new nodes and the ``init.sh`` script is executed in each of the new
nodes. All the other nodes which were already up before the execution of the
command will be notified about the addition of the new nodes to the service,
so ``notify.sh`` is executed in their case. The ``init.sh`` script is never
executed twice for the same agent and the same code version.

Nodes can be removed with::

  $ cps-generic remove_nodes <app_name_or_id> <serv_name_or_id> --count <number_of_nodes>

After the command completes and the specified number of nodes are terminated,
the ``notify.sh`` script is executed for all the remaining nodes to notify
them of the change.

The Generic service also offers an easy way to run the application on every
agent, interrupt a running application or cleanup the agents after the
execution is completed.

In the web frontend, the ``run``, ``interrupt`` and ``cleanup`` buttons
are conveniently located on the top of the page, above the instances view.
Pressing such a button will execute the corresponding script in all the agents.
Above the buttons, there is also a parameters field which allows the user to
specify parameters which will be forwarded to the script during the execution.

On the command line, the following commands may be used::

  $ cps-generic run <app_name_or_id> <serv_name_or_id> -p <parameters>
  $ cps-generic interrupt <app_name_or_id> <serv_name_or_id> -p <parameters>
  $ cps-generic cleanup <app_name_or_id> <serv_name_or_id> -p <parameters>

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
this is highlighted by renaming the ``interrupt`` button to ``kill``.

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

  $ cps-generic get_script_status <app_name_or_id> <serv_name_or_id>

The Generic service also facilitates retrieving the agent's log file and
the contents of standard output and error streams. In the web frontend,
three links are present in the instance's view of each agent. Using the
command line, the logs can be retrieved with the following commands::

  $ cps-generic get_agent_log <app_name_or_id> <serv_name_or_id> <agent_id>
  $ cps-generic get_agent_log <app_name_or_id> <serv_name_or_id> <agent_id> -f agent.out
  $ cps-generic get_agent_log <app_name_or_id> <serv_name_or_id> <agent_id> -f agent.err

To find out the agent_id of a specific instance, you may issue the following command::

  $ cps-generic list_nodes <app_name_or_id> <serv_name_or_id>


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

#. Open VirtualBox and start the Nutshell VM by selecting it from the list on the
   left side and then clicking the *Start* button.

#. Wait for the Nutshell VM to finish booting. Depending on your computer's
   hardware configuration, this process may take a few minutes. Any messages
   that may appear in the VM window at this stage are usually harmless debug
   messages which can be ignored.

#. When the login prompt appears, the Nutshell VM is ready to be used.

Using the Nutshell via the graphical frontend
---------------------------------------------

You can access the ConPaaS frontend by inserting the IP address of the
Nutshell VM in your Web browser, **making sure to add https:// in front of it**::

  https://192.168.56.2

.. warning::
  The first time you access the web frontend, a security warning will appear,
  stating that the SSL certificate of the website is invalid. This is normal, as
  the certificate is self-signed. To proceed further, you need to confirm
  that you want to continue anyway. The procedure is different depending on your
  web browser.

Note that the frontend is accessible only from your local machine. Other
machines will not be able to access it. A default ConPaaS user is available
for you, its credentials are::

  ConPaaS
  Username: test
  Password: password

You can now use the frontend in the same way as any ConPaaS system,
creating applications, services etc. Note that the services are also
only accessible from your local machine.

Note that also *Horizon* (the OpenStack dashboard) is running on it as
well. In case you are curious and want to have a look under the hood,
Horizon can be reached (using HTTP, not HTTPS) at the same IP address::

  http://192.168.56.2

The credentials for Horizon are::

  Openstack
  Username: admin
  Password: password


Using the Nutshell via the command-line interface
-------------------------------------------------

You can also use the command-line to control your Nutshell installation.
You need to log in as the *stack* user directly in the VirtualBox window
or using SSH to connect to the Nutshell VM's IP address (the preferred method)::

  $ ssh stack@192.168.56.2

The login credentials are::
   
    Username: stack
    Password: conpaas

On login, both the ConPaaS and OpenStack users will already be authenticated.
You should be able to execute ConPaaS commands, for example creating an
application and starting a *helloworld* service can be done with::

  $ cps-tools application create "First app"
  $ cps-tools application start 1
  $ cps-tools service add helloworld 1
  $ cps-tools service start 1 1

OpenStack commands are also available. For example::

  $ nova list

lists all the active instances and::

  $ cinder list

lists all the existing storage volumes.

The Nutshell contains a *Devstack* installation of OpenStack,
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

In the standard configuration, the Nutshell VM is assigned the static IP
address ``192.168.56.2``, part of the ``192.168.56.0/24`` subnet that is
used by the host-only network of VirtualBox. ConPaaS services running
inside the Nutshell VM also need to have IP addresses assigned, one for
each container that is started inside the Nutshell VM. This is done using
OpenStack's floating IP mechanism, which is configured to use an IP range
from ``192.168.56.10`` to ``192.168.56.99``, part of the same
``192.168.56.0/24`` subnet.

This configuration was carefully chosen to not overlap with the pool used
by the DHCP server of the host-only network of VirtualBox which, in the
default settings, uses a range from ``192.168.56.101`` to ``192.168.56.254``.
To check the range that is used in your system, you can navigate in the
VirtualBox window to the following menu: *File* > *Preferences* > *Network*
> *Host-only Networks*. Select the *vboxnet0* network and click on the
*Edit host-only network* button and then *DHCP server*.

To modify the IP address range used by the Nutshell VM, you need to change
the static address assigned to the Nutshell VM itself and also the IP range
used by OpenStack to assign floating IP addresses to the containers. You
need to make sure that all these addresses are part of the subnet used by
the host-only network of VirtualBox and also that they do not overlap with
this network's DHCP server pool (in the case other VMs with interfaces in
the host-only network are started and receive addresses from this pool).
You may need to adjust the host-only network's configuration in VirtualBox
for this these conditions to be met.

The static IP address of the Nutshell VM can be changed by editing the
``/etc/network/interfaces`` file. The interface that is part of the host-only
network is the second one (``eth1``), this is the one that should have the
IP assigned. The first one (``eth0``) is only used to provide Internet access
to the Nutshell VM.

To modify the IP range used to assign floating IP addresses to containers,
execute the following commands on the Nutshell as the *stack* user::

  $ nova floating-ip-bulk-delete 192.168.56.0/25
  $ nova floating-ip-bulk-create --pool public --interface eth1 <new_range>

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
physical network interface that provides Internet access. As in the previous
scenario, the Nutshell's IP address can be configured by editing the
``/etc/network/interfaces`` file. If the Nutshell is publicly accessible,
you may want to make sure that tighter security is implemented: the default
user for the ConPaaS frontend should be removed and access to SSH and OpenStack
dashboard should be blocked.


.. _raspberrypi-guide:

ConPaaS on Raspberry PI
=======================

The following ConPaaS services are supported on the Raspberry PI version of ConPaaS:

-  **php**: PHP version 5.6 with Nginx

-  **java**: Apache Tomcat 7.0 servlet container

-  **xtreemfs**: XtreemFS-1.5 distributed file system

-  **flink**: Apache Flink 1.1 stream and batch data processing

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
  password: conpaas


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

#. Start the Backend VM. Start the Raspberry PI. Allow them some time to finish booting.

#. Make sure the time is synchronized between the Raspberry PI and the Backend VM. This step
   is crucial in order to allow the SSL certificates-based authentication in ConPaaS to succeed. 
   As the Raspberry PI does not have an internal battery to keep the time when powered off, it
   relies on the NTP protocol to set its time. If there is no Internet connectivity or updating
   the time through NTP fails, the correct time will have to be set manually using the ``date``
   command after every reboot.

#. Check that the OpenStack services are up and running. On the backend server, run the
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

#. Create a new application using ConPaaS::
   
     stack@nutshell:~$ cps-tools application create "Test application"
     Application 'Test application' created with id 1.

#. Start the application. This will start a new container for the
   Application Manager::
   
     stack@nutshell:~$ time cps-tools application start 1
     Application 'Test application' with id 1 is starting...  done.
     
     real	2m04.515s
     user	0m0.704s
     sys	0m0.152s
   
   This step should take around 2-3 minutes. During this time, the first container is created
   and the ConPaaS Application Manager is started and initialized.
   
   Check that the container is up and running with ``nova list``::
   
     stack@nutshell:~$ nova list
     +--------------------------------------+-----------------------+--------+------------+-------------+-----------------------------------+
     | ID                                   | Name                  | Status | Task State | Power State | Networks                          |
     +--------------------------------------+-----------------------+--------+------------+-------------+-----------------------------------+
     | 3c5c3375-1e73-4e0a-b6cc-223460c726e0 | conpaas-rpi-u1-a1-mgr | ACTIVE | -          | Running     | private=172.16.0.42, 172.16.0.225 |
     +--------------------------------------+-----------------------+--------+------------+-------------+-----------------------------------+

#. Add a Generic service to the application::
   
   stack@nutshell:~$ cps-tools service add generic 1
   Service generic successfully added to application 1 with id 1.

#. Start the newly added service. This will start the second container on the Raspberry PI
   in which the first ConPaaS agent can host an application::
   
     stack@nutshell:~$ time cps-tools service start 1 1
     Service 1 is starting...
     
     real	1m02.043s
     user	0m4.948s
     sys	0m1.384s
   
   This step should take around 1-2 minutes. During this time, the second container is created
   and the ConPaaS Agent is started and initialized.

#. Find out the IP address of the newly started container::
   
     stack@nutshell:~$ cps-tools generic list_nodes 1 1
     aid sid role   ip           agent_id       cloud  
     --------------------------------------------------
       1   1 master 172.16.0.226 iaasi-00000012 default
   
   You can also determine the IP addresses of the containers with ``nova list``::
   
     stack@nutshell:~$ nova list
     +--------------------------------------+------------------------------+--------+------------+-------------+-----------------------------------+
     | ID                                   | Name                         | Status | Task State | Power State | Networks                          |
     +--------------------------------------+------------------------------+--------+------------+-------------+-----------------------------------+
     | 3c5c3375-1e73-4e0a-b6cc-223460c726e0 | conpaas-rpi-u1-a1-mgr        | ACTIVE | -          | Running     | private=172.16.0.42, 172.16.0.225 |
     | 2a1d758d-5300-4d7f-8ba2-4f1499838a7d | conpaas-rpi-u1-a1-s1-generic | ACTIVE | -          | Running     | private=172.16.0.43, 172.16.0.226 |
     +--------------------------------------+------------------------------+--------+------------+-------------+-----------------------------------+

#. Log on to the container and check that the ConPaaS Agent is running correctly (the default
   script just prints some information)::
   
     stack@nutshell:~$ ssh root@172.16.0.226
     root@172.16.0.226's password: [conpaas]
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
   
   For more information on the Generic service, please refer to section :ref:`the-generic-service`.

#. Do not forget to delete the service after you're done with it::
   
     stack@nutshell:~$ cps-tools service remove 1 1
     Service 1 of application 1 has been successfully removed.
