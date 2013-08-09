import unittest
from ConfigParser import ConfigParser

from conpaas.core import manager
from conpaas.core import ganglia

from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse

import mock

def config_parser():
    config_parser = ConfigParser()
    config_parser.add_section('manager')
    config_parser.set('manager', 'TYPE', 'test')
    config_parser.set('manager', 'USER_ID', '1')
    config_parser.set('manager', 'SERVICE_ID', '1')
    config_parser.set('manager', 'APP_ID', '1')
    config_parser.set('manager', 'CONPAAS_HOME', '/dev/null')
    config_parser.set('manager', 'LOG_FILE', '/dev/null')
    config_parser.set('manager', 'CREDIT_URL', 'https://director.example.org')
    config_parser.set('manager', 'CA_URL', 'https://director.example.org')
    config_parser.set('manager', 'TERMINATE_URL',
            'https://director.example.org')
    return config_parser

class MockManagerGanglia(ganglia.ManagerGanglia):
    """Mock Ganglia class, produces no errors"""

    def configure(self):
        return None

    def start(self):
        return None

def mock_manager_ganglia(self):
    return MockManagerGanglia(config_parser())

class MockManagerGangliaStartError(MockManagerGanglia):
    """Mock Ganglia class, something goes wrong while starting up"""

    def start(self):
        return 'Error starting Ganglia'

def mock_manager_ganglia_error(self):
    return MockManagerGangliaStartError(config_parser())
        
class TestManager(unittest.TestCase):

    def setUp(self):
        self.config_parser = config_parser()

    def tearDown(self):
        try:
            if self.manager.controller is None:
                return
        except AttributeError: 
            return

        rmap = self.manager.controller._Controller__reservation_map
        for reservation_timer in rmap.values():
            reservation_timer.stop()

    def test_manager_init(self):
        self.manager = manager.BaseManager(self.config_parser)

        self.assertEquals('INIT', self.manager.state)
        self.assertEquals(None, self.manager.ganglia)
        self.assertEquals([], self.manager.volumes)

    @mock.patch('conpaas.core.manager.ManagerGanglia', mock_manager_ganglia)
    def test_manager_init_with_ganglia(self):
        self.manager = manager.BaseManager(self.config_parser)

        self.assertEquals('INIT', self.manager.state)
        self.failUnless(self.manager.ganglia)

    @mock.patch('conpaas.core.manager.ManagerGanglia',
            mock_manager_ganglia_error)
    def test_manager_init_with_ganglia_error(self):
        self.manager = manager.BaseManager(self.config_parser)

        self.assertEquals('INIT', self.manager.state)
        self.assertEquals(None, self.manager.ganglia)

    def test_check_manager_exception(self):
        exception = manager.ManagerException(code=1)
        self.assertEquals('Failed to commit configuration', exception.message)

        exception = manager.ManagerException(code=0, detail='test')
        self.assertEquals('Failed to read configuration DETAIL:test', 
            exception.message)

if __name__ == "__main__":
    unittest.main()
