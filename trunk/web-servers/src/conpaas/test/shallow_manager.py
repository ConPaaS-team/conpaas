'''
Created on Mar 30, 2011

@author: ielhelw
'''

import sys
import memcache
from tempfile import mkdtemp
from os import mkdir
from os.path import join
from threading import Thread

from conpaas.test.mock import agentClient
from conpaas.test.mock.iaas import IaaSClient
from optparse import OptionParser
from ConfigParser import ConfigParser

config_parser = ConfigParser()
config_parser.add_section('manager')
config_parser.set('manager', 'LOG_FILE', '/var/log/conpaas.log')

from conpaas import log
log.init(config_parser)

# PATCH the real implementations with mock
from conpaas.web.manager import server, internals
from conpaas.web.manager.config import Configuration
server.IaaSClient = IaaSClient
internals.client = agentClient

parser = OptionParser()
parser.add_option('-p', type='int', dest='port', default=None)
parser.add_option('-m', type='int', dest='mc', default=None)
opts, args = parser.parse_args()

if not opts.port or not opts.mc:
  parser.print_help()
  sys.exit(1)

mc = memcache.Client(['localhost:'+str(opts.mc)])
mc.set(internals.CONFIG, Configuration())
mc.set(internals.DEPLOYMENT_STATE, internals.S_INIT)

server_port = opts.port
tdir = mkdtemp(prefix='conpaas-web-manager-', dir='/tmp')
code_repo = join(tdir, 'code-repo')
mkdir(code_repo)

server = server.DelpoymentManager(('0.0.0.0', server_port), 'localhost:'+str(opts.mc), config_parser, code_repo, '')
t = Thread(target=server.serve_forever)

t.start()
