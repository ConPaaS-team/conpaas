import os
import sys

from .service import ServiceCmd


class WebCmd(ServiceCmd):

    def __init__(self, web_parser, client, service_type="web",
                 description="Web server service sub-commands help"):
        roles = ['backend', 'proxy', 'web']
        ServiceCmd.__init__(self, web_parser, client, service_type, roles,
                            description)
        self._add_upload_key()
        self._add_list_keys()
        self._add_upload_code()
        self._add_list_codes()
        self._add_download_code()
        self._add_migrate_nodes()

    # ========== upload_key
    def _add_upload_key(self):
        subparser = self.add_parser('upload_key',
                                    help="upload key to Web server")
        subparser.set_defaults(run_cmd=self.upload_key, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('filename',
                               help="File containing the key")

    def upload_key(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        contents = open(args.filename).read()
        params = {'method': "upload_authorized_key"}
        files = [('key', args.filename, contents)]
        res = self.client.call_manager_post(service_id, "/", params, files)
        if 'error' in res:
            print res['error']
        else:
            print res['outcome']

    # ========== list_keys
    def _add_list_keys(self):
        subparser = self.add_parser('list_keys',
                                    help="list authorized keys of Web service")
        subparser.set_defaults(run_cmd=self.list_keys, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def list_keys(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        res = self.client.call_manager_get(service_id, "list_authorized_keys")

        if 'error' in res:
            self.client.error("Cannot list keys: %s" % res['error'])
        else:
            print "%s" % res['authorizedKeys']

    # ========== upload_code
    def _add_upload_code(self):
        subparser = self.add_parser('upload_code',
                                    help="upload code to Web server")
        subparser.set_defaults(run_cmd=self.upload_code, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('filename',
                               help="File containing the code")

    def upload_code(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        contents = open(args.filename).read()

        files = [('code', args.filename, contents)]

        res = self.client.call_manager_post(service_id, "/",
                                            {'method': "upload_code_version", },
                                            files)
        if 'error' in res:
            self.client.error("Cannot upload code: %s" % res['error'])
        else:
            print "Code version %(codeVersionId)s uploaded" % res

    # ========== list_codes
    def _add_list_codes(self):
        subparser = self.add_parser('list_codes',
                                    help="list code versions from web service")
        subparser.set_defaults(run_cmd=self.list_codes, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def list_codes(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        res = self.client.call_manager_get(service_id, "list_code_versions")

        if 'error' in res:
            self.client.error("Cannot list code versions: %s" % res['error'])

        for code in res['codeVersions']:
            current = "*" if 'current' in code else ""
            print " %s %s: %s \"%s\"" % (current, code['codeVersionId'],
                                         code['filename'], code['description'])

    # ========== download_code
    def _add_download_code(self):
        subparser = self.add_parser('download_code',
                                    help="download code from Web server")
        subparser.set_defaults(run_cmd=self.download_code, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        # TODO: make version optional to retrieve the last version by default
        subparser.add_argument('version',
                               help="Version of code to download")

    def download_code(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)

        res = self.client.call_manager_get(service_id, "list_code_versions")

        if 'error' in res:
            self.client.error("Cannot list code versions: %s" % res['error'])
            sys.exit(0)

        filenames = [ code['filename'] for code in res['codeVersions']
                if code['codeVersionId'] == args.version ]
        if not filenames:
            self.client.error("Cannot download code: invalid version %s" % args.version)
            sys.exit(0)

        destfile = filenames[0]

        params = {'codeVersionId': args.version}
        res = self.client.call_manager_get(service_id, "download_code_version",
                                           params)

        if 'error' in res:
            self.client.error("Cannot download code: %s" % res['error'])

        else:
            open(destfile, 'w').write(res)
            print destfile, 'written'

    # ========== migrate_nodes
    def _add_migrate_nodes(self):
        subparser = self.add_parser('migrate_nodes', help="migrate nodes in Web service")
        subparser.set_defaults(run_cmd=self.migrate_nodes, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('nodes', metavar='c1:n:c2[,c1:n:c2]*',
                               help="Nodes to migrate: node n from cloud c1 to cloud c2")
        subparser.add_argument('--delay', '-d', metavar='SECONDS', type=int, default=0,
                               help="Delay in seconds before removing the original nodes")

    def migrate_nodes(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        if args.delay < 0:
            self.client.error("Cannot delay %s seconds." % args.delay)
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
            self.client.error('Argument "nodes" does not match format c1:n:c2[,c1:n:c2]*: %s' % args.nodes)

        data = {'migration_plan': nodes, 'delay': args.delay}
        res = self.client.call_manager_post(service_id, "migrate_nodes", data)
        if 'error' in res:
            self.client.error("Could not migrate nodes in Web service %s: %s"
                              % (service_id, res['error']))
        else:
            if args.delay == 0:
                print("Migration of nodes %s has been successfully started"
                      " for Web service %s." % (args.nodes, service_id))
            else:
                print("Migration of nodes %s has been successfully started"
                      " for Web service %s with a delay of %s seconds."
                      % (args.nodes, service_id, args.delay))
