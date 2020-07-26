from cps.base import BaseClient

class Client(BaseClient):

    def info(self, service_id):
        service = BaseClient.info(self, service_id)

        nodes = self.callmanager(service['sid'], "list_nodes", False, {})
        if 'mains' in nodes:
            for main in nodes['mains']:
                params = { 'serviceNodeId': main }
                details = self.callmanager(service['sid'], 
                    "get_node_info", False, params)

                print "main namenode url:", 
                print "http://%s:50070" % details['serviceNode']['ip']

                print "main job tracker url:", 
                print "http://%s:50030" % details['serviceNode']['ip']

                print "main HUE url:", 
                print "http://%s:8088" % details['serviceNode']['ip']

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
