#
# Makefile: build and install conpaas-taskfarm
#
# TODO: mavenize the project

NAME     = conpaas-taskfarm
SHELL    = /bin/bash
JAVAC    = javac -cp $(CURDIR)/lib/*:$(CURDIR)/ipl-2.2/lib/*
JAR      = jar

SRCFILES = $(shell find $(CURDIR)/src -name '*.java')
WORK     = $(CURDIR)/work
TARGET   = $(CURDIR)/target
JARFILE  = $(TARGET)/$(NAME).jar
PACKAGE  = $(TARGET)/$(NAME).tar.gz

DESTDIR  =
PREFIX   = /usr/local
LIBDIR   = /lib/conpaas/$(NAME)
ETCDIR   = /etc/conpaas/$(NAME)


build: $(JARFILE)
$(JARFILE): $(SRCFILES)
	mkdir -p $(WORK) $(TARGET)
	$(JAVAC) -d $(WORK) $(SRCFILES)
	$(JAR) cf $@ -C $(WORK) .

dist: 
	rm -fr $(TARGET)
	mkdir $(TARGET)
	tar czf $(PACKAGE) --exclude-vcs --exclude=target --exclude=pom.xml .

install: build
	mkdir -p $(DESTDIR)$(PREFIX)$(LIBDIR) $(DESTDIR)$(ETCDIR)
	install -m 0644 $(CURDIR)/ipl-2.2/lib/*.jar $(JARFILE) $(DESTDIR)$(PREFIX)$(LIBDIR)
	install -m 0644 $(CURDIR)/ipl-2.2/*.properties $(DESTDIR)$(ETCDIR)

clean:
	rm -fr $(WORK) $(TARGET)


.PHONY: clean dist
.POSIX:
