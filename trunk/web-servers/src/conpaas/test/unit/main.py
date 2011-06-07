'''
Created on Jan 25, 2011

@author: ielhelw
'''

import unittest
from conpaas.test.unit import role, agent, manager
import logging

if __name__ == '__main__':
  from conpaas.log import set_logging_level
  set_logging_level(logging.CRITICAL)
  
  suite = unittest.TestSuite()
  loader = unittest.TestLoader()
  
  suite.addTest(loader.loadTestsFromModule(role))
  suite.addTest(loader.loadTestsFromModule(agent))
  suite.addTest(loader.loadTestsFromModule(manager))
  
  runner = unittest.TextTestRunner(verbosity=2)
  result = runner.run(suite)
