PWD 		= 	`pwd`
PYTHONPATH 	= 	`pwd`/src
DESTDIR 	?= 	/usr/local
BASENAME	=	conpaassql
BINNAME		=	$(PWD)/$(BASENAME)-bin.tar.gz
BINDIR		=	$(PWD)/bindist
PACKAGE_NAME	=	conpaassql.tar
DEST_DIR_PCKG	=	$(DESTDIR)/$(PACKAGE_NAME)
PYTHON_VER	= 	`scripts/print_python_version.py`

bdist_egg: check	
	python setup.py bdist_egg

install_egg:	bdist_egg
	easy_install dist/conpaassql_server*.egg

all:	binary

check: 	
	#echo "Python version is $(PYTHON_VER)"
	#PYTHONPATH=./src python src/conpaas/mysql/test/unit/agent.py
	#PYTHONPATH=./src python src/conpaas/mysql/test/unit/manager.py

install: check
	echo $(DESTDIR)
	mkdir -p $(DESTDIR)/lib/python$(PYTHON_VER)/site-packages/
	PYTHONPATH=$(DESTDIR)/lib/python$(PYTHON_VER)/site-packages python setup.py install --prefix=$(DESTDIR)

binary: bdist_egg
	
clean:
	rm -rf $(PWD)/build $(BINDIR) dist
	find src -iname "*.pyc" -exec rm {} \;
	find contrib -iname "*.pyc" -exec rm {} \;
