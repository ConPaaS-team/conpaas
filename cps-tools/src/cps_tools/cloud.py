
import argcomplete
import logging
import sys

from .base import BaseClient
from .config import config


def check_cloud(client, cloud_name):
    """
    Check if a given cloud name is valid, raise an exception otherwise.
    """

    if cloud_name is None:
        return

    clouds = client.call_director_get("available_clouds")

    if not cloud_name in clouds:
        raise Exception("Unknown cloud name '%s'" % cloud_name)


class CloudCmd:

    def __init__(self, parser, client):
        self.client = client

        self.subparsers = parser.add_subparsers(help=None, title=None,
                                                description=None,
                                                metavar="<sub-command>")
        self._add_list()
        self._add_list_resources()
        self._add_help(parser)

    def add_parser(self, *args, **kwargs):
        return self.subparsers.add_parser(*args, **kwargs)

    # ========== help
    def _add_help(self, parser):
        subparser = self.add_parser('help', help="show help")
        subparser.set_defaults(run_cmd=self.user_help, parser=parser)

    def user_help(self, args):
        args.parser.print_help()

    # ========== list
    def _add_list(self):
        subparser = self.add_parser('list', help="list clouds")
        subparser.set_defaults(run_cmd=self.list_cloud, parser=subparser)

    def list_cloud(self, _args):
        clouds = self.client.call_director_get("available_clouds")
        if clouds:
            for cloud in clouds:
                print("%s" % cloud)


    # ========== list
    def _add_list_resources(self):
        subparser = self.add_parser('list_resources', help="list resources")
        subparser.set_defaults(run_cmd=self.list_resources, parser=subparser)

    def list_resources(self, _args):
        resources = self.client.call_director_get("list_resources")
        if resources:
            print(self.client.prettytable(('rid', 'app_id', 'vmid', 'ip', 'role', 'cloud'), resources))
        else:
            print "No existing resources"


def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS clouds.', logger)

    _cloud_cmd = CloudCmd(parser, cmd_client)

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
