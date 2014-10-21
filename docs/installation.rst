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
or private clouds. If you wish to install them on Amazon EC2, the `Official Debian
Wheezy EC2 image (ami-1d620e74)`_ is known to work well. Please note that the
*root* account is disabled and that you should instead login as *admin*.

.. _Official Debian Wheezy EC2 image (ami-1d620e74): https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#Images:filter=all-images;platform=all-platforms;visibility=public-images;search=ami-1d620e74

ConPaaS services are designed to run either in an `OpenNebula` cloud
installation or in the `Amazon Web Services` cloud.

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
ConPaaS director on a Debian GNU/Linux system. Although the ConPaaS director
might run on other distributions, only Debian versions 6.0 (Squeeze) and 7.0
(Wheezy) are officially supported. Also, only official Debian APT repositories
should be enabled in :file:`/etc/apt/sources.list` and
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
   Machine Image (AMI) in case you want to use ConPaaS on Amazon EC2, or
   an OpenNebula image if you want to use ConPaaS on OpenNebula.
   Section :ref:`conpaas-on-ec2` explains how to use the Amazon Machine Images
   provided by the ConPaaS team, as well as how to make your own images
   if you wish to do so. A description of how to create an OpenNebula
   image suitable for ConPaaS is available in :ref:`conpaas-on-opennebula`.

The installation process will create an `Apache VirtualHost` for the ConPaaS
director in :file:`/etc/apache2/sites-available/conpaas-director.conf`. There should
be no need for you to modify such a file, unless its defaults conflict with
your Apache configuration.

Run the following commands as root to start your ConPaaS director for
the first time::

    $ sudo a2enmod ssl
    $ sudo a2enmod wsgi
    $ sudo a2ensite conpaas-director.conf
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
   
If the director fails to respond to requests, and you receive:
``No ConPaaS Director at the provided URL: HTTP Error 403: Forbidden`` , or ``403 Access Denied`` ,
you need to allow access to the root file system, which is denied by default in the new 
version of apache2.  
You can fix it modifying: :file: '/etc/apache2/apache2.conf'.
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

Recommended installation order is first ``python2.7``, then ``virtualenv`` (you will need about 0.5GB of free disk space.)
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

Install python modules::

    (ve)$ pip install argparse
    (ve)$ pip install argcomplete


.. _frontend-installation:

Frontend installation
=====================
As for the Director, only Debian versions 6.0 (Squeeze) and 7.0 (Wheezy) are
supported, and no external APT repository should be enabled. In a typical setup
Director and Frontend are installed on the same host, but such does not need to
be the case.

The ConPaaS Frontend can be downloaded from
http://www.conpaas.eu/dl/cpsfrontend-1.x.x.tar.gz. 

After having uncompressed it you should install the required Debian packages::

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
whether you plan to run ConPaaS on Amazon EC2 or OpenNebula. Depending on the
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
However, in order to generete a regular customized VM image make sure that both 
*container* and *nutshell* flags in this section are set to false.

Once you are done with the configuration, you should run this command in the
create_vm directory:: 

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

-  ``ami-f4c75fc4`` United States West (Oregon)

-  ``ami-c3045aaa`` United States East (Northern Virginia)

-  ``ami-b79271c0`` Europe West (Ireland)

You can use one of these values when configuring your ConPaaS director
installation as described in :ref:`director-installation`.

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
More information on Amazon credetials can be found at 
`About AWS Security Credentials <http://docs.aws.amazon.com/AWSSecurityCredentials/1.0/AboutAWSCredentials.html>`_.

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

-  TCP ports 2633, 8475, 8999 – used by the TaskFarm service

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

Registering your ConPaaS image to OpenNebula
--------------------------------------------
This section assumed that you already have created a ConPaaS services image as
explained in :ref:`image-creation`. Upload your image (i.e. *conpaas.img*) to
your OpenNebula headnode. The headnode is where OpenNebula services are
running. You need have a valid OpenNebula account on the headnode (i.e. onevm
list works!). Although you have a valid account on OpenNebula, you may have a problem similar to this:

*/usr/lib/one/ruby/opennebula/client.rb:119:in `initialize': ONE_AUTH file not present (RuntimeError)*

You can fix it setting the ONE_AUT variable like follows::

    $  export ONE_AUTH="/var/lib/one/.one/one_auth"

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
providing a cloud environent and a ConPaaS installation running on it, all
in a single VM, called the Nutshell. More specifically, this VM has an 
all-in-one OpenStack installation running on top of LXC containers, as well 
as a ConPaaS installation, including all of its components, already configured 
to work in this environment.

The Nutshell VM can be deployed on various virtual environments, not only
standard clouds such as OpenNebula, OpenStack and EC2 but also on simpler 
virtualization tools such as VirtualBox. Therefore, it provides a great developing 
and testing environemnt for ConPaaS without the need of accessing a cloud. 


Creating a Nutshell image
-------------------------
The procedure for creating a Nutshell image is very similar to the one for 
creating a standard costumized image described in section :ref:`image-creation`.
However, there are a few settings in the configuration file which need 
to be considered.

Most importantly, there are two flags in the **Nutshell** section of the 
configuration file, *nutshell* and *container* which control the kind of image
that is going to be generated. Since these two flags can take either value
true of false, we distinguish four cases:

#. nutshell = false, container = false: In this case a standard ConPaaS VM
   image is generated and the nutshell configurations are not taken into consideration.
   This is the default configuration which should be used when ConPaaS is deployed on a
   standard cloud.

#. nutshell = false, container = true: In this case the user indicates that the
   image that will be generated will be a LXC container image. This image is similar
   to a standard VM one, but it does not contain a kernel installation. 

#. nutshell = true, container = false. In this case a Nutshell image is generated
   and a standard ConPaaS VM image will be embedded in it. This configuraiton should be
   used for deploying ConPaaS in nested standard VMs within a single VM.

#. nutshell = true, container = true. Similar to the previous case, a Nutshell image
   is generated but this time a container image is embedded in it instead of a VM one.
   Therefore, in order to generate a Nutshell based on contaners make sure to set these 
   flags to this configuration. This is the default configuraiton for our distribution of
   nutshell.

Another important setting for generating the Nutshell image is also the path to a direcotry
containing the ConPaaS tarballs (cps*.tar.gz files). 
The rest of the settings specify the distro and kernel versions that the Nutshell VM would have.
For the moment we have tested it only for Ubuntu 12.04 with kernel 3.5.0.

In order to run the image generating script, the procedure is almost the same as for a standard image.
From the create_vm diretory run:: 

    $ python create-img-script.py
    $ sudo ./create-img-nutshell.sh

Note that if the nutshell flag is enabled the generated script file is called *create-img-nutshell.sh*.
Otherwise, the generated script file is called create-img-conpaas.sh as indicated previously.


   
Creating a Nutshell image for VirtualBox
----------------------------------------

As mentioned earlier the Nutshell VM can run on VirtualBox. In order to generate a Nutshell image
compatible with VirtualBox, you have to set the *cloud* value to *vbox* on the **Customizable** section of the configuration file.
The rest of the procedure is the same as for other clouds. The result of the image generation script would be a
nutshell.vdi image file which can be used as a virtual hard drive when creating a new appliance on VirtualBox.

The procedure for creating a new appliance on VirtualBox is quite standard:
  
#. Name and OS: You choose a custom name for the appliance but use *Linux* and *Ubuntu (64 bit)* for the type and version.

#. Memory size: Since the nutshell runs a significat number of services and requires also some memory for the containers we suggest to choose at least 3 GB of RAM.

#. Hard drive: Select "User an existing virtual hard drive file", browse to the location of the nutshell.vdi file generated earlier and press create.

Running the Nutshell in VirtualBox
----------------------------------
  
From the 1.4.1 release though, ConPaaS is shipped together with a VirtualBox appliance containing the Nutshell
VM image as well. 

Before running the appliance it is strongly suggested to 
create a host-only network on VirtualBox in case there is not already one created. To do so from the VirtualBox GUI, go to: File>Preferences>Network>Host-only Networks and click add.  Then use the File>Import appliance menu to import the image in VirtualBox.


For more information regarding the usage of the Nutshell please consult the :ref:`nutshell-guide` section in the guide.
