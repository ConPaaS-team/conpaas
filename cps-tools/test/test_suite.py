import sys
import unittest

import test_config

suites = [
    unittest.TestLoader().loadTestsFromTestCase(test_config.TestConfig),
]

alltests = unittest.TestSuite(suites)
result = unittest.TextTestRunner(verbosity=2).run(alltests)

if not result.wasSuccessful():
    sys.exit(1)
