'''
Copyright (C) 2010-2011 Contrail consortium.

This file is part of ConPaaS, an integrated runtime environment 
for elastic cloud applications.

ConPaaS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ConPaaS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.


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
