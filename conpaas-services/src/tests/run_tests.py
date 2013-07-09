import unittest

from core import test_agent
from core import test_git

agent_suite = unittest.TestLoader().loadTestsFromTestCase(test_agent.TestAgent)
git_suite = unittest.TestLoader().loadTestsFromTestCase(test_git.TestGit)

alltests = unittest.TestSuite([agent_suite, git_suite])

alltests.run(unittest.result.TestResult())
