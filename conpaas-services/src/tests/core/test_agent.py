import unittest
from ConfigParser import ConfigParser

from conpaas.core import agent
from conpaas.core import ganglia

from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse

import mock

def config_parser():
    config_parser = ConfigParser()
    config_parser.add_section('agent')
    config_parser.set('agent', 'TYPE', 'test')
    config_parser.set('agent', 'USER_ID', '1')
    config_parser.set('agent', 'SERVICE_ID', '1')
    config_parser.set('agent', 'IP_WHITE_LIST', '127.0.0.1')
    config_parser.set('agent', 'CONPAAS_HOME', '/dev/null')
    return config_parser

class MockAgentGanglia(ganglia.AgentGanglia):
    """Mock Ganglia class, produces no errors"""

    def configure(self):
        return None

    def start(self):
        return None

def mock_agent_ganglia(self):
    return MockAgentGanglia(config_parser())

class MockAgentGangliaStartError(MockAgentGanglia):
    """Mock Ganglia class, something goes wrong while starting up"""

    def start(self):
        return 'Error starting Ganglia'

def mock_agent_ganglia_error(self):
    return MockAgentGangliaStartError(config_parser())
        
class TestAgent(unittest.TestCase):

    def setUp(self):
        self.config_parser = config_parser()

    def test_agent_init(self):
        test_agent = agent.BaseAgent(self.config_parser)

        self.assertEquals('INIT', test_agent.state)
        self.assertEquals(None, test_agent.ganglia)

    @mock.patch('conpaas.core.agent.AgentGanglia', mock_agent_ganglia)
    def test_agent_init_with_ganglia(self):
        test_agent = agent.BaseAgent(self.config_parser)

        self.assertEquals('INIT', test_agent.state)
        self.failUnless(test_agent.ganglia)

    @mock.patch('conpaas.core.agent.AgentGanglia', mock_agent_ganglia_error)
    def test_agent_init_with_ganglia_error(self):
        test_agent = agent.BaseAgent(self.config_parser)

        self.assertEquals('INIT', test_agent.state)
        self.assertEquals(None, test_agent.ganglia)

    def test_check_agent_process(self):
        test_agent = agent.BaseAgent(self.config_parser)

        error_res = test_agent.check_agent_process({ 'argument': 42 })
        self.assertEquals(HttpErrorResponse, type(error_res))

        json_res = test_agent.check_agent_process({})
        self.assertEquals(HttpJsonResponse, type(json_res))

    def test_check_agent_exception(self):
        exception = agent.AgentException(code=4)
        self.assertEquals('Failed to commit configuration', exception.message)

        exception = agent.AgentException(code=0, detail='test')
        self.assertEquals('No configuration exists DETAIL:test', 
            exception.message)

if __name__ == "__main__":
    unittest.main()
