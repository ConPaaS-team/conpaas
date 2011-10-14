This directory contains the ConPaaS front-end. This is the Web
application that allows ConPaaS users to easily create, start, stop,
and manage their ConPaaS services. This Web application can run
outside of the Cloud.  Detailed installation instructions can be found
in the "../doc" directory.

In short:

- All files located in the "www" directory must be made available in a
  PHP-enabled Web server.

- All files located in the "conf" directory must be made available
  *out* of the Web server directory. For example one may want to store
  them in /etc/conpaas/ or a similar path. These files must be filled
  in with configuration details of the local ConPaaS installation.

- You must edit the file __init__.php in the www directory such that
  it points to the location of the configuration files.

- You must download the AWS JDK for PHP from 
  http://aws.amazon.com/sdkforphp/ and expand it in the "www/lib" 
  directory (thereby creating a directory "www/lib/aws-jdk" containing 
  a number of PHP files and subdirectories).

Guillaume Pierre
gpierre@cs.vu.nl
