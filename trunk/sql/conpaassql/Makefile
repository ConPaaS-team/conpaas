BASENAME	=	conpaassql
BINNAME		=	$(PWD)/$(BASENAME)-bin.tar.gz
BINDIR		=	$(PWD)/bindist
# This is for deploying (testing).
PACKAGE_NAME	=	conpaas-sql.tar
DEST_DIR_PCKG	=	$(DESTDIR)/$(PACKAGE_NAME)

all:

check: all
	#PYTHONPATH=$(PYTHONPATH) python src/conpaas/mysql/test/unit/agent-manager.py

install: check
	python $(PWD)/setup.py install --prefix=$(DESTDIR)/usr

binary: check
	python $(PWD)/setup.py install --prefix=$(BINDIR)/usr
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
