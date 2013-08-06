import sys
import unittest

from core import test_agent
from core import test_git
from core import test_clouds
from core import test_ipop
from core import test_controller

suites = [
    unittest.TestLoader().loadTestsFromTestCase(test_agent.TestAgent),
    unittest.TestLoader().loadTestsFromTestCase(test_git.TestGit),
    unittest.TestLoader().loadTestsFromTestCase(test_clouds.TestCloudsBase),
    unittest.TestLoader().loadTestsFromTestCase(test_clouds.TestCloudDummy),
    unittest.TestLoader().loadTestsFromTestCase(test_ipop.TestIPOP),
    unittest.TestLoader().loadTestsFromTestCase(test_controller.TestController),
    unittest.TestLoader().loadTestsFromTestCase(test_controller.TestReservationTimer),
]

alltests = unittest.TestSuite(suites)
result = unittest.TextTestRunner(verbosity=2).run(alltests)

if not result.wasSuccessful():
    sys.exit(1)
