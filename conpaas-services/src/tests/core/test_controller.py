import unittest
from ConfigParser import ConfigParser

from conpaas.core import controller
from conpaas.core.clouds.dummy import DummyCloud

import os
import mock
import logging
from netaddr import IPNetwork


CONPAAS_HOME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
        '..', '..', '..')

def config_parser():
    config_parser = ConfigParser()
    config_parser.add_section('manager')
    config_parser.set('manager', 'CREDIT_URL', 'http://example.org:443')
    config_parser.set('manager', 'TERMINATE_URL', 'http://example.org:443')
    config_parser.set('manager', 'CONPAAS_HOME', CONPAAS_HOME)
    config_parser.set('manager', 'SERVICE_ID', '1')
    config_parser.set('manager', 'USER_ID', '1')
    config_parser.set('manager', 'APP_ID', '1')
    config_parser.set('manager', 'CA_URL', 'http://example.org:443')
    return config_parser

def mock_post(hostname, port, path, params):
    return None, '{ "error": false }'

def mock_get_certificate(self):
    return { 'ca_cert': 'ca_cert',
             'key': 'key',
             'cert': 'cert' }

class TestController(unittest.TestCase):

    def setUp(self):
        self.config_parser = config_parser()
        self.controller = None

    def tearDown(self):
        if self.controller is None:
            return
            
        rmap = self.controller._Controller__reservation_map
        for reservation_timer in rmap.values():
            reservation_timer.stop()

    def __get_dummy_controller(self):
        self.config_parser.add_section('iaas')
        self.config_parser.set('iaas', 'DRIVER', 'dummy')

        return controller.Controller(self.config_parser)

    def test_controller_init(self):
        self.controller = controller.Controller(self.config_parser)

        self.assertEquals('agent', self.controller.role)

        self.assertEquals(None, self.controller._Controller__ipop_base_ip)
        self.assertEquals(None, self.controller._Controller__ipop_netmask)
        self.assertEquals(None, self.controller._Controller__ipop_subnet)

        self.assertEquals(None, self.controller._Controller__default_cloud)

    def test_controller_init_ipop(self):
        self.config_parser.set('manager', 'IPOP_BASE_IP', '127.0.0.0')
        self.config_parser.set('manager', 'IPOP_NETMASK', '255.0.0.0')
        self.config_parser.set('manager', 'IPOP_SUBNET', '127.0.0.0/24')

        self.controller = controller.Controller(self.config_parser)

        self.assertEquals('127.0.0.0', 
            self.controller._Controller__ipop_base_ip)
        self.assertEquals('255.0.0.0', 
            self.controller._Controller__ipop_netmask)
        self.assertEquals(IPNetwork('127.0.0.0/24'), 
            self.controller._Controller__ipop_subnet)

    def test_controller_init_iaas(self):
        self.controller = self.__get_dummy_controller()

        self.failUnless(isinstance(self.controller._Controller__default_cloud,
                        DummyCloud))

    def test_controller_init_iaas_multicloud(self):
        # default cloud
        self.config_parser.add_section('iaas')
        self.config_parser.set('iaas', 'DRIVER', 'dummy')

        # additional cloud
        self.config_parser.set('iaas', 'OTHER_CLOUDS', 'dummy2')
        self.config_parser.add_section('dummy2')
        self.config_parser.set('dummy2', 'DRIVER', 'dummy')

        self.controller = controller.Controller(self.config_parser)

        clouds = self.controller._Controller__available_clouds

        self.assertEquals(2, len(clouds))

    def test_get_available_ipop_address(self):
        self.config_parser.set('manager', 'IPOP_BASE_IP', '127.0.0.0')
        self.config_parser.set('manager', 'IPOP_NETMASK', '255.0.0.0')
        self.config_parser.set('manager', 'IPOP_SUBNET', '127.0.0.0/24')

        self.controller = controller.Controller(self.config_parser)

        self.assertEquals('127.0.0.3', 
            self.controller.get_available_ipop_address())

    def test_create_nodes_no_credit(self):
        self.controller = self.__get_dummy_controller()

        # our https_post to deduct_credit will fail
        self.assertRaises(Exception, self.controller.create_nodes, 
            1, lambda x,y: True, '5555') 

    # patch https_post to pretend we have enough credit
    @mock.patch('conpaas.core.controller.https.client.https_post', mock_post)
    def test_create_nodes(self):
        self.config_parser.add_section('iaas')
        self.config_parser.set('iaas', 'DRIVER', 'dummy')

        self.config_parser.set('manager', 'TYPE', 'mysql')
        #self.config_parser.set('manager', 'IPOP_BASE_IP', '127.0.0.0')
        #self.config_parser.set('manager', 'IPOP_NETMASK', '255.0.0.0')
        #self.config_parser.set('manager', 'IPOP_SUBNET', '127.0.0.0/24')
        
        self.controller = controller.Controller(self.config_parser)

        nodes = self.controller.create_nodes(count=2, 
                                             test_agent=lambda x, y: True, 
                                             port='5555',
                                             inst_type='small')

        self.assertEquals('127.0.0.3', nodes[0].ip)

    def test_delete_nodes(self):
        self.controller = self.__get_dummy_controller()

        class Node:
            id = 1
            cloud_name = 'iaas'

        nodes = [ Node ]

        self.assertEquals(None, self.controller.delete_nodes(nodes))

    def test_list_vms(self):
        self.controller = self.__get_dummy_controller()

        vms = self.controller.list_vms()

        self.assertEquals(2, len(vms))
        self.assertEquals('127.0.0.1', vms[0].ip)
        
    @mock.patch('conpaas.core.controller.Controller._get_certificate', 
        mock_get_certificate)
    def test_generate_context(self):
        self.config_parser.add_section('iaas')
        self.config_parser.set('iaas', 'DRIVER', 'dummy')

        self.config_parser.set('manager', 'BOOTSTRAP', 'test')
        self.config_parser.set('manager', 'MY_IP', '127.0.0.1')
        self.config_parser.set('manager', 'IPOP_BASE_IP', '127.0.0.0')
        self.config_parser.set('manager', 'IPOP_NETMASK', '255.0.0.0')
        self.config_parser.set('manager', 'IPOP_SUBNET', '127.0.0.0/24')

        self.controller = controller.Controller(self.config_parser)

        self.assertEquals(None, self.controller.get_clouds()[0]._context)

        self.controller.generate_context('mysql')

        self.failUnless('MySQL_configuration' in 
            self.controller._Controller__default_cloud._context)

    @mock.patch('conpaas.core.controller.Controller._get_certificate', 
        mock_get_certificate)
    def test_generate_context_with_cloud(self):
        self.config_parser.add_section('iaas')
        self.config_parser.set('iaas', 'DRIVER', 'dummy')

        self.config_parser.set('manager', 'BOOTSTRAP', 'test')
        self.config_parser.set('manager', 'MY_IP', '127.0.0.1')

        self.controller = controller.Controller(self.config_parser)

        self.controller.generate_context('mysql', 
            self.controller.get_cloud_by_name('iaas'))

        self.failUnless('MySQL_configuration' in 
            self.controller._Controller__default_cloud._context)

    def test_update_context(self):
        self.test_generate_context()

        self.failIf('username=test' in
            self.controller._Controller__default_cloud._context)

        self.controller.add_context_replacement({ 'mysql_username': 'test' })

        self.failUnless('username=test' in
            self.controller._Controller__default_cloud.get_context())

    def test_get_unknown_cloud_by_name(self):
        self.controller = self.__get_dummy_controller()
        self.assertRaises(Exception, self.controller.get_cloud_by_name, 'none')

    def test_config_cloud(self):
        self.controller = self.__get_dummy_controller()

        cloud = self.controller.get_cloud_by_name('iaas')
        self.assertEquals(None, 
            self.controller.config_cloud(cloud, {}))

    def test_config_clouds(self):
        self.controller = self.__get_dummy_controller()
        self.assertEquals(None, 
            self.controller.config_clouds({}))

    @mock.patch('conpaas.core.controller.https.client.https_post', mock_post)
    def test_force_terminate_service(self):
        self.controller = self.__get_dummy_controller()
        self.controller._Controller__force_terminate_service()

    def test_force_terminate_service_exception(self):
        self.controller = self.__get_dummy_controller()
        self.controller._Controller__force_terminate_service()

    def test_deduct_and_check_credit(self):
        self.controller = self.__get_dummy_controller()
        self.controller._Controller__deduct_and_check_credit(10)

class TestReservationTimer(unittest.TestCase):

    def setUp(self):
        self.timer = controller.ReservationTimer(nodes=[ 42 ], delay=0, 
            callback=lambda x: None, reservation_logger=logging, interval=0)

    def test_init(self):
        self.assertEquals(0, self.timer.delay)
        self.assertEquals([ 42 ], self.timer.nodes)

    def test_remove_node(self):
        self.failUnless(42 in self.timer.nodes)

        self.timer.remove_node(42)

        self.failIf(42 in self.timer.nodes)

    def test_run(self):
        self.timer.stop()
        self.timer.run()
        
if __name__ == "__main__":
    unittest.main()
