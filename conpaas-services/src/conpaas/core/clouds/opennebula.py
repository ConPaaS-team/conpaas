# -*- coding: utf-8 -*-

"""
    conpaas.core.clouds.opennebula
    ==============================

    ConPaaS core: OpenNebula IaaS code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import urlparse

from ConfigParser import NoOptionError

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeImage

from .base import Cloud

DEFAULT_API_VERSION = '2.2'

class OpenNebulaCloud(Cloud):

    def __init__(self, cloud_name, iaas_config):
        Cloud.__init__(self, cloud_name)

        # required parameters to describe this cloud
        cloud_params = ['URL', 'USER', 'PASSWORD',
                        'IMAGE_ID', 'INST_TYPE',
                        'NET_ID', 'NET_GATEWAY',
                        'NET_NETMASK', 'NET_NAMESERVER',
                        'OS_ARCH',
                        'OS_ROOT',
                        'DISK_TARGET',
                        'CONTEXT_TARGET']

        self._check_cloud_params(iaas_config, cloud_params)

        def _get(param):
            return iaas_config.get(cloud_name, param)

        self.url = _get('URL')
        self.user = _get('USER')
        self.passwd = _get('PASSWORD')
        self.img_id = _get('IMAGE_ID')
        self.inst_type = _get('INST_TYPE')
        self.net_id = _get('NET_ID')
        self.net_gw = _get('NET_GATEWAY')
        self.net_nm = _get('NET_NETMASK')
        self.net_ns = _get('NET_NAMESERVER')
        self.os_arch = _get('OS_ARCH')
        self.os_root = _get('OS_ROOT')
        self.disk_target = _get('DISK_TARGET')
        self.context_target = _get('CONTEXT_TARGET')

        try:
            self.api_version = _get('OPENNEBULA_VERSION')
        except NoOptionError:
            self.api_version = DEFAULT_API_VERSION

        self.cpu = None
        self.mem = None
        
        self.logger.info('OpenNebula cloud ready. API_VERSION=%s' % 
            self.api_version)

    def get_cloud_type(self):
        return 'opennebula'

    def _connect(self):
        """connect to opennebula cloud"""
        parsed = urlparse.urlparse(self.url)
        ONDriver = get_driver(Provider.OPENNEBULA)

        self.driver = ONDriver(self.user,
                               secret=self.passwd,
                               secure=(parsed.scheme == 'https'),
                               host=parsed.hostname,
                               port=parsed.port,
                               api_version=self.api_version)

        self.connected = True

    def set_context_template(self, cx):
        self.cx_template = cx
        self.cx = cx.encode('hex')

    def config(self, config_params={}, context=None):
        if 'inst_type' in config_params:
            self.inst_type = config_params['inst_type']

        if 'cpu' in config_params:
            self.cpu = config_params['cpu']

        if 'mem' in config_params:
            self.mem = config_params['mem']

        if context is not None:
            self.cx = context.encode('hex')

    def list_vms(self):
        return Cloud.list_vms(self, False)

    def list_instace_types(self):
        return self.inst_types

    def new_instances(self, count, name='conpaas', inst_type=None):
        '''Asks the provider for new instances.

           @param    count:   Id of the node type of this driver (optional)

        '''
        if self.connected is False:
            self._connect()

        kwargs = {}

        # 'NAME'
        kwargs['name'] = name

        # 'INSTANCE_TYPE'
        if inst_type is None:
            inst_type = self.inst_type

        # available sizes
        sizes = self.driver.list_sizes()

        # available size names
        size_names = [ size.name for size in sizes ]

        try:
            # index of the size we want
            size_idx = size_names.index(inst_type)
        except ValueError:
            # size not found
            raise Exception("Requested size not found. '%s' not in %s" % (
                inst_type, size_names))

        kwargs['size'] = sizes[size_idx]

        # 'CPU'
        if self.cpu is not None:
            kwargs['cpu'] = self.cpu

        # 'MEM'
        if self.mem is not None:
            kwargs['mem'] = self.mem

        # 'OS'
        kwargs['os_arch'] = self.os_arch
        kwargs['os_root'] = self.os_root

        # 'DISK'
        kwargs['image'] = NodeImage(self.img_id, '', None)
        kwargs['disk_target'] = self.disk_target

        # 'NIC': str(network.id) is how libcloud gets the network ID. Let's
        # create an object just like that and pass it in the 'networks' kwarg
        class OneNetwork(object):
            def __str__(self):
                return str(self.id)
        network = OneNetwork()
        network.id = self.net_id
        network.address = None
        kwargs['networks'] = network

        # 'CONTEXT'
        context = {}
        context['HOSTNAME'] = '$NAME'
        context['IP_PUBLIC'] = '$NIC[IP]'
        context['IP_GATEWAY'] = self.net_gw
        context['NETMASK'] = self.net_nm
        context['NAMESERVER'] = self.net_ns
        context['USERDATA'] = self.cx
        context['TARGET'] = self.context_target
        kwargs['context'] = context

        return [self._create_service_nodes(self.driver.
                create_node(**kwargs), False) for _ in range(count)]
