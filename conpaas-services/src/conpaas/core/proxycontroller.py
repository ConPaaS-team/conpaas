from conpaas.core.controller import Controller

import os.path
import urlparse, httplib, json
import ast

from conpaas.core.node import ServiceNode
from conpaas.core import https

class ProxyController(Controller):
    """Class used to manage the VMs associated with agents thrugh the
    director.
    """
    def __init__(self, config_parser):
        self.config_parser = config_parser
        Controller.__init__(self, config_parser)
        #TODO fix harcoded links
        self.create_node_url = "https://10.100.0.42:5555/nestedapi/create_node.php"
        self.delete_node_url = "https://10.100.0.42:5555/nestedapi/delete_node.php"
        self.update_configuration_url = "https://10.100.0.42:5555/nestedapi/update_configuration.php"
       
        self._stop_reservation_timers() 
        self._update_configuration()
        
    def create_nodes(self, count, test_agent, port, cloudobj=None, inst_type=None):
        """Override the create_nodes function from Controller.
        """
        nodes = []
        
        if not cloudobj:
            cloud = 'default'
        else:
            cloud = cloudobj.get_cloud_name()
        
        for i in range(count):
            #send requests to the director for creating the nodes one by one
            node = self._remote_create_node(1, test_agent, port, cloud)
            nodes.append(node)

        #wait for the nodes to be up
        poll, failed = self.wait_for_nodes(nodes, test_agent, int(port))        
        
        if failed:
            self.controller.delete_nodes(failed)

        return poll

    def delete_nodes(self, nodes):
        """Override the delete_nodes from Controller.
        """
        for node in nodes:
            self._remote_delete_node(node)

    def _stop_reservation_timers(self):
        for reservation_timer in self._Controller__reservation_map.values():
            reservation_timer.stop()

    def _update_configuration(self):
        cert = self._get_cert()

        parsed_url = urlparse.urlparse(self.update_configuration_url)
        status, body = https.client.https_post(parsed_url.hostname,
                                parsed_url.port,
                                parsed_url.path,
                                params={'config': self.config_parser._sections,
                                        'cert': cert})        

    def _get_cert(self):
        """Extract the public certificate of the manager. It will be enclosed in
        the request sent to the director (for identification).
        """
        cert_dir = self.config_parser.get('manager', 'CERT_DIR')
        cert_file = open(os.path.join(cert_dir, 'cert.pem'), 'r')
        cert = cert_file.read()

        return cert   

    def _remote_create_node(self, count, test_agent, port, cloud=None, inst_type=None):
        cert = self._get_cert()

        parsed_url = urlparse.urlparse(self.create_node_url)
        status, body = https.client.https_post(parsed_url.hostname,
                                parsed_url.port,
                                parsed_url.path,
                                params={'config': self.config_parser._sections, 
                                        'cloud': cloud,
                                        'cert': cert})

        data = json.loads(body)
        node_info = data['result']
        node = ServiceNode(node_info['id'], node_info['ip'], 
                           node_info['private_ip'], node_info['cloud_name'], 
                           node_info['weightBackend'])

        return node
        

    def _remote_delete_node(self, node):
        cert = self._get_cert()
        parsed_url = urlparse.urlparse(self.delete_node_url)
        status, body = https.client.https_post(parsed_url.hostname,
                                parsed_url.port,
                                parsed_url.path,
                                params={'cert': cert, 'node': node.__dict__})
