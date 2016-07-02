# import argcomplete
# import logging
# import sys

# from .base import BaseClient
# from .config import config
# from .service import ServiceCmd


# class ScalarisCmd(ServiceCmd):

#     def __init__(self, parser, client):
#         ServiceCmd.__init__(self, parser, client, "scalaris", ['scalaris'],
#                             "Scalaris service sub-commands help")

#     def _add_add_nodes(self):
#         """Overrides ServiceCmd._add_add_nodes(self)."""
#         subparser = self.add_parser('add_nodes',
#                                     help="add scalaris nodes to a scalaris service")
#         subparser.set_defaults(run_cmd=self.add_nodes, parser=subparser)
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of the scalaris service")
#         for role in self.roles:
#             subparser.add_argument('--%s' % role, type=int, default=0,
#                                    help="Number of %s nodes to add" % role)
#         subparser.add_argument('--cloud', '-c', metavar='CLOUD_NAME',
#                                default='iaas',
#                                help="Name of the cloud in which the nodes are to be added.\n "
#                                     "Set to \'auto\' to automatically place nodes across multiple clouds.")

#     def add_nodes(self, args):
#         """Overrides ServiceCmd.add_nodes(self, args)."""
#         total_nodes, data = self._get_roles_nb(args)
#         if total_nodes <= 0:
#             self.client.error("Cannot add %s nodes." % total_nodes)
#         if args.cloud == "auto":
#             data['auto_placement'] = True
#             data['cloud'] = 'default'
#         else:
#             data['cloud'] = args.cloud
#         service_id = self.check_service(args.serv_name_or_id)
#         res = self.client.call_manager_post(service_id, "add_nodes", data)
#         if 'error' in res:
#             raise Exception("Could not add nodes to service %s: %s" % (service_id, res['error']))
#         else:
#             # TODO: display the following message only in verbose mode  ===> use logger.info() ?
#             print("Starting %s new nodes for service %s..."
#                   % (total_nodes, service_id))
#             state = self.client.wait_for_service_state(service_id, ['RUNNING', 'ERROR'])
#             if state in ['ERROR']:
#                 self.client.error("Failed to add nodes to service %s." % service_id)


# def main():
#     logger = logging.getLogger(__name__)
#     console = logging.StreamHandler()
#     formatter = logging.Formatter('%(levelname)s - %(message)s')
#     console.setFormatter(formatter)
#     logger.addHandler(console)

#     cmd_client = BaseClient(logger)

#     parser, argv = config('Manage ConPaaS PHP services.', logger)

#     _serv_cmd = ScalarisCmd(parser, cmd_client)

#     argcomplete.autocomplete(parser)
#     args = parser.parse_args(argv)
#     cmd_client.set_config(args.director_url, args.username, args.password,
#                           args.debug)
#     try:
#         args.run_cmd(args)
#     except:
#         e = sys.exc_info()[1]
#         sys.stderr.write("ERROR: %s\n" % e)
#         sys.exit(1)


# if __name__ == '__main__':
#     main()
