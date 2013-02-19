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

Created on Jan 25, 2012

@file
'''

from conpaas.core.node import ServiceNode


class Cloud:
    ''' Abstract Cloud '''

    def __init__(self, cloud_name):
        #TODO: it shouldn't be cloud_name == config file section name
        self.cloud_name = cloud_name
        self.connected = False
        self.driver = None
        self.cx_template = None
        self.cx = None

    def get_cloud_name(self):
        return self.cloud_name

    def _check_cloud_params(self, iaas_config, cloud_params=[]):
        for field in cloud_params:
            if (
                not iaas_config.has_option(self.cloud_name, field)
                or iaas_config.get(self.cloud_name, field) == ''
            ):
                raise Exception('Missing %s config param %s for %s' %
                                (self.get_cloud_type, field, self.cloud_name))

    def _connect(self):
        '''
        _connect is the method used to set the driver and connect to the cloud

        '''
        raise NotImplementedError(
            '_connect not implemented for this cloud driver')

    def get_cloud_type(self):
        raise NotImplementedError(
            'get_cloud_type not implemented for this cloud driver')

    def get_context_template(self):
        return self.cx_template

    def set_context_template(self, cx):
        """
        Set the context template (i.e. without replacing anything in it)
        """
        self.cx_template = cx
        self.cx = cx

    def config(self, config_params, context):
        raise NotImplementedError(
            'config not implemented for this cloud driver')

    def list_vms(self, has_private_ip=True):
        '''
        lists the service nodes in the cloud instances

        @return vms: Dict{id,state,name,ip,private_ip}

        '''
        return [serviceNode for serviceNode in
                self._create_service_nodes(self.driver.list_nodes())]

    def new_instances(self, count, name='conpaas'):
        raise NotImplementedError(
            'new_instances not implemented for this cloud driver')

    def _create_service_nodes(self, instances, has_private_ip=True):
        '''
        creates a list of ServiceNode

        @param  instances: List of nodes provide by the driver or a single node
        @type   instances: L{libcloud.compute.Node} or C{libcloud.compute.Node}

        @param  has_private_ip: some instances only need the public ip
        @type   has_private_ip: C{bool}

        '''
        try:
            return [self.__create_one_service_node(node, has_private_ip)
                    for node in instances]
        except TypeError:
            return self.__create_one_service_node(instances, has_private_ip)

    def __create_one_service_node(self, instance, has_private_ip=True):
        '''
        creates a single ServiceNode

        @param  instance: node provided by the driver
        @type   instance: C{libcloud.compute.Node}

        @param  has_private_ip: some instances only need the public ip
        @type   has_private_ip: C{bool}

        '''
        ip, private_ip = self.__get_ips(instance, has_private_ip)
        return ServiceNode(instance.id, ip, private_ip, self.cloud_name)

    def __get_ips(self, instance, has_private_ip):
        if instance.public_ips:
            ip = instance.public_ips[0]
        else:
            ip = ''
        if has_private_ip:
            if instance.private_ips:
                private_ip = instance.private_ips[0]
            else:
                private_ip = ''
        else:
            private_ip = ip
        return ip, private_ip

    def kill_instance(self, node):
        '''Kill a VM instance.

           @param node: A ServiceNode instance, where node.id is the
                        vm_id
        '''
        if self.connected is False:
            raise Exception('Not connected to cloud')
        return self.driver.destroy_node(node)
