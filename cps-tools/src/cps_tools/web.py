import os
import sys

from .service import ServiceCmd


class WebCmd(ServiceCmd):

    def __init__(self, web_parser, client, service_type="web",
                 description="Web server service sub-commands help"):
        roles = [('backend', 1), ('proxy', 0), ('web', 0)] # (role name, default number)
        ServiceCmd.__init__(self, web_parser, client, service_type, roles,
                            description)
        self._add_upload_key()
        self._add_list_keys()
        self._add_upload_code()
        self._add_list_codes()
        self._add_download_code()
        self._add_delete_code()
        # self._add_migrate_nodes()

    # ========== upload_key
    def _add_upload_key(self):
        subparser = self.add_parser('upload_key',
                                    help="upload an SSH key to a service")
        subparser.set_defaults(run_cmd=self.upload_key, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('filename',
                               help="File containing the key")

    def upload_key(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        contents = open(args.filename).read()
        params = { 'service_id': service_id,
                   'method': "upload_authorized_key" }
        files = [('key', args.filename, contents)]
        res = self.client.call_manager_post(app_id, service_id, "/", params, files)

        print "%s." % res['outcome']

    # ========== list_keys
    def _add_list_keys(self):
        subparser = self.add_parser('list_keys',
                                    help="list the authorized SSH keys of a service")
        subparser.set_defaults(run_cmd=self.list_keys, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def list_keys(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "list_authorized_keys")

        for key in res['authorizedKeys']:
            print "%s" % key

    # ========== upload_code
    def _add_upload_code(self):
        subparser = self.add_parser('upload_code',
                                    help="upload a new code version")
        subparser.set_defaults(run_cmd=self.upload_code, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('filename',
                               help="File containing the code")

    def upload_code(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        params = { 'service_id': service_id,
                   'method': "upload_code_version" }
        contents = open(args.filename).read()
        files = [('code', args.filename, contents)]
        res = self.client.call_manager_post(app_id, service_id, "/", params, files)

        print "Code version '%(codeVersionId)s' uploaded." % res

    # ========== list_codes
    def _add_list_codes(self):
        subparser = self.add_parser('list_codes',
                                    help="list uploaded code versions")
        subparser.set_defaults(run_cmd=self.list_codes, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def list_codes(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "list_code_versions")

        code_versions = []
        for code in res['codeVersions']:
            if 'current' in code:
                code['current'] = '      *'
            else:
                code['current'] = ''
            code_versions.append(code)

        print self.client.prettytable(
                ( 'current', 'codeVersionId', 'filename', 'description' ),
                code_versions)

    # ========== download_code
    def _add_download_code(self):
        subparser = self.add_parser('download_code',
                                    help="download a specific code version")
        subparser.set_defaults(run_cmd=self.download_code, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('-v', '--version', metavar='CODE', default=None,
                               help="Version of code to download (default is the active one)")

    def download_code(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)
        destfile = self.check_code_version(app_id, service_id, args.version)

        if args.version:
            params = { 'codeVersionId': args.version }
        else:
            params = {}
        res = self.client.call_manager_get(app_id, service_id, "download_code_version",
                                           params)

        open(destfile, 'w').write(res)
        print "File '%s' written." % destfile

    def check_code_version(self, app_id, service_id, code_version):
        res = self.client.call_manager_get(app_id, service_id, "list_code_versions")

        if code_version:
            filenames = [ code['filename'] for code in res['codeVersions']
                    if code['codeVersionId'] == code_version ]
            if not filenames:
                raise Exception("Invalid code version '%s'" % code_version)

            return filenames[0]
        else:
            for code in res['codeVersions']:
                if 'current' in code:
                    return code['filename']

            raise Exception("There is no code version currently enabled.")

    # ========== delete_code
    def _add_delete_code(self):
        subparser = self.add_parser('delete_code',
                                    help="delete a specific code version")
        subparser.set_defaults(run_cmd=self.delete_code, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('code_version',
                               help="Code version to be deleted")

    def delete_code(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        code_version = args.code_version
        params = { 'codeVersionId': code_version }
        self.client.call_manager_post(app_id, service_id, "delete_code_version", params)

        print "Code version '%s' deleted." % code_version

    # ========== migrate_nodes
    def _add_migrate_nodes(self):
        subparser = self.add_parser('migrate_nodes', help="migrate nodes in Web service")
        subparser.set_defaults(run_cmd=self.migrate_nodes, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('nodes', metavar='c1:n:c2[,c1:n:c2]*',
                               help="Nodes to migrate: node n from cloud c1 to cloud c2")
        subparser.add_argument('--delay', '-d', metavar='SECONDS', type=int, default=0,
                               help="Delay in seconds before removing the original nodes")

    def migrate_nodes(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        if args.delay < 0:
            raise Exception("Cannot delay %s seconds." % args.delay)
        try:
            migr_all = args.nodes.split(',')
            nodes = []
            for migr in migr_all:
                from_cloud, vmid, to_cloud = migr.split(':')
                migr_dict = {'from_cloud': from_cloud,
                             'vmid': vmid,
                             'to_cloud': to_cloud}
                nodes.append(migr_dict)
        except:
            raise Exception('Argument "nodes" does not match format c1:n:c2[,c1:n:c2]*: %s' % args.nodes)

        data = {'migration_plan': nodes, 'delay': args.delay}
        self.client.call_manager_post(app_id, service_id, "migrate_nodes", data)

        if args.delay == 0:
            print("Migration of nodes %s has been successfully started"
                  " for Web service %s." % (args.nodes, service_id))
        else:
            print("Migration of nodes %s has been successfully started"
                  " for Web service %s with a delay of %s seconds."
                  % (args.nodes, service_id, args.delay))
