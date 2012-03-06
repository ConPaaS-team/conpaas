'''
Created on Jan 21, 2011

@author: ielhelw
'''

import string
import urlparse
import oca

from socket import gethostbyname

from libcloud.compute.types import Provider, NodeState
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeImage, NodeSize
from libcloud.compute.drivers.opennebula import OpenNebulaNodeDriver
from libcloud.compute.drivers.ec2 import EC2NodeDriver

import libcloud.security
from libcloud.compute.base import NodeDriver
from conpaas.log import create_logger
from random import Random
import random
from conpaas.mysql.utils.log import get_logger_plus
libcloud.security.VERIFY_SSL_CERT = False

logger, flog, mlog = get_logger_plus(__name__)

'''
For Unit testing
'''
class DummyNode():
    
    class DummyNic():
        
        def __init__(self, ip):
            self.ip = ip
            
    class DummyTemplate():
        
        def __init__(self):
            self.nics = {}
            self.nics[0] = DummyNode.DummyNic("127.0.0.1")
    
    def __init__(self, id, str_state, name, template, ip):
        logger.debug("Entering __init__")
        self.id = id
        self.vmid=id
        self.str_state = str_state
        self.name = name
        self.template = self.DummyTemplate()    
        self.isRunningMySQL = True  
        self.ip = ip
        self.port = 60000
        self.state = str_state   

class OneXmlrpcNode():
    
    def __init__(self, node):
        self.id = node.id
        self.state = node.str_state
        self.name = node.name
        self.template = node.template
        self.public_ip = node.template.nics[0].ip

'''
    Dummy driver for ONE - used for testing.
'''
class DummyONEDriver(NodeDriver):
    
    nodes = {}
        
    def get_dummy_list(self):                        
        return self.nodes
    
    def __init__(self, uname, password, scheme, host, port):        
        self.client = None
        node1 = DummyNode(1, "conpaas01", NodeState.RUNNING, "UnitTest", "127.0.0.1");
        node2 = DummyNode(2, "conpaas01", NodeState.RUNNING, "UnitTest", "127.0.0.1");
        node3 = DummyNode(3, "conpaas01", NodeState.RUNNING, "UnitTest", "127.0.0.1");               
        self.nodes[node1.id] = node1
        self.nodes[node2.id] = node2
        self.nodes[node3.id] = node3

    def list_nodes(self):        
        logger.debug("Dummy VMs:")
        #nodes={}        
        retnodes={}        
        for i in self.nodes:            
            logger.debug( str(self.nodes[i].id) + ": " +str(self.nodes[i].name) + ", " +str(self.nodes[i].str_state))
            retnodes[self.nodes[i].id]=OneXmlrpcNode(self.nodes[i])
        return retnodes            
        
    '''
        Create new node.
    '''
    def create_node(self, **kwargs):
        logger.debug("Entering create_node")
        if kwargs['function'] == 'agent':
            logger.debug("creating agent")
            template='''NAME   = conpaassql-server
CPU    = 0.2
MEMORY = 512
   OS     = [
   arch = "i686",
   boot = "hd",
   root     = "hda" ]
DISK   = [
   image_id = "''' + str(kwargs['image'].id) + '''",
   bus = "scsi",
   readonly = "no" ]
NIC    = [ NETWORK_ID = '''+str(kwargs['ex_network_id'])+''' ]
GRAPHICS = [
  type="vnc"
  ]
CONTEXT = [
  target=sdc,
  files = '''+str(kwargs['ex_userdata_agent'])+'''
  ]
RANK = "- RUNNING_VMS"
'''
        elif kwargs['function'] == 'manager':
            logger.debug("creating manager")
            template='''NAME   = conpaassql-server
CPU    = 0.2
MEMORY = 512
   OS     = [
   arch = "i686",
   boot = "hd",
   root     = "hda" ]
DISK   = [
   image_id = "''' + str(kwargs['image'].id) + '''",
   bus = "scsi",
   readonly = "no" ]
NIC    = [ NETWORK_ID = '''+str(kwargs['ex_network_id'])+''' ]
GRAPHICS = [
  type="vnc"
  ]
CONTEXT = [
  target=sdc,
  files = '''+str(kwargs['ex_userdata_manager'])+''']
RANK = "- RUNNING_VMS"
'''
        else:
            logger.debug("creating")
            template='''NAME   = conpaassql_server
CPU    = 0.2
MEMORY = 512
   OS     = [
   arch = "i686",
   boot = "hd",
   root     = "hda" ]
DISK   = [
   image_id = "''' + str(kwargs['image'].id) + '''",
   bus = "scsi",
   readonly = "no" ]
NIC    = [ NETWORK_ID = '''+str(kwargs['ex_network_id'])+''' ]
GRAPHICS = [
  type="vnc"
  ]
RANK = "- RUNNING_VMS"
'''
        logger.debug('Provisioning VM:' + template)
        randid = random.randint(1,100)
        newnode = DummyNode(randid, "conpaas"+str(randid), NodeState.RUNNING, "UnitTest", "127.0.0.1");               
        self.nodes[newnode.id] = newnode
        logger.debug("Exiting create_node")
        return newnode.id

    '''
        Destroying ONE node with XML RPC.
    '''
    def destroy_node(self, id):
        logger.debug("Entering destroy_node with id " + str(id))
        del self.nodes[id]
        logger.debug("Exiting destroy_node")        
        
    def list_sizes(self, location=None):
        return [
          NodeSize(id=1,
                   name="small",
                   ram=None,
                   disk=None,
                   bandwidth=None,
                   price=None,
                   driver=self),
          NodeSize(id=2,
                   name="medium",
                   ram=None,
                   disk=None,
                   bandwidth=None,
                   price=None,
                   driver=self),
          NodeSize(id=3,
                   name="large",
                   ram=None,
                   disk=None,
                   bandwidth=None,
                   price=None,
                   driver=self),
        ]
        
'''
    XMLRPC driver for OpenNebula
'''
class OneXmlrpc(NodeDriver):
    
    def __init__(self, uname, password, scheme, host, port):        
        self.client = oca.Client(uname+":"+password, scheme+"://"+host+":"+str(port)+"/RPC2")
    
    @mlog
    def read_template(self, file):
        logger.debug("Reading the ONE image template from %s" % file )
        fin = open(file, "r")
        templatestr = fin.read()
        fin.close()        
        return string.Template(templatestr)
        
    @mlog
    def list_nodes(self):
        vm_pool=oca.VirtualMachinePool(self.client)
        vm_pool.info(-2)
        logger.debug("All VMs:")
        nodes={}        
        for i in vm_pool:            
            logger.debug( str(i.id) + ": " +str(i.name) + ", " +str(i.str_state))
            nodes[i.id]=OneXmlrpcNode(i)
        return nodes
    
    @mlog
    def read_userdata(self, file):
        logger.debug("Reading agent user data from file %s " % file)
        fin = open(file, "r")
        templatestr = fin.read()
        fin.close()        
        return templatestr
    
    '''
        Create new node.
    '''
    @mlog
    def create_node(self, **kwargs):
        logger.debug("Entering create_node")        
        agent_data = self.read_userdata(kwargs['template']['userdata'])
        agent_data_template = string.Template(agent_data)
        agent_data_template = agent_data_template.substitute(IP_PUBLIC='$IP_PUBLIC', NETMASK='$NETMASK', IP_GATEWAY='$IP_GATEWAY',NAMESERVER='$NAMESERVER',VMID='$VMID', NAME='$NAME',MANAGER_IP=str(kwargs['template']['_manager_ip']),MANAGER_PORT=str(kwargs['template']['_manager_port']))
        logger.debug('Trying the agent user data %s ' % str(agent_data_template))        
        hex_user_data= str(agent_data_template).encode('hex')
        context = str(kwargs['template']['context'])
        logger.debug("This is context: %s" % str(context))
        context_template = string.Template(context)
        context_template = context_template.substitute()
        logger.debug("Modified context is: %s" % str(context_template))
        if kwargs['function'] == 'agent':            
            logger.debug("creating agent")
            template = self.read_template(kwargs['template']['filename'])            
            template = template.substitute(NAME= str(kwargs['template']['vm_name']),CPU= str(kwargs['template']['cpu']),MEM_SIZE= str(kwargs['template']['mem_size']), OS= str(kwargs['template']['os']),IMAGE_ID= str(kwargs['template']['image_id']), NETWORK_ID= str(kwargs['template']['network_id']), CONTEXT= context_template, AGENT_USER_DATE=hex_user_data,DISK= str(kwargs['template']['disk'])) 
        elif kwargs['function'] == 'manager':
            logger.debug("creating manager")
            template = template.substitute(NAME= str(kwargs['template']['vm_name']),CPU= str(kwargs['template']['cpu']),MEM_SIZE= str(kwargs['template']['mem_size']), OS= str(kwargs['template']['os']),IMAGE_ID= str(kwargs['template']['image_id']), NETWORK_ID= str(kwargs['template']['network_id']), CONTEXT= context_template, AGENT_USER_DATE=hex_user_data,DISK= str(kwargs['template']['disk']))
        else:
            logger.debug("creating")
            template = template.substitute(NAME= str(kwargs['template']['vm_name']),CPU= str(kwargs['template']['cpu']),MEM_SIZE= str(kwargs['template']['mem_size']), OS= str(kwargs['template']['os']),IMAGE_ID= str(kwargs['template']['image_id']), NETWORK_ID= str(kwargs['template']['network_id']), CONTEXT= context_template, AGENT_USER_DATE=hex_user_data,DISK= str(kwargs['template']['disk']))
        logger.debug('Provisioning VM:' + template)
        rez = None
        try:
            logger.debug('Template: %s ' % str(template))
            rez=oca.VirtualMachine.allocate(self.client, template)
        except Exception as err:
            logger.error(str(err))        
        logger.debug('Result:' + str(rez))
        logger.debug("Exiting create_node")
        return rez

    '''
        Destroying ONE node with XML RPC.
    '''
    def destroy_node(self, id):
        logger.debug("Entering destroy_node")
        #oca.VirtualMachine.finalize(self.client.id)
        vm_pool=oca.VirtualMachinePool(self.client)
        vm_pool.info(-2)
        vm = vm_pool.get_by_id(id)
        vm.finalize()
        logger.debug("Exiting destroy_node")

    def list_sizes(self, location=None):
        return [
          NodeSize(id=1,
                   name="small",
                   ram=None,
                   disk=None,
                   bandwidth=None,
                   price=None,
                   driver=self),
          NodeSize(id=2,
                   name="medium",
                   ram=None,
                   disk=None,
                   bandwidth=None,
                   price=None,
                   driver=self),
          NodeSize(id=3,
                   name="large",
                   ram=None,
                   disk=None,
                   bandwidth=None,
                   price=None,
                   driver=self),
        ]

class IaaSClient:   
        
    RUNNING = NodeState.RUNNING
    REBOOTING = NodeState.REBOOTING
    TERMINATED = NodeState.TERMINATED
    PENDING = NodeState.PENDING
    UNKNOWN = NodeState.UNKNOWN

    driver = None

    def __config_opennebula_dummy(self, iaas_config):
        if not iaas_config.has_option('iaas', 'OPENNEBULA_URL'): raise Exception('Configuration error: [iaas] OPENNEBULA_URL not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_USER'): raise Exception('Configuration error: [iaas] OPENNEBULA_USER not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_PASSWORD'): raise Exception('Configuration error: [iaas] OPENNEBULA_PASSWORD not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_NETWORK_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_NETWORK_ID not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_SIZE_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_SIZE_ID not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_IMAGE_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_IMAGE_ID not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_CONTEXT_SCRIPT_MANAGER'): raise Exception('Configuration error: [iaas] OPENNEBULA_CONTEXT_SCRIPT_MANAGER not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_CONTEXT_SCRIPT_AGENT'): raise Exception('Configuration error: [iaas] OPENNEBULA_CONTEXT_SCRIPT_AGENT not set')
        
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
        self.one_context_manager_script = iaas_config.get('iaas', 'OPENNEBULA_CONTEXT_SCRIPT_MANAGER')        
        self.one_context_agent_script = iaas_config.get('iaas', 'OPENNEBULA_CONTEXT_SCRIPT_AGENT')
        self.driver = DummyONEDriver(self.username, self.password, self.scheme, self.host, self.port);
  
    def __config_opennebula_xmlrpc(self, iaas_config):
        if not iaas_config.has_option('iaas', 'OPENNEBULA_URL'): raise Exception('Configuration error: [iaas] OPENNEBULA_URL not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_USER'): raise Exception('Configuration error: [iaas] OPENNEBULA_USER not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_PASSWORD'): raise Exception('Configuration error: [iaas] OPENNEBULA_PASSWORD not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_NETWORK_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_NETWORK_ID not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_SIZE_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_SIZE_ID not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_IMAGE_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_IMAGE_ID not set')
        
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
        
        self.template = dict()
        self.template['filename']=iaas_config.get('onevm_agent_template', 'FILENAME')
        self.template['vm_name']=iaas_config.get('onevm_agent_template', 'NAME')
        self.template['cpu']=iaas_config.get('onevm_agent_template', 'CPU')
        self.template['mem_size']=iaas_config.get('onevm_agent_template', 'MEM_SIZE')
        self.template['disk']=iaas_config.get('onevm_agent_template', 'DISK')
        self.template['os']=iaas_config.get('onevm_agent_template', 'OS')
        self.template['image_id']=iaas_config.get('onevm_agent_template', 'IMAGE_ID')
        self.template['network_id']=iaas_config.get('onevm_agent_template', 'NETWORK_ID')
        self.template['context']=iaas_config.get('onevm_agent_template', 'CONTEXT')
        self.template['userdata']=iaas_config.get('onevm_agent_template', 'USERDATA')
        self.template['_manager_ip']=iaas_config.get('_manager', 'ip')
        self.template['_manager_port']=iaas_config.get('_manager', 'port')
        logger.debug('template: %s' % self.template);
        self.driver = OneXmlrpc(self.username, self.password, self.scheme, self.host, self.port)
  
    def __config_opennebula(self, iaas_config):
        if not iaas_config.has_option('iaas', 'OPENNEBULA_URL'): raise Exception('Configuration error: [iaas] OPENNEBULA_URL not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_USER'): raise Exception('Configuration error: [iaas] OPENNEBULA_USER not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_PASSWORD'): raise Exception('Configuration error: [iaas] OPENNEBULA_PASSWORD not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_IMAGE_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_IMAGE_ID not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_SIZE_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_SIZE_ID not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_NETWORK_ID'): raise Exception('Configuration error: [iaas] OPENNEBULA_NETWORK_ID not set')
        if not iaas_config.has_option('iaas', 'OPENNEBULA_NETWORK_GATEWAY'): raise Exception('Configuration error: [iaas] OPENNEBULA_NETWORK_GATEWAY not set')
        
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
        
        self.template = dict()
        self.template['filename']=iaas_config.get('iaas', 'OPENNEBULA_NAME')
        
        
        ONDriver = get_driver(Provider.OPENNEBULA)
        self.driver = ONDriver(self.username, secret=self.password, secure=(self.scheme == 'https'), host=self.host, port=self.port)
  
    def __config_ec2(self, iaas_config):
        if not iaas_config.has_option('iaas', 'EC2_USER'): raise Exception('Configuration error: [iaas] EC2_USER not set')
        if not iaas_config.has_option('iaas', 'EC2_PASSWORD'): raise Exception('Configuration error: [iaas] EC2_PASSWORD not set')
        if not iaas_config.has_option('iaas', 'EC2_IMAGE_ID'): raise Exception('Configuration error: [iaas] EC2_IMAGE_ID not set')
        if not iaas_config.has_option('iaas', 'EC2_SIZE_ID'): raise Exception('Configuration error: [iaas] EC2_SIZE_ID not set')
        
        if not iaas_config.has_option('iaas', 'EC2_SECURITY_GROUP_NAME'): raise Exception('Configuration error: [iaas] EC2_SECURITY_GROUP_NAME not set')
        if not iaas_config.has_option('iaas', 'EC2_KEY_NAME'): raise Exception('Configuration error: [iaas] EC2_KEY_NAME not set')
        
        self.username = iaas_config.get('iaas', 'EC2_USER')
        self.password = iaas_config.get('iaas', 'EC2_PASSWORD')
        
        self.ec2_ex_securitygroup = iaas_config.get('iaas', 'EC2_SECURITY_GROUP_NAME')
        self.ec2_ex_keyname = iaas_config.get('iaas', 'EC2_KEY_NAME')
        
        self.img_id = iaas_config.get('iaas', 'EC2_IMAGE_ID')
        self.size_id = iaas_config.get('iaas', 'EC2_SIZE_ID')
        
        EC2Driver = get_driver(Provider.EC2_US_EAST)
        self.driver = EC2Driver(self.username, self.password)
  
    def __setdriver(self, iaas_config):
        if not iaas_config.has_option('iaas', 'DRIVER'): raise Exception('Configuration error: [iaas] DRIVER not set')
        drivername = iaas_config.get('iaas', 'DRIVER')
        if drivername == 'OPENNEBULA':
            self.__config_opennebula(iaas_config)
        if drivername == 'OPENNEBULA_XMLRPC':
            self.__config_opennebula_xmlrpc(iaas_config)
        if drivername == 'OPENNEBULA_DUMMY':
            self.__config_opennebula_dummy(iaas_config)            
        elif drivername == 'EC2':
            self.__config_ec2(iaas_config)
      
    def __init__(self, iaas_config):
        self.__setdriver(iaas_config)
      
    '''List VMs which are part of my configuration.
    '''
    def listVMs(self):
        nodes = self.driver.list_nodes()
        vms = {}
        for node in nodes.values():
            vms[node.id] = {'id': node.id,
            'state': node.state,
            'name': node.name,
            'ip': node.public_ip}
        return vms
  
    def getVMInfo(self, vm_id):
        return self.listVMs()[vm_id]
  
    def newInstance(self, function):
        size_one = [ i for i in self.driver.list_sizes() if i.id == self.size_id ]
        size = size_one[0]
        img = NodeImage(self.img_id, '', None)
        kwargs = {'size': size,
                  'image': img,
                  'function' : function
                  }
        if isinstance(self.driver, OneXmlrpc):
            kwargs['template'] = self.template
        if isinstance(self.driver, DummyONEDriver):
            kwargs['ex_network_id'] = self.on_ex_network_id
            kwargs['ex_userdata_manager'] = self.one_context_manager_script        
            kwargs['ex_userdata_agent'] = self.one_context_agent_script
        if isinstance(self.driver, OpenNebulaNodeDriver):
            kwargs['ex_network_id'] = self.on_ex_network_id
            kwargs['ex_network_gateawy'] = self.on_ex_network_gateawy
        if isinstance(self.driver, EC2NodeDriver):
            kwargs['ex_securitygroup'] = self.ec2_ex_securitygroup
            kwargs['ex_keyname'] = self.ec2_ex_keyname
            kwargs['ex_userdata'] = '''#!/bin/bash
    wget -P /root/ http://hppc644.few.vu.nl/contrail/ConPaaSWeb.tar.gz
    wget -P /root/ http://hppc644.few.vu.nl/contrail/agent-start
    wget -P /root/ http://hppc644.few.vu.nl/contrail/agent-stop
    
    chmod 755 /root/agent-start
    chmod 755 /root/agent-stop
    
    /root/agent-start
    '''
        
        node = self.driver.create_node(name='conpaas', **kwargs)
        nodes = self.driver.list_nodes()
        
        return {'id': nodes[node].id,
            'state': nodes[node].state,
            'name': nodes[node].name,
            'ip': nodes[node].public_ip}
  
    def killInstance(self, vm_id):
        nodes = self.driver.list_nodes()
        for i in nodes:
            if int(i) == int(vm_id):
                return self.driver.destroy_node(i)
        return False