					-------------------------------------------						
						ConPaasSql - Conpaas SQL Server
					-------------------------------------------
					ales.cernivec@xlab.si
					-------------------------------------------
							2012-01-24


Installation and Dependencies

----
apt-get update
apt-get install -y unzip python python-mysqldb python-pycurl python-dev python-setuptools python-pip
----

Installing

----
# python setup.py bdist_egg
# easy_install dist/conpaassql_server<ver>.egg
----

Removing

----------
# pip uninstall conpaassql_server
----------

Configuration
-------------
./src/conpaas/mysql/server/agent/configuration.cnf

Running agent-server

How to run the agent-server:

----
sudo PYTHONPATH=<path to checked out svnroot/contrail/conpaas/trunk/sql/conpaassql> python server.py
----

Running unit tests

----
make check
----

or directly invoking by

----
PYTHONPATH=./src:./contrib python src/conpaas/mysql/test/unit/agent.py
PYTHONPATH=./src:./contrib python src/conpaas/mysql/test/unit/manager.py
----

Generating documentation

----
../doc$ sphinx-build -a -b html source/ build/
----
