============
Introduction
============

ConPaaS (http://www.conpaas.eu) is an open-source runtime environment
for hosting applications in the cloud which aims at offering the full
power of the cloud to application developers while shielding them from
the associated complexity of the cloud.

ConPaaS is designed to host both high-performance scientific
applications and online Web applications. It runs on a variety of
public and private clouds, and is easily extensible. ConPaaS automates
the entire life-cycle of an application, including collaborative
development, deployment, performance monitoring, and automatic
scaling. This allows developers to focus their attention on
application-specific concerns rather than on cloud-specific details.

ConPaaS is organized as a collection of services, where each service
acts as a replacement for a commonly used runtime environment. For
example, to replace a MySQL database, ConPaaS provides a cloud-based
MySQL service which acts as a high-level database abstraction. The
service uses real MySQL databases internally, and therefore makes it
easy to port a cloud application to ConPaaS. Unlike a regular
centralized database, however, it is self-managed and fully elastic:
one can dynamically increase or decrease its processing capacity by
requesting it to reconfigure itself with a different number of virtual
machines.
