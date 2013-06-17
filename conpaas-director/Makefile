#

PYTHON=`which python`
COVERAGE=`which python-coverage`
DESTDIR=/
PROJECT=cpsdirector

all:
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make clean - Get rid of scratch and byte files"

source:
	$(PYTHON) setup.py sdist 

install:
	$(PYTHON) setup.py install 
	cpsconf.py

clean:
	$(PYTHON) setup.py clean
	rm -rf build/ MANIFEST cpsdirector.egg-info conpaas ConPaaS.tar.gz
	find . -name '*.pyc' -delete
    
test:
	$(COVERAGE) run --source=cpsdirector test.py
	$(COVERAGE) report -m
