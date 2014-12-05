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
        print "    add_nodes         serviceid count [cloud] # add the specified number of scalaris nodes."
        print "                                              # Set \'cloud\' to \'auto\' to automatically place nodes across multiple clouds."
        print "    remove_nodes      serviceid count [cloud] # remove the specified number of scalaris nodes"
        print "    list_nodes        serviceid               # list all nodes"
        print "    get_node_info     serviceid nodeid        # get information about the specified node"

    def main(self, argv):

        command = argv[1]

        if command in ( 'add_nodes', 'list_nodes', 'get_node_info',
                'remove_nodes' ):
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                print_usage_and_exit(argv[0])

            self.check_service_id(sid)

        if command in ('add_nodes', 'remove_nodes'):
            try:
                params = {'scalaris' : int(argv[3])}
            except (IndexError, ValueError):
                print_usage_and_exit(argv[0])

            if len(argv) == 4:
                params['auto_placement'] = True
                params['cloud'] = 'default'
            elif argv[4] == 'auto':
                params['auto_placement'] = True
                params['cloud'] = 'default'
            else:
                params['auto_placement'] = False
                params['cloud'] = argv[4]

            res = self.callmanager(sid, command, True, params)
            if 'error' in res:
                print res['error']
            else:
                if command == 'add_nodes':
                    print params['scalaris'], "nodes added to service ", sid
                if command == 'remove_nodes':
                    print params['scalaris'], "nodes removed from service ", sid

        if command == 'list_nodes':
            res = self.callmanager(sid, command, False, {})
            if 'error' in res:
                print res['error']
            else:
                print res['scalaris']

        if command == 'get_node_info':
            try:
                params = {'serviceNodeId': argv[3]}
            except IndexError:
                print_usage_and_exit(argv[0])

            res = self.callmanager(sid, command, False, params)
            if 'error' in res:
                print res['error']
            else:
                print res['serviceNode']

    def print_usage_and_exit(arg):
        self.usage(arg)
        sys.exit(0)
