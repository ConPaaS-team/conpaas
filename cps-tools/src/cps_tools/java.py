
from .web import WebCmd


class JavaCmd(WebCmd):

    def __init__(self, java_parser, client):
        WebCmd.__init__(self, java_parser, client, "java",
                        "Java server sub-commands help")
        self._add_enable_code()


    # ========== enable_code
    def _add_enable_code(self):
        subparser = self.add_parser('enable_code',
                                    help="select Java code to enable")
        subparser.set_defaults(run_cmd=self.enable_code, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('code_version', help="Code version")

    def enable_code(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        code_version = args.code_version
        params = { 'codeVersionId': code_version }
        self.client.call_manager_post(app_id, service_id,
                                            "update_java_configuration",
                                            params)

        print "Enabling code version '%s'... " % code_version,
        sys.stdout.flush()

        state = self.client.wait_for_service_state(app_id, service_id,
                                ['INIT', 'STOPPED', 'RUNNING', 'ERROR'])
        if state != 'ERROR':
            print "done."
        else:
            print "FAILED!"
