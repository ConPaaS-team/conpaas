              ConPaaS: an integrated runtime environment
		   for elastic Cloud applications 
                       http://www.conpaas.eu


Introduction
============

ConPaaS aims at simplifying the deployment and management of
applications in the Cloud. In ConPaaS, an application is defined as a
composition of one or more services. Each service is an elastic
component dedicated to the hosting of a particular type of
functionality. A service can be seen as a standalone component of a
distributed application.

Each ConPaaS service is self-managed and elastic: it can deploy itself
on the Cloud, monitor its own performance, and increase or decrease
its processing capacity by dynamically (de-)provisioning instances of
itself in the Cloud.  Services are designed to be composable: an
application can for example use a Web hosting service, a database
service to store the internal application state, a file storage
service to store access logs, and a MapReduce service to periodically
compute statistics from these logs. Application providers simply need
to submit a manifest file describing the structure of their
application and its performance requirements.

ConPaaS currently contains:

- A Web frontend that can be installed within or outside the
  Cloud. This is the website that developers can use to create, delete
  and manage applications in ConPaaS.

- One service dedicated to hosting static Web content as well as Web
  applications written in PHP.

- More services are currently being developed. They will be released
  as soon as they are reasonably well tested and integrated with the
  frontend.


Installation
============

You will find a small documentation in the "doc" directory.


Bugs
====

No matter how carefully we have tested this system, it most certainly
still contains a number of remaining bugs. If you encounter any
abnormal behavior, please let us know at info@conpaas.eu.

