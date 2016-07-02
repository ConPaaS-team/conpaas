#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import sys

if sys.hexversion < 0x02070000:
    sys.exit("Python 2.7 or newer is required to run this program.")

import logging
import traceback
import argcomplete

from argparse import HelpFormatter

from .base import BaseClient
from .user import UserCmd
from .application import ApplicationCmd
from .service import ServiceCmd
from .mysql import MySQLCmd
# from .htc import HTCCmd
from .cloud import CloudCmd
from .java import JavaCmd
from .php import PHPCmd
from .config import config
# from .scalaris import ScalarisCmd
# from .selenium import SeleniumCmd
# from .taskfarm import TaskFarmCmd
from .xtreemfs import XtreemFSCmd
from .helloworld import HelloWorldCmd
from .generic import GenericCmd

CONF_FILE = "cps-tools.conf"


class HelpCmd:

    def __init__(self, subparsers, parser):
        #, aliases=['h'])
        subparser = subparsers.add_parser('help', help="display the help")
        subparser.set_defaults(run_cmd=self.help, parser=parser)

    def help(self, args):
        args.parser.print_help()


def format_help(prog):
    return HelpFormatter(prog, max_help_position=70)


def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    parser, argv = config('', logger)

    subparsers = parser.add_subparsers(help='',
                                       metavar="<sub-command>")

    cmd_client = BaseClient(logger)

    def add_sub_command(cmd_name, help_msg, cmd_class):
        subparser = subparsers.add_parser(cmd_name, help=help_msg,
                                          formatter_class=format_help)
        _sub_cmd = cmd_class(subparser, cmd_client)

    add_sub_command('user', "manage users", UserCmd)
    add_sub_command('cloud', "manage clouds", CloudCmd)
    add_sub_command('application', "manage applications", ApplicationCmd)
    add_sub_command('service', "manage services", ServiceCmd)
    add_sub_command('mysql', "manage MySQL services", MySQLCmd)
    # add_sub_command('htc', "manage HTC services", HTCCmd)
    add_sub_command('php', "manage PHP services", PHPCmd)
    add_sub_command('java', "manage Java services", JavaCmd)
    # add_sub_command('scalaris', "manage Scalaris services", ScalarisCmd)
    # add_sub_command('selenium', "manage Selenium services", SeleniumCmd)
    # add_sub_command('taskfarm', "manage TaskFarm services", TaskFarmCmd)
    add_sub_command('xtreemfs', "manage XtreemFS services", XtreemFSCmd)
    add_sub_command('helloworld', "manage HelloWorld services", HelloWorldCmd)
    add_sub_command('generic', "manage Generic services", GenericCmd)

    _help_cmd = HelpCmd(subparsers, parser)

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
