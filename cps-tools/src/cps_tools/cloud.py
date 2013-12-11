
import argcomplete
import logging
import sys

from .base import BaseClient
from .config import config


def check_cloud_name(client, cloud_name_or_id):
    """
    Check if a given cloud name is a valid name or a valid
    cloud identifier.

    :return  a pair (cloud_identifier, cloud_name) if correct,
             raise an exception otherwise.
    """

    if cloud_name_or_id is None:
        return (None, None)

    clouds = client.call_director("available_clouds", True)
    cloud_ids = [cloud['cid'] for cloud in clouds]

    try:
        cloud_id = int(cloud_name_or_id)
    except ValueError:
        cloud_ids = [cloud['cid'] for cloud in clouds
                     if cloud['name'] == cloud_name_or_id]
        if len(cloud_ids) == 0:
            client.error('Unknown cloud \'%s\'' % cloud_name_or_id)
        elif len(cloud_ids) > 1:
            raise Exception('%s clouds match the cloud name \'%s\''
                            % (len(cloud_ids), cloud_name_or_id))
        else:
            cloud_id = cloud_ids[0]

    if not cloud_id in cloud_ids:
        raise Exception('Unknown cloud identifier \'%s\'' % cloud_id)

    cloud_name = [cloud['name'] for cloud in clouds
                  if cloud['cid'] == cloud_id][0]

    return cloud_id, cloud_name


class CloudCmd:

    def __init__(self, parser, client):
        self.client = client

        self.subparsers = parser.add_subparsers(help=None, title=None,
                                                description=None,
                                                metavar="<sub-command>")
        self._add_list()
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
    except Exception, ex:
        sys.stderr.write("ERROR: %s\n" % ex)
        sys.exit(1)

if __name__ == '__main__':
    main()
