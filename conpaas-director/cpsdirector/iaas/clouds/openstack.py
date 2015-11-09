import math, time

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.common.exceptions import BaseHTTPError

from .base import Cloud

class OpenStackCloud(Cloud):

    def __init__(self, cloud_name, iaas_config):
        Cloud.__init__(self, cloud_name)

        self.config = iaas_config
        self.cloud_name = cloud_name
        cloud_params = [
            'USER', 'PASSWORD', 'HOST',
            'IMAGE_ID', 'SIZE_ID',
            'KEY_NAME',
            'SECURITY_GROUP_NAME',
        ]

        self._check_cloud_params(self.config, cloud_params)

        self.user = self.config.get(self.cloud_name, 'USER')
        self.passwd = self.config.get(self.cloud_name, 'PASSWORD')
        self.host = self.config.get(self.cloud_name, 'HOST')
        
    def get_by_id_or_name(self, label, id_or_name, rlist):
        by_id = filter(lambda x: x.id==id_or_name, rlist)
        if len(by_id) > 0:
            return by_id[0]
        by_name = filter(lambda x: x.name==id_or_name, rlist)
        if len(by_name) > 0:
            return by_name[0]
        raise ValueError('%s is not a valid value for %s' % (id_or_name, label))

    def set_instance_attributes(self):
        self.img = self.get_by_id_or_name('IMAGE_ID', 
                                          self.config.get(self.cloud_name, 'IMAGE_ID'), 
                                          self.driver.list_images())

        self.size = self.get_by_id_or_name('SIZE_ID', 
                                          self.config.get(self.cloud_name, 'SIZE_ID'), 
                                          self.driver.list_sizes())

        self.network = None
        if self.config.has_option(self.cloud_name, 'NETWORK_ID'):
            self.network = self.get_by_id_or_name('NETWORK_ID', 
                                              self.config.get(self.cloud_name, 'NETWORK_ID'), 
                                              self.driver.ex_list_networks())
        
        self.floating_pool = self.driver.ex_list_floating_ip_pools()[0]    
        self.key_name = self.config.get(self.cloud_name, 'KEY_NAME')
        self.sg = self.config.get(self.cloud_name, 'SECURITY_GROUP_NAME')
        self.auto_assing_floating = True
        if self.config.has_option(self.cloud_name, 'AUTO_ASSIGN_FLOATING_IP'):
            self.auto_assing_floating = self.config.getboolean(self.cloud_name, 'AUTO_ASSIGN_FLOATING_IP')

    def get_cloud_type(self):
        return 'openstack'

    # connect to openstack cloud
    def _connect(self):
        # Driver = get_driver(Provider.EUCALYPTUS)
        Driver = get_driver(Provider.OPENSTACK)

        # self.driver = Driver(self.user, self.passwd, secure=False,
        #     host=self.host, port=8773, path='/services/Cloud')
        self.driver = Driver(self.user, self.passwd, secure=False,
                   ex_force_auth_url='http://%s:5000' % self.host,
                   ex_force_auth_version='2.0_password', 
                   ex_tenant_name=self.user)
        
        self.set_instance_attributes()

        self.connected = True

    def config(self, config_params={}, context=None):
        if context is not None:
            self._context = context

    def new_instances(self, count, name='conpaas', inst_type=None):
        if self.connected is False:
            self._connect()

        flavor = self.size
        if inst_type is not None:
            flavor = self.get_by_id_or_name('SIZE_ID', inst_type, self.driver.list_sizes())
        
        kwargs = {
            'size': flavor,
            'image': self.img,
            'name': name,
            'ex_mincount': str(count),
            'ex_maxcount': str(count),
            'ex_securitygroup': self.sg,
            'ex_keyname': self.key_name,
            'ex_userdata': self.get_context()
        }
        
        if self.network:
            kwargs['networks'] = [self.network]

        lc_nodes = self.driver.create_node(**kwargs)
        if not self.auto_assing_floating:
            self.associate_floating_ips(lc_nodes)

        nodes = self._create_service_nodes(lc_nodes)

        if count > 1:
            return nodes

        return [ nodes ]

    def associate_floating_ips(self, instances):
        
        if type(instances) is not list:
            instances = [instances]

        nr_attempts = 3 * len(instances)
        
        for instance in instances:
            while nr_attempts > 0:
                try: 
                    self.driver.ex_attach_floating_ip_to_node(instance, self.get_floating_ip().ip_address)
                    break
                except BaseHTTPError:
                    self.logger.debug('Attaching failed probly because the VM was not on a network yet, let\'s wait a bit and retry')
                    time.sleep(1)
                    nr_attempts -= 1

        if nr_attempts == 0:
            raise Exception('Error assigning floating IPs')

    def get_floating_ip(self):
        free_fips = filter(lambda x: x.node_id==None, self.driver.ex_list_floating_ips())
        return free_fips[0] if len(free_fips) > 0 else self.floating_pool.create_floating_ip()

    def create_volume(self, size, name, vm_id=None):
        # OpenStack expects volume size in GiB.
        size /= 1024.0
        size = int(math.ceil(size))

        return self.driver.create_volume(size, name)

    def attach_volume(self, node, volume, device):
        device = '/dev/%s' % device
        return self.driver.attach_volume(node, volume, device)
