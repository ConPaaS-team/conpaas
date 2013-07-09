import unittest

from core import test_agent
from core import test_git
from core import test_clouds

suites = [
    unittest.TestLoader().loadTestsFromTestCase(test_agent.TestAgent),
    unittest.TestLoader().loadTestsFromTestCase(test_git.TestGit),
    unittest.TestLoader().loadTestsFromTestCase(test_clouds.TestCloudsBase),
    unittest.TestLoader().loadTestsFromTestCase(test_clouds.TestCloudDummy),
]

alltests = unittest.TestSuite(suites)

alltests.run(unittest.result.TestResult())
