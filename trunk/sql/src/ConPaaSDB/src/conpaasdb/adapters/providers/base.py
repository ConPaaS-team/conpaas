from conpaasdb.libcloudcontrib.utils import SSHKeygen
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class Provider(object):
    @mlog
    def generate_ssh_key(self):
        return SSHKeygen()
    
    def nodes(self):
        raise NotImplementedError('BaseProvider.nodes')
    
    def images(self):
        raise NotImplementedError('BaseProvider.images')
    
    def sizes(self):
        raise NotImplementedError('BaseProvider.sizes')
    
    def networks(self):
        raise NotImplementedError('BaseProvider.networks')
    
    def deploy(self, name, size, image, network):
        raise NotImplementedError('BaseProvider.deploy')
