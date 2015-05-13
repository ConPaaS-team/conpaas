import sys

from cps.base import BaseClient

# TODO: as this file was created from a BLUEPRINT file,
#   you may want to change ports, paths and/or methods (e.g. for hub)
#   to meet your specific service/server needs

class Client(BaseClient):

    def info(self, service_id):
        service = BaseClient.info(self, service_id)
        
        nodes = self.callmanager(service['sid'], "list_nodes", False, {})
        if 'node' in nodes:
            # Multiple nodes
            for node in nodes['node']:
                params = { 'serviceNodeId': node }
                details = self.callmanager(service['sid'], "get_node_info", False, params)
                print "node url:", "http://%s:3306" % details['serviceNode']['ip']

    def addremove(self, command, sid, count):
        

        # call the method
        res = self.callmanager(sid, command, True, { 'count': count })
        if 'error' in res:
            print res['error']
        else:
            print "Service", sid, "is performing the requested operation (%s)" % command

    def test(self, sid):
        res = self.callmanager(sid, 'test', False, {})
        if 'error' in res:
            print res['error']
        else:
            print res['msgs']

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    add_nodes    serviceid count"
        print "    remove_nodes serviceid count"
        print "    test         serviceid "

    def main(self, argv):
        command = argv[1]

        if command in ( 'add_nodes', 'remove_nodes' , 'test' ):
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
                
            self.check_service_id(sid)
            
            if command == 'test':
                self.test(sid)
            if command in ( 'add_nodes', 'remove_nodes'):
                try:
                    count = int(argv[3])
                except (IndexError, ValueError):
                    self.usage(argv[0])
                    sys.exit(0)
                
                self.addremove(command, sid, count)
            


