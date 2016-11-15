
import sys
import logging
import argcomplete
import traceback

from .base import BaseClient
from .config import config
from .service import ServiceCmd


class FlinkCmd(ServiceCmd):

    def __init__(self, flink_parser, client):
        ServiceCmd.__init__(self, flink_parser, client, "flink",
                            [('count', 1)], # (role name, default number)
                            "Flink service sub-commands help")
        self._add_help(flink_parser) # defined in base class (ServiceCmd)


def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS Flink services.', logger)

    _flink_cmd = FlinkCmd(parser, cmd_client)

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
