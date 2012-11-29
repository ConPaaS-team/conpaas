import sys

from cps.base import BaseClient

class Client(BaseClient):

    def info(self, service_id):
        service = BaseClient.info(self, service_id)
        
        nodes = self.callmanager(service['sid'], "list_nodes", False, {})
        if 'hub' in nodes and nodes['hub']:
            # Only one HUB
            hub = nodes['hub'][0]
            params = { 'serviceNodeId': hub }
            details = self.callmanager(service['sid'], "get_node_info", False, params)
            print "hub url: ", "http://%s:4444" % details['serviceNode']['ip']
            print "node url:", "http://%s:3306" % details['serviceNode']['ip']

        if 'node' in nodes:
            # Multiple nodes
            for node in nodes['node']:
                params = { 'serviceNodeId': node }
                details = self.callmanager(service['sid'], "get_node_info", False, params)
                print "node url:", "http://%s:3306" % details['serviceNode']['ip']

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    add_nodes    serviceid count"
        print "    remove_nodes serviceid count"

    def main(self, argv):
        command = argv[1]

        if command in ( 'add_nodes', 'remove_nodes' ):
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
                
            self.check_service_id(sid)

            try:
                count = int(argv[3])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            # call the method
            res = self.callmanager(sid, command, True, { 'count': count })
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command
