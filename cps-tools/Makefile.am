SUBDIRS = src
DIST_SUBDIRS= src

#nobase_dist_sysconf_DATA = bash_completion.d/cps-tools
dist_sysconf_DATA = cps-tools.conf

dist_bin_SCRIPTS = \
	bin/cps-tools \
	bin/cps-application \
	bin/cps-service \
	bin/cps-user \
	bin/cps-cloud \
	bin/cps-director \
	bin/cps-php \
	bin/cps-java \
	bin/cps-mysql \
	bin/cps-xtreemfs \
	bin/cps-generic \
	bin/cps-flink \
	bin/cps-helloworld
	#\
	#bin/cps-scalaris \
	#bin/cps-taskfarm


install-exec-hook:
	for cmd in cps-tools cps-application cps-service cps-user cps-cloud cps-director cps-php cps-java cps-mysql cps-xtreemfs cps-generic cps-flink cps-helloworld; \
	do \
	  eval "$$(register-python-argcomplete $$cmd)"; \
	done; \
	activate-global-python-argcomplete
