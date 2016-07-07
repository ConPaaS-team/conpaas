
import sys
import logging
import argcomplete
import traceback

from .base import BaseClient
from .config import config
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


def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS Java services.', logger)

    _java_cmd = JavaCmd(parser, cmd_client)

    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)
    cmd_client.set_config(args.director_url, args.username, args.password,
                          args.debug)
    try:
        args.run_cmd(args)
    except Exception:
        if args.debug:
            traceback.print_exc()
        else:
            ex = sys.exc_info()[1]
            if str(ex).startswith("ERROR"):
                sys.stderr.write("%s\n" % ex)
            else:
                sys.stderr.write("ERROR: %s\n" % ex)
        sys.exit(1)


if __name__ == '__main__':
    main()
