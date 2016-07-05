import os
import sys

from .service import ServiceCmd


class GenericCmd(ServiceCmd):

    def __init__(self, generic_parser, client):
        ServiceCmd.__init__(self, generic_parser, client, "generic",
                            ['node'], "Generic service sub-commands help")
        self._add_upload_key()
        self._add_list_keys()
        self._add_upload_code()
        self._add_list_codes()
        self._add_download_code()
        self._add_enable_code()
        self._add_delete_code()
        self._add_run()
        self._add_interrupt()
        self._add_cleanup()
        self._add_get_script_status()

    # ========== upload_key
    def _add_upload_key(self):
        subparser = self.add_parser('upload_key',
                                    help="upload key to Generic server")
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

        print res['outcome']

    # ========== list_keys
    def _add_list_keys(self):
        subparser = self.add_parser('list_keys',
                                    help="list authorized keys of Generic service")
        subparser.set_defaults(run_cmd=self.list_keys, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def list_keys(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "list_authorized_keys")

        print "%s" % res['authorizedKeys']

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

        filename = args.filename
        if not (os.path.isfile(filename) and os.access(filename, os.R_OK)):
            raise Exception("Cannot upload code: filename '%s' not found or "
                            "access is denied" % filename)

        params = { 'service_id': service_id,
                   'method': "upload_code_version" }
        contents = open(filename).read()
        files = [ ( 'code', filename, contents ) ]

        res = self.client.call_manager_post(app_id, service_id, "/", params, files)

        print "Code version %(codeVersionId)s uploaded" % res

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
                                    help="download code from Generic service")
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

            raise Exception("There is no code version currently enabled")

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
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)
        code_version = args.code_version

        params = { 'codeVersionId': code_version }
        self.client.call_manager_post(app_id, service_id, "enable_code", params)

        print "Enabling code version '%s'... " % code_version,
        sys.stdout.flush()

        state = self.client.wait_for_service_state(app_id, service_id,
                                ['INIT', 'STOPPED', 'RUNNING', 'ERROR'])
        if state != 'ERROR':
            print "done."
        else:
            print "FAILED!"

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

        print code_version, 'deleted'

    # ========== run
    def _add_run(self):
        subparser = self.add_parser('run',
                                    help="execute the run.sh script")
        subparser.set_defaults(run_cmd=self.run, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('-p', '--parameters', metavar='PARAM',
                               default='', help="parameters for the script")

    def run(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        params = { 'command': 'run', 'parameters': args.parameters }
        self.client.call_manager_post(app_id, service_id, "execute_script", params)

        print "Service started executing 'run.sh' on all the agents."

    # ========== interrupt
    def _add_interrupt(self):
        subparser = self.add_parser('interrupt',
                                    help="execute the interrupt.sh script")
        subparser.set_defaults(run_cmd=self.interrupt, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('-p', '--parameters', metavar='PARAM',
                               default='', help="parameters for the script")

    def interrupt(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        params = { 'command': 'interrupt', 'parameters': args.parameters }
        self.client.call_manager_post(app_id, service_id, "execute_script", params)

        print "Service started executing 'interrupt.sh' on all the agents"\
              " or killing all scripts if 'interrupt.sh' is already running."

    # ========== cleanup
    def _add_cleanup(self):
        subparser = self.add_parser('cleanup',
                                    help="execute the cleanup.sh script")
        subparser.set_defaults(run_cmd=self.cleanup, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('-p', '--parameters', metavar='PARAM',
                               default='', help="parameters for the script")

    def cleanup(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        params = { 'command': 'cleanup', 'parameters': args.parameters }
        self.client.call_manager_post(app_id, service_id, "execute_script", params)

        print "Service started executing 'cleanup.sh' on all the agents."

    # ========== get_script_status
    def _add_get_script_status(self):
        subparser = self.add_parser('get_script_status',
                                    help="get the status of the scripts for each agent")
        subparser.set_defaults(run_cmd=self.get_script_status, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def get_script_status(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "get_script_status")

        if res['agents']:
            print
            for agent in sorted(res['agents']):
                print "Agent %s:" % agent
                status = res['agents'][agent]
                for script in ('init.sh', 'notify.sh', 'run.sh',
                                'interrupt.sh', 'cleanup.sh'):
                    print "  %s\t%s" % (script, status[script])
                print
        else:
            print "No generic agents are running"
