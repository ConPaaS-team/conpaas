import unittest
from ConfigParser import ConfigParser

from conpaas.core import ipop

import os
import mock

IPOP_CONF_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
        '..', '..', '..')

def config_parser(role='agent'):
    config_parser = ConfigParser()
    config_parser.add_section(role)
    config_parser.set(role, 'APP_ID', '1')
    config_parser.set(role, 'IPOP_BASE_NAMESPACE', 'http://example.org:443')
    config_parser.set(role, 'CONPAAS_HOME', IPOP_CONF_DIR)
    return config_parser

class TestIPOP(unittest.TestCase):

    def setUp(self):
        self.config_parser = config_parser()

    def tearDown(self):
        for expected in ( 'node', 'ipop', 'ipop.vpn', 'bootstrap', 'dhcp' ):
            filename = os.path.join(IPOP_CONF_DIR, '%s.config' % expected)
            if os.path.isfile(filename):
                os.unlink(filename)

    def test_agent_get_ipop_namespace(self):
        namespace = ipop.get_ipop_namespace(self.config_parser)

        self.assertEquals('cps-example.org:443-1', namespace)

    def test_manager_get_ipop_namespace(self):
        namespace = ipop.get_ipop_namespace(config_parser('manager'))

        self.assertEquals('cps-example.org:443-1', namespace)

    @mock.patch('conpaas.core.ipop.run_cmd', lambda x, y: ('127.0.0.1\n', ''))
    def test_get_ip_address(self):
        self.assertEquals('127.0.0.1', ipop.get_ip_address())

    def test_configure_conpaas_node_ipop_not_installed(self):
        # No IPOP_IP_ADDRESS in config_parser, role=agent
        self.assertEquals(None, ipop.configure_conpaas_node(
            self.config_parser))

        # No IPOP_IP_ADDRESS in config_parser, role=manager
        self.assertEquals(None, ipop.configure_conpaas_node(
            config_parser(role='manager')))

        # IPOP not installed
        self.config_parser.set('agent', 'IPOP_IP_ADDRESS', '127.0.0.1')
        self.assertEquals(None, ipop.configure_conpaas_node(
            self.config_parser))

    @mock.patch('conpaas.core.ipop.IPOP_CONF_DIR', IPOP_CONF_DIR)
    def test_configure_conpaas_node_ipop_installed(self):
        self.config_parser.set('agent', 'IPOP_IP_ADDRESS', '127.0.0.1')
        self.config_parser.set('agent', 'IPOP_BASE_IP', '127.0.0.0')
        self.config_parser.set('agent', 'IPOP_NETMASK', '255.0.0.0')

        self.assertEquals(None, ipop.configure_conpaas_node(
            self.config_parser))

        for required_file in ( 'node', 'ipop', 'bootstrap', 'dhcp' ):
            filename = os.path.join(IPOP_CONF_DIR, '%s.config' % required_file)
            self.failUnless(os.path.isfile(filename))

    @mock.patch('conpaas.core.ipop.IPOP_CONF_DIR', IPOP_CONF_DIR)
    def test_configure_ipop(self):
        print ipop.configure_ipop(
            os.path.join(IPOP_CONF_DIR, 'config', 'ipop'), 
            'test', '127.0.0.0', '255.0.0.0')

if __name__ == "__main__":
    unittest.main()
