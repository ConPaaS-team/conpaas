from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

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

    # connect to openstack cloud
    def _connect(self):
        Driver = get_driver(Provider.EUCALYPTUS)

        self.driver = Driver(self.user, self.passwd, secure=False,
            host=self.host, port=8773, path='/services/Cloud')
        self.connected = True

    def config(self, config_params={}, context=None):
        if context is not None:
            self.cx = context

    def new_instances(self, count, name='conpaas', inst_type=None):
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
            'ex_userdata': self.cx
        }

        return self._create_service_nodes(self.driver.create_node(**kwargs))
