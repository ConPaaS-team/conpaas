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
	bin/cps-galera \
	bin/cps-xtreemfs \
	bin/cps-scalaris \
	bin/cps-taskfarm


install-exec-hook:
	for cmd in cps-tools cps-user cps-application cps-service cps-cloud cps-php cps-galera cps-xtreemfs cps-scalaris cps-taskfarm; \
	do \
	  eval "$$(register-python-argcomplete $$cmd)"; \
	done; \
	activate-global-python-argcomplete

