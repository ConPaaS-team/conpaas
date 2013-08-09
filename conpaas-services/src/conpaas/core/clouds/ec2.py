# -*- coding: utf-8 -*-

"""
    conpaas.core.clouds.ec2
    =======================

    ConPaaS core: Amazon EC2 IaaS code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import time

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeImage

from .base import Cloud


class EC2Cloud(Cloud):

    def __init__(self, cloud_name, iaas_config):
        Cloud.__init__(self, cloud_name)

        cloud_params = ['USER', 'PASSWORD',
                        'IMAGE_ID', 'SIZE_ID',
                        'SECURITY_GROUP_NAME',
                        'KEY_NAME', 'REGION']

        self._check_cloud_params(iaas_config, cloud_params)

        # TODO: multiple img_id, key_name?
        self.user = iaas_config.get(cloud_name, 'USER')
        self.passwd = iaas_config.get(cloud_name, 'PASSWORD')
        self.img_id = iaas_config.get(cloud_name, 'IMAGE_ID')
        self.size_id = iaas_config.get(cloud_name, 'SIZE_ID')
        self.key_name = iaas_config.get(cloud_name, 'KEY_NAME')
        self.sg = iaas_config.get(cloud_name, 'SECURITY_GROUP_NAME')
        self.ec2_region = iaas_config.get(cloud_name, 'REGION')

        self.logger.info('EC2 cloud ready. REGION=%s' % self.ec2_region)

    def get_cloud_type(self):
        return 'ec2'

    # connect to ec2 cloud
    def _connect(self):
        if self.ec2_region == "ec2.us-east-1.amazonaws.com":
            EC2Driver = get_driver(Provider.EC2_US_EAST)
        elif self.ec2_region == "ec2.us-west-2.amazonaws.com":
            EC2Driver = get_driver(Provider.EC2_US_WEST_OREGON)
        elif self.ec2_region == "ec2.eu-west-1.amazonaws.com":
            EC2Driver = get_driver(Provider.EC2_EU_WEST)
        else:
            raise Exception('Unknown EC2 region: %s' % self.ec2_region)

        self.driver = EC2Driver(self.user,
                                self.passwd)
        self.connected = True

    def config(self, config_params={}, context=None):
        if 'inst_type' in config_params:
            self.size_id = config_params['inst_type']

        if context is not None:
            self._context = context

    def new_instances(self, count, name='conpaas', inst_type=None):
        if self.connected is False:
            self._connect()

        if inst_type is None:
            inst_type = self.size_id

        # available sizes
        sizes = self.driver.list_sizes()

        # available size IDs
        size_ids = [ size.id for size in sizes ] 

        try:
            # index of the size we want
            size_idx = size_ids.index(inst_type)
        except ValueError:
            # size not found
            raise Exception("Requested size not found. '%s' not in %s" % (
                inst_type, size_ids)) 

        size = sizes[size_idx]

        img = NodeImage(self.img_id, '', None)
        kwargs = {'size': size,
                  'image': img,
                  'name': name}
        kwargs['ex_mincount'] = str(count)
        kwargs['ex_maxcount'] = str(count)
        kwargs['ex_securitygroup'] = self.sg
        kwargs['ex_keyname'] = self.key_name
        kwargs['ex_userdata'] = self.get_context()

        nodes = self._create_service_nodes(self.driver.create_node(**kwargs))

        if type(nodes) is list:
            return nodes

        return [ nodes ]

    def create_volume(self, size, name):
        location = self.driver.list_locations()[0]
        return self.driver.create_volume(size, name, location)

    def attach_volume(self, node, volume, device):
        for _ in range(10):
            try:
                return self.driver.attach_volume(node, volume, device)
            except Exception:
                self.logger.info("Volume %s not available yet" % volume)
                time.sleep(10)

        self.logger.exception("Volume %s NOT available after timeout" %
                volume)

