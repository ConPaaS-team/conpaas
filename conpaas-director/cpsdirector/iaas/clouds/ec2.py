# -*- coding: utf-8 -*-

"""
    conpaas.core.clouds.ec2
    =======================

    ConPaaS core: Amazon EC2 IaaS code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import math
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
        EC2Driver = get_driver(Provider.EC2)
        if self.ec2_region == "ec2.us-east-1.amazonaws.com":
            self.driver = EC2Driver(self.user, self.passwd, region='us-east-1')
        elif self.ec2_region == "ec2.us-west-1.amazonaws.com":
            self.driver = EC2Driver(self.user, self.passwd, region='us-west-1')
        elif self.ec2_region == "ec2.us-west-2.amazonaws.com":
            self.driver = EC2Driver(self.user, self.passwd, region='us-west-2')
        elif self.ec2_region == "ec2.eu-west-1.amazonaws.com":
            self.driver = EC2Driver(self.user, self.passwd, region='eu-west-1')
        elif self.ec2_region == "ec2.sa-east-1.amazonaws.com":
            self.driver = EC2Driver(self.user, self.passwd, region='sa-east-1')
        elif self.ec2_region == "ec2.ap-northeast-1.amazonaws.com":
            self.driver = EC2Driver(self.user, self.passwd, region='ap-northeast-1')
        elif self.ec2_region == "ec2.ap-southeast-1.amazonaws.com":
            self.driver = EC2Driver(self.user, self.passwd, region='ap-southeast-1')
        elif self.ec2_region == "ec2.ap-southeast-2.amazonaws.com":
            self.driver = EC2Driver(self.user, self.passwd, region='ap-southeast-2')
        else:
            raise Exception('Unknown EC2 region: %s' % self.ec2_region)

        self.connected = True

    def config(self, config_params={}, context=None):
        if 'inst_type' in config_params:
            self.size_id = config_params['inst_type']

        if context is not None:
            self._context = context

    def new_instances(self, nodes_info):
        if self.connected is False:
            self._connect()

        lc_nodes = []

        for node_info in nodes_info:

            if 'inst_type' in node_info and node_info['inst_type'] is not None:
                inst_type = node_info['inst_type']
            else:
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

            kwargs = {
                'size': size,
                'image': img,
                'name': node_info['name'],
                'ex_mincount': 1,
                'ex_maxcount': 1,
                'ex_securitygroup': self.sg,
                'ex_keyname': self.key_name,
                'ex_userdata': self.get_context(),
            }

            lc_node = self.driver.create_node(**kwargs)

            node_info['id'] = lc_node.id

            if 'volumes' in node_info:
                for vol in node_info['volumes']:
                    vol['vm_id'] = lc_node.id
                    vol['vol_name'] = vol['vol_name'] % vol
                    lc_volume = self.create_volume(vol['vol_size'], vol['vol_name'], vol['vm_id'])
                    vol['vol_id'] = lc_volume.id
                    class volume:
                        id = vol['vol_id']
                    class node:
                        id = vol['vm_id']
                    self.attach_volume(node, volume, vol['dev_name'])

            lc_nodes += [lc_node]

        nodes = self._create_service_nodes(lc_nodes, nodes_info)

        return nodes

    # def new_instances(self, count, name='conpaas', inst_type=None):
    #     if self.connected is False:
    #         self._connect()

    #     if inst_type is None:
    #         inst_type = self.size_id

    #     # available sizes
    #     sizes = self.driver.list_sizes()

    #     # available size IDs
    #     size_ids = [ size.id for size in sizes ]

    #     try:
    #         # index of the size we want
    #         size_idx = size_ids.index(inst_type)
    #     except ValueError:
    #         # size not found
    #         raise Exception("Requested size not found. '%s' not in %s" % (
    #             inst_type, size_ids))

    #     size = sizes[size_idx]

    #     img = NodeImage(self.img_id, '', None)

    #     kwargs = {
    #         'size': size,
    #         'image': img,
    #         'name': name,
    #         'ex_mincount': str(count),
    #         'ex_maxcount': str(count),
    #         'ex_securitygroup': self.sg,
    #         'ex_keyname': self.key_name,
    #         'ex_userdata': self.get_context(),
    #     }

    #     nodes = self._create_service_nodes(self.driver.create_node(**kwargs))

    #     if type(nodes) is list:
    #         return nodes

    #     return [ nodes ]

    def kill_instance(self, node):
        '''Kill a VM instance.

           @param node: A ServiceNode instance, where node.id is the
                        vm_id
        '''
        self.logger.debug('kill_instance(node=%s)' % node)

        if self.connected is False:
            self._connect()

        libcloud_node = node.as_libcloud_node()

        volumes = self.list_instance_volumes(libcloud_node)
        destroy_res = self.driver.destroy_node(libcloud_node)

        # for ec2 we can delete instances first and then volumes
        self.logger.debug('delete these volumes: %s' % volumes)
        for volume in volumes:
            max_trials = 20
            status=volume.extra['state']
            while status != 'available' and max_trials > 0:
                status=filter(lambda x: x.id==volume.id, self.driver.list_volumes())[0].extra['state']
                time.sleep(10)
                max_trials -= 1

            self.driver.destroy_volume(volume)        
        
        return destroy_res


    def create_volume(self, size, name, vm_id):

        # Make sure that we wait a little until the new node shows up
        while True:
            try:
                nodes = self.driver.list_nodes()
            except:
                self.logger.debug('[create_volume] list_nodes() failed,'
                                  ' sleeping 1 second')
                time.sleep(1)
                continue
            nodes = [ node for node in nodes if node.id == vm_id ]
            if nodes:
                node = nodes[0]
                break
            else:
                self.logger.debug('[create_volume] new node is not in'
                                  ' list_nodes(), sleeping 1 second')
                time.sleep(1)

        # We have to create the volume in the same availability zone as the
        # instance we want to attach it to. Let's find out the availability
        # zone we need to create this volume into.
        location = [ location for location in self.driver.list_locations() 
                if location.name == node.extra['availability'] ][0]

        # EBS expects volume size in GiB.
        size /= 1024.0
        size = int(math.ceil(size))

        self.logger.debug("self.driver.create_volume(%s, %s, %s)" % (size,
            name, location))

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

    def destroy_volume(self, volume):
        for _ in range(10):
            try:
                return self.driver.destroy_volume(volume)
            except Exception:
                self.logger.info("Volume %s cannot be destroyed yet" % volume)
                time.sleep(10)

        self.logger.exception("Volume %s still cannot be destroyed after timeout" %
                volume)

    def list_instance_volumes(self, instance):
        return filter(lambda x: x.extra['instance_id']==instance.id and x.extra['device']!='/dev/sda1', self.driver.list_volumes())
