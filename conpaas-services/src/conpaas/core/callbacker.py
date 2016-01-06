
import urlparse, json, os
from conpaas.core import https
from conpaas.core.log import create_logger
from conpaas.core.node import ServiceNode

class DirectorCallbacker(object):
    
    def __init__(self, config_parser):
        self.__logger = create_logger(__name__)
    	self.config_parser = config_parser


    # def create_nodes(self, count, service_id, service_manager, cloud_name='default', inst_type=None):
    #     params = {'count':count, 'cloud_name':cloud_name, 'inst_type':inst_type, 
    #              'app_id':self.config_parser.get("manager", "APP_ID"), 
    #              'service_id':service_id,
    #              'manager_ip':self.config_parser.get("manager", "MY_IP"), 
    #              'service_type':service_manager.get_service_type(),
    #              'context': service_manager.get_context_replacement()}
    #     ret = self._dic_callback('/create_nodes', params)
    #     nodes = None
    #     if ret:
    #         nodes = [ServiceNode(node['vmid'], node['ip'],node['private_ip'],node['cloud_name'],node['weight_backend']) for node in ret]        
        
    #     return nodes

    def create_nodes(self, nodes_info, service_id, service_manager):
        #set cloud if not already set
        for node in nodes_info:
            if not node['cloud']:
                node['cloud'] = 'default'

        params = {'nodes_info':nodes_info, 
                 'app_id':self.config_parser.get("manager", "APP_ID"), 
                 'service_id':service_id,
                 'manager_ip':self.config_parser.get("manager", "MY_IP"), 
                 'service_type':service_manager.get_service_type(),
                 'context': service_manager.get_context_replacement()}

        basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
        filename = 'startup.sh'
        fullpath = os.path.join(basedir, str(service_id), filename) 

        # files=[]
        if os.path.exists(fullpath):
            contents = open(fullpath).read()
            params['startup_script'] = contents
        #     files = [ ( 'script', filename, contents ) ]

        ret = self._dic_callback('/create_nodes', params)
        nodes = None
        if ret:
            if 'error' in ret:
                return ret
            else:
                nodes = [ServiceNode.from_dict(node) for node in ret]        
        return nodes

    def remove_nodes(self, nodes):
        dict_nodes = [node.to_dict() for node in nodes]
        params = {'nodes': json.dumps(dict_nodes)}
        ret = self._dic_callback('/remove_nodes', params)
        return ret
  
    def create_volume(self, size, name, vm_id, cloud='default'):
        params = {'size':size, 'name':name, 'vm_id':vm_id, 'cloud':cloud}
        return self._dic_callback('/create_volume', params)

    def attach_volume(self, vm_id, volume_id, device_name, cloud):
        params = {'vm_id':vm_id, 'volume_id':volume_id, 'device_name':device_name, 'cloud':cloud}
        return self._dic_callback('/attach_volume', params)

    def detach_volume(self, volume_id, cloud):
        params = {'volume_id':volume_id, 'cloud':cloud}
        return self._dic_callback('/detach_volume', params)

    def destroy_volume(self, volume_id, cloud):
        params = {'volume_id':volume_id, 'cloud':cloud}
        return self._dic_callback('/destroy_volume', params)

    def check_credits(self):
        params = {}
        return self._dic_callback('/credit', params)

    def _dic_callback(self, path, params, files=[]):
        try:
            director_url = self.config_parser.get('manager', 'DIRECTOR_URL')
            parsed_url = urlparse.urlparse(director_url)
            _, body = https.client.https_post(parsed_url.hostname,
                                              parsed_url.port or 443,
                                              path,
                                              params,
                                              files)
            obj = json.loads(body)
            return obj
        except:
            self.__logger.exception('Failed to call method %s' % path)
            return False
