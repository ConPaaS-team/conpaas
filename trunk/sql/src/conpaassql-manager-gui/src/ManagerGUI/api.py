from flask import json

from conpaas.mysql.client import manager_client as mc
from conpaas.mysql.client import agent_client as ac

class Manager(object):
    def __init__(self, manager_host, manager_port, agent_port):
        self.manager_host = manager_host
        self.manager_port = manager_port
        self.agent_port = agent_port
    
    def _manager_list_nodes(self):
        data = mc.list_nodes(self.manager_host, self.manager_port)
        return data['serviceNode']
    
    def _manager_get_node_info(self, id):
        data = mc.get_node_info(self.manager_host, self.manager_port, id)
        return data['serviceNode']
    
    def _manager_add_nodes(self, func='agent'):
        data = mc.add_nodes(self.manager_host, self.manager_port, func)
        return data['serviceNode']
    
    def _manager_remove_nodes(self, id):
        data = mc.remove_nodes(self.manager_host, self.manager_port, id)
        return data['result'] == 'OK'
    
    def _agent_configure_user(self, agent_host, username, password):
        data = ac.configure_user(str(agent_host), self.agent_port,
                                    username, password)
        return data
    
    def _agent_get_all_users(self, agent_host):
        data = ac.get_all_users(str(agent_host), self.agent_port)
        
        users = []
        
        for key, value in json.loads(data[1])['result']['users'].items():
            if key.startswith('info'):
                users.append(value)
        
        return users
    
    def _agent_remove_user(self, agent_host, name):
        method = 'delete_user'
        params = {'username': name}
        
        try:
            ac._check(ac._jsonrpc_post(str(agent_host), self.agent_port,
                                            '/', method, params=params))
        except:
            pass
        
        return True
    
    def _agent_send_mysqldump(self, agent_host, location):
        data = ac.send_mysqldump(str(agent_host), self.agent_port, location)
        return data
    
    def agent_list(self):
        node_ids = self._manager_list_nodes()
        
        nodes = map(self._manager_get_node_info, node_ids)
        
        return nodes
    
    def agent_create(self):
        return self._manager_add_nodes()
    
    def agent_detail(self, id):
        return self._manager_get_node_info(id)
    
    def agent_remove(self, id):
        return self._manager_remove_nodes(id)
    
    def agent_user_list(self, host):
        return self._agent_get_all_users(host)
    
    def agent_user_create(self, host, username, password):
        return self._agent_configure_user(host, username, password)
    
    def agent_user_remove(self, host, username):
        return self._agent_remove_user(host, username)
    
    def agent_upload_sql(self, host, file):
        return self._agent_send_mysqldump(host, file)
