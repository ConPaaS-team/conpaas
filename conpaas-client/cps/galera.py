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
        if type(res) is dict and 'error' in res:
            print res['error']
            sys.exit(1)
        else:
            print res

    def load_dump(self, service_id, filename):
        with open(filename) as dump_file:
            contents = dump_file.read()
        files = [('mysqldump_file', filename, contents)]
        res = self.callmanager(service_id, "/", True, {'method': "load_dump", }, files)
        if 'error' in res:
            print res['error']

    def migrate_nodes(self, service_id, migration_plan, delay=None):
        data = {}
        data['nodes'] = migration_plan
        if delay is not None:
            data['delay'] = delay
        res = self.callmanager(service_id, "migrate_nodes", True, data)
        return res

    def info(self, service_id):
        service = BaseClient.info(self, service_id)
        
        nodes = self.callmanager(service['sid'], "list_nodes", False, {})

        for node in nodes['nodes']:
            params = {'serviceNodeId': node}
            details = self.callmanager(service['sid'], "get_node_info", False, params)
            node_info = details['serviceNode']
            print "node: ip=%s cloud=%s vmid=%s" % (node_info['ip'], node_info['cloud'], node_info['vmid'])

        for node in nodes['glb_nodes']:
            params = {'serviceNodeId': node}
            details = self.callmanager(service['sid'], "get_node_info", False, params)
            node_info = details['serviceNode']
            print "glb node: ip=%s cloud=%s vmid=%s" % (node_info['ip'], node_info['cloud'], node_info['vmid'])

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    set_password      serviceid password"
        print "    add_nodes         serviceid count [cloud]"
        print "    add_glb_nodes     serviceid count [cloud]"
        print "    remove_nodes      serviceid count"
        print "    remove_glb_nodes  serviceid count"
        print "    sqldump           serviceid"
        print "    load_dump         serviceid filename"
        print "    migrate_nodes     serviceid origin_cloud:node_id:dest_cloud[,o_cloud:node_id:d_cloud]* [delay]"

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

        if command in ('add_nodes', 'add_glb_nodes', 'remove_nodes', 'remove_glb_nodes'):
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
            if (command == 'add_nodes') or (command == 'add_glb_nodes'):
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
                res = self.callmanager(sid, command, True, {'nodes': count,
                                                            'cloud': cloud})
            else:
                res = self.callmanager(sid, command, True, {'nodes': count})
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command

        if command == 'migrate_nodes':
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                print "ERROR: missing the service identifier argument after the sub-command name."
                sys.exit(1)

            self.check_service_id(sid)
            delay = None

            if len(sys.argv) < 4:
                print "ERROR: missing arguments to migrate_nodes sub-command."
                sys.exit(1)
            elif len(sys.argv) > 4:
                delay = sys.argv[4]
                if not isinstance(delay, int) or int(delay) < 0:
                    print "ERROR: delay argument must be a positive or null integer."
                delay = int(delay)
            elif len(sys.argv) > 5:
                print "ERROR: too many arguments to migrate_nodes sub-command."
                sys.exit(1)
            migration_plan = []
            migr_arg = sys.argv[3].split(',')
            for migrate_node in migr_arg:
                try:
                    from_cloud, node_id, dest_cloud = migrate_node.split(':')
                    migr_node = {'from_cloud': from_cloud, 'vmid': node_id, 'to_cloud': dest_cloud}
                    migration_plan.append(migr_node)
                except:
                    print "ERROR: format error on migration argument '%s'." % migrate_node
                    sys.exit(1)

            res = self.migrate_nodes(sid, migration_plan, delay)
            if 'error' in res:
                print "ERROR: %s" % (res['error'])
            else:
                print "Migration started..."

        if command == 'load_dump':
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                print "ERROR: missing the service identifier argument after the sub-command name."
                sys.exit(1)

            self.check_service_id(sid)
            if len(sys.argv) < 4:
                print "ERROR: missing arguments to load_dump."
                sys.exit(1)
            elif len(sys.argv) > 5:
                print "ERROR: too many arguments to migrate_nodes sub-command."
                sys.exit(1)
            filename = sys.argv[3]
            self.load_dump(sid, filename)
