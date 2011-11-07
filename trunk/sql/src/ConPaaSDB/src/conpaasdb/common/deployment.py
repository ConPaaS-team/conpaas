import inject

from conpaasdb.adapters.providers.base import Provider
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class ObjectNotFound(Exception):
    pass

class Deployment(object):
    provider = inject.attr(Provider)
    
    @mlog
    def deploy(self, name, image_id, network_id):
        image = self.get_image(image_id)
        network = self.get_network(network_id)
        size = self.get_size()
        
        return self.provider.deploy(name=name, image=image,
                                    network=network, size=size)
    
    @mlog
    def get_node(self, uuid):
        for node in self.node_list():
            if node.uuid == uuid:
                return node
        
        raise ObjectNotFound()
    
    def is_node(self, node):
        raise NotImplementedError()
    
    @mlog
    def node_list(self):
        nodes = self.provider.nodes()
        
        for node in nodes:
            if self.is_node(node):
                yield node
    
    @mlog
    def get_image(self, image_id):
        for image in self.provider.images():
            if int(image.id) == image_id:
                return image
        
        raise ObjectNotFound()
    
    @mlog
    def get_network(self, network_id):
        for network in self.provider.networks():
            if int(network.id) == network_id:
                return network
        
        raise ObjectNotFound()
    
    @mlog
    def get_size(self):
        return self.provider.sizes()[0]
