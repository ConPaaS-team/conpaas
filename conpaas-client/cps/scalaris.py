from cps.base import BaseClient

class Client(BaseClient):

    def info(self, service_id):
        service = BaseClient.info(self, service_id)
        
        nodes = self.callmanager(service['sid'], "list_nodes", False, {})
        if 'scalaris' in nodes:
            for node in nodes['scalaris']:
                params = { 'serviceNodeId': node }
                details = self.callmanager(service['sid'], 
                    "get_node_info", False, params)

                print "management server url:",
                print "http://%s:8000" % details['serviceNode']['ip']

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
