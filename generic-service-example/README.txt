generic-service-example

Files in this directory are meant to show the use of ConPaaS generic service.
The use case is in development (not yet completely finished) and files are as is.
The goal is to start a shemdros (see https://github.com/Dans-labs/shemdros) service.
In the tests run so far, it turned out that the image used to deploy and run the ConPaaS generic service for shemdros needs to have a disk size of at least 4GB.

The testrun script depends on the availability of the ConPaaS cpsclient.py script.

Description of files
====================
All files with a * are not in the repository, but will be created once scripts are run.

testrun
-------
This script is used to deploy the ConPaaS generic service if it is not yet deployed.
After deploying the generic service, the service is started, if not yet started.
All shell script files (*.sh) and shemdros.zip are packed into code-test.tar and this file is uploaded to the generic service VM.
If this file has been uploaded before, the testrun script will select the newest version, unpack it and start it.

code-test.tar   *
-------------
File created by testrun script, contains all files needed to start and run the generic service.
This file will be uploaded to the generic service by the testrun script.

init.sh
-------
File required to install the generic service.

init-2.sh
---------
Called by init.sh, calls emdros-install.sh and reports time used for installation.

start.sh
-------
File required to run the generic service.

start-2.sh
-------
Called by start.sh, currently a no-op.

emdros-install.sh
-----------------
The core script to install emdros/shemdros

log.sh
------
This script is source'd and contains a generic log command that is use to log and execute commands.

log.err *
-------
Created on the generic service and contains installation error messages.

log.out *
-------
Created on the generic service and contains installation output messages.

logtest.sh
----------
Small script to test the log command.

logtest-1.sh
------------
Helper script to test the log command.

mql-test.sh
-----------
Create mql-test.txt file.

mql-test.txt    *
------------
Mql test command.

README.txt
----------
This file.

shemdros.zip    *
------------
You have to create shemdros.zip from the files that can currently be found on 
https://www.dropbox.com/sh/nhwuvghc3afui8j/AAB4wndZKeBicdE-gP8qsr16a?dl=0

