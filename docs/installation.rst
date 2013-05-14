============
Installation 
============
ConPaaS_ is a Platform-as-a-Service system. It aims at simplifying the
deployment and management of applications in the Cloud.  

The central component of ConPaaS, called *ConPaaS Director* (**cpsdirector**),
is responsible for handling user authentication, creating new applications,
handling their life-cycle and much more. **cpsdirector** is a web service
exposing all its functionalities via an HTTP-based API.

ConPaaS can be used either via a command line interface called **cpsclient** or
through a web frontend (**cpsfrontend**). This document explains how to install
and configure all the aforementioned components.

.. _ConPaaS: http://www.conpaas.eu
.. _Flask: http://flask.pocoo.org/

Both **cpsdirector** and **cpsfrontend** can be installed on your own hardware
or on virtual machines running on public or private clouds. ConPaaS services
are designed to run either in an `OpenNebula` cloud installation or in the
`Amazon Web Services` cloud.

Installing ConPaaS requires to take the following steps:

#. Choose a VM image customized for hosting the services, or create a
   new one. Details on how to do this vary depending on the choice of cloud
   where ConPaaS will run. Instructions on how to find or create a ConPaaS image
   suitable to run on Amazon EC2 can be found in :ref:`conpaas-on-ec2`.
   The section :ref:`conpaas-on-opennebula` describes how to create a ConPaaS
   image for OpenNebula.

#. Install and configure **cpsdirector** as explained in
   :ref:`director-installation`. All system configuration takes place in the
   director. 

#. Install **cpsfrontend** and configure it to use your ConPaaS
   director as explained in :ref:`frontend-installation`.

.. _director-installation:

Director installation
=====================

The ConPaaS Director is a web service that allows users to manage their ConPaaS
applications. Users can create, configure and terminate their cloud
applications through it. This section describes the process of setting up a
ConPaaS director on a Debian GNU/Linux system. Although the ConPaaS director
might run on other distributions, only Debian versions 6.0 (Squeeze) and 7.0
(Wheezy) are officially supported. 

#. Install the required packages::

   $ sudo apt-get update
   $ sudo apt-get install build-essential python-setuptools python-dev 
   $ sudo apt-get install libapache2-mod-wsgi libcurl4-openssl-dev

#. Make sure that your system's time and date are set correctly by installing
   and running **ntpdate**::

   $ sudo apt-get install ntpdate
   $ sudo ntpdate 0.us.pool.ntp.org

#. Download http://www.conpaas.eu/dl/cpsdirector-1.1.0.tar.gz and
   uncompress it

#. Run :command:`make install` as root

#. Edit :file:`/etc/cpsdirector/director.cfg` providing your cloud
   configuration. Among other things, you will have to choose an Amazon
   Machine Image (AMI) in case you want to use ConPaaS on Amazon EC2, or
   an OpenNebula image if you want to use ConPaaS on OpenNebula.
   Section :ref:`conpaas-on-ec2` explains how to use the Amazon Machine Images
   provided by the ConPaaS team, as well as how to make your own images
   if you wish to do so. A description of how to create an OpenNebula
   image suitable for ConPaaS is available in :ref:`conpaas-on-opennebula`.

The installation process will create an `Apache VirtualHost` for the ConPaaS
director in :file:`/etc/apache2/sites-available/conpaas-director`. There should
be no need for you to modify such a file, unless its defaults conflict with
your Apache configuration.

Run the following commands as root to start your ConPaaS director for
the first time::

    $ sudo a2enmod ssl
    $ sudo a2ensite conpaas-director
    $ sudo service apache2 restart

If you experience any problems with the previously mentioned commands,
it might be that the default VirtualHost created by the ConPaaS director
installation process conflicts with your Apache configuration. The
Apache Virtual Host documentation might be useful to fix those issues:
http://httpd.apache.org/docs/2.2/vhosts/.

SSL certificates
----------------
ConPaaS uses SSL certificates in order to secure the communication
between you and the director, but also to ensure that only authorized
parties such as yourself and the various component of ConPaaS can
interact with the system.

It is therefore crucial that the SSL certificate of your director contains the
proper information. In particular, the `commonName` field of the certificate
should carry the **public hostname of your director**, and it should match the
*hostname* part of :envvar:`DIRECTOR_URL` in
:file:`/etc/cpsdirector/director.cfg`. The installation procedure takes care
of setting up such a field. However, should your director hostname change,
please ensure you run the following commands::

    $ sudo cpsconf.py
    $ sudo service apache2 restart

Director database
-----------------
The ConPaaS Director uses a sqlite database to store information about
registered users and running services. It is not normally necessary for
ConPaaS administrators to directly access such a database. However,
should the need arise, it is possible to inspect and modify the database
as follows::

    $ sudo apt-get install sqlite3
    $ sudo sqlite3 /etc/cpsdirector/director.db

Troubleshooting
---------------
There are a few things you can check if for some reason your Director
installation is not behaving as expected.

If you cannot create services, this is what you should try to do on your
Director:

1. Run the **cpscheck.py** command as root to attempt an automatic detection of
   possible misconfigurations.
2. Check your system's time and date settings as explained previously.
3. Test network connectivity between the director and the virtual machines
   deployed on the cloud(s) you are using.

If services get created, but they fail to startup properly, you should try to
ssh into your manager VM as root and:

1. Make sure that a ConPaaS manager process has been started::

    root@conpaas:~# ps x | grep cpsmanage[r]
      968 ?        Sl     0:02 /usr/bin/python /root/ConPaaS/sbin/manager/php-cpsmanager -c /root/config.cfg -s 192.168.122.15
    
    
2. If a ConPaaS manager process has **not** been started, you should check if
   the manager VM can download a copy of the ConPaaS source code from the
   director. From the manager VM::

    root@conpaas:~# wget --ca-certificate /etc/cpsmanager/certs/ca_cert.pem \
        `awk '/BOOTSTRAP/ { print $3 }' /root/config.cfg`/ConPaaS.tar.gz

   The URL used by your manager VM to download the ConPaaS source code depends
   on the value you have set on your Director in
   :file:`/etc/cpsdirector/director.cfg` for the variable :envvar:`DIRECTOR_URL`.

3. See if your manager's port **443** is open *and* reachable from your
   Director. In the following example, our manager's IP address is 192.168.122.15
   and we are checking if *the director* can contact *the manager* on port 443::

    root@conpaas-director:~# nmap -p443 192.168.122.15
    Starting Nmap 6.00 ( http://nmap.org ) at 2013-05-14 16:17 CEST
    Nmap scan report for 192.168.122.15
    Host is up (0.00070s latency).
    PORT    STATE SERVICE
    443/tcp open  https

    Nmap done: 1 IP address (1 host up) scanned in 0.08 seconds

.. _frontend-installation:

Frontend installation
=====================
The ConPaaS Frontend can be downloaded from
http://www.conpaas.eu/dl/cpsfrontend-1.1.0.tar.gz.

After having uncompressed it you should:

-  Install the ``libapache2-mod-php5`` and ``php5-curl`` Debian packages

-  Copy all the files contained in the :file:`www` directory underneath your
   web server document root

-  Copy :file:`conf/main.ini` and :file:`conf/welcome.txt` in your ConPaaS
   Director configuration folder (:file:`/etc/cpsdirector`). Modify those files
   to suit your needs

-  Create a :file:`config.php` file in the web server directory where you
   have chosen to install the frontend. Please refer to
   :file:`config-example.php` for a detailed explaination of all the
   configuration options. Note that :file:`config.php` must contain the
   :envvar:`CONPAAS_CONF_DIR` option, pointing to the directory mentioned in
   the previous step

Enable SSL if you want to use your frontend via https, for example by
issuing the following commands::

    $ sudo a2enmod ssl
    $ sudo a2ensite default-ssl

Details about the SSL certificate you want to use have to be specified
in :file:`/etc/apache2/sites-available/default-ssl`.

As a last step, restart your Apache web server::

    $ sudo service apache2 restart

At this point, your front-end should be working!

.. _conpaas-on-ec2:

ConPaaS on Amazon EC2
=====================
The Web Hosting Service is capable of running over the Elastic Compute
Cloud (EC2) of Amazon Web Services (AWS). This section describes the
process of configuring an AWS account to run the Web Hosting Service.
You can skip this section if you plan to install ConPaaS over
OpenNebula.

If you are new to EC2, you will need to create an account on the `Amazon
Elastic Compute Cloud <http://aws.amazon.com/ec2/>`_. A very good introduction
to EC2 is `Getting Started with Amazon EC2 Linux Instances
<http://docs.amazonwebservices.com/AWSEC2/latest/GettingStartedGuide/>`_.

Pre-built Amazon Machine Images
-------------------------------
ConPaaS requires the usage of an Amazon Machine Image (AMI) to contain the
dependencies of its processes. For your convenience we provide a pre-built
public AMI, already configured and ready to be used on Amazon EC2, for each
availability zone supported by ConPaaS. The AMI IDs of said images are:

-  ``ami-4055db70`` United States West (Oregon)

-  ``ami-4b249322`` United States East (Northern Virginia)

-  ``ami-db0a0ba`` Europe West (Ireland)

You can use one of these values when configuring your ConPaaS director
installation as described in :ref:`director-installation`.

Create a custom Amazon Machine Image
------------------------------------
Using pre-built Amazon Machine Images is the recommended way of running
ConPaaS on Amazon EC2, as described in the previous section. However,
you can also create a new Elastic Block Store backed Amazon Machine
Image yourself, for example in case you wish to run ConPaaS in a
different Availability Zone. The easiest way to do that is to start from
an already existing AMI, customize it and save the resulting filesystem
as a new image. The following steps explains how to setup an AMI using
this methodology.

#. Log in the AWS management console, select the “EC2” tab, then “AMIs”
   in the left-side menu. Search the public AMIs for a Debian Squeeze
   EBS AMI and start an instance of it. If you are going to use
   micro-instances then the AMI with ID ``ami-e0e11289`` in the US East
   zone could be a good choice.

#. Upload the *conpaas/scripts/create\_vm/ec2-setup-new-vm-image.sh*
   script to the instance:

   ::

           chmod 0400 yourpublickey.pem
           scp -i yourpublickey.pem \
             conpaas/scripts/create_vm/ec2-setup-new-vm-image.sh \
             root@instancename.com:
         

#. Now, ssh to your instance:

   ::

           ssh -i yourpublickey.pem root@your.instancename.com
         

   Run the ``ec2-setup-new-vm-image.sh`` script inside the instance.
   This script will install all of the dependencies of the manager and
   agent processes as well as create the necessary directory structure.

#. Clean the filesystem by removing the ``ec2-setup-new-vm-image.sh``
   file and any other temporary files you might have created.

#. Go to the EC2 administration page at the AWS website, right click on
   the running instance and select “*Create Image (EBS AMI)*”. This step
   will take several minutes. More information about this step can be
   found at
   http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/index.html?Tutorial\_CreateImage.html.

#. After the image has been fully created, you can return to the EC2
   dashboard, right-click on your instance, and terminate it.

Security Group
--------------
An AWS security group is an abstraction of a set of firewall rules to
limit inbound traffic. The default policy of a new group is to deny all
inbound traffic. Therefore, one needs to specify a whitelist of
protocols and destination ports that are accessible from the outside.
The following ports should be open for all running instances:

-  TCP ports 80, 443, 5555, 8000, 8080 and 9000 – used by the Web
   Hosting service

-  TCP port 3306 – used by the MySQL service

-  TCP ports 8020, 8021, 8088, 50010, 50020, 50030, 50060, 50070, 50075,
   50090, 50105, 54310 and 54311 – used by the Map Reduce service

-  TCP ports 4369, 14194 and 14195 – used by the Scalarix service

-  TCP ports 8475, 8999 – used by the TaskFarm service

-  TCP ports 32636, 32638 and 32640 – used by the XtreemFS service

AWS documentation is available at
http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/index.html?using-network-security.html.

.. _conpaas-on-opennebula:

ConPaaS on OpenNebula
=====================
The Web Hosting Service is capable of running over an OpenNebula
installation. This section describes the process of configuring
OpenNebula to run ConPaaS. You can skip this section if you plan to
deploy ConPaaS over Amazon Web Services.

Creating an OpenNebula image
----------------------------
To create an image for OpenNebula you can execute the script
*conpaas/scripts/create\_vm/opennebula-create-new-vm-image.sh* in any
64-bit Debian or Ubuntu machine. Please note that you will need to have
root privileges on such a system. In case you do not have root access to
a Debian or Ubuntu machine please consider installing a virtual machine
using your favorite virtualization technology, or running a
Debian/Ubuntu instance in the cloud.

#. Make sure your system has the following executables installed (they
   are usually located in ``/sbin`` or ``/usr/sbin``, so make sure these
   directories are in your ``$PATH``): *dd parted losetup kpartx
   mkfs.ext3 tune2fs mount debootstrap chroot umount grub-install*

#. It is particularly important that you use Grub version 2. To install
   it:

   ::

         sudo apt-get install grub2
         

#. Edit the
   *conpaas/scripts/create\_vm/opennebula-create-new-vm-image.sh* script
   if necessary: there are two sections in the script that you might
   need to customize with parameters that are specific to your system.
   These sections are marked by comment lines containing the text "TO
   CUSTOMIZE:". There are comments explaining each customizable
   parameter.

#. Obtain the id of the OpenNebula datastore you want to use by running
   ``onedatastore list``. In the following example, we will use "100" as
   our datastore id.

#. Execute the image generation script as root.

#. The script generates an image file called ``conpaas.img`` by default.
   You can now register it in OpenNebula, replacing ’100’ in this
   example with the datastore id obtained with ``onedatastore list``.

   ::

         cat <<EOF > /tmp/conpaas-one.image
         NAME          = "Conpaas"
         PATH          = ${PWD}/conpaas.img
         PUBLIC        = YES
         DESCRIPTION   = "Conpaas vm image"
         EOF
         oneimage create /tmp/conpaas-one.image -d 100

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
   Unmount everything using:

   ::

           sudo umount /tmp/tmp.X/dev /tmp/tmp.X/proc /tmp/tmp.X
         

#. Find which loop device your using:

   ::

           sudo losetup -a
         

#. Remove the device mapping:

   ::

           sudo kpartx -d /dev/loopX
         

#. Remove the binding of the loop device:

   ::

           sudo losetup -d /dev/loopX
         

#. Delete the image file

#. Your system should be back to its original state.

Make sure OpenNebula is properly configured
-------------------------------------------
OpenNebula’s OCCI daemon is used by ConPaaS to communicate with your
OpenNebula cluster.

#. Ensure your occi-server.conf contains the following lines in
   instance\_types:

   ::

       :custom:
         :template: custom.erb

#. At the end of the OCCI profile file ``occi_templates/common.erb``
   from your OpenNebula installation, add the content of the file
   ``misc/common.erb`` from the ConPaaS distribution. This new version
   features a number of improvements from the standard version:

   -  The match for ``OS TYPE:arch`` allows the caller to specify the
      architecture of the machine.

   -  The graphics line allows for using vnc to connect to the VM. This
      is very useful for debugging purposes and is not necessary once
      testing is complete.

#. Make sure you started OpenNebula’s OCCI daemon
