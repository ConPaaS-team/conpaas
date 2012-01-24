					-------------------------------------------						
						ConPaasSql - Conpaas SQL Server
					-------------------------------------------
					ales.cernivec@xlab.si
					-------------------------------------------
							2012-01-24


Installation and Dependencies

 Dependencies: 
 * unzip
 * >=python2.6
 * python-mysqldb
 * python-pycurl
 * OCA bindings
 * setuptools

----
apt-get install -y unzip
apt-get install -y python
apt-get install -y python-mysqldb
apt-get install -y python-pycurl
apt-get install -y python-pip

wget https://github.com/lukaszo/python-oca/zipball/0.2.3
wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz#md5=7df2a529a074f613b509fb44feefe74e
----

Setuptool installation

----
tar xvfz setuptools-0.6c11.tar.gz
cd setuptools-0.6c11
python setup.py build
python setup.py install
----

OCA installation

----
unzip 0.2.3
cd lukaszo-python-oca-61992c1
python setup.py build
python setup.py install
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