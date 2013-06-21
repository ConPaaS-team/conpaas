# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import os
import re
from functools import wraps

def test_rw_permissions(f):
	"""
	Checks the read/write permissions of the specified file
	"""
	@wraps(f)
	def rw_check(thefile, *args, **kwargs):
		if not os.access(thefile, os.R_OK | os.W_OK):
			raise Exception("Cannot read/write file %s " % thefile)
		else:
			return f(thefile, *args, **kwargs)
	return rw_check

@test_rw_permissions
def add_node_info(hostsfile, ip, vmid):
	"""
	Add the newly created agent-IP and VM-id to the hostsfile
	"""
	targetfile = open(hostsfile,'a')
	targetfile.write("%s	worker-%s.htc\n" % (ip, vmid))
	targetfile.close()

def remove_node_info(hostsfile, ip):
	"""
	Remove the agent-IP and VM-id from the hostsfile
	"""
	contentlines = open(hostsfile).readlines()
	targetfile = open(hostsfile, 'w')
	for line in contentlines:
		if not re.search('^' + ip, line):
			targetfile.write(line)
