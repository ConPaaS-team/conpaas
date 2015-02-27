import sys
import os

from cps.base import BaseClient

class Client(BaseClient):

    def info(self, service_id):
        service = BaseClient.info(self, service_id)

        nodes = self.callmanager(service['sid'], "list_nodes", False, {})
        if 'master' in nodes and nodes['master']:
            # Only one master
            master = nodes['master'][0]
            params = { 'serviceNodeId': master }
            details = self.callmanager(service['sid'], "get_node_info", False, params)
            print "master:", details['serviceNode']['ip']

        if 'node' in nodes:
            # Multiple nodes
            for node in nodes['node']:
                params = { 'serviceNodeId': node }
                details = self.callmanager(service['sid'], "get_node_info", False, params)
                print "node:", details['serviceNode']['ip']

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    add_nodes         serviceid count"
        print "    remove_nodes      serviceid count"
        print "    upload_code       serviceid filename  # upload a new code version"
        print "    list_keys         serviceid           # list authorized SSH keys"
        print "    upload_key        serviceid filename  # upload an SSH key"
        print "    list_uploads      serviceid           # list uploaded code versions"
        print "    download_code     serviceid version   # download a specific code version"
        print "    enable_code       serviceid version   # set a specific code version active"
        print "    delete_code       serviceid version   # delete a specific code version"
        print "    list_volumes      serviceid           # list the volumes in use by the Generic agents"
        print "    create_volume     serviceid vol_name size(MB) agent_id # create a volume and attatch it to a Generic agent"
        print "    delete_volume     serviceid vol_name  # detach and delete a volume"
        print "    run               serviceid           # execute the run.sh script"
        print "    interrupt         serviceid           # execute the interrupt.sh script"
        print "    cleanup           serviceid           # execute the cleanup.sh script"

    def main(self, argv):
        command = argv[1]

        if command in ( 'add_nodes', 'remove_nodes', 'list_keys',
                        'upload_key', 'upload_code', 'list_uploads',
                        'download_code', 'enable_code', 'delete_code',
                        'list_volumes', 'create_volume', 'delete_volume',
                        'run', 'interrupt', 'cleanup' ):
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            self.check_service_id(sid)


        if command in ( 'add_nodes', 'remove_nodes'):
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

        if command in ( 'enable_code', 'download_code', 'delete_code' ):
            try:
                code_version = argv[3]
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            getattr(self, command)(sid, code_version)

        if command == 'list_volumes':
            res = self.callmanager(sid, 'list_volumes', False, {})
            if 'error' in res:
                print res['error']
            elif res['volumes']:
                print self.prettytable(( 'volumeName', 'volumeSize',
                                         'agentId' ), res['volumes'])
            else:
                print 'No volumes defined'

        if command == 'create_volume':
            try:
                volumeName = argv[3]
                volumeSize = argv[4]
                agentId = argv[5]
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            getattr(self, command)(sid, volumeName, volumeSize, agentId)

        if command == 'delete_volume':
            try:
                volumeName = argv[3]
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            getattr(self, command)(sid, volumeName)

        if command in ( 'run', 'interrupt', 'cleanup' ):
            self.execute_script(sid, command)


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
        res = self.callmanager(service_id, 'list_code_versions', False, {})

        if 'error' in res:
            print res['error']
            sys.exit(0)

        filenames = [ code['filename'] for code in res['codeVersions']
                if code['codeVersionId'] == version ]

        if not filenames:
            print "ERROR: Cannot download code: invalid version %s" % version
            sys.exit(0)

        destfile = filenames[0]

        params = { 'codeVersionId': version }
        res = self.callmanager(service_id, "download_code_version",
            False, params)

        if 'error' in res:
            print res['error']

        else:
            open(destfile, 'w').write(res)
            print destfile, 'written'


    def enable_code(self, service_id, code_version):
        params = { 'codeVersionId': code_version }

        res = self.callmanager(service_id, "enable_code",
            True, params)

        if 'error' in res:
            print res['error']

        else:
            print code_version, 'enabled'


    def delete_code(self, service_id, code_version):
        params = { 'codeVersionId': code_version }

        res = self.callmanager(service_id, "delete_code_version",
            True, params)

        if 'error' in res:
            print res['error']

        else:
            print code_version, 'deleted'


    def create_volume(self, service_id, volumeName, volumeSize, agentId):
        params = { 'volumeName': volumeName,
                   'volumeSize': volumeSize,
                   'agentId': agentId}

        res = self.callmanager(service_id, "generic_create_volume",
            True, params)

        if 'error' in res:
            print 'E: %s' % res['error']
        else:
            print ("Creating volume %s and attaching it to %s... " %
                    (volumeName, agentId))
            sys.stdout.flush()

            self.wait_for_state(service_id, "RUNNING")

            print "done."
            sys.stdout.flush()


    def delete_volume(self, service_id, volumeName):
        params = { 'volumeName': volumeName }

        res = self.callmanager(service_id, "generic_delete_volume",
            True, params)

        if 'error' in res:
            print 'E: %s' % res['error']
        else:
            print ("Detaching and deleting volume %s... " %
                    volumeName)
            sys.stdout.flush()

            self.wait_for_state(service_id, "RUNNING")

            print "done."
            sys.stdout.flush()


    def execute_script(self, service_id, command):
        params = { 'command': command }
        res = self.callmanager(service_id, "execute_script", True, params)

        if 'error' in res:
            print res['error']
        else:
            print ("Service started executing '%s.sh' on all the agents..."
                    % command)
