
import sys
import logging
import argcomplete
import traceback

from .base import BaseClient
from .config import config
from .service import ServiceCmd


class HelloWorldCmd(ServiceCmd):

    def __init__(self, helloworld_parser, client):
        ServiceCmd.__init__(self, helloworld_parser, client, "helloworld",
                            [('count', 1)], # (role name, default number)
                            "HelloWorld service sub-commands help")
        self._add_get_helloworld()

    # ========== get_helloworld
    def _add_get_helloworld(self):
        subparser = self.add_parser('get_helloworld',
                                    help="test function of the HelloWorld service")
        subparser.set_defaults(run_cmd=self.get_helloworld, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def get_helloworld(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "get_helloworld")

        print res['helloworld']


def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS HelloWorld services.', logger)

    _helloworld_cmd = HelloWorldCmd(parser, cmd_client)

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
