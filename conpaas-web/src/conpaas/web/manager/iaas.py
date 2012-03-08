'''
Copyright (C) 2010-2011 Contrail consortium.

This file is part of ConPaaS, an integrated runtime environment 
for elastic cloud applications.

ConPaaS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ConPaaS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.


Created on Jan 21, 2011

@author: ielhelw
'''

import urlparse 
from string import Template

from conpaas.web.misc import get_ip_address

from libcloud.types import Provider, NodeState
from libcloud.providers import get_driver
from libcloud.base import NodeImage
from libcloud.drivers.opennebula import OpenNebulaNodeDriver
from libcloud.drivers.ec2 import EC2NodeDriver

import libcloud.security
libcloud.security.VERIFY_SSL_CERT = False


class IaaSClient:
  RUNNING = NodeState.RUNNING
  REBOOTING = NodeState.REBOOTING
  TERMINATED = NodeState.TERMINATED
  PENDING = NodeState.PENDING
  UNKNOWN = NodeState.UNKNOWN
  
  def __config_opennebula(self, iaas_config):
    if not iaas_config.has_option('iaas', 'OPENNEBULA_URL'): raise Exception('Configuration error: [iaas] OPENNEBULA_URL not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_USER'): raise Exception('Configuration error: [iaas] OPENNEBULA_USER not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_PASSWORD'): raise Exception('Configuration error: [iaas] OPENNEBULA_PASSWORD not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_IMAGE_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_IMAGE_ID not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_SIZE_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_SIZE_ID not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_NETWORK_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_NETWORK_ID not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_NETWORK_GATEWAY'): raise Exception('Configuration error: [iaas] OPENNEBULA_NETWORK_GATEWAY not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_NETWORK_NAMESERVER'): raise Exception('Configuration error: [iaas] OPENNEBULA_NETWORK_NAMESERVER not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_AGENT_USERDATA'): raise Exception('Configuration error: [iaas] OPENNEBULA_AGENT_USERDATA not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_VIRT_SOLUTION'): raise Exception('Configuration error: [iaas] OPENNEBULA_VIRT_SOLUTION not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_OS_ARCH'): raise Exception('Configuration error: [iaas] OPENNEBULA_OS_ARCH not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_OS_BOOTLOADER'): raise Exception('Configuration error: [iaas] OPENNEBULA_OS_BOOTLOADER not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_OS_ROOT'): raise Exception('Configuration error: [iaas] OPENNEBULA_OS_ROOT not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_DISK_TARGET'): raise Exception('Configuration error: [iaas] OPENNEBULA_DISK_TARGET not set')
    if not iaas_config.has_option('iaas', 'OPENNEBULA_CONTEXT_TARGET'): raise Exception('Configuration error: [iaas] OPENNEBULA_CONTEXT_TARGET not set')

    parsed = urlparse.urlparse(iaas_config.get('iaas', 'OPENNEBULA_URL'))
    self.scheme = parsed.scheme
    self.host = parsed.hostname
    self.port = parsed.port
    self.path = parsed.path
    self.username = iaas_config.get('iaas', 'OPENNEBULA_USER')
    self.password = iaas_config.get('iaas', 'OPENNEBULA_PASSWORD')
    
    self.img_id = iaas_config.get('iaas', 'OPENNEBULA_IMAGE_ID')
    self.size_id = iaas_config.get('iaas', 'OPENNEBULA_SIZE_ID')
    
    self.on_ex_network_id = iaas_config.get('iaas', 'OPENNEBULA_NETWORK_ID')
    self.on_ex_network_gateawy = iaas_config.get('iaas', 'OPENNEBULA_NETWORK_GATEWAY')
    self.on_ex_network_nameserver = iaas_config.get('iaas', 'OPENNEBULA_NETWORK_NAMESERVER')

    self.on_ex_virt_solution = iaas_config.get('iaas', 'OPENNEBULA_VIRT_SOLUTION')
    self.on_ex_os_arch = iaas_config.get('iaas', 'OPENNEBULA_OS_ARCH')
    self.on_ex_os_bootloader = iaas_config.get('iaas', 'OPENNEBULA_OS_BOOTLOADER')
    self.on_ex_os_root = iaas_config.get('iaas', 'OPENNEBULA_OS_ROOT')
    self.on_ex_disk_target = iaas_config.get('iaas', 'OPENNEBULA_DISK_TARGET')
    self.on_ex_context_target = iaas_config.get('iaas', 'OPENNEBULA_CONTEXT_TARGET')
    
    fd = open(iaas_config.get('iaas', 'OPENNEBULA_AGENT_USERDATA'), 'r')
    self.on_ex_agent_userdata_template = ''
    buf = fd.read()
    while len(buf) != 0:
      self.on_ex_agent_userdata_template += buf
      buf = fd.read()
    fd.close()
    
    self.on_ex_agent_userdata_template = Template(self.on_ex_agent_userdata_template).safe_substitute(SOURCE=self.bootstrap,
                                                                                 MANAGER_IP=get_ip_address('eth0'))
    ONDriver = get_driver(Provider.OPENNEBULA)
    self.driver = ONDriver(self.username, secret=self.password, secure=(self.scheme == 'https'), host=self.host, port=self.port)
  
  def __config_ec2(self, iaas_config):
    if not iaas_config.has_option('iaas', 'EC2_USER'): raise Exception('Configuration error: [iaas] EC2_USER not set')
    if not iaas_config.has_option('iaas', 'EC2_PASSWORD'): raise Exception('Configuration error: [iaas] EC2_PASSWORD not set')
    if not iaas_config.has_option('iaas', 'EC2_IMAGE_ID'): raise Exception('Configuration error: [iaas] EC2_IMAGE_ID not set')
    if not iaas_config.has_option('iaas', 'EC2_SIZE_ID'): raise Exception('Configuration error: [iaas] EC2_SIZE_ID not set')
    
    if not iaas_config.has_option('iaas', 'EC2_SECURITY_GROUP_NAME'): raise Exception('Configuration error: [iaas] EC2_SECURITY_GROUP_NAME not set')
    if not iaas_config.has_option('iaas', 'EC2_KEY_NAME'): raise Exception('Configuration error: [iaas] EC2_KEY_NAME not set')
    if not iaas_config.has_option('iaas', 'EC2_AGENT_USERDATA'): raise Exception('Configuration error: [iaas] EC2_AGENT_USERDATA not set')
    
    self.username = iaas_config.get('iaas', 'EC2_USER')
    self.password = iaas_config.get('iaas', 'EC2_PASSWORD')
    
    self.ec2_ex_securitygroup = iaas_config.get('iaas', 'EC2_SECURITY_GROUP_NAME')
    self.ec2_ex_keyname = iaas_config.get('iaas', 'EC2_KEY_NAME')
    
    fd = open(iaas_config.get('iaas', 'EC2_AGENT_USERDATA'), 'r')
    self.ec2_ex_agent_userdata = ''
    buf = fd.read()
    while len(buf) != 0:
      self.ec2_ex_agent_userdata += buf
      buf = fd.read()
    fd.close()
    
    self.ec2_ex_agent_userdata = Template(self.ec2_ex_agent_userdata).safe_substitute(SOURCE=self.bootstrap,
                                                                                 MANAGER_IP=get_ip_address('eth0'))
    
    self.img_id = iaas_config.get('iaas', 'EC2_IMAGE_ID')
    self.size_id = iaas_config.get('iaas', 'EC2_SIZE_ID')
    
    EC2Driver = get_driver(Provider.EC2_US_EAST)
    self.driver = EC2Driver(self.username, self.password)
  
  def __setdriver(self, iaas_config):
    if not iaas_config.has_option('iaas', 'DRIVER'): raise Exception('Configuration error: [iaas] DRIVER not set')
    drivername = iaas_config.get('iaas', 'DRIVER')
    if drivername == 'OPENNEBULA':
      self.__config_opennebula(iaas_config)
    elif drivername == 'EC2':
      self.__config_ec2(iaas_config)
    else:
      raise Exception('Configuration error: Invalid [iaas] DRIVER')
  
  def __init__(self, iaas_config):
    self.bootstrap = iaas_config.get('manager', 'BOOTSTRAP')
    self.__setdriver(iaas_config)
  
  def listVMs(self):
    nodes = self.driver.list_nodes()
    vms = {}
    for i in nodes:
      vms[i.id] = {'id': i.id,
        'state': i.state,
        'name': i.name,
        'ip': i.public_ip[0]}
    return vms
  
  def getVMInfo(self, vm_id):
    return self.listVMs()[vm_id]
  
  def newInstances(self, count):
    size = [ i for i in self.driver.list_sizes() if i.id == self.size_id ][0]
    img = NodeImage(self.img_id, '', None)
    kwargs = {'size': size,
              'image': img
              }
    nodes = []
    if isinstance(self.driver, OpenNebulaNodeDriver):
      kwargs['ex_network_id'] = self.on_ex_network_id
      kwargs['ex_network_gateawy'] = self.on_ex_network_gateawy
      kwargs['ex_network_nameserver'] = self.on_ex_network_nameserver
      kwargs['ex_virt_solution'] = self.on_ex_virt_solution
      kwargs['ex_os_arch'] = self.on_ex_os_arch
      kwargs['ex_os_bootloader'] = self.on_ex_os_bootloader
      kwargs['ex_os_root'] = self.on_ex_os_root
      kwargs['ex_disk_target'] = self.on_ex_disk_target
      kwargs['ex_context_target'] = self.on_ex_context_target	
      kwargs['ex_userdata'] = self.on_ex_agent_userdata_template.encode('hex')
      for _ in range(count):
        node = self.driver.create_node(name='conpaas', **kwargs)
        nodes.append({'id': node.id,
                      'state': node.state,
                      'name': node.name,
                      'ip': node.public_ip[0]})
    if isinstance(self.driver, EC2NodeDriver):
      kwargs['ex_mincount'] = str(count)
      kwargs['ex_maxcount'] = str(count)
      kwargs['ex_securitygroup'] = self.ec2_ex_securitygroup
      kwargs['ex_keyname'] = self.ec2_ex_keyname
      kwargs['ex_userdata'] = self.ec2_ex_agent_userdata
      instances = self.driver.create_node(name='conpaas', **kwargs)
      if count == 1: instances = [instances]
      for node in instances:
        nodes.append({'id': node.id,
                      'state': node.state,
                      'name': node.name,
                      'ip': node.public_ip[0]})
    return nodes
  
  
  def killInstance(self, vm_id):
    nodes = self.driver.list_nodes()
    for i in nodes:
      if i.id == vm_id:
        return self.driver.destroy_node(i)
    return False

