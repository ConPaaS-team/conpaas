PWD 		= 	`pwd`
PYTHONPATH 	= 	`pwd`/src
DESTDIR 	?= 	`/usr/local`
BASENAME	=	conpaassql
BINNAME		=	$(PWD)/$(BASENAME)-bin.tar.gz
BINDIR		=	$(PWD)/bindist
# This is for deploying (testing).
PACKAGE_NAME	=	conpaassql.tar
DEST_DIR_PCKG	=	$(DESTDIR)/$(PACKAGE_NAME)
PYTHON_VER	= 	2.6

all:

check: all
	#PYTHONPATH=./src:./contrib python -m unittest conpaas.mysql.test.unit.agent.TestServerAgent
	#PYTHONPATH=./src:./contrib python -m unittest conpaas.mysql.test.unit.manager.TestServerManager
	PYTHONPATH=./src:./contrib python src/conpaas/mysql/test/unit/agent.py
	PYTHONPATH=./src:./contrib python src/conpaas/mysql/test/unit/manager.py

install: check
	#PYTHONPATH=$(DESTDIR)/usr/lib/python${PYTHON_VER}/site-packages/contrib:$(DESTDIR)/usr/lib/python${PYTHON_VER}/site-packages python $(PWD)/setup.py install --prefix=$(DESTDIR)/usr
	echo $(DESTDIR)
	mkdir -p $(DESTDIR)/usr/lib/python2.6/site-packages/
	PYTHONPATH=$(DESTDIR)/usr/lib/python${PYTHON_VER}/site-packages/contrib:$(DESTDIR)/usr/lib/python${PYTHON_VER}/site-packages python $(PWD)/setup.py install --prefix=$(DESTDIR)/usr

binary: check
	PYTHONPATH=$(BINDIR)/usr/lib/python${PYTHON_VER}/site-packages/contrib:$(BINDIR)/usr/lib/python${PYTHON_VER}/site-packages $(PWD)/setup.py install --prefix=$(BINDIR)/usr
	tar czvf $(BINNAME) -C $(BINDIR) .

deploy: check
	mkdir -p $(DESTDIR)
	tar --exclude=".svn" -cvf $(DEST_DIR_PCKG) .
	## Untar there
	tar xvf $(DEST_DIR_PCKG) -C $(DESTDIR)
	# Remove the package
	#rm $(DEST_DIR_PCKG)
	# Deployment complete!
clean:
	rm -rf $(PWD)/build $(BINDIR) $(BINNAME)
	find src -iname "*.pyc" -exec rm {} \;
	find contrib -iname "*.pyc" -exec rm {} \;
