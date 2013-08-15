import sys
import getpass

import codecs
import locale

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

from cps.base import BaseClient

class Client(BaseClient):

    def set_password(self, service_id, password=None):
        if password:
            p1 = password
        else:
            pprompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))

            p1, p2 = pprompt()

            while p1 != p2:
                print('Passwords do not match. Try again')
                p1, p2 = pprompt()

        data = { 'user': 'mysqldb', 'password': p1 }
        res = self.callmanager(service_id, "set_password", True, data)
        if 'error' in res:
            print res['error']
            sys.exit(1)
        else:
            print "Password updated successfully"

    def sqldump(self, service_id):
        res = self.callmanager(service_id, "sqldump", False, {})
        if type('error') is dict and 'error' in res:
            print res['error']
            sys.exit(1)
        else:
            print res

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
        print "    set_password      serviceid password"
        print "    add_nodes         serviceid count [cloud]"
        print "    remove_nodes      serviceid count"
        print "    sqldump           serviceid"

    def main(self, argv):
        command = argv[1]

        if command == 'sqldump':
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
                
            self.check_service_id(sid)
            self.sqldump(sid)

        if command == 'set_password':
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
                
            self.check_service_id(sid)

            try:
                password = argv[3]
                getattr(self, command)(sid, password)
            except IndexError:
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
            if command == 'add_nodes':
                try:
                    if len(sys.argv) == 4:
                        cloud = 'default'
                    else:
                        cloud = argv[4]
                    if cloud not in self.available_clouds():
                        raise IndexError
                except IndexError:
                    print 'Cloud name must be one of ' + self.available_clouds()
                    sys.exit(0)
                res = self.callmanager(sid, command, True, { 'slaves': count,
                    'cloud': cloud})
            else:
                res = self.callmanager(sid, command, True, { 'slaves': count })
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command
