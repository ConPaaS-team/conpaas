'''
Created on Jan 25, 2011

@author: ielhelw
'''

import unittest
from unit import role, agent
from unit.manager import provision, php, java

if __name__ == '__main__':
  suite = unittest.TestSuite()
  loader = unittest.TestLoader()
  
  suite.addTest(loader.loadTestsFromModule(role))
  suite.addTest(loader.loadTestsFromModule(agent))
  suite.addTest(loader.loadTestsFromModule(provision))
  suite.addTest(loader.loadTestsFromModule(php))
  suite.addTest(loader.loadTestsFromModule(java))
  
  runner = unittest.TextTestRunner(verbosity=2)
  result = runner.run(suite)
