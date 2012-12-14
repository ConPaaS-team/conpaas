#

PYTHON=`which python`
DESTDIR=/
PROJECT=cpsdirector
VERSION=1.1.0

all:
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make clean - Get rid of scratch and byte files"

source:
	$(PYTHON) setup.py sdist 

install:
	$(PYTHON) setup.py install 
	cpsconf.py
	cpsadduser.py

clean:
	$(PYTHON) setup.py clean
	rm -rf build/ MANIFEST cpsdirector.egg-info conpaas ConPaaS.tar.gz
	find . -name '*.pyc' -delete
    
