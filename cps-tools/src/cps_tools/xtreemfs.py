
import argcomplete
import logging
import sys

from .base import BaseClient
from .config import config
from .service import ServiceCmd

POLICIES = {'osd_sel': {'list': 'list_osd_sel_policies',
                        'set': 'set_osd_sel_policy',
                        },
            'replica_sel': {'list': 'list_replica_sel_policies',
                            'set': 'set_replica_sel_policy',
                            },
            'replication': {'list': 'list_replication_policies',
                            'set': 'set_replication_policy',
                            },
            }


class XtreemFSCmd(ServiceCmd):

    def __init__(self, xtreemfs_parser, client):
        ServiceCmd.__init__(self, xtreemfs_parser, client, "xtreemfs",
                            ['osd', 'mrc', 'dir'],
                            "XtreemFS service sub-commands help")
        self._add_add_volume()
        self._add_list_volumes()
        self._add_remove_volume()
        self._add_list_policies()
        self._add_set_policy()
        self._add_toggle_persistent()
        self._add_set_osd_size()

    # ========== list_volumes
    def _add_list_volumes(self):
        subparser = self.add_parser('list_volumes',
                                    help="list volumes of an XtreemFS service")
        subparser.set_defaults(run_cmd=self.list_volumes, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def list_volumes(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        res = self.client.call_manager_get(service_id, "listVolumes")
        if 'error' in res:
            self.client.error("Could not list volumes: %s" % res['error'])
        else:
            print "%s" % res['volumes']

    # ========== add_volume
    def _add_add_volume(self):
        subparser = self.add_parser('add_volume',
                                    help="add a volume to XtreemFS service")
        subparser.set_defaults(run_cmd=self.add_volume, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('volume_name', help="Name of volume")

    def add_volume(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        data = {'volumeName': args.volume_name}
        res = self.client.call_manager_post(service_id, "createVolume", data)
        if 'error' in res:
            self.client.error("Could not add volume to XtreemFS service %d: %s"
                              % (service_id, res['error']))
        else:
            # TODO: display the following message only in verbose mode  ===> use self.client.info() ?
            print("Volume %s has been added." % args.volume_name)

    # ========== remove_volume
    def _add_remove_volume(self):
        subparser = self.add_parser('remove_volume',
                                    help="remove volume from XtreemFS service")
        subparser.set_defaults(run_cmd=self.remove_volume, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('volume_name', help="Name of volume")

    def remove_volume(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        data = {'volumeName': args.volume_name}
        res = self.client.call_manager_post(service_id, "deleteVolume", data)
        if 'error' in res:
            self.client.error("Could not remove volume %s from XtreemFS service %d: %s"
                              % (args.volume_name, service_id, res['error']))
        else:
            print("Volume %s has been successfully removed from XtreemFS service %d."
                  % (args.volume_name, service_id))

    # ========== list_policies
    def _add_list_policies(self):
        subparser = self.add_parser('list_policies',
                                    help="List XtreemFS policies")
        subparser.set_defaults(run_cmd=self.list_policies, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('policy_type', choices=POLICIES.keys(),
                               help="Type of XtreemFS policy.")

    def list_policies(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        res = self.client.call_manager_get(service_id, POLICIES[args.policy_type]['list'])
        if 'error' in res:
            self.client.error('Could not list XtreemFS policies'
                              ' for service id %s'
                              ' for policy type %s'
                              ': %s'
                              % (service_id, args.policy_type, res['error']))
        else:
            print '%s' % res['policies']

    # ========== set_policy
    def _add_set_policy(self):
        subparser = self.add_parser('set_policy',
                                    help="Set an XtreemFS policy")
        subparser.set_defaults(run_cmd=self.set_policy, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('policy_type', choices=POLICIES.keys(),
                               help="Type of XtreemFS policy.")

    def set_policy(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        res = self.client.call_manager_post(service_id, POLICIES[args.policy_type]['set'])
        if 'error' in res:
            self.client.error('Could not set XtreemFS policy'
                              ' for service id %s'
                              ' for policy type %s'
                              ': %s'
                              % (service_id, args.policy_type, res['error']))
        else:
            print '%s' % res['stdout']

    # ========== toggle_persistent
    def _add_toggle_persistent(self):
        subparser = self.add_parser('toggle_persistent',
                                    help="Toggle persistency of an XtreemFS service")
        subparser.set_defaults(run_cmd=self.toggle_persistent, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def toggle_persistent(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        res = self.client.call_manager_post(service_id, 'toggle_persistent')
        if 'error' in res:
            self.client.error('Could not set XtreemFS policy'
                              ' for service id %s'
                              ' for policy type %s'
                              ': %s'
                              % (service_id, args.policy_type, res['error']))
        else:
            print '%s' % res['stdout']

    # ========== set_osd_size
    def _add_set_osd_size(self):
        subparser = self.add_parser('set_osd_size',
                                    help="Set a new size for an XtreemFS volume")
        subparser.set_defaults(run_cmd=self.set_osd_size, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('volume_size', type=int,
                               help="Size of volume in MB.")

    def set_osd_size(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        if args.volume_size <= 0:
            self.client.error('Cannot resize a volume to %s MB.' % args.volume_size)
        data = {'size': args.volume_size}
        res = self.client.call_manager_post(service_id, 'set_osd_size', data)
        if 'error' in res:
            self.client.error('Could not set XtreemFS volume size'
                              ' for service id %s'
                              ' for policy type %s'
                              ': %s'
                              % (service_id, args.policy_type, res['error']))
        else:
            print "OSD volume size is now %s MBs" % res['osd_volume_size']


def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS PHP services.', logger)

    _serv_cmd = XtreemFSCmd(parser, cmd_client)

    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)
    cmd_client.set_config(args.director_url, args.username, args.password,
                          args.debug)
    try:
        args.run_cmd(args)
    except:
        e = sys.exc_info()[1]
        sys.stderr.write("ERROR: %s\n" % e)
        sys.exit(1)

if __name__ == '__main__':
    main()
