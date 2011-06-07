'''
Created on Feb 8, 2011

@author: ielhelw
'''

import sys
import memcache
from os.path import exists
from optparse import OptionParser
from ConfigParser import ConfigParser

from conpaas.web.manager.config import Configuration
from conpaas.web.manager.internals import DEPLOYMENT_STATE, CONFIG

def config_set(mc):
  config = Configuration()
  config.php_count = 0
  config.web_count = 1
  config.proxy_count = 0
#  oldconfig = mc.get(CONFIG)
#  config.serviceNodes = oldconfig.serviceNodes
#  if oldconfig:
#    config.currentCodeVersion = oldconfig.currentCodeVersion
  mc.set(DEPLOYMENT_STATE, 'INIT')
  mc.set(CONFIG, config)

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('-c', '--config', type='string', default='./config.cfg', dest='config')
  options, args = parser.parse_args()
  if not exists(options.config):
    print >>sys.stderr, 'Failed to find configuration file'
    sys.exit(1)
  config_parser = ConfigParser()
  config_parser.read(options.config)
  mc = memcache.Client([config_parser.get('manager', 'MEMCACHE_ADDR')])
  from conpaas.web.manager import config
  config.memcache = memcache
  
  config_set(mc)

