# -*- coding: utf-8 -*-

"""
    conpaas.core.clouds.dummy
    =========================

    ConPaaS core: Dummy cloud IaaS code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from .base import Cloud


class DummyCloud(Cloud):
    '''Support for "dummy" clouds'''

    def __init__(self, cloud_name, iaas_config):
        Cloud.__init__(self, cloud_name)

    def get_cloud_type(self):
        return 'dummy'

    def _connect(self):
        '''Connect to dummy cloud'''
        DummyDriver = get_driver(Provider.DUMMY)
        self.driver = DummyDriver(0)
        self.connected = True

    def config(self, config_params={}, context=None):
        if context is not None:
            self._context = context

    def new_instances(self, count, name='conpaas', inst_type=None):
        if not self.connected:
            self._connect()

        return [self._create_service_nodes(self.driver.create_node(), False)
                for _ in range(count)]

    def kill_instance(self, node):
        '''Kill a VM instance.

        @param node: A ServiceNode instance, where node.id is the vm_id
        '''
        if self.connected is False:
            raise Exception('Not connected to cloud')

        # destroy_node does not work properly in libcloud's dummy
        # driver. Just return True.
        return True
