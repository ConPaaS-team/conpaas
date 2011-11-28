'''
OpenNebula OCA driver
'''

import oca
import time
import urlparse
from fabric.api import run, settings, env
from fabric.state import connections

from libcloud.common.base import ConnectionUserAndKey
from libcloud.common.types import LibcloudError
from libcloud.compute.providers import Provider
from libcloud.compute.types import NodeState, DeploymentError
from libcloud.compute.base import NodeDriver, Node, NodeLocation,\
    NODE_ONLINE_WAIT_TIMEOUT
from libcloud.compute.base import NodeImage, NodeSize
from libcloud.compute.ssh import SSHClient

from conpaasdb.libcloudcontrib.opennebula.template import OneTemplate

API_HOST = '127.0.0.1'
API_PORT = 2633

class OpenNebulaException(Exception):
    pass

class OpenNebulaConnection(ConnectionUserAndKey):
    '''
    Connection class for the OpenNebula driver
    '''

    host = API_HOST
    port = API_PORT
    secure = False
    
    def __init__(self, user_id, key, secure=False, host=None, port=None):
        self.user_id = user_id
        self.key = key
        self.host = host
        self.port = port
    
    def connect(self, host=None, port=None):
        host = host or self.host
        port = port or self.port
        
        if not ':' in host:
            host = '%s:%d' % (host, int(port))
        
        auth = ':'.join((self.user_id, self.key))
        url = urlparse.urlunsplit(('http', host, '/RPC2', None, None))
        
        self.client = oca.Client(auth, url)

class OpenNebulaNetwork(object):
    def __init__(self, id, name, driver, extra=None):
        self.id = str(id)
        self.name = name
        self.driver = driver
        self.extra = extra or {}

    def __repr__(self):
        return (('<OpenNebulaNetwork: id=%s, name=%s, driver=%s  ...>')
                % (self.id, self.name, self.driver.name))

class OpenNebulaNodeDriver(NodeDriver):
    '''
    OpenNebula node driver
    '''

    connectionCls = OpenNebulaConnection
    type = Provider.OPENNEBULA
    name = 'OpenNebula'
    default_cpu = 1
    
    NODE_STATE_LCM_INIT = 0
    NODE_STATE_PROLOG = 1
    NODE_STATE_BOOT = 2
    NODE_STATE_RUNNING = 3
    NODE_STATE_MIGRATE = 4
    NODE_STATE_SAVE_STOP = 5
    NODE_STATE_SAVE_SUSPEND = 6
    NODE_STATE_SAVE_MIGRATE = 7
    NODE_STATE_PROLOG_MIGRATE = 8
    NODE_STATE_PROLOG_RESUME = 9
    NODE_STATE_EPILOG_STOP = 10
    NODE_STATE_EPILOG = 11
    NODE_STATE_SHUTDOWN = 12
    NODE_STATE_CANCEL = 13
    NODE_STATE_FAILURE = 14
    NODE_STATE_DELETE = 15
    NODE_STATE_UNKNOWN = 16
    
    NODE_STATE_MAP = {
        NODE_STATE_LCM_INIT: NodeState.PENDING,
        NODE_STATE_PROLOG: NodeState.PENDING,
        NODE_STATE_BOOT: NodeState.PENDING,
        NODE_STATE_RUNNING: NodeState.RUNNING,
        NODE_STATE_MIGRATE: NodeState.TERMINATED,
        NODE_STATE_SAVE_STOP: NodeState.TERMINATED,
        NODE_STATE_SAVE_SUSPEND: NodeState.TERMINATED,
        NODE_STATE_SAVE_MIGRATE: NodeState.TERMINATED,
        NODE_STATE_PROLOG_MIGRATE: NodeState.TERMINATED,
        NODE_STATE_PROLOG_RESUME: NodeState.TERMINATED,
        NODE_STATE_EPILOG_STOP: NodeState.TERMINATED,
        NODE_STATE_EPILOG: NodeState.TERMINATED,
        NODE_STATE_SHUTDOWN: NodeState.TERMINATED,
        NODE_STATE_CANCEL: NodeState.TERMINATED,
        NODE_STATE_FAILURE: NodeState.UNKNOWN,
        NODE_STATE_DELETE: NodeState.TERMINATED,
        NODE_STATE_UNKNOWN: NodeState.UNKNOWN,
    }
    
    def list_sizes(self, location=None):
        return [
          NodeSize(id=1,
                   name='default',
                   ram=512,
                   disk=None,
                   bandwidth=None,
                   price=None,
                   driver=self),
        ]
    
    def _get_vms(self):
        pool = oca.VirtualMachinePool(self.connection.client)
        pool.info(-2)
        return pool
    
    def _get_images(self):
        pool = oca.ImagePool(self.connection.client)
        pool.info(-2)
        return pool
    
    def _get_vns(self):
        pool = oca.VirtualNetworkPool(self.connection.client)
        pool.info(-2)
        return pool
    
    def list_nodes(self):
        return self._to_nodes(self._get_vms())

    def list_images(self, location=None):
        return self._to_images(self._get_images())

    def ex_list_networks(self):
        return self._to_networks(self._get_vns())

    def list_locations(self):
        return [NodeLocation(0,  'OpenNebula', 'ONE', self)]

    def reboot_node(self, node):
        vms = self._get_vms()
        vm = vms.get_by_id(int(node.id))
        vm.restart()
        
        return True

    def destroy_node(self, node):
        vms = self._get_vms()
        vm = vms.get_by_id(int(node.id))
        vm.finalize()
        
        return True
    
    def get_template(self, name, cpu, size, image, network, context=None):
        template = dict(
            name = name,
            cpu = cpu,
            memory = size.ram,
            os = dict(
                arch = 'i686',
                boot = 'hd',
                root = 'hda',
            ),
            disk = dict(
                image_id = image.id,
                bus = 'scsi',
                readonly = False
            ),
            nic = dict(
                network_id = network.id
            ),
            graphics = dict(
                type = 'vnc'
            ),
            context = context,
        )
        
        return template
    
    def create_node(self, **kwargs):
        '''Create a new OpenNebula node

        See L{NodeDriver.create_node} for more keyword args.
        '''
        
        name = kwargs['name']
        cpu = float(kwargs.get('cpu', self.default_cpu))
        size = kwargs['size']
        image = kwargs['image']
        network = kwargs['network']
        context = kwargs.get('context', None)
        
        template = self.get_template(name, cpu, size, image, network, context)
        
        tpl = str(OneTemplate(template))
        
        vm_id = oca.VirtualMachine.allocate(self.connection.client, tpl)
        
        vms = self._get_vms()
        vm = vms.get_by_id(int(vm_id))
        
        return self._to_node(vm)
    
    def deploy_node(self, **kwargs):
        private_key = kwargs.get('private_key', None)
        
        if not private_key:
            raise ValueError('"private_key" param is required')
        
        node = self.create_node(**kwargs)

        try:
            # Wait until node is up and running and has public IP assigned
            self._wait_until_running(node=node, wait_period=3,
                                     timeout=NODE_ONLINE_WAIT_TIMEOUT)
            
            ssh_username = kwargs.get('ssh_username', 'root')
            ssh_ip = node.public_ip[0]
            ssh_port = int(kwargs.get('ssh_port', 22))
            
            ssh_host = '%s@%s:%d' % (ssh_username, ssh_ip, ssh_port)
            
            def host_settings(ssh_host=ssh_host, private_key=private_key):
                return settings(host_string=str(ssh_host),
                                key_filename=private_key,
                                password='__invalid__password__',
                                abort_on_prompts=True)
            
            with host_settings():
                self._wait_to_connect()
            
            return node, host_settings
        except Exception, e:
            raise DeploymentError(node, e)
        
        return node
    
    def _wait_to_connect(self, timeout=300):
        start = time.time()
        end = start + timeout

        while time.time() < end:
            try:
                run('true')
                return
            except:
                import traceback
                traceback.print_exc()
                connections.pop(env.host_string, None)
            
            time.sleep(1)

        raise LibcloudError(value='Could not connect to the remote SSH ' +
                            'server. Giving up.', driver=self)
    
    def _to_images(self, oca_images):
        images = map(self._to_image, oca_images)
        return images

    def _to_image(self, oca_image):
        return NodeImage(id=oca_image.id,
                         name=oca_image.name,
                         driver=self.connection.driver,
                         extra=vars(oca_image))
    
    def _to_networks(self, oca_vns):
        networks = map(self._to_network, oca_vns)
        return networks

    def _to_network(self, oca_vn):
        return OpenNebulaNetwork(id=oca_vn.id,
                         name=oca_vn.name,
                         driver=self.connection.driver,
                         extra=vars(oca_vn))
    
    def _to_nodes(self, oca_vms):
        computes = map(self._to_node, oca_vms)
        return computes

    def _to_node(self, oca_vm):
        state = self.NODE_STATE_MAP.get(oca_vm.lcm_state, NodeState.UNKNOWN)
        networks = [x.ip for x in oca_vm.template.nics]
        
        return Node(id=oca_vm.id,
                    name=oca_vm.name,
                    state=state,
                    public_ip=networks,
                    private_ip=[],
                    driver=self.connection.driver)
