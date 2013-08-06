import unittest
from ConfigParser import ConfigParser

from conpaas.core import ipop

import os
import mock

import xml.etree.ElementTree as etree


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

    def _check_bootstrap_nodes(self, dest_file, expected):
        tree = etree.ElementTree().parse(dest_file)
        result = tree.findall('RemoteTAs/Transport')
        transports = [res.text for res in result]
        for exp in expected:
            self.assertTrue(exp in transports,
                            "Cannot find expected bootstrap node %s in %s " % (exp, transports))

    @mock.patch('conpaas.core.ipop.IPOP_CONF_DIR', IPOP_CONF_DIR)
    def test_bootstrap_nodes_unset(self):
        self.config_parser.set('agent', 'IPOP_IP_ADDRESS', '127.0.0.1')
        self.config_parser.set('agent', 'IPOP_BASE_IP', '127.0.0.0')
        self.config_parser.set('agent', 'IPOP_NETMASK', '255.0.0.0')
        self.config_parser.set('agent', 'CONPAAS_HOME', IPOP_CONF_DIR)
        if (self.config_parser.has_option('agent', 'IPOP_BOOTSTRAP_NODES')):
            self.config_parser.remove_option('agent', 'IPOP_BOOTSTRAP_NODES')
        ipop.configure_conpaas_node(self.config_parser)
        dest_file = os.path.join(IPOP_CONF_DIR, 'bootstrap.config')

        # a few bootstrap nodes from default bootstrap.config file
        expected = ["brunet.tcp://193.136.166.56:49302",
                    "brunet.udp://193.136.166.56:49302",
                    "brunet.udp://169.226.40.4:49302",
                    "brunet.tcp://156.62.231.244:49302",
                    ]
        self._check_bootstrap_nodes(dest_file, expected)

    @mock.patch('conpaas.core.ipop.IPOP_CONF_DIR', IPOP_CONF_DIR)
    def test_bootstrap_nodes_set(self):
        bootstrap_nodes = 'udp://192.168.122.1:40000\ntcp://192.168.54.3:40001'
        self.config_parser.set('agent', 'IPOP_IP_ADDRESS', '127.0.0.1')
        self.config_parser.set('agent', 'IPOP_BASE_IP', '127.0.0.0')
        self.config_parser.set('agent', 'IPOP_NETMASK', '255.0.0.0')
        self.config_parser.set('agent', 'CONPAAS_HOME', IPOP_CONF_DIR)
        self.config_parser.set('agent', 'IPOP_BOOTSTRAP_NODES', bootstrap_nodes)
        ipop.configure_conpaas_node(self.config_parser)
        dest_file = os.path.join(IPOP_CONF_DIR, 'bootstrap.config')
        expected = ["brunet." + node for node in bootstrap_nodes.split()]
        self._check_bootstrap_nodes(dest_file, expected)

if __name__ == "__main__":
    unittest.main()
