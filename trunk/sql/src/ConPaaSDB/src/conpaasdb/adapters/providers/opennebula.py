from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider as ComputeProvider

from conpaasdb.adapters.providers.base import Provider
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

### Monkeypatch OpenNebula

from libcloud.compute import providers
providers.DRIVERS[ComputeProvider.OPENNEBULA] = (
        'conpaasdb.libcloudcontrib.opennebula', 'OpenNebulaNodeDriver')

###

### Monkeypatch Fabric (asking for password

from fabric import network as fnetwork
fnetwork.prompt_for_password = lambda *args, **kwargs: '__invalid__password__'

###

class OpenNebulaProvider(Provider):
    @mlog
    def __init__(self, username, password, host, port):
        Driver = get_driver(ComputeProvider.OPENNEBULA)
        
        self.driver = Driver(username, password, host=host, port=port)
    
    @mlog
    def nodes(self):
        return self.driver.list_nodes()
    
    @mlog
    def images(self):
        return self.driver.list_images()
    
    @mlog
    def sizes(self):
        return self.driver.list_sizes()
    
    @mlog
    def networks(self):
        return self.driver.ex_list_networks()
    
    @mlog
    def deploy(self, name, size, image, network):
        ssh_key = self.generate_ssh_key()
    
        kwargs = dict(
            name = name,
            size = size,
            image = image,
            network = network,
            context = dict(
                public_key = ssh_key.public_key()
            ),
            private_key = ssh_key.private_key_file()
        )
        
        node, host_settings = self.driver.deploy_node(**kwargs)
        
        return node, host_settings
