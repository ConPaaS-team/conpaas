import os
import sys

from .service import ServiceCmd


class GenericCmd(ServiceCmd):

    def __init__(self, generic_parser, client):
        ServiceCmd.__init__(self, generic_parser, client, "generic",
                            ['count'], "Generic service sub-commands help")
        self._add_upload_code()
        self._add_list_uploads()
        self._add_download_code()
        self._add_enable_code()
        self._add_delete_code()
        self._add_run()

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
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
        filename = args.filename
        if not (os.path.isfile(filename) and os.access(filename, os.R_OK)):
            self.client.error("Cannot upload code: filename %s not found or "
                              "access is denied" % filename)

        contents = open(filename).read()
        files = [ ( 'code', filename, contents ) ]

        res = self.client.call_manager_post(app_id, service_id,  "/",
                                            {'method': "upload_code_version", },
                                            files)
        if 'error' in res:
            print res['error']
        else:
            print "Code version %(codeVersionId)s uploaded" % res



    # ========== list_uploads
    def _add_list_uploads(self):
        subparser = self.add_parser('list_uploads',
                                    help="list uploaded code versions")
        subparser.set_defaults(run_cmd=self.list_uploads, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def list_uploads(self, args):
        
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "list_code_versions")

        if 'error' in res:
            self.client.error("Cannot list code versions: %s" % res['error'])

        for code in res['codeVersions']:
            current = "*" if 'current' in code else ""
            print " %s %s: %s \"%s\"" % (current, code['codeVersionId'],
                                         code['filename'], code['description'])


    # ========== download_code
    def _add_download_code(self):
        subparser = self.add_parser('download_code',
                                    help="download code from Generic service")
        subparser.set_defaults(run_cmd=self.download_code, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        # TODO: make version optional to retrieve the last version by default
        subparser.add_argument('version',
                               help="Version of code to download")

    def download_code(self, args):
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "list_code_versions")

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
        res = self.client.call_manager_get(app_id, service_id, "download_code_version",
                                           params)

        if 'error' in res:
            self.client.error("Cannot download code: %s" % res['error'])

        else:
            open(destfile, 'w').write(res)
            print destfile, 'written'

    # ========== enable_code
    def _add_enable_code(self):
        subparser = self.add_parser('enable_code',
                                    help="set a specific code version active")
        subparser.set_defaults(run_cmd=self.enable_code, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('code_version',
                               help="Code version to be activated")

    def enable_code(self, args):
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
        code_version = args.code_version

        params = { 'codeVersionId': code_version }

        res = self.client.call_manager_post(app_id, service_id, "enable_code", params)

        if 'error' in res:
            print res['error']
        else:
            print code_version, 'enabled'

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
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
        code_version = args.code_version

        params = { 'codeVersionId': code_version }

        res = self.client.call_manager_post(app_id, service_id, "delete_code_version", params)

        if 'error' in res:
            print res['error']
        else:
            print code_version, 'deleted'

    # ========== run
    def _add_run(self):
        subparser = self.add_parser('run',
                                    help="deploy the application")
        subparser.set_defaults(run_cmd=self.run, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def run(self, args):
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_post(app_id, service_id, "run")

        if 'error' in res:
            print res['error']
        else:
            print 'Service running'
