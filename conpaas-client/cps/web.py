import os
import sys

from cps.base import BaseClient

class WebClient(BaseClient):

    def info(self, service_id):
        service = BaseClient.info(self, service_id)

        nodes = self.callmanager(service['sid'], "list_nodes", False, {})
        if 'error' in nodes:
            return 

        errmsg = ''

        for what in 'proxy', 'web', 'backend':
            print what,
            for proxy in nodes[what]:
                params = { 'serviceNodeId': proxy }
                details = self.callmanager(service['sid'], "get_node_info", False, params)
                if 'error' in details:
                    errmsg = errmsg + details['error'] + "\n"
                else:
                    print details['serviceNode']['ip'],

            print

        if errmsg:
            print 'WARNING: %s' % errmsg

    def upload_key(self, service_id, filename):
        contents = open(filename).read()

        files = [ ( 'key', filename, contents ) ]

        res = self.callmanager(service_id, "/", True, { 'method': "upload_authorized_key",  }, files)
        if 'error' in res:
            print res['error']
        else:
            print res['outcome']

    def upload_code(self, service_id, filename):
        contents = open(filename).read()

        files = [ ( 'code', filename, contents ) ]

        res = self.callmanager(service_id, "/", True, { 'method': "upload_code_version",  }, files)
        if 'error' in res:
            print res['error']
        else:
            print "Code version %(codeVersionId)s uploaded" % res

    def download_code(self, service_id, version):
        params = { 'codeVersionId': version }

        res = self.callmanager(service_id, "download_code_version", 
            False, params)

        if 'error' in res:
            print res['error']

        else:
            destfile = os.path.join(os.getenv('TMPDIR', '/tmp'), version) + '.tar.gz'
            open(destfile, 'w').write(res)
            print destfile, 'written'

    def migrate_nodes(self, service_id, migration_plan, delay=None):
        data = {}
        data['migration_plan'] = migration_plan
        if delay is not None:
            data['delay'] = delay
        res = self.callmanager(service_id, "migrate_nodes", True, data)
        return res

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    add_nodes         serviceid b w p [cloud]     # add    b backend, w web and p proxy nodes"
        print "    remove_nodes      serviceid b w p     # remove b backend, w web and p proxy nodes"
        print "    list_keys         serviceid           # list authorized SSH keys"
        print "    upload_key        serviceid filename  # upload an SSH key"
        print "    list_uploads      serviceid           # list uploaded code versions"
        print "    upload_code       serviceid filename  # upload a new code version"
        print "    download_code     serviceid version   # download a specific code version"
        # implemented in {php,java}.py
        print "    enable_code       serviceid version   # set a specific code version active"
        print "    migrate_nodes     serviceid from_cloud:vmid:to_cloud[,from_cloud:vmid:to_cloud]*  [delay]"

    def main(self, argv):
        command = argv[1]

        # Check serviceid for all the commands requiring one
        if command in ( 'add_nodes', 'remove_nodes', 'list_keys', 
                        'upload_key', 'list_uploads', 'upload_code',
                        'enable_code', 'download_code' ):
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
                
            self.check_service_id(sid)

        # Check provided filename for all the commands requiring one
        if command in ( 'upload_key', 'upload_code' ):
            try:
                filename = argv[3]
                if not (os.path.isfile(filename) and os.access(filename, os.R_OK)):
                    raise IndexError
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            getattr(self, command)(sid, filename)

        if command == 'list_keys':
            res = self.callmanager(sid, 'list_authorized_keys', False, {})
            for key in res['authorizedKeys']:
                print key

        if command == 'list_uploads':
            res = self.callmanager(sid, 'list_code_versions', False, {})

            def add_cur(row):
                if 'current' in row:
                    row['current'] = '      *'
                else:
                    row['current'] = ''
                return row

            data = [ add_cur(el) for el in res['codeVersions'] ]
            print self.prettytable(( 'current', 'codeVersionId', 'filename', 'description' ), data)

        if command in ( 'enable_code', 'download_code' ):
            try:
                code_version = argv[3]
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            getattr(self, command)(sid, code_version)
    
        if command in ( 'add_nodes', 'remove_nodes' ):
            try:
                params = {
                    'backend': int(argv[3]),
                    'web':     int(argv[4]),
                    'proxy':   int(argv[5])
                }
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            if command == 'add_nodes':
                if len(argv) == 6:
                    params['cloud'] = 'default'
                else:
                    params['cloud'] = argv[6]
            # call the method
            res = self.callmanager(sid, command, True, params)

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
