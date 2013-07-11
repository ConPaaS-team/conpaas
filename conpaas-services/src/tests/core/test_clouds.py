
import unittest
from ConfigParser import ConfigParser

from conpaas.core.clouds import base
from conpaas.core.clouds import dummy

class MockPrivateIP(object):
    address = '127.0.0.1'

class MockPublicIP(object):
    address = '192.168.0.1'

class MockNodeNoPublic(object):
    id = 1
    private_ips = [ MockPrivateIP ]
    public_ips = []

    def as_libcloud_node(self):
        return None

class MockNode(MockNodeNoPublic):
    id = 2
    public_ips = [ MockPublicIP ]
    private_ips = []

class MockDriver(object):
    def list_nodes(self):
        return [ MockNode, MockNodeNoPublic ]

    def destroy_node(self, node):
        return True

class TestCloudsBase(unittest.TestCase):

    def setUp(self):
        self.cloud = base.Cloud('test_cloud')

    def test_cloud_init(self):
        self.assertEquals('test_cloud', self.cloud.cloud_name)
        self.assertFalse(self.cloud.connected)
        self.assertEquals(None, self.cloud.driver)
        self.assertEquals(None, self.cloud._context)

    def test_get_cloud_name(self):
        self.assertEquals('test_cloud', self.cloud.get_cloud_name())

    def test_check_cloud_params(self):
        config_parser = ConfigParser()
        config_parser.add_section('test_cloud')
        config_parser.set('test_cloud', 'OPTION1', 'VALUE1')
        config_parser.set('test_cloud', 'OPTION2', 'VALUE2')

        self.assertEquals(None, self.cloud._check_cloud_params(
            config_parser, [ 'OPTION1', 'OPTION2' ]))

        # Needed to get a meaningful error message in Exception
        self.cloud.get_cloud_type = lambda: 'test'

        # missing parameter
        self.assertRaises(Exception, self.cloud._check_cloud_params,
            config_parser, [ 'OPTION1', 'OPTION2', 'OPTION3' ])

        expected = 'Missing test config param OPTION3 for test_cloud'
        try:
            self.cloud._check_cloud_params(config_parser, 
                [ 'OPTION1', 'OPTION2', 'OPTION3' ])
        except Exception, err:
            self.assertEquals(expected, err.message)

        # empty parameter
        config_parser.set('test_cloud', 'OPTION3', '')

        self.assertRaises(Exception, self.cloud._check_cloud_params,
            config_parser, [ 'OPTION1', 'OPTION2', 'OPTION3' ])

        expected = 'Empty test config param OPTION3 for test_cloud'
        try:
            self.cloud._check_cloud_params(config_parser, 
                [ 'OPTION1', 'OPTION2', 'OPTION3' ])
        except Exception, err:
            self.assertEquals(expected, err.message)

    def test_connect(self):
        self.assertRaises(NotImplementedError, self.cloud._connect)

    def test_get_cloud_type(self):
        self.assertRaises(NotImplementedError, self.cloud.get_cloud_type)

    def test_get_context(self):
        self.assertEquals(self.cloud._context, self.cloud.get_context())

    def test_set_context(self):
        self.cloud.set_context(self.cloud._context)
        self.assertEquals(self.cloud._context, self.cloud.get_context())

    def test_config(self):
        self.assertRaises(NotImplementedError, self.cloud.config, None, None)

    def test_list_vms(self):
        # _connect is not implemented in base.Cloud
        self.assertRaises(NotImplementedError, self.cloud.list_vms)

        self.cloud.connected = True

        self.cloud.driver = MockDriver()
        vms = self.cloud.list_vms()
        self.assertEquals("192.168.0.1", vms[0].ip)

    def test_new_instances(self):
        self.assertRaises(NotImplementedError, self.cloud.new_instances, None)

    def test_create_service_nodes(self):
        self.assertEquals([], self.cloud._create_service_nodes([]))

        node = self.cloud._create_service_nodes(MockNode)
        self.assertEquals("192.168.0.1", node.ip)

        node = self.cloud._create_service_nodes(MockNode, False)
        self.assertEquals("192.168.0.1", node.ip)

    def test_kill_instance(self):
        # _connect is not implemented in base.Cloud
        self.assertRaises(NotImplementedError, self.cloud.kill_instance, None)

        self.cloud.connected = True

        self.cloud.driver = MockDriver()
        self.failUnless(self.cloud.kill_instance(MockNode()))

class TestCloudDummy(TestCloudsBase):

    def setUp(self):
        self.cloud = dummy.DummyCloud('test_cloud', None)

    def test_get_cloud_type(self):
        self.assertEquals('dummy', self.cloud.get_cloud_type())

    def test_config(self):
        self.cloud.config(context={})
        self.assertEquals({}, self.cloud._context)

    def test_connect(self):
        self.failIf(self.cloud.connected)

        self.cloud._connect()

        self.failUnless(self.cloud.connected)

    def test_new_instances(self):
        new_instances = self.cloud.new_instances(2)
        self.assertEquals(2, len(new_instances))

        self.assertEquals('127.0.0.3', new_instances[0].ip)

    def test_list_vms(self):
        vms = self.cloud.list_vms()
        self.assertEquals("127.0.0.1", vms[0].ip)

    def test_kill_instance(self):
        # Trying to kill an instance without being connected should raise an
        # exception
        self.assertRaises(Exception, self.cloud.kill_instance, None)

        self.cloud._connect()

        self.failUnless(self.cloud.kill_instance(MockNode()))

if __name__ == "__main__":
    unittest.main()
