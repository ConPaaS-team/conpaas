#
# Makefile: build and install conpaas-mysql
#

NAME     = conpaas-mysql
SHELL    = /bin/bash
PYTHON   = python2.6
PACKAGE  = $(NAME).tar.gz

DESTDIR  =
PREFIX   = /usr/local

export PYTHONPATH=$(DESTDIR)$(PREFIX)/lib/python2.6/site-packages/


build:
	$(PYTHON) setup.py bdist_egg

dist: 
	mkdir target
	tar czf $(CURDIR)/target/$(PACKAGE) --transform 's|^\.|$(NAME)|' --exclude-vcs --exclude=target --exclude=build --exclude=dist --exclude='**.egg-info' --exclude=pom.xml .

install: build
	mkdir -p $(PYTHONPATH)
	$(PYTHON) setup.py install --prefix=$(DESTDIR)$(PREFIX)

install_egg: build
	easy_install $(wildcard dist/conpaassql_server*.egg)

clean:
	rm -rf $(CURDIR)/build $(CURDIR)/dist $(CURDIR)/target $(CURDIR)/src/conpaassql_server.egg-info


.PHONY: clean dist
.POSIX:
