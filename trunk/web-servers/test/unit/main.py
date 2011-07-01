'''
Created on Jan 25, 2011

@author: ielhelw
'''

import unittest
from unit import role, agent, manager

if __name__ == '__main__':
  suite = unittest.TestSuite()
  loader = unittest.TestLoader()
  
  suite.addTest(loader.loadTestsFromModule(role))
  suite.addTest(loader.loadTestsFromModule(agent))
  suite.addTest(loader.loadTestsFromModule(manager))
  
  runner = unittest.TextTestRunner(verbosity=2)
  result = runner.run(suite)
