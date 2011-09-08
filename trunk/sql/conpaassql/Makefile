BASENAME	=	conpaassql
BINNAME		=	$(PWD)/$(BASENAME)-bin.tar.gz
BINDIR		=	$(PWD)/bindist

all:

check: all
	#PYTHONPATH=$(PYTHONPATH) python src/conpaas/mysql/test/unit/agent-manager.py

install: check
	python $(PWD)/setup.py install --prefix=$(DESTDIR)/usr
	#tar --exclude=".svn" -cvf $(DEST_DIR_PCKG) $(SOURCE)
	## Untar there
	#tar xvf $(DEST_DIR_PCKG) -C $(DIR)
	## Remove the package
	##rm $(DEST_DIR_PCKG)
	## Installation complete!

binary: check
	python $(PWD)/setup.py install --prefix=$(BINDIR)/usr
	tar czvf $(BINNAME) -C $(BINDIR) .

clean:
	rm -rf $(PWD)/build $(BINDIR) $(BINNAME)
	find src -iname "*.pyc" -exec rm {} \;
	find contrib -iname "*.pyc" -exec rm {} \;
