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


Created on Jan 21, 2011

@author: ielhelw, aaasz
'''

import urlparse 
from string import Template

from libcloud.compute.types import Provider, NodeState
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeImage

import libcloud.security
libcloud.security.VERIFY_SSL_CERT = False

from .base import Cloud

from conpaas.core.node import ServiceNode

class EC2Cloud(Cloud):

    # connect to ec2 cloud 
    def __init__(self, cloud_name, iaas_config):
        Cloud.__init__(self, cloud_name)

        self.connected = False
        self.cx_template = None
 
        cloud_params = ['USER', 'PASSWORD',    \
                        'IMAGE_ID', 'SIZE_ID', \
                        'SECURITY_GROUP_NAME', \
                        'KEY_NAME']

        for field in cloud_params:
            if not iaas_config.has_option(cloud_name, field)\
              or iaas_config.get(cloud_name, field) == '':
                raise Exception('Missing ec2 config param %s for %s' % \
                                               (field, cloud_name))

        # TODO: multiple img_id, key_name?
        self.user = iaas_config.get(cloud_name, 'USER')
        self.passwd = iaas_config.get(cloud_name, 'PASSWORD')
        self.img_id = iaas_config.get(cloud_name, 'IMAGE_ID')
        self.size_id = iaas_config.get(cloud_name, 'SIZE_ID')
        self.key_name = iaas_config.get(cloud_name, 'KEY_NAME')
        self.sg = iaas_config.get(cloud_name, 'SECURITY_GROUP_NAME')
        self.ec2_region = iaas_config.get(cloud_name, 'REGION')

    def get_cloud_type(self):
        return 'ec2'

    # connect to ec2 cloud 
    def _connect(self):
        if self.ec2_region == "ec2.us-east-1.amazonaws.com":
            EC2Driver = get_driver(Provider.EC2_US_EAST)
        elif self.ec2_region == "ec2.us-west-2.amazonaws.com":
            EC2Driver = get_driver(Provider.EC2_US_WEST_OREGON)
        elif  self.ec2_region == "ec2.eu-west-1.amazonaws.com":
            EC2Driver = get_driver(Provider.EC2_EU_WEST)

        self.driver = EC2Driver(self.user, \
                                self.passwd)
        self.connected = True

    # set the context template (i.e. without replacing anything in it)
    def set_context_template(self, cx):
        self.cx_template = cx
        self.cx = cx

    def get_context_template(self):
        return self.cx_template

    # set some VM specific parameters (TODO: what else?)
    def config(self, config_params={}, context=None):
        if 'inst_type' in config_params:  
            self.size_id = config_params['inst_type']

        if context != None:
            self.cx = context
   
    def list_vms(self):
        nodes = self.driver.list_nodes()
        vms = {}
        for i in nodes:
            if i.public_ips:
                ip = i.public_ips[0]
            else:
                ip = ''   
            if i.private_ips:
                private_ip = i.private_ips[0]
            else:
                private_ip = ''   
            vms[i.id] = {'id': i.id, \
                         'state': i.state, \
                         'name': i.name, \
                         'ip': ip,
                         'private_ip': private_ip}
        return vms

    def new_instances(self, count):
        if self.connected == False:
            self._connect()

        size = [ i for i in self.driver.list_sizes() \
                   if i.id == self.size_id ][0]
        img = NodeImage(self.img_id, '', None)
        kwargs = {'size': size,
                  'image': img
                }
        nodes = []
        kwargs['ex_mincount'] = str(count)
        kwargs['ex_maxcount'] = str(count)
        kwargs['ex_securitygroup'] = self.sg
        kwargs['ex_keyname'] = self.key_name
        kwargs['ex_userdata'] = self.cx
        instances = self.driver.create_node(name='conpaas', **kwargs)
        if count == 1:
            instances = [instances]
        for node in instances:
            if node.public_ips:
                ip = node.public_ips[0]
            else:
                ip = ''   
            if node.private_ips:
                private_ip = node.private_ips[0]
            else:
                private_ip = ''   
            nodes.append(ServiceNode(node.id, ip, private_ip, self.cloud_name))
        return nodes

    def kill_instance(self, node):
        '''Kill a VM instance.

           @param node: A ServiceNode instance, where node.id is the
                        vm_id
        '''
        if self.connected == False:
            raise Exception('Not connected to cloud')
        return self.driver.destroy_node(node)

