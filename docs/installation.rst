============
Installation 
============

The central component of ConPaaS is called the *ConPaaS Director*
(**cpsdirector**). It is responsible for handling user authentication,
creating new applications, handling their life-cycle and much
more. **cpsdirector** is a web service exposing all its
functionalities via an HTTP-based API.

ConPaaS can be used either via a command line interface (called
**cps-tools**) or through a web frontend (**cpsfrontend**). This
document explains how to install and configure all the aforementioned
components.


.. _ConPaaS: http://www.conpaas.eu
.. _Flask: http://flask.pocoo.org/

ConPaaS's **cpsdirector** and its two clients, **cps-tools** and **cpsfrontend**,
can be installed on your own hardware or on virtual machines running on public
or private clouds. If you wish to install them on Amazon EC2, the Official Debian
Wheezy, Ubuntu 12.04, Ubuntu 14.04 and Ubuntu 16.04 images are known to work well.

ConPaaS services are designed to run either in an `OpenStack` cloud installation
or in the `Amazon Web Services` cloud.

Installing ConPaaS requires to take the following steps:

#. Choose a VM image customized for hosting the services, or create a
   new one. Details on how to do this vary depending on the choice of cloud
   where ConPaaS will run. Instructions on how to configure ConPaaS with
   Amazon EC2 can be found in :ref:`conpaas-on-ec2`. The section
   :ref:`conpaas-on-openstack` describes how to configure ConPaaS to work
   with an OpenStack cloud.

#. Install and configure **cpsdirector** as explained in
   :ref:`director-installation`. All system configuration takes place in the
   director. 

#. Install and configure **cps-tools** as explained in
   :ref:`cpstools-installation`.

#. Install **cpsfrontend** and configure it to use your ConPaaS
   director as explained in :ref:`frontend-installation`.

.. _director-installation:

Director installation
=====================

The ConPaaS Director is a web service that allows users to manage their ConPaaS
applications. Users can create, configure and terminate their cloud
applications through it. This section describes the process of setting up a
ConPaaS director on a Debian/Ubuntu GNU/Linux system. Although the ConPaaS director
might run on other distributions, only Debian versions 6.0 (Squeeze) and 7.0 (Wheezy),
and Ubuntu versions 12.04 (Precise Pangolin), 14.04 (Trusty Tahr) and 16.04 (Xenial
Xerus) are officially supported. Also, only official APT repositories should be
enabled in :file:`/etc/apt/sources.list` and :file:`/etc/apt/sources.list.d/`.

**cpsdirector** is available here:
http://www.conpaas.eu/dl/cpsdirector-2.1.0.tar.gz. The tarball includes an
installation script called :file:`install.sh` for your convenience. You can
either run it as root or follow the installation procedure outlined below in
order to setup your ConPaaS Director installation.

#. Install the required packages::

   $ sudo apt-get update
   $ sudo apt-get install libssl-dev libffi-dev
   $ sudo apt-get install build-essential python-setuptools python-dev 
   $ sudo apt-get install apache2 libapache2-mod-wsgi libcurl4-openssl-dev

#. Make sure that your system's time and date are set correctly by installing
   and running **ntpdate**::

    $ sudo apt-get install ntpdate
    $ sudo ntpdate 0.us.pool.ntp.org

    >> If the NTP socket is in use, you can type:
    $ sudo service ntp stop
    >> and again
    $ sudo ntpdate 0.us.pool.ntp.org

#. Download http://www.conpaas.eu/dl/cpsdirector-2.1.0.tar.gz and
   uncompress it

#. Run :command:`make install` as root

#. After all the required packages are installed, you will get prompted for
   your hostname. Please provide your **public** IP address / hostname

#. Edit :file:`/etc/cpsdirector/director.cfg` providing your cloud
   configuration. Among other things, you will have to choose an Amazon
   Machine Image (AMI) in case you want to use ConPaaS on Amazon EC2 or
   an OpenStack image if you want to use ConPaaS on OpenStack.
   Section :ref:`conpaas-on-ec2` explains how to use the Amazon Machine Images
   provided by the ConPaaS team, as well as how to make your own images
   if you wish to do so. A description of how to create an OpenStack
   image suitable for ConPaaS is available in :ref:`conpaas-on-openstack`.

The installation process will create an `Apache VirtualHost` for the ConPaaS
director in :file:`/etc/apache2/sites-available/conpaas-director.conf` for Apache 2.4
or :file:`/etc/apache2/sites-available/conpaas-director` for older versions of Apache.
There should be no need for you to modify such a file, unless its defaults conflict with
your Apache configuration.

Run the following commands as root to start your ConPaaS director for
the first time::

    $ sudo a2enmod ssl
    $ sudo a2enmod wsgi
    $ sudo a2ensite conpaas-director
    $ sudo service apache2 restart

If you experience any problems with the previously mentioned commands,
it might be that the default VirtualHost created by the ConPaaS director
installation process conflicts with your Apache configuration. The
Apache Virtual Host documentation might be useful to fix those issues:
http://httpd.apache.org/docs/2.4/vhosts/.

Finally, you can start adding users to your ConPaaS installation as follows::

    $ sudo cpsadduser.py

SSL certificates
----------------
ConPaaS uses SSL certificates in order to secure the communication
between you and the director, but also to ensure that only authorized
parties such as yourself and the various components of ConPaaS can
interact with the system.

It is, therefore, crucial that the SSL certificate of your director contains the
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
The ConPaaS Director uses a SQLite database to store information about
registered users and running services. It is not normally necessary for
ConPaaS administrators to directly access such a database. However,
should the need arise, it is possible to inspect and modify the database
as follows::

    $ sudo apt-get install sqlite3
    $ sudo sqlite3 /etc/cpsdirector/director.db

On a fresh installation the database will be created on the fly.

Multi-cloud support
-------------------
ConPaaS services can be created and scaled on multiple heterogeneous clouds.

In order to configure **cpsdirector** to use multiple clouds, you need to set
the :envvar:`OTHER_CLOUDS` variable in the **[iaas]** section of
:file:`/etc/cpsdirector/director.cfg`. For each cloud name defined in
:envvar:`OTHER_CLOUDS` you need to create a new configuration section named
after the cloud itself. Please refer to
:file:`/etc/cpsdirector/director.cfg.multicloud-example` for an example.

Troubleshooting
---------------
If for some reason your Director installation is not behaving as expected, here are a few frequent issues and their solutions.

If you cannot create services, try to run this on the machine holding your Director:

1. Run the **cpscheck.py** command as root to attempt an automatic detection of
   possible misconfigurations.
2. Check your system's time and date settings as explained previously.
3. Test network connectivity between the director and the virtual machines
   deployed on the cloud(s) you are using.
4. Check the contents of :file:`/var/log/apache2/director-access.log` and
   :file:`/var/log/apache2/director-error.log`.

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

    root@conpaas-director:~# apt-get install nmap
    root@conpaas-director:~# nmap -p443 192.168.122.15
    Starting Nmap 6.00 ( http://nmap.org ) at 2013-05-14 16:17 CEST
    Nmap scan report for 192.168.122.15
    Host is up (0.00070s latency).
    PORT    STATE SERVICE
    443/tcp open  https

    Nmap done: 1 IP address (1 host up) scanned in 0.08 seconds

4. Check the contents of :file:`/root/manager.err`, :file:`/root/manager.out`
   and :file:`/var/log/cpsmanager.log`.
   
5. If the Director fails to respond to requests and you receive errors such as
   ``No ConPaaS Director at the provided URL: HTTP Error 403: Forbidden`` or
   ``403 Access Denied``, you need to allow access to the root file system,
   which is denied by default in newer versions of **apache2**.
   You can fix this by modifying the file :file:`/etc/apache2/apache2.conf`.
   In particular, you need to replace these lines::


             <Directory />
                     Options FollowSymLinks
                     AllowOverride all
                     Order deny,allow
                     Allow from all
             </Directory>
             
             
   with these others::


             <Directory />
                     Options Indexes FollowSymLinks Includes ExecCGI
                     AllowOverride all
                     Order deny,allow
                     Allow from all
             </Directory> 
             
             
Command line tool installation
================================

The new command line client for ConPaaS is called ``cps-tools``.

.. _cpstools-installation:

Installing and configuring cps-tools
------------------------------------

The command line ``cps-tools`` is a command line client to interact with
ConPaaS. It has essentially a modular internal architecture that is easier
to extend. It has also *object-oriented* arguments where ConPaaS objects
are services, users, clouds, and applications. The arguments consist of
stating the object first and then calling a sub-command on it. It also
replaces the command line tool ``cpsadduser.py``.

``cps-tools`` requires:

    * Python 2.7 
    * Python argparse module
    * Python argcomplete module

If these are not yet installed, first follow the guidelines in :ref:`python-and-ve`.

Installing ``cps-tools``::

    $ tar -xaf cps-tools-2.1.0.tar.gz
    $ cd cps-tools-2.1.0
    $ ./configure --sysconf=/etc
    $ sudo make install
    >> or:
    $ make prefix=$HOME/src/virtualenv-1.11.4/ve install |& tee my-make-install.log
    $  cd ..
    $  pip install simplejson |& tee sjson.log
    $  apt-get install libffi-dev |& tee libffi.log
    $  pip install cpslib-2.1.0.tar.gz |& tee my-ve-cpslib.log

Configuring ``cps-tools``::

    $ mkdir -p $HOME/.conpaas
    $ cp /etc/cps-tools.conf $HOME/.conpaas/
    $ vim $HOME/.conpaas/cps-tools.conf
    >> update 'director_url' and 'username'
    >> do not update 'password' unless you want to execute scripts that must retrieve a certificate without interaction
    $ cps-user get_certificate
    >> enter you password
    >> now you can use cps-tools commands

.. _python-and-ve:

Installing Python2.7 and virtualenv
-----------------------------------

Recommended installation order is first ``python2.7``, then ``virtualenv`` (you will need about 0.5GB of free disk space).
Check if the following packages are installed, and install them if not::

    apt-get install gcc
    apt-get install libreadline-dev
    apt-get install -t squeeze-backports libsqlite3-dev libsqlite3-0
    apt-get install tk8.4-dev libgdbm-dev libdb-dev libncurses-dev

Installing ``python2.7``::

    $ mkdir ~/src        (choose a directory)
    $ cd ~/src
    $ wget --no-check-certificate http://www.python.org/ftp/python/2.7.2/Python-2.7.2.tgz
    $ tar xzf Python-2.7.2.tgz
    $ cd Python-2.7.2
    $ mkdir $HOME/.localpython
    $ ./configure --prefix=$HOME/.localpython |& tee my-config.log
    $ make |& tee my-make.log
    >> here you may safely ignore complaints about missing modules: bsddb185   bz2   dl   imageop   sunaudiodev  
    $ make install |& tee my-make-install.log

Installing ``virtualenv`` (here version 1.11.4)::

    $ cd ~/src
    $ wget --no-check-certificate http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.4.tar.gz
    $ tar xzf virtualenv-1.11.4.tar.gz
    $ cd virtualenv-1.11.4
    $ $HOME/.localpython/bin/python setup.py install     (install virtualenv using P2.7)
    
    $ $HOME/.localpython/bin/virtualenv ve -p $HOME/.localpython/bin/python2.7 
    New python executable in ve/bin/python2.7
    Also creating executable in ve/bin/python
    Installing setuptools, pip...done.
    Running virtualenv with interpreter $HOME/.localpython/bin/python2.7

Activate ``virtualenv``::

    $ alias startVE='source $HOME/src/virtualenv-1.11.4/ve/bin/activate'
    $ alias stopVE='deactivate'
    $ startVE
    (ve)$ python -V
    Python 2.7.2
    (ve)$

Install python ``argparse`` and ``argcomplete`` modules::

    (ve)$ pip install argparse
    (ve)$ pip install argcomplete
    (ve)$ activate-global-python-argcomplete


.. _frontend-installation:

Frontend installation
=====================
As for the Director, only Debian versions 6.0 (Squeeze) and 7.0 (Wheezy), and
Ubuntu versions 12.04 (Precise Pangolin), 14.04 (Trusty Tahr) and 16.04 (Xenial
Xerus) are officially supported, and no external APT repository should be
enabled. In a typical setup, Director and Frontend are installed on the same
host, but such does not need to be the case.

The ConPaaS Frontend can be downloaded from
http://www.conpaas.eu/dl/cpsfrontend-2.1.0.tar.gz.

After having uncompressed it you should install the required packages::

   $ sudo apt-get install libapache2-mod-php5 php5-curl

If you use Ubuntu 16.04 (which ships with PHP 7), the following command
may be used (the Frontend supports PHP 7 as well)::

   $ sudo apt-get install libapache2-mod-php php-curl php-zip

Copy all the files contained in the :file:`www` directory underneath your web
server document root. For example::

   $ sudo cp -a www/ /var/www/

Copy :file:`conf/main.ini` and :file:`conf/welcome.txt` in your ConPaaS
Director configuration folder (:file:`/etc/cpsdirector`). Modify those files to
suit your needs::

   $ sudo cp conf/{main.ini,welcome.txt} /etc/cpsdirector/

Create a :file:`config.php` file in the web server directory where you have
chosen to install the frontend. :file:`config-example.php` is a good starting
point::

   $ sudo cp www/config-example.php /var/www/config.php

Note that :file:`config.php` must contain the :envvar:`CONPAAS_CONF_DIR`
option, pointing to the directory mentioned in the previous step

By default, PHP sets a default maximum size for uploaded files to 2Mb
(and 8Mb to HTTP POST requests).
However, in the web frontend, users will need to upload larger files
(for example, a WordPress tarball is about 5Mb, a MySQL dump can be tens of Mb).
To set higher limits, set the properties `post_max_size` and `upload_max_filesize`
in file :file:`/etc/php5/apache2/php.ini` (or
:file:`nano /etc/php/7.0/apache2/php.ini` for PHP 7.0). Note that property
`upload_max_filesize` cannot be larger than property `post_max_size`.

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
ConPaaS is capable of running over the Elastic Compute Cloud (EC2) of Amazon
Web Services (AWS). This section describes the process of configuring an AWS
account to run ConPaaS. You can skip this section if you plan to install ConPaaS
over OpenStack or use specialized versions such as the Nutshell or ConPaaS on
Raspberry PI.

If you are new to EC2, you will need to create an account on the `Amazon
Elastic Compute Cloud <http://aws.amazon.com/ec2/>`_. A very good introduction
to EC2 is `Getting Started with Amazon EC2 Linux Instances
<http://docs.amazonwebservices.com/AWSEC2/latest/GettingStartedGuide/>`_.

Pre-built Amazon Machine Images
-------------------------------
ConPaaS requires the usage of an Amazon Machine Image (AMI) to contain the
dependencies of its processes. For your convenience, we provide a pre-built
public AMI, already configured and ready to be used on Amazon EC2, for each
availability zone supported by ConPaaS. The AMI IDs of said images are:

-  ``ami-41890256`` United States East (Northern Virginia)

-  ``ami-f7aaeb97`` United States West (Northern California)

-  ``ami-2531fd45`` United States West (Oregon)

-  ``ami-8fa1c3fc`` Europe West (Ireland)

-  ``ami-148a7175`` Asia Pacific (Tokyo)

-  ``ami-558b5436`` Asia Pacific (Singapore)

-  ``ami-6690ba05`` Asia Pacific (Sydney)

-  ``ami-7af56216`` South America (Sao Paulo)

You can use one of these values when configuring your ConPaaS director
installation as described in :ref:`director-installation`.

.. _registering-image-on-ec2:

Registering your custom VM image to Amazon EC2
----------------------------------------------
Using prebuilt Amazon Machine Images is the recommended way of running ConPaaS
on Amazon EC2, as described in the previous section. If you plan to use one
of these AMIs, you can skip this section and continue with the configuration of
the Security Group. 

You can also download a prebuilt ConPaaS services image that is suitable to be
used with Amazon EC2, for example in case you wish to run ConPaaS in a different
Availability Zone. This image is available from the following link:

**ConPaaS VM image for Amazon EC2 (x86_64):**
  | http://www.conpaas.eu/dl/conpaas-2.1.0-amazon.img.tar.gz
  | MD5: c6017f277f01777121dae3f2fb085e92
  | size: 481 MB

In case you prefer to use a custom services image, you can also create a new
Amazon Machine Image yourself, by following the instructions from the Internals
guide: :ref:`image-creation`. Come back to this section after you already
generated the ``conpaas.img`` file.

Amazon AMIs are either stored on Amazon S3 (i.e. S3-backed AMIs) or on Elastic
Block Storage (i.e. EBS-backed AMIs). Each option has its own advantages;
S3-backed AMIs are usually more cost-efficient, but if you plan to use *t1.micro*
(free tier) your VM image should be hosted on EBS.

For an EBS-backed AMI, you should either create your ``conpaas.img`` on an Amazon
EC2 instance or transfer the image to one. Once ``conpaas.img`` is there, you
should execute ``register-image-ec2-ebs.sh`` as root on the EC2 instance to
register your AMI. The script requires your **EC2_ACCESS_KEY** and
**EC2_SECRET_KEY** to proceed. At the end, the script will output your new AMI
ID. You can check this in your Amazon dashboard in the AMI section.

For an S3-backed AMI, you do not need to register your image from an EC2
instance. Simply run ``register-image-ec2-s3.sh`` where you have created your
``conpaas.img``. Note that you need an EC2 certificate with a private key to be
able to do so. Registering an S3-backed AMI requires administrator privileges.
More information on Amazon credentials can be found at
`About AWS Security Credentials <http://docs.aws.amazon.com/AWSSecurityCredentials/1.0/AboutAWSCredentials.html>`_.

.. _security-group-ec2:

Security Group
--------------
An AWS security group is an abstraction of a set of firewall rules to
limit inbound traffic. The default policy of a new group is to deny all
inbound traffic. Therefore, one needs to specify a whitelist of
protocols and destination ports that are accessible from the outside.
The following ports should be open for all running instances:

-  TCP ports 443 and 5555 used by the ConPaaS system (director, managers,
   and agents)

-  TCP ports 80, 8000, 8080 and 9000 – used by the Web Hosting service

-  TCP ports 3306, 4444, 4567, 4568 – used by the MySQL service with
   Galera extensions

-  TCP ports 32636, 32638 and 32640 – used by the XtreemFS service

AWS documentation is available at
http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/index.html?using-network-security.html.


.. _conpaas-on-openstack:

ConPaaS on OpenStack
=====================

ConPaaS can be deployed over an OpenStack installation. This section
describes the process of configuring the DevStack version of OpenStack
to run ConPaaS. You can skip this section if you plan to deploy
ConPaaS over Amazon Web Services.

In the rest of this section, the command-line examples assume that the user is
authenticated and able to run OpenStack commands (such as ``nova list``) on the
controller node. If this is not the case, please refer first to the OpenStack
documentation:
http://docs.openstack.org/openstack-ops/content/lay_of_the_land.html.

If OpenStack was installed using the DevStack script, the easiest way to
set the environment variables that authenticate the user is to source the
``openrc`` script from the ``devstack`` directory::

    $ source devstack/openrc admin admin

.. _registering-image-on-openstack:

Registering your ConPaaS image to OpenStack
--------------------------------------------
The prebuilt ConPaaS images suitable to be used with OpenStack can be downloaded
from the following links, depending on the virtualization technology and
system architecture you are using:

**ConPaaS VM image for OpenStack with KVM (x86_64):**
  | http://www.conpaas.eu/dl/conpaas-2.1.0-openstack-kvm.img.tar.gz
  | MD5: 495098f986b8a059041e4e0063bb20c4
  | size: 480 MB

**ConPaaS VM image for OpenStack with LXC (x86_64):**
  | http://www.conpaas.eu/dl/conpaas-2.1.0-openstack-lxc.img.tar.gz
  | MD5: 24d67aa77aa1e6a2b3a74c1b291579e6
  | size: 449 MB

**ConPaaS VM image for OpenStack with LXC for the Raspberry Pi (arm):**
  | http://www.conpaas.eu/dl/ConPaaS-RPI/conpaas-rpi.img
  | MD5: c29cd086e8e0ebe7f0793e7d54304da4
  | size: 2.0 GB

This section assumes that you already downloaded and decompressed one of the
images above or created one as explained in :ref:`image-creation` and uploaded
it to your OpenStack controller node. To register this image with OpenStack,
you may use either Horizon or the command line client of Glance (the OpenStack
image management service).

In Horizon, you can register the ConPaaS image by navigating to the *Project* >
*Compute* > *Images* menu in the left pane and then pressing the *Create Image*
button. In the next form, you should fill-in the image name, select *Image File*
as the image source and then click the *Choose File* button and select your
image (i.e. *conpaas.img*). The image format should be set to *Raw*.

Alternatively, using the command line, the ConPaaS image can be registered in
the following way::

    $ glance image-create --name <image-name> --disk-format raw --container-format bare --file <conpaas.img>

Networking setup
----------------
ConPaaS requires instances to have public (floating) IP addresses assigned and
will only communicate with an instance using its public IP address.

First, you need to make sure that floating addresses are configured. You can
get a list containing all the configured floating IP addresses as follows::

    $ nova floating-ip-bulk-list

If there are no addresses configured, you can add a new IP address range using
the following command::

    $ nova floating-ip-bulk-create --pool public --interface <interface> <new_range>

for example, using the **br100** interface and the **172.16.0.224/27** address
range::

    $ nova floating-ip-bulk-create --pool public --interface br100 172.16.0.224/27

Second, OpenStack should be configured to assign a floating IP address at every
new instance creation. This can be done by adding the following line to the *[DEFAULT]*
section of the nova configuration file (``/etc/nova/nova.conf``)::

    auto_assign_floating_ip = True

Security Group
--------------
As in the case of Amazon Web Services deployments, OpenStack deployments use
security groups to limit the network connections allowed to an instance.
The list of ports that should be opened for every instance is the same as in
the case of Amazon Web Services and can be consulted here: :ref:`security-group-ec2`.

Your configured security groups can be found in Horizon by navigating to the
*Project* > *Compute* > *Access & Security* menu in the left pane of the dashboard
and then selecting the *Security Groups* tab.

Using the command line, the security groups can be listed using::

    $ nova secgroup-list

You can use the ``default`` security group that is automatically created in every
project. However note that, unless its default settings are changed, this
security group denies all incoming traffic.

For more details on creating and editing a security group, please refer to the
OpenStack documentation available at
http://docs.openstack.org/openstack-ops/content/security_groups.html.

SSH Key Pair
------------
In order to use your OpenStack deployment with ConPaaS, you need to configure
an SSH key pair that will allow you to login to an instance without using a
password.

In Horizon, the key pairs can be found by navigating to the *Project* > *Compute* >
*Access & Security* menu and then selecting the *Key Pairs* tab.

Using the command line, the key pairs can be listed using::

    $ nova keypair-list

By default there is no key pair configured, so you should create a new one or
import an already existing one.

Flavor
------
ConPaaS needs to know which instance type it can use, called *flavor* in OpenStack
terminology. There are quite a few flavors configured by default, which can also
be customized if needed.

The list of available flavors can be obtained in Horizon by navigating to the
*Admin* > *System* > *Flavors* menu. Using the command line, the same result can
be obtained using::

    $ nova flavor-list


.. _conpaas-in-a-nutshell:

ConPaaS in a Nutshell
=====================

ConPaaS in a Nutshell is an extension to the ConPaaS project which aims at 
providing a cloud environment and a ConPaaS installation running on it, all
in a single VM, called the Nutshell. More specifically, this VM has an 
all-in-one OpenStack installation running on top of LXC containers, as well 
as a ConPaaS installation, including all of its components, already configured 
to work in this environment.

The Nutshell VM can be deployed on various virtual environments, not only
standard clouds such as OpenStack and EC2 but also on simpler 
virtualization tools such as VirtualBox. Therefore, it provides a great developing 
and testing environment for ConPaaS without the need of accessing a cloud.

The easiest way to try the Nutshell is to download the preassembled image
for VirtualBox. This can be done from the following link:

**VirtualBox VM containing ConPaaS in a Nutshell (2.5 GB):**
  | http://www.conpaas.eu/dl/ConPaaS-Nutshell-2.1.0.ova
  | MD5: 81ef97d50c9f2cd6d029e5213a7a5d2a

.. warning::
  It is always a good idea to check the integrity of a downloaded image before continuing
  with the next step, as a corrupted image can lead to unexpected behavior. You can do
  this by comparing its MD5 hash with the one shown above. To obtain the MD5 hash, you
  can use the ``md5sum`` command.

Alternatively, you can also create such an image or a similar one that runs
on standard clouds (OpenStack and Amazon EC2 are supported) by
following the instructions in the Internals guide, section :ref:`creating-a-nutshell`.

Running the Nutshell in VirtualBox
----------------------------------

The easiest way to start the Nutshell is using VirtualBox.

As a lot of services run inside the Nutshell VM, it requires a significant amount
of resources. The minimum requirements for a system to be able to run the Nutshell
are as follows::

  CPU: dual-core processor with hardware virtualization instructions
  Memory: at least 6 GM of RAM (from which 3 GB should be allocated to the VM)
  HDD: at least 30 GB of available space

The recommended system requirements for optimal performance::

  CPU: Intel i7 processor or equivalent
  Memory: at least 8 GB of RAM (from which 4 GB should be allocated to the VM)
  HDD: Solid State Drive (SSD) with at least 30 GB of available space

.. warning::
  It is highly advised to run the Nutshell on a system that meets the recommended
  system requirements, or else its performance may be severely impacted. For
  systems that do not meet the recommended requirements (but still meet the minimum
  requirements), a very careful split of the resources between the VM and the host
  system needs to be performed.

#. Make sure that hardware virtualization extensions are activated in your
   computer's BIOS. The procedure for activating them is highly dependent on
   your computer's manufacturer and model. Some general instructions can be found
   here:
   
   https://goo.gl/ZGxK9Z

#. If you haven't done this already, create a host-only network in VirtualBox.
   This is needed in order to allow access to the Nutshell VM and to the applications
   deployed in it from your host machine. To do so from the VirtualBox GUI, go to:
   *File* > *Preferences* > *Network* > *Host-only Networks*. Check if there
   is already a host-only network configured (usually called *vboxnet0*). If not,
   add one by clicking on the *Add host-only network* button.

#. Verify the settings of the host-only network. In the same window, select the
   host-only network (*vboxnet0*) and press the *Edit host-only network* button.
   In the *Adapter* tab, make sure that the following fields have these values::
   
     IPv4 address: 192.168.56.1
     IPv4 Network Mask: 255.255.255.0
   
   and in the *DHCP Server* tab::
   
     Enable Server is checked
     Server Address: 192.168.56.100
     Server Mask: 255.255.255.0
     Lower Address Bound: 192.168.56.101
     Upper Address Bound: 192.168.56.254
   
   You can also use other values than the defaults presented above. In this case,
   note that you will also need to adjust the IP address range allocated by
   OpenStack to the containers to match your settings. You can do this by following
   the instructions from the following section of the User guide:
   :ref:`changing-the-ips-of-the-nutshell`.

#. Import the Nutshell appliance using the menu *File* > *Import Appliance*, or by
   simply double-clicking the *.ova* file in your file manager.
   
   .. warning::
      Make sure you have enough free space on your hard drive before attempting this
      step as importing the appliance will extract the VM's hard disk image from the
      *.ova* archive, which occupies around 21 GB of hard disk space. Creating snapshots
      of the Nutshell VM will also require additional space, so for optimal operation,
      the recommended free space that should be available before importing the VM is
      30 GB.

#. Once the Nutshell has been imported, you may adjust the amount of memory and
   the number of CPUs you want to dedicate to it by clicking on the Nutshell VM,
   then following the menu: *Settings* > *System* > *Motherboard* / *Processor*.
   We recommend allocating at least 4 GB of RAM for the Nutshell to function properly.
   Make sure that enough memory remains for the host system to operate properly and
   never allocate more CPUs than what is available on your host computer.

#. It is also a very good idea to create a snapshot of the initial state of the
   Nutshell VM, immediately after it was imported. This allows the possibility to
   quickly revert to the initial state without importing the VM again when something
   goes wrong.

For more information regarding the usage of the Nutshell please consult the
:ref:`nutshell-guide` section in the User guide.


.. _conpaas-on-raspberrypi:

ConPaaS on Raspberry PI
=======================
ConPaaS on Raspberry PI is an extension to the ConPaaS project which uses one (or more)
Raspberry PI(s) 2 or 3 Model B to create a cloud for deploying applications. Each Raspberry PI is
configured as an OpenStack compute node (using LXC containers), running only the minimal
number of OpenStack services required on such a node (``nova-compute`` and ``cinder-volume``).
All the other OpenStack services, such as Glance, Keystone, Horizon etc., are moved outside
of the PI, on a more powerful machine configured as an OpenStack controller node. The ConPaaS
Director and both clients (command line and web frontend) also run on the controller node.

To ease the deployment of the system, we provide an image containing the raw contents of
the Raspberry PI's SD card, along with a VirtualBox VM image (in the Open Virtualization
Archive format) that contains the controller node and can be deployed on any machine
connected to the same local network as the Raspberry PI(s). So, for a minimal working setup,
you will need at least one Raspberry PI 2 or 3 Model B (equipped with a 32 GB SD card) and one
laptop/desktop computer (with VirtualBox installed) that will host the backend VM. The two
have to be connected to the same local network which, in the default configuration, uses IPs
in the ``172.16.0.0/24`` range.

The two images can be downloaded from the following links:

**RPI's SD card image (4.7 GB):**
  | http://www.conpaas.eu/dl/ConPaaS-RPI/ConPaaS-RPI-SDCard-32G.img.tar.gz
  | MD5: b49a33dac4c6bdba9417b4feef1cd2aa

**VirtualBox VM containing the backend server (7.4 GB):**
  | http://www.conpaas.eu/dl/ConPaaS-RPI/ConPaaS-RPI-Backend-VM.ova
  | MD5: 0e6022423b3f940c73204320a5f4f669

.. warning::
  It is always a good idea to check the integrity of a downloaded image before continuing
  with the next steps, as a corrupted image can lead to unexpected behavior. You can do
  this by comparing its MD5 hash with the ones shown above. To obtain the MD5 hash, you
  can use the ``md5sum`` command.

Installing the image on the Raspberry PI
----------------------------------------
You need to write the image to the Raspberry PI's SD card on a different machine (equipped
with an SD card reader) and then move the SD card back into the Raspberry PI.

Download and decompress the image, then write it to the SD card using the *dd* utility.
You can follow the official instructions from the RaspberryPi.org website:

**Linux**:
  https://www.raspberrypi.org/documentation/installation/installing-images/linux.md

**MacOS**:
  https://www.raspberrypi.org/documentation/installation/installing-images/mac.md

.. warning::
  Decompressing the image will result in a 32 GB file (the raw SD card image), so please
  make sure that you have enough free space before attempting this step.

.. warning::
  Before writing the image, please make sure that the SD card has a capacity of at least
  31998345216 bytes.

The image was designed to fit the majority of the 32 GB SD cards, as the actual size varies
between manufacturers. As a result, its size may be a little lower than the actual size of
your card, leaving some unused space near the end of the card. A lot more unused space
remains if a bigger SD card (64 GB) is used. To recover this wasted space, you may adjust
the partitions by moving the swap partition near the end of the card and expanding the main
*ext4* partition.

.. warning::
  If you adjust the partitions, please make sure that the beginning of every partition
  remains aligned on a 4 MB boundary (the usual size of the SD card's erase block) or else
  performance may be negatively affected.

Deploying the Backend VM
------------------------
Download the *.ova* file and import it into VirtualBox. In a graphical environment, you
can usually do this by double-clicking the *.ova* file.

Adjust the resources allocated to the VM. Although the default settings use a pretty
generous amount of resources (4 CPUs and 4 GB of RAM), reducing this to a less powerful
configuration should work fine (for example 1 CPU and 2 GB of RAM). 

Another very important configuration is setting the VM's network interfaces. Two interfaces
should be present: the first one (called *eth0* inside the VM) should be configured as the
*NAT* type to allow Internet access to the VM. The second interface (*eth1* inside the VM)
should be bridged to an adapter connected to the same local network as the Raspberry PI,
so in the VM's properties select *Bridged adapter* and choose the interface to which the
Raspberry PIs are connected.

For more information regarding the usage of ConPaaS on Raspberry PI, please consult the
:ref:`raspberrypi-guide` section in the user guide.
