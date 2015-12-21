============
Installation 
============

The central component of ConPaaS is called the *ConPaaS Director*
(**cpsdirector**). It is responsible for handling user authentication,
creating new applications, handling their life-cycle and much
more. **cpsdirector** is a web service exposing all its
functionalities via an HTTP-based API.

ConPaaS can be used either via a command line interface (called
**cpsclient**) or through a web frontend (**cpsfrontend**).  Recently
a new experimental command line interface called **cps-tools** has
become available (note: **cps-tools** requires Python 2.7). This
document explains how to install and configure all the aforementioned
components.


.. _ConPaaS: http://www.conpaas.eu
.. _Flask: http://flask.pocoo.org/

ConPaaS's **cpsdirector** and its two clients, **cpsclient** and **cpsfrontend**,
can be installed on your own hardware or on virtual machines running on public
or private clouds. If you wish to install them on Amazon EC2, the Official Debian
Wheezy, Ubuntu 12.04 or Ubuntu 14.04 images are known to work well.

ConPaaS services are designed to run either in an `OpenStack` or `OpenNebula` cloud
installation or in the `Amazon Web Services` cloud.

Installing ConPaaS requires to take the following steps:

#. Choose a VM image customized for hosting the services, or create a
   new one. Details on how to do this vary depending on the choice of cloud
   where ConPaaS will run. Instructions on how to find or create a ConPaaS image
   suitable to run on Amazon EC2 can be found in :ref:`conpaas-on-ec2`.
   The section :ref:`conpaas-on-openstack` describes how to create a ConPaaS
   image for OpenStack and section :ref:`conpaas-on-opennebula` describes how to
   create an image for OpenNebula.

#. Install and configure **cpsdirector** as explained in
   :ref:`director-installation`. All system configuration takes place in the
   director. 

#. Install and configure **cpsclient** as explained in
   :ref:`cpsclient-installation`.

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
and Ubuntu versions 12.04 (Precise Pangolin) and 14.04 (Trusty Tahr) are officially supported.
Also, only official APT repositories should be enabled in :file:`/etc/apt/sources.list` and
:file:`/etc/apt/sources.list.d/`. 

**cpsdirector** is available here:
http://www.conpaas.eu/dl/cpsdirector-1.x.x.tar.gz. The tarball includes an
installation script called :file:`install.sh` for your convenience. You can
either run it as root or follow the installation procedure outlined below in
order to setup your ConPaaS Director installation.

#. Install the required packages::

   $ sudo apt-get update
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

#. Download http://www.conpaas.eu/dl/cpsdirector-1.x.x.tar.gz and
   uncompress it

#. Run :command:`make install` as root

#. After all the required packages are installed, you will get prompted for
   your hostname. Please provide your **public** IP address / hostname

#. Edit :file:`/etc/cpsdirector/director.cfg` providing your cloud
   configuration. Among other things, you will have to choose an Amazon
   Machine Image (AMI) in case you want to use ConPaaS on Amazon EC2,
   an OpenStack image if you want to use ConPaaS on OpenStack, or
   an OpenNebula image if you want to use ConPaaS on OpenNebula.
   Section :ref:`conpaas-on-ec2` explains how to use the Amazon Machine Images
   provided by the ConPaaS team, as well as how to make your own images
   if you wish to do so. A description of how to create an OpenStack
   image suitable for ConPaaS is available in :ref:`conpaas-on-openstack` and
   :ref:`conpaas-on-opennebula` contains instructions for OpenNebula.

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
http://httpd.apache.org/docs/2.2/vhosts/.

Finally, you can start adding users to your ConPaaS installation as follows::

    $ sudo cpsadduser.py

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
The ConPaaS Director uses a SQLite database to store information about
registered users and running services. It is not normally necessary for
ConPaaS administrators to directly access such a database. However,
should the need arise, it is possible to inspect and modify the database
as follows::

    $ sudo apt-get install sqlite3
    $ sudo sqlite3 /etc/cpsdirector/director.db

If you have an existing installation (version 1.4.0 and earlier) you
should upgrade your database to contain the extra ``uuid`` field needed 
for external IdP usage (see next topic) and the extra ``openid`` field
needed for OpenID support::

    $ sudo add-user-columns-to-db.sh

This script will warn you when you try to upgrade an already upgraded database.

On a fresh installation the database will be created on the fly.

Contrail IdP and SimpleSAML
---------------------------
ConPaaS can optionally delegate its user authentication to an external
service. For registration and login through the Contrail
Identification Provider you have to install the SimpleSAML package
simplesamlphp-1.11.0 as follows::

    $ wget http://simplesamlphp.googlecode.com/files/simplesamlphp-1.11.0.tar.gz
    $ tar xzf simplesamlphp-1.11.0.tar.gz
    $ cd simplesamlphp-1.11.0
    $ cd cert ; openssl req -newkey rsa:2048 -new -x509 -days 3652 -nodes -out saml.crt -keyout saml.pem

Edit file :file:`../metadata/saml20-idp-remote.php` and replace the ``$metadata
array`` by the code found in the simpleSAMLphp flat file format part at 
the end of the browser output of
https://multi.contrail.xlab.si/simplesaml/saml2/idp/metadata.php?output=xhtml .

Modify the authentication sources to contain the following lines (do 
not copy the line numbers)::

    $ cd ../config ; vi authsources.php
    25                  // 'idp' => NULL,
    26                  'idp' => 'https://multi.contrail.xlab.si/simplesaml/saml2/idp/metadata.php',

    32                  //  next lines added by (your name)
    33                  'privatekey' => 'saml.pem',
    34                  'certificate' => 'saml.crt',

Copy your SimpleSAML tree to :file:`/usr/share` ::

    $ cd ../../
    $ tar cf - simplesamlphp-1.11.0 | ( cd /usr/share ; sudo tar xf - )

Change ownerships::
        
    $ cd /usr/share/simplesamlphp-1.11.0
    $ sudo chown www-data www log
    $ sudo chgrp www-data www log

Now edit :file:`/etc/apache2/sites-enabled/default-ssl.conf` to contain the
following lines (line numbers may vary depending on your current 
situation)::

    5          Alias /simplesaml /usr/share/simplesamlphp-1.11.0/www

    18         <Directory /usr/share/simplesamlphp-1.11.0/www>
    19                 Options Indexes FollowSymLinks MultiViews
    20                 AllowOverride None
    21                 Order allow,deny
    22                 allow from all
    23         </Directory>

And the last thing to do: **register** your director domain name or IP at
*contrail@lists.xlab.si*. This will enable you to use the federated login
service provided by the Contrail project.

Multi-cloud support
-------------------
ConPaaS services can be created and scaled on multiple heterogeneous clouds.

In order to configure **cpsdirector** to use multiple clouds, you need to set
the :envvar:`OTHER_CLOUDS` variable in the **[iaas]** section of
:file:`/etc/cpsdirector/director.cfg`. For each cloud name defined in
:envvar:`OTHER_CLOUDS` you need to create a new configuration section named
after the cloud itself. Please refer to
:file:`/etc/cpsdirector/director.cfg.multicloud-example` for an example.

Virtual Private Networks with IPOP
----------------------------------
Network connectivity between private clouds running on different
networks can be achieved in ConPaaS by using IPOP_ (IP over P2P). This
is useful in particular to deploy ConPaaS instances across multiple
clouds. IPOP adds a virtual network interface to all ConPaaS instances
belonging to an application, allowing services to communicate over a
virtual private network as if they were deployed on the same LAN. This
is achieved transparently to the user and applications - the only
configuration needed to enable IPOP is to determine the network's base
IP address, mask, and the number of IP addresses in this virtual
network that are allocated to each service.

VPN support in ConPaaS is per-application: each application you create will get
its own isolated IPOP Virtual Private Network. VMs running in the same application will
be able to communicate with each other.

In order to enable IPOP you need to set the following variables in
:file:`/etc/cpsdirector/director.cfg`:

    * :envvar:`VPN_BASE_NETWORK` 
    * :envvar:`VPN_NETMASK`
    * :envvar:`VPN_SERVICE_BITS`

Unless you need to access 172.16.0.0/12 networks, the default settings
available in :file:`/etc/cpsdirector/director.cfg.example` are probably going
to work just fine.

The maximum number of services per application, as well as the number of agents
per service, is influenced by your choice of :envvar:`VPN_NETMASK` and
:envvar:`VPN_SERVICE_BITS`::

    services_per_application = 2^VPN_SERVICE_BITS
    agents_per_service = 2^(32 - NETMASK_CIDR - VPN_SERVICE_BITS) - 1

For example, by using 172.16.0.0 for :envvar:`VPN_BASE_NETWORK`, 255.240.0.0
(/12) for :envvar:`VPN_NETMASK`, and 5 :envvar:`VPN_SERVICE_BITS`, you will get
a 172.16.0.0/12 network for each of your applications. Such a network space
will be then logically partitioned between services in the same application.
With 5 bits to identify the service, you will get a maximum number of 32
services per application (2^5) and 32767 agents per service (2^(32-12-5)-1).

*Optional*: specify your own bootstrap nodes.
When two VMs use IPOP, they need a bootstrap node to find each other.
IPOP comes with a default list of bootstrap nodes from PlanetLab servers which
is enough for most use cases.
However, you may want to specify your own bootstrap nodes (replacing the default list).
Uncomment and set :envvar:`VPN_BOOTSTRAP_NODES` to the list of addresses
of your bootstrap nodes, one address per line.
A bootstrap node address specifies a protocol, an IP address and a port.
For example::

    VPN_BOOTSTRAP_NODES =
        udp://192.168.35.2:40000
        tcp://192.168.122.1:40000
        tcp://172.16.98.5:40001


.. _IPOP: http://www.grid-appliance.org/wiki/index.php/IPOP

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

There are two command line clients: an old one called ``cpsclient.py``
and a more recent one called ``cps-tools``.

.. _cpsclient-installation:

Installing and configuring cpsclient.py
---------------------------------------

The command line tool ``cpsclient`` can be installed as root or as a
regular user. Please note that libcurl development files (binary package
:file:`libcurl4-openssl-dev` on Debian/Ubuntu systems) need to be installed on
your system.

As root::
    
    $ sudo easy_install http://www.conpaas.eu/dl/cpsclient-1.x.x.tar.gz

(do not forget to replace 1.x.x with the exact number of the ConPaaS release you are using)

Or, if you do not have root privileges, ``cpsclient`` can also be installed in
a Python virtual environment if ``virtualenv`` is available on your machine::

    $ virtualenv conpaas # create the 'conpaas' virtualenv
    $ cd conpaas
    $ source bin/activate # activate it
    $ easy_install http://www.conpaas.eu/dl/cpsclient-1.x.x.tar.gz

Configuring ``cpsclient.py``::

    $ cpsclient.py credentials
    Enter the director URL: https://your.director.name:5555
    Enter your username: xxxxx
    Enter your password: 
    Authentication succeeded



.. _cpstools-installation:

Installing and configuring cps-tools
------------------------------------

The command line ``cps-tools`` is a more recent command line client to interact
with ConPaaS.
It has essentially a modular internal architecture that is easier to extend.
It has also "object-oriented" arguments where "ConPaaS" objects are services, users, clouds and applications.
The argument consists in stating the "object" first and then calling a sub-command on it.
It also replaces the command line tool ``cpsadduser.py``.

``cps-tools`` requires:

    * Python 2.7 
    * Python argparse module
    * Python argcomplete module

If these are not yet installed, first follow the guidelines in :ref:`python-and-ve`.

Installing ``cps-tools``::

    $ tar -xaf cps-tools-1.x.x.tar.gz
    $ cd cps-tools-1.x.x
    $ ./configure --sysconf=/etc
    $ sudo make install

or::
	
    $ make prefix=$HOME/src/virtualenv-1.11.4/ve install |& tee my-make-install.log
    $  cd ..
    $  pip install simplejson |& tee sjson.log
    $  apt-get install libffi-dev |& tee libffi.log
    $  pip install cpslib-1.x.x.tar.gz |& tee my-ve-cpslib.log

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

Install python argparse and argcomplete modules::

    (ve)$ pip install argparse
    (ve)$ pip install argcomplete
    (ve)$ activate-global-python-argcomplete


.. _frontend-installation:

Frontend installation
=====================
As for the Director, only Debian versions 6.0 (Squeeze) and 7.0 (Wheezy), and
Ubuntu versions 12.04 (Precise Pangolin) and 14.04 (Trusty Tahr) are officially
supported, and no external APT repository should be enabled. In a typical setup
Director and Frontend are installed on the same host, but such does not need to
be the case.

The ConPaaS Frontend can be downloaded from
http://www.conpaas.eu/dl/cpsfrontend-1.x.x.tar.gz. 

After having uncompressed it you should install the required packages::

   $ sudo apt-get install libapache2-mod-php5 php5-curl

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
in file :file:`/etc/php5/apache2/php.ini`. Note that property `upload_max_filesize`
cannot be larger than property `post_max_size`.

Enable SSL if you want to use your frontend via https, for example by
issuing the following commands::

    $ sudo a2enmod ssl
    $ sudo a2ensite default-ssl

Details about the SSL certificate you want to use have to be specified
in :file:`/etc/apache2/sites-available/default-ssl`.

As a last step, restart your Apache web server::

    $ sudo service apache2 restart

At this point, your front-end should be working!

.. _image-creation:

Creating A ConPaaS Services VM Image
====================================
Various services require certain packages and configurations to be present in
the VM image. ConPaaS provides facilities for creating specialized VM images
that contain these dependencies. Furthermore, for the convenience of users,
there are prebuilt Amazon AMIs that contain the dependencies for *all*
available services. If you intend to run ConPaaS on Amazon EC2 and do not need
a specialized VM image, then you can skip this section and proceed to
:ref:`conpaas-on-ec2`.

Configuring your VM image
-------------------------
The configuration file for customizing your VM image is located at 
*conpaas-services/scripts/create_vm/create-img-script.cfg*. 

In the **CUSTOMIZABLE** section of the configuration file, you can define
whether you plan to run ConPaaS on Amazon EC2, OpenStack or OpenNebula. Depending on the
virtualization technology that your target cloud uses, you should choose either
KVM or Xen for the hypervisor. Note that for Amazon EC2 this variable needs to
be set to Xen. Please do not make the recommended size for the image file
smaller than the default. The *optimize* flag enables certain optimizations to
reduce the necessary packages and disk size. These optimizations allow for
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
*create_vm* directory:: 

    $ python create-img-script.py

This program generates a script file named *create-img-conpaas.sh*. This script
is based on your specific configurations.

Creating your VM image
----------------------
To create the image you can execute *create-img-conpaas.sh* in any 64-bit
Debian or Ubuntu machine. Please note that you will need to have root
privileges on such a system. In case you do not have root access to a Debian or
Ubuntu machine please consider installing a virtual machine using your favorite
virtualization technology, or running a Debian/Ubuntu instance in the cloud.

#. Make sure your system has the following executables installed (they
   are usually located in ``/sbin`` or ``/usr/sbin``, so make sure these
   directories are in your ``$PATH``): *dd parted losetup kpartx
   mkfs.ext3 tune2fs mount debootstrap chroot umount grub-install*

#. It is particularly important that you use Grub version 2. To install
   it::

         sudo apt-get install grub2
         
#. Execute *create-img-conpaas.sh* as root.


The last step can take a very long time. If all goes well, the final VM image
is stored as *conpaas.img*. This file is later registered to your target IaaS
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


.. _conpaas-on-ec2:

ConPaaS on Amazon EC2
=====================
ConPaaS is capable of running over the Elastic Compute
Cloud (EC2) of Amazon Web Services (AWS). This section describes the
process of configuring an AWS account to run ConPaaS.
You can skip this section if you plan to install ConPaaS over
OpenStack or OpenNebula.

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

-  ``ami-7a565912`` United States East (Northern Virginia)

-  ``ami-b7dd31f3`` United States West (Northern California)

-  ``ami-e57f49d5`` United States West (Oregon)

-  ``ami-7f7e1108`` Europe West (Ireland)

-  ``ami-3a0bc83a`` Asia Pacific (Tokyo)

-  ``ami-fcdde1ae`` Asia Pacific (Singapore)

-  ``ami-0b473b31`` Asia Pacific (Sydney)

-  ``ami-a154d0bc`` South America (Sao Paulo)

You can use one of these values when configuring your ConPaaS director
installation as described in :ref:`director-installation`.

.. _registering-image-on-ec2:

Registering your custom VM image to Amazon EC2
----------------------------------------------
Using pre-built Amazon Machine Images is the recommended way of running ConPaaS
on Amazon EC2, as described in the previous section. However, you can also
create a new Amazon Machine Image yourself, for example in case you wish to run
ConPaaS in a different Availability Zone or if you prefer to use a custom
services image. If this is the case, you should have already created your VM
image (*conpaas.img*) as explained in :ref:`image-creation`.

Amazon AMIs are either stored on Amazon S3 (i.e. S3-backed AMIs) or on Elastic
Block Storage (i.e. EBS-backed AMIs). Each option has its own advantages;
S3-backed AMIs are usually more cost-efficient, but if you plan to use t1.micro
(free tier) your VM image should be hosted on EBS.

For an EBS-backed AMI, you should either create your *conpaas.img* on an Amazon
EC2 instance, or transfer the image to one. Once *conpaas.img* is there, you
should execute *register-image-ec2-ebs.sh* as root on the EC2 instance to
register your AMI. The script requires your **EC2_ACCESS_KEY** and
**EC2_SECRET_KEY** to proceed. At the end, the script will output your new AMI
ID. You can check this in your Amazon dashboard in the AMI section.

For a S3-backed AMI, you do not need to register your image from an EC2
instance. Simply run *register-image-ec2-s3.sh* where you have created your
*conpaas.img*. Note that you need an EC2 certificate with private key to be
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

-  TCP ports 80, 443, 5555, 8000, 8080 and 9000 – used by the Web
   Hosting service

-  TCP ports 3306, 4444, 4567, 4568 – used by the MySQL service with
   Galera extensions

-  TCP ports 8020, 8021, 8088, 50010, 50020, 50030, 50060, 50070, 50075,
   50090, 50105, 54310 and 54311 – used by the Map Reduce service

-  TCP ports 4369, 14194 and 14195 – used by the Scalarix service

-  TCP ports 2633, 8475, 8999 – used by the TaskFarm service

-  TCP ports 32636, 32638 and 32640 – used by the XtreemFS service

AWS documentation is available at
http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/index.html?using-network-security.html.

.. _conpaas-on-openstack:

ConPaaS on OpenStack
=====================

ConPaaS can be deployed over an OpenStack installation. This section
describes the process of configuring the DevStack version of OpenStack
to run ConPaaS. You can skip this section if you plan to deploy
ConPaaS over Amazon Web Services or OpenNebula.

In the rest of this section, the command-line examples assume that the user is
authenticated and able to run OpenStack commands (such as ``nova list``) on the
controller node. If this is not the case, please refer first to the OpenStack
documentation:
http://docs.openstack.org/openstack-ops/content/lay_of_the_land.html.

If OpenStack was installed using the DevStack script, the easiest way to
set the environment variables that authenticate the user is to source the
``openrc`` script from the ``devstack`` directory::

    $ source devstack/openrc admin admin

Getting the OpenStack API access credentials
--------------------------------------------
ConPaaS talks with an OpenStack deployment using the EC2 API, so first make
sure that EC2 API access is enabled for the OpenStack deployment and note
down the EC2 Access Key and EC2 Secret Key.

Using Horizon (the OpenStack dashboard), the EC2 access credentials can be
recovered by navigating to the *Project* > *Compute* > *Access & Security*
menu in the left pane of the dashboard and then selecting the *API Access*
tab. The EC2 Access Key and EC2 Secret key can be revealed by pressing the
*View Credentials* button located on the right side of the page.

Using the command line, the same credentials can be obtained by interrogating
Keystone (the OpenStack identity manager service) using the following command::

    $ keystone ec2-credentials-list

For testing the EC2 API or obtaining necessary information, it is very often
useful to install the Eucalyptus client API tools (euca2ools). On a Debian /
Ubuntu system, this can be done using the following command::

    $ sudo apt-get install euca2ools

Before executing any commands from this package, you must first export the
**EC2_URL**, **EC2_ACCESS_KEY** and **EC2_SECRET_KEY** environment variables,
using the values obtained by following the instructions above. In newer versions
of this package, these environment variables are renamed to **EC2_URL**,
**AWS_ACCESS_KEY** and **AWS_SECRET_KEY**.

Alternatively, OpenStack provides a script that, when sourced, automatically
exports all the required environment variables. Using the Horizon dashboard,
this script can be found by navigating to the *Project* > *Compute* > *Access &
Security* menu in the left pane and then selecting the *API Access* tab. An
archive containing this script (named ``ec2rc.sh``) can be downloaded by
pressing the *Download EC2 Credentials* button.

An easy way to check that euca2ools commands work is by listing all the active
instances using::

    $ euca-describe-instances

.. _registering-image-on-openstack:

Registering your ConPaaS image to OpenStack
--------------------------------------------
This section assumes that you already have created a ConPaaS services image as
explained in :ref:`image-creation` and uploaded it to your OpenStack controller
node. To register this image with OpenStack, you may use either Horizon or the
command line client of Glance (the OpenStack image management service).

In Horizon, you can register the ConPaaS image by navigating to the *Project* >
*Compute* > *Images* menu in the left pane and then pressing the *Create Image*
button. In the next form, you should fill-in the image name, select *Image File*
as the image source and then click the *Choose File* button and select your
image (i.e. *conpaas.img*). The image format should be set to *Raw*.

Alternatively, using the command line, the ConPaaS image can be registered in
the following way::

    $ glance image-create --name <image_name> --disk-format raw --container-format bare --file <conpaas.img>

In both cases, you need to obtain the AMI ID associated with the image in order
to allow ConPaaS to refer to it when using the EC2 API. To do this, you need to
execute the following command::

    $ euca-describe-images

The AMI ID appears in the second column of the output.

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
security groups to limit the the network connections allowed to an instance.
The list of ports that should be opened for every instance is the same as in
the case of Amazon Web Services and can be consulted here: :ref:`security-group-ec2`.

Your configured security groups can be found in Horizon by navigating to the
*Project* > *Compute* > *Access & Security* menu in the left pane of the dashboard
and then selecting the *Security Groups* tab.

Using the command line, the security groups can be listed using::

    $ nova secgroup-list

You can use the ``default`` security group that is automatically created in every
project. However note that, unless the its default settings are changed, this
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

The list of available flavors can obtained in Horizon by navigating to the
*Admin* > *System* > *Flavors* menu. Using the command line, the same result can
be obtained using::

    $ nova flavor-list


.. _conpaas-on-opennebula:

ConPaaS on OpenNebula
=====================
ConPaaS is capable of running over an OpenNebula
installation. This section describes the process of configuring
OpenNebula to run ConPaaS. You can skip this section if you plan to
deploy ConPaaS over Amazon Web Services or OpenStack.

.. _registering-image-on-opennebula:

Registering your ConPaaS image to OpenNebula
--------------------------------------------
This section assumed that you already have created a ConPaaS services image as
explained in :ref:`image-creation`. Upload your image (i.e. *conpaas.img*) to
your OpenNebula headnode. The headnode is where OpenNebula services are
running. You need have a valid OpenNebula account on the headnode (i.e. onevm
list works!). Although you have a valid account on OpenNebula, you may have a problem similar to this:

*/usr/lib/one/ruby/opennebula/client.rb:119:in `initialize': ONE_AUTH file not present (RuntimeError)*

You can fix it setting the ONE_AUT variable like follows::

    $ export ONE_AUTH="/var/lib/one/.one/one_auth"

To register your image, you should execute *register-image-opennebula.sh* on
the headnode. *register-image-opennebula.sh* needs the path to *conpaas.img* as
well as OpenNebula's datastore ID and  architecture Type.

To get the datastore ID, you should execute this command on the headnode::
    
    $ onedatastore list

The output of *register-image-opennebula.sh* will be your ConPaaS OpenNebula
image ID.

Make sure OpenNebula is properly configured
-------------------------------------------
OpenNebula’s OCCI daemon is used by ConPaaS to communicate with your
OpenNebula cluster. The OCCI daemon is included in OpenNebula only up to
version 4.6 (inclusive), so later versions of OpenNebula are not officially
supported at the moment.

#. The OCCI server should be configured to listen on the correct interface so that
   it can receive connections from the managers located on the VMs. This can be 
   achieved by modifying the "host" IP (or FQDN - fully qualified domain name) 
   parameter from ``/etc/one/occi-server.conf`` and restarting the OCCI server.

#. Ensure the OCCI server configuration file ``/etc/one/occi-server.conf``
   contains the following lines in section instance\_types::

       :custom:
         :template: custom.erb

#. At the end of the OCCI profile file ``/etc/one/occi_templates/common.erb``
   from your OpenNebula installation, append the following lines::
   
       <% @vm_info.each('OS') do |os| %>
            <% if os.attr('TYPE', 'arch') %>
              OS = [ arch = "<%= os.attr('TYPE', 'arch').split('/').last %>" ]
            <% end %>
       <% end %>
       GRAPHICS = [type="vnc",listen="0.0.0.0"]


   These new lines adds a number of improvements from the standard version:

   -  The match for ``OS TYPE:arch`` allows the caller to specify the
      architecture of the machine.

   -  The last line allows for using VNC to connect to the VM. This
      is very useful for debugging purposes and is not necessary once
      testing is complete.

#. Make sure you started OpenNebula’s OCCI daemon::

       sudo occi-server start

Please note that, by default, OpenNebula's OCCI server performs a reverse DNS
lookup for each and every request it handles. This can lead to very poor
performances in case of lookup issues. It is recommended *not* to install
**avahi-daemon** on the host where your OCCI server is running. If it is
installed, you can remove it as follows::
    
       sudo apt-get remove avahi-daemon

If your OCCI server still performs badly after removing **avahi-daemon**, we
suggest to disable reverse lookups on your OCCI server by editing
``/usr/lib/ruby/$YOUR_RUBY_VERSION/webrick/config.rb`` and replacing the line::

    :DoNotReverseLookup => nil,

with::

    :DoNotReverseLookup => true,


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
standard clouds such as OpenNebula, OpenStack and EC2 but also on simpler 
virtualization tools such as VirtualBox. Therefore, it provides a great developing 
and testing environment for ConPaaS without the need of accessing a cloud.

The easiest way to try the Nutshell is to download the preassembled image
for VirtualBox. This can be done from the following link:

**VirtualBox VM containing ConPaaS in a Nutshell (7.6 GB):**
  | http://www.conpaas.eu/dl/Nutshell-1.5.1.ova
  | MD5: 018ea0eaa6b6108ef020e00391ef3a96

.. warning::
  It is always a good idea to check the integrity of a downloaded image before continuing
  with the next step, as a corrupted image can lead to unexpected behaviour. You can do
  this by comparing its MD5 hash with the one shown above. To obtain the MD5 hash, you
  can use the ``md5sum`` command.

Alternatively, you can also create such an image or a similar one that runs
on standard clouds (OpenNebula, OpenStack and Amazon EC2 are supported) by
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
  system requirements, or else the its performance may be severely impacted. For
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
   We recommend allocating at least 3 GB of RAM for the Nutshell to function properly
   (4 GB is recommended). Make sure that enough memory remains for the host system to
   operate properly and never allocate more CPUs than what is available in your host
   computer.

#. It is also a very good idea to create a snapshot of the initial state of the
   Nutshell VM, immediately after it was imported. This allows the possibility to
   quickly revert to the initial state without importing the VM again, when something
   goes wrong.

For more information regarding the usage of the Nutshell please consult the
:ref:`nutshell-guide` section in the User guide.


.. _conpaas-on-raspberrypi:

ConPaaS on Raspberry PI
=======================
ConPaaS on Raspberry PI is an extension to the ConPaaS project which uses one (or more)
Raspberry PI(s) 2 Model B to create a cloud for deploying applications. Each Raspberry PI is
configured as an OpenStack compute node (using LXC containers), running only the minimal
number of OpenStack services required on such a node (``nova-compute`` and ``cinder-volume``).
All the other OpenStack services, such as Glance, Keystone, Horizon etc., are moved outside
of the PI, on a more powerful machine configured as an OpenStack controller node. The ConPaaS
Director and both clients (command line and web frontend) also run on the controller node.

To ease the deployment of the system, we provide an image containing the raw contents of
the Raspberry PI's SD card, along with a VirtualBox VM image (in the Open Virtualization
Archive format) that contains the controller node and can be deployed on any machine
connected to the same local network as the Raspberry PI(s). So, for a minimal working setup,
you will need at least one Raspberry PI 2 Model B (equipped with a 32 GB SD card) and one
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
  with the next steps, as a corrupted image can lead to unexpected behaviour. You can do
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
