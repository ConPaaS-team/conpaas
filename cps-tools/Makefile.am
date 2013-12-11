SUBDIRS = src
DIST_SUBDIRS= src

#nobase_dist_sysconf_DATA = bash_completion.d/cps-tools
dist_sysconf_DATA = cps-tools.conf

dist_bin_SCRIPTS = \
	bin/cps-tools \
	bin/cps-application \
	bin/cps-service \
	bin/cps-cloud \
	bin/cps-user


install-exec-hook:
	for cmd in cps-tools cps-user cps-application cps-service cps-cloud; \
	do \
	  eval "$$(register-python-argcomplete $$cmd)"; \
	done; \
	activate-global-python-argcomplete

