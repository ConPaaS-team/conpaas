
import urlparse, json
from conpaas.core import https
from conpaas.core.log import create_logger, init
from conpaas.core.node import ServiceNode

class DirectorCallbacker(object):
    
    def __init__(self, config_parser):
        self.__logger = create_logger(__name__)
    	self.config_parser = config_parser

    def create_nodes(self, count, service_id, service_manager, cloud_name='default', inst_type=None):
        params = {'count':count, 'cloud_name':cloud_name, 'inst_type':inst_type, 
                 'app_id':self.config_parser.get("manager", "APP_ID"), 
                 'service_id':service_id,
                 'manager_ip':self.config_parser.get("manager", "MY_IP"), 
                 'service_type':service_manager.get_service_type(),
                 'context': service_manager.get_context_replacement()}
        ret = self._dic_callback('/create_nodes', params)
        nodes = None
        if ret:
            nodes = [ServiceNode(node['vmid'], node['ip'],node['private_ip'],node['cloud_name'],node['weight_backend']) for node in ret]        
        
        return nodes

    def remove_nodes(self, nodes):
        dict_nodes = [node.to_dict() for node in nodes]
        params = {'nodes': json.dumps(dict_nodes)}
        ret = self._dic_callback('/remove_nodes', params)
        return ret
         

    def _dic_callback(self, path, params):
        try:
            director_url = self.config_parser.get('manager', 'DIRECTOR_URL')
            parsed_url = urlparse.urlparse(director_url)
            _, body = https.client.https_post(parsed_url.hostname,
                                              parsed_url.port or 443,
                                              path,
                                              params)
            obj = json.loads(body)
            return obj
        except:
            self.__logger.exception('Failed to deduct credit')
            return False