This directory contains the ConPaaS front-end. This is the Web
application that allows ConPaaS users to easily create, start, stop,
and manage their ConPaaS services. This Web application can run
outside of the Cloud.  Detailed installation instructions can be found
in the "../doc" directory.

In short:

- All files located in the "www" directory must be made available in a
  PHP-enabled Web server.

- The file conf/main.ini should be copied in a directory outside of the web
  server directory. Such a directory must contain your Director's certificates
  under a subdirectory called "certs".

- A file called config.php should be created. Please refer to
  config-example.php for a detailed explaination of all the configuration
  options. Note that config.php must contain the CONPAAS_CONF_DIR option,
  pointing to the directory mentioned in the previous step.

Guillaume Pierre
gpierre@cs.vu.nl
