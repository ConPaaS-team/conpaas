SUBDIRS = src
DIST_SUBDIRS= src

#nobase_dist_sysconf_DATA = bash_completion.d/cps-tools
dist_sysconf_DATA = cps-tools.conf

dist_bin_SCRIPTS = \
	bin/cps-tools \
	bin/cps-application \
	bin/cps-service \
	bin/cps-cloud \
	bin/cps-user \
	bin/cps-php \
	bin/cps-mysql \
	bin/cps-xtreemfs 
	#\
	#bin/cps-scalaris \
	#bin/cps-taskfarm


install-exec-hook:
	#for cmd in cps-tools cps-user cps-application cps-service cps-cloud cps-php cps-mysql cps-xtreemfs cps-scalaris cps-taskfarm; \
	for cmd in cps-tools cps-user cps-application cps-service cps-cloud cps-php cps-mysql cps-xtreemfs; \
	do \
	  eval "$$(register-python-argcomplete $$cmd)"; \
	done; \
	activate-global-python-argcomplete

