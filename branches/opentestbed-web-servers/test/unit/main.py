'''
Created on Jan 25, 2011

@author: ielhelw
'''

import unittest, sys
from ConfigParser import ConfigParser
from optparse import OptionParser

from unit import role, agent
from unit.manager import provision, php, java

if __name__ == '__main__':
  suite = unittest.TestSuite()
  loader = unittest.TestLoader()
  parser = OptionParser()
  parser.add_option('-c', '--config', type='string', default=None, dest='config')
  options, args = parser.parse_args()
  if not options.config:
    print >>sys.stderr, 'Failed to find configuration file'
    sys.exit(1)
  config_parser = ConfigParser()
  config_parser.read(options.config)
  
  role.init(config_parser)
  agent.init(config_parser)
  
  suite.addTest(loader.loadTestsFromModule(role))
  suite.addTest(loader.loadTestsFromModule(agent))
  suite.addTest(loader.loadTestsFromModule(provision))
  suite.addTest(loader.loadTestsFromModule(php))
  suite.addTest(loader.loadTestsFromModule(java))
  
  runner = unittest.TextTestRunner(verbosity=2)
  result = runner.run(suite)
