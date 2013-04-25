"""
Copyright (c) 2010-2013, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the Contrail consortium nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
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
