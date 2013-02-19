'''
Copyright (c) 2010-2012, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms,
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the Contrail consortium nor the
    names of its contributors may be used to endorse
    or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

import urlparse

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeImage

from .base import Cloud


class OpenNebulaCloud(Cloud):

    def __init__(self, cloud_name, iaas_config):
        Cloud.__init__(self, cloud_name)

        # required parameters to describe this cloud
        cloud_params = ['URL', 'USER', 'PASSWORD',
                        'IMAGE_ID', 'INST_TYPE',
                        'NET_ID', 'NET_GATEWAY',
                        'NET_NAMESERVER',
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
        self.net_ns = _get('NET_NAMESERVER')
        self.os_arch = _get('OS_ARCH')
        self.os_root = _get('OS_ROOT')
        self.disk_target = _get('DISK_TARGET')
        self.context_target = _get('CONTEXT_TARGET')

        self.cpu = None
        self.mem = None

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
                               api_version='2.2')

        self.connected = True

    def set_context_template(self, cx):
        self.cx_template = cx
        self.cx = cx.encode('hex')

    def config(self, config_params={}, context=None):
        '''Sets some configuration parameters (Overrides the default ones).

           @keyword    inst_type:   (optional)
                                    Id of the node type of this driver
           @type       inst_type:   int

           @keyword    cpu:   Number of cpus for the VM. (optional)
           @type       cpu:   int

           @keyword    memory:  Quantity of RAM. (optional)
           @type       memory:  int

           @param      context: The context file

        '''

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

    def new_instances(self, count, name='conpaas'):
        '''Asks the provider for new instances.

           @param    count:   Id of the node type of this driver (optional)

        '''
        if self.connected is False:
            self._connect()

        kwargs = {}

        # 'NAME'
        kwargs['name'] = name

        # 'INSTANCE_TYPE'
        kwargs['size'] = [i for i in self.driver.list_sizes()
                          if i.name == self.inst_type][0]

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
        context['NAMESERVER'] = self.net_ns
        context['USERDATA'] = self.cx
        context['TARGET'] = self.context_target
        kwargs['context'] = context

        return [self._create_service_nodes(self.driver.
                create_node(**kwargs), False) for _ in range(count)]
