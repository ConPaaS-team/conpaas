import sys
import getpass

from cps.base import BaseClient

class Client(BaseClient):

    def set_password(self, service_id):
        pprompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))

        p1, p2 = pprompt()

        while p1 != p2:
            print('Passwords do not match. Try again')
            p1, p2 = pprompt()

        data = { 'user': 'mysqldb', 'password': p1 }
        res = self.callmanager(service_id, "set_password", True, data)
        if 'error' in res:
            print res['error']
        else:
            print "Password updated successfully"

    def info(self, service_id):
        service = BaseClient.info(self, service_id)
        
        nodes = self.callmanager(service['sid'], "list_nodes", False, {})

        for node in nodes['masters']:
            params = { 'serviceNodeId': node }
            details = self.callmanager(service['sid'], "get_node_info", False, params)
            print "master url:", "mysql://%s:3306" % details['serviceNode']['ip']

        for node in nodes['slaves']:
            params = { 'serviceNodeId': node }
            details = self.callmanager(service['sid'], "get_node_info", False, params)
            print "slave url: ", "mysql://%s:3306" % details['serviceNode']['ip']

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    set_password      serviceid"
        print "    add_nodes         serviceid count"
        print "    remove_nodes      serviceid count"

    def main(self, argv):
        command = argv[1]

        if command == 'set_password':
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
                
            self.check_service_id(sid)
            getattr(self, command)(sid)

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
            res = self.callmanager(sid, command, True, { 'slaves': count })
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command
