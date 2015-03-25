import sys

from cps.base import BaseClient

class Client(BaseClient):

    def info(self, app_id, service_id):
        service = BaseClient.info(self, app_id, service_id)

        nodes = self.callmanager(app_id, service['sid'], "list_nodes", False, {})
        if not 'error' in nodes:
            for node in nodes['helloworld']:
                params = { 'serviceNodeId': node }
                details = self.callmanager(app_id, service['sid'], "get_node_info", False, params)
                print "helloworld agent:", details['serviceNode']['ip']

    def usage(self, aid, sid ):
        BaseClient.usage(self, aid, sid)
        print ""
        print "    ----Service specific commands-------"
        print ""
        print "    get_helloworld appid serviceid"
        print "    add_nodes      appid serviceid count [cloud]"
        print "    remove_nodes   appid serviceid count"

    def main(self, argv):
        command = argv[1]
        try:
            aid = int(argv[2])
            sid = int(argv[3])
        except (IndexError, ValueError):
            self.usage(0,0)
            sys.exit(0)

        if command == 'get_helloworld':
            self.check_service_id(aid, sid)
            res = self.callmanager(aid, sid, "get_helloworld", False, {})
            if 'error' in res:
                print res['error']
            else:
                print res['helloworld']

        if command in ( 'add_nodes', 'remove_nodes' ):
            self.check_service_id(aid, sid)
            try:
                count = int(argv[4])
            except (IndexError, ValueError):
                self.usage(0,0)
                sys.exit(0)

            params = { 'count': count }

            if command == 'add_nodes' and len(argv) == 4:
                params['cloud'] = 'default'
            else:
                params['cloud'] = argv[4]

            # call the method
            res = self.callmanager(aid, sid, command, True, params)
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command
