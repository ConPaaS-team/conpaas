==========
User Guide
==========
ConPaaS is an open-source runtime environment for hosting applications in the
cloud which aims at offering the full power of the cloud to application
developers while shielding them from the associated complexity of the cloud.

ConPaaS is designed to host both high-performance scientific
applications and online Web applications. It runs on a variety of public
and private clouds, and is easily extensible. ConPaaS automates the
entire life-cycle of an application, including collaborative
development, deployment, performance monitoring, and automatic scaling.
This allows developers to focus their attention on application-specific
concerns rather than on cloud-specific details.

ConPaaS is organized as a collection of **services**, where each service
acts as a replacement for a commonly used runtime environment. For
example, to replace a MySQL database, ConPaaS provides a cloud-based
MySQL service which acts as a high-level database abstraction. The
service uses real MySQL databases internally, and therefore makes it
easy to port a cloud application to ConPaaS. Unlike a regular
centralized database, however, it is self-managed and fully elastic: one
can dynamically increase or decrease its processing capacity by
requesting it to reconfigure itself with a different number of virtual
machines.

ConPaaS currently contains nine services:

-  **Two Web hosting services** respectively specialized for hosting PHP
   and JSP applications;

-  **MySQL database** service;

-  **Scalarix service** offering a scalable in-memory key-value store;

-  **MapReduce service** providing the well-known high-performance
   computation framework;

-  **TaskFarming service** high-performance batch processing;

-  **Selenium service** for functional testing of web applications;

-  **XtreemFS service** offering a distributed and replicated file
   system;

-  **HTC service** providing a throughput-oriented scheduler for bags of tasks
  submitted on demand.

ConPaaS applications can be composed of any number of services. For
example, a bio-informatics application may make use of a PHP and a MySQL
service to host a Web-based frontend, and link this frontend to a
MapReduce backend service for conducting high-performance genomic
computations on demand.

Usage overview
==============

Most operations in ConPaaS can be done using the ConPaaS frontend, which
gives a Web-based interface to the system. The front-end allows users to
register, create services, upload code and data to the services, and
configure each service.

-  The Dashboard page displays the list of services currently active in
   the system.

-  Each service comes with a separate page which allows one to configure
   it, upload code and data, and scale it up and down.

All the functionalities of the frontend are also available using a
command-line interface. This allows one to script commands for ConPaaS.
The command-line interface also features additional advanced
functionalities, which are not available using the front-end.

Controlling services using the front-end
----------------------------------------

The ConPaaS front-end provides a simple and intuitive interface for
controlling services. We discuss here the features that are common to
all services, and refer to the next sections for service-specific
functionality.

Create a service.
    Click on “create new service”, then select the service you want to
    create. This operation starts a new “Manager” virtual machine
    instance. The manager is in charge of taking care of the service,
    but it does not host applications itself. Other instances in charge
    of running the actual application are called “agent” instances.

Start a service.
    Click on “start”, this will create a new virtual machine which can
    host applications, depending on the type of service.

Rename the service.
    By default all new services are named “New service.” To give a
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

Archives can be either in the ``tar`` or ``zip`` format. Attention: the
archive must expand *in the current directory* rather than in a
subdirectory. The service does not immediately use new applications when
they are uploaded. The frontend shows the list of versions that have
been uploaded; choose one version and click “make active” to activate
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
session\_start() is encountered. This file overwrites the session
handlers using the session\_set\_save\_handler() function.

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
version and click “make active” to activate it.

Note that the frontend only allows uploading archives smaller than a
certain size. To upload large archives, you must use the command-line
tools or Git.

The following example illustrates how to upload an archive with the
``cpsclient.py`` command line tool:

::

    $ cpsclient.py upload_code serviceid archivename

To upload new versions of your application via Git, please refer to
section :ref:`code_upload`.

Access the application
----------------------

The frontend gives a link to the running application. This URL will
remain valid as long as you do not stop the service.

The MySQL database service
==========================

The MySQL service provides the famous database in the form of a ConPaaS
service. When scaling the service up and down, it creates (or deletes)
database replicas using the master-slave mechanism. At the moment, the
service does not implement load balancing of database queries between
the master and its slaves. Replication therefore provides
fault-tolerance properties but no performance improvement.

Resetting the user password
---------------------------

When a MySQL service is started, a new user ``mysqldb`` is created with
a randomly-generated password. To gain access to the database you must
first reset this password. Click “Reset password” in the front-end, and
choose the new password.

Note that the user password is *not* kept by the ConPaaS frontend. If
you forget the password the only thing you can do is reset the password
again to a new value.

Accessing the database
----------------------

The frontend provides the command-line to access the database.
Copy-paste this command in a terminal. You will be asked for the user
password, after which you can use the database as you wish.

Note that the ``mysqldb`` user has extended privileges. It can create
new databases, new users etc.

Uploading a database dump
-------------------------

The ConPaaS frontend allows to easily upload database dumps to a MySQL
service. Note that this functionality is restricted to dumps of a
relatively small size. To upload larger dumps you can always use the
regular ``mysql`` command for this:

::

    $ mysql mysql-ip-address -u mysqldb -p < dumpfile.sql

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

**IMPORTANT:** This service requires virtual machines with *at least* 384 MB of
RAM to function properly.

The TaskFarm service
====================

The TaskFarm service provides a bag of tasks scheduler for ConPaaS. The
user needs to provide a list of independent tasks to be executed on the
cloud and a file system location where the tasks can read input data
and/or write output data to it. The service first enters a sampling
phase, where its agents sample the runtime of the given tasks on
different cloud instances. The service then based on the sampled
runtimes, provides the user with a list of schedules. Schedules are
presented in a graph and the user can choose between cost/makespan of
different schedules for the given set of tasks.fter the choice is made
the service enters the execution phase and completes the execution of
the rest of the tasks according to the user’s choice.

Preparing the ConPaaS services image
------------------------------------

By default, the TaskFarm service can execute the user code that is
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
bag of tasks file containing three tasks:

::

    /bin/sleep 1 && echo "slept for 1 seconds" >> /mnt/xtreemfs/log
    /bin/sleep 2 && echo "slept for 2 seconds" >> /mnt/xtreemfs/log
    /bin/sleep 3 && echo "slept for 3 seconds" >> /mnt/xtreemfs/log

The minimum number of tasks required by the service to start sampling is
depending on the number of tasks itself, but a bag with more than thirty
tasks is large enough.

The filesystem location
-----------------------

TaskFarm service uses XtreemFS for data input/output. The actual task
code can also reside in the XtreemFS. The user can optionally provide an
XtreemFS location which is then mounted on TaskFarm agents.

The demo mode
-------------

With large bags of tasks and/or with long running tasks, the TaskFarm
service can take a long time to execute the given bag. The service
provides its users with a progress bar and reports the amount of money
spent so far. TaskFarm service also provides a “demo” mode where the
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

Accessing volumes directly
--------------------------

Once a volume has been created, it can be directly mounted on a remote site by
using the mount.xtreemfs command. A mounted volume can be used like any local
POSIX-compatible filesystem.

Policies
--------

Different aspects of XtreemFS (e.g. replica- and OSD-selection) can be 
customised by setting certain policies. Those policies can be set via the 
ConPaaS command line client (recommended) or directly via xtfsutil (see the
XtreemFS user guide).

Persistency
-----------

If the XtreemFS service is shut down, all its data is permanently lost. If 
persistency beyond the service runtime is needed, the XtreemFS service can be
moved into a snapshot by using the download_manifest operation of the command
line client. This operation will automatically shut down the service. 
The service and all of its stored volumes with their data can be moved back
into a running ConPaaS service by using the manifest operation.

Important notes
---------------

When a service is scaled down by removing OSDs, the data of those OSDs is
migrated to the remaining OSDs. Always make sure there is enough free space 
for this operation to succeed. Otherwise you risk data loss.
The download_manifest operation of the XtreemFS service will also shut the 
service down. This behaviour might differ from other ConPaaS services, but is 
neccessary to avoid copying the whole filesystem (which would be a very 
expensive operation). This might change in future releases.

The HTC service
===============
The HTC service provides a throughput-oriented scheduler for bags of tasks
submitted on demand for ConPaaS. An inial bag of tasks is sampled generating a
throughput = f(cost) function.  The user is allowed at any point, including
upon new tasks submission,to request the latest throughput = f(cost) function
and insert his target throughput.  After the first bag is sample and submitted
for execution the user is allowed to add tasks to the job with the
corresponding identifier. The user is allowed at any point, including upon new
tasks submission,to request the latest throughput = f(cost) function and adjust
his target throughput.  All tasks that are added on are immediately submitted
for execution using the latest configuration requested by the user,
corresponding to the target throughput.

Available commands
------------------
start service_id - prompts the user to specify a mode (’real’ or ’demo’) and
type (’batch’, ’online’ or ’workflow’) for the service. Starts the service
under the selected context and intializes all the internal data structures for
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
