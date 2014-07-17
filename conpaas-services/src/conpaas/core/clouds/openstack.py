from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from conpaas.core.clouds.nested import base_clouds
from .base import Cloud

class OpenStackCloud(Cloud):

    def __init__(self, cloud_name, iaas_config):
        Cloud.__init__(self, cloud_name)

        cloud_params = [
            'USER', 'PASSWORD', 'HOST',
            'IMAGE_ID', 'SIZE_ID',
            'KEY_NAME',
            'SECURITY_GROUP_NAME',
        ]

        self._check_cloud_params(iaas_config, cloud_params)

        self.user = iaas_config.get(cloud_name, 'USER')
        self.passwd = iaas_config.get(cloud_name, 'PASSWORD')
        self.host = iaas_config.get(cloud_name, 'HOST')
        self.img_id = iaas_config.get(cloud_name, 'IMAGE_ID')
        self.size_id = iaas_config.get(cloud_name, 'SIZE_ID')
        self.key_name = iaas_config.get(cloud_name, 'KEY_NAME')
        self.sg = iaas_config.get(cloud_name, 'SECURITY_GROUP_NAME')

    def get_cloud_type(self):
        return 'openstack'

    def x_connect(self):
        Driver = get_driver(Provider.EUCALYPTUS)

        self.driver = Driver(self.user, self.passwd, secure=False,
            host=self.host, port=8773, path='/services/Cloud')
        self.connected = True

    # connect to openstack cloud
    def _connect(self):
        import libcloud.security
        libcloud.security.VERIFY_SSL_CERT = False
        
        OpenStack = get_driver(Provider.OPENSTACK)
        self.driver = OpenStack('admin', 'password',
                            host='10.100.0.42', port=35357, secure=False,
                            ex_force_auth_url='http://10.100.0.42:35357',
                            ex_force_auth_version='2.0_password',
                            ex_force_service_name='nova',
                            ex_tenant_name = 'admin')
        
        self.connected = True
        
    
    def config(self, config_params={}, context=None):
        if context is not None:
            self._context = context

    def new_instances(self, app_id, count, name='conpaas', inst_type=None):
        if self.connected is False:
            self._connect()

        if inst_type is None:
            inst_type = self.size_id

        size = [size for size in self.driver.list_sizes() if size.name == inst_type][0]
        img = [image for image in self.driver.list_images() if image.name == self.img_id][0]
        
        kwargs = {
            'size': size,
            'image': img,
            'name': name,
            'ex_mincount': str(count),
            'ex_maxcount': str(count),
            'ex_securitygroup': self.sg,
            'ex_keyname': self.key_name,
            'ex_userdata': self.get_context()
        }

        node = self.driver.create_node(**kwargs)
       
        #node = base_clouds.get_active_cloud().create_container(self.driver, kwargs, app_id) 
        
        return [ self._create_service_nodes(node) ]

    def add_compute_vm(self, app_id, name, inst_type=None):
        return base_clouds.get_active_cloud().add_compute_vm(app_id, name, inst_type)
     
    def xnew_instances(self, count, name='conpaas', inst_type=None):
        if self.connected is False:
            self._connect()

        if inst_type is None:
            inst_type = self.size_id

        class size:
            id = inst_type

        class img:
            id = self.img_id

        kwargs = {
            'size': size,
            'image': img,
            'name': name,
            'ex_mincount': str(count),
            'ex_maxcount': str(count),
            'ex_securitygroup': self.sg,
            'ex_keyname': self.key_name,
            'ex_userdata': self.get_context()
        }

        node = self.driver.create_node(**kwargs)

        return [ self._create_service_nodes(node) ]

    def kill_instance(self, node):
        '''Kill a VM instance.

           @param node: A ServiceNode instance, where node.id is the
                        vm_id
        '''
        if self.connected is False:
            self._connect()
        #size = [size for size in self.driver.list_sizes() if size.name == inst_type][0]
        #base_clouds.get_active_cloud().clean_shared_pool(self.driver, size)
        return self.driver.destroy_node(node.as_libcloud_node())
