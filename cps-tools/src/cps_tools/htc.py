
# from .service import ServiceCmd


# class HTCCmd(ServiceCmd):

#     def __init__(self, htc_parser, client):
#         ServiceCmd.__init__(self, htc_parser, client, "htc",
#                             ['node'], "HTC service sub-commands help")
#         self._add_create_job()
#         self._add_upload_file()
#         self._add_add()
#         self._add_sample()
#         self._add_submit()
#         self._add_get_config()
#         self._add_throughput()
#         self._add_select()

#     # ========== remove_nodes
#     def _add_remove_nodes(self):
#         """Overrides ServiceCmd._add_remove_nodes(self)."""
#         subparser = self.add_parser('remove_nodes',
#                                     help="remove nodes from a service")
#         subparser.set_defaults(run_cmd=self.remove_nodes, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('node_id', help="Identifier of node to remove")

#     def remove_nodes(self, args):
#         """Overrides ServiceCmd.remove_nodes(self, args)."""
#         app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
#         data = {'node': 1, 'id': args.node_id}
#         res = self.client.call_manager_post(app_id, service_id, "remove_nodes", data)
#         if 'error' in res:
#             self.client.error("Could not remove node %s from service %s: %s"
#                               % (args.node_id, service_id, res['error']))
#         else:
#             print("Node %s has been successfully removed from service %s."
#                   % (args.node_id, service_id))


#     # ========== create_job
#     def _add_create_job(self):
#         subparser = self.add_parser('create_job', help="create a job")
#         subparser.set_defaults(run_cmd=self.create_job, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('filename', help="path to job file")

#     def create_job(self, args):
#         app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
#         with open(args.filename, 'r') as jobfile:
#             contents = jobfile.read()
#         files = [(args.filename, args.filename, contents)]
#         params = {'method': 'create_job'}
#         res = self.client.call_manager_post(app_id, service_id, "/", params, files)
#         if 'error' in res:
#             print res['error']
#         else:
#             print res['id']

#     # ========== upload_file
#     def _add_upload_file(self):
#         subparser = self.add_parser('upload_file', help="upload a file")
#         subparser.set_defaults(run_cmd=self.upload_file, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('filename', help="path to file")

#     def upload_file(self, args):
#         app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
#         with open(args.filename, 'r') as jobfile:
#             contents = jobfile.read()
#         files = [(args.filename, args.filename, contents)]
#         params = {'method': 'upload_file'}
#         res = self.client.call_manager_post(app_id, service_id, "/", params, files)
#         if 'error' in res:
#             print res['error']
#         else:
#             print res['out']

#     # ========== add
#     def _add_add(self):
#         subparser = self.add_parser('add', help="add tasks to a job")
#         subparser.set_defaults(run_cmd=self.add, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('job_id', type=int, help="Job identifier")
#         subparser.add_argument('filename', help="path to job file")

#     def add(self, args):
#         app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
#         with open(args.filename, 'r') as jobfile:
#             contents = jobfile.read()
#         files = [(args.filename, args.filename, contents)]
#         params = {'method': 'add', 'job_id': args.job_id}
#         res = self.client.call_manager_post(app_id, service_id, "/", params, files)
#         if 'error' in res:
#             print res['error']
#         else:
#             print res["id"]

#     # ========== sample
#     def _add_sample(self):
#         subparser = self.add_parser('sample', help="sample a job")
#         subparser.set_defaults(run_cmd=self.sample, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('job_id', type=int, help="Job identifier")

#     def sample(self, args):
#         app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
#         params = {'job_id': args.job_id}
#         res = self.client.call_manager_post(app_id, service_id, "sample", params)
#         if 'error' in res:
#             print res['error']
#         else:
#             print res["out"]

#     # ========== submit
#     def _add_submit(self):
#         subparser = self.add_parser('submit', help="execute a job")
#         subparser.set_defaults(run_cmd=self.submit, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('job_id', type=int, help="Job identifier")

#     def submit(self, args):
#         app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)

#         params = {'job_id': args.job_id}
#         res = self.client.call_manager_post(app_id, service_id, "execute", params)
#         if 'error' in res:
#             print res['error']
#         else:
#             print res['out']

#     # ========== get_config
#     def _add_get_config(self):
#         subparser = self.add_parser('get_config',
#                                     help="get configuration for a throughput")
#         subparser.set_defaults(run_cmd=self.get_config, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('throughput', type=int, help="target throughput")

#     def get_config(self, args):
#         app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
#         params = {'t': args.throughput}
#         res = self.client.call_manager_post(app_id, service_id, "get_config", params)
#         print "%s" % res

#     # ========== throughput
#     def _add_throughput(self):
#         subparser = self.add_parser('throughput', help="throughput (??)")
#         subparser.set_defaults(run_cmd=self.get_config, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('throughput', type=int, help="target throughput")

#     def throughput(self, args):
#         app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
#         params = {'t': args.throughput}
#         res = self.client.call_manager_post(app_id, service_id, "get_m", params)
#         print "%s" % res

#     # ========== select
#     def _add_select(self):
#         subparser = self.add_parser('select', help="select a throughput")
#         subparser.set_defaults(run_cmd=self.get_config, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('throughput', type=int, help="target throughput")

#     def select(self, args):
#         app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
#         params = {'t': args.throughput}
#         res = self.client.call_manager_post(app_id, service_id, "select", params)
#         print "%s" % res
