import sys

from cps.base import BaseClient

class Client(BaseClient):

    def info(self, service_id):
        service = BaseClient.info(self, service_id)
        
        nodes = self.callmanager(service['sid'], "list_nodes", False, {})
        if 'error' in nodes:
            return

        print nodes

        for role in ( 'dir', 'mrc', 'osd' ):
            print "\n", role.upper(), "nodes:"

            for node in nodes[role]:
                params = { 'serviceNodeId': node }
                details = self.callmanager(service['sid'], "get_node_info", False, params)

                if 'error' in details:
                    print node, details['error']
                    continue

                if role == 'dir':
                    port = 30638

                if role == 'osd':
                    port = 30640
                    
                if role == 'mrc':
                    port = 30636

                print "http://%s:%s" % (details['serviceNode']['ip'], port)

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    add_nodes         serviceid count     # add the specified number of osd nodes"
        print "    remove_nodes      serviceid count     # remove the specified number of osd nodes"
        print "    create_volume     serviceid vol_name"
        print "    list_volumes      serviceid"

    def main(self, argv):
        command = argv[1]

        if command in ( 'add_nodes', 'remove_nodes', 'list_volumes', 'create_volume' ):
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
                
            self.check_service_id(sid)

        if command in ( 'add_nodes', 'remove_nodes' ):
            try:
                params = {
                    'osd': int(argv[3]),
                    #'dir': int(argv[4]),
                    #'mrc': int(argv[5])
                }
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            if len(argv) == 4:
                params['cloud'] = 'default'
            else:
                params['cloud'] = argv[4]
            # call the method
            res = self.callmanager(sid, command, True, params)
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command

        if command == 'create_volume':
            try:
                params = { 'volumeName': argv[3] }
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            res = self.callmanager(sid, 'createVolume', True, params)
            if 'error' in res:
                print res['error']
            else:
                print "Volume", params['volumeName'], "created" 

        if command == 'list_volumes':
            res = self.callmanager(sid, 'viewVolumes', False, {})
            if 'error' in res:
                print res['error']
            else:
                print res['volumes']
