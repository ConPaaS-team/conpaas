# import argcomplete
# import httplib
# import logging
# import simplejson
# import sys
# import urllib2
# from time import strftime, localtime

# from conpaas.core import https

# from .base import BaseClient
# from .config import config
# from .service import ServiceCmd


# MODES = ['DEMO', 'REAL']
# TASKFARM_MNG_PORT = 8475


# def http_jsonrpc_post(hostname, uri, method, port=TASKFARM_MNG_PORT, params=None):
#     """Perform a plain HTTP JSON RPC post (for task farming)"""
#     if params is None:
#         params = {}
#     url = "http://%s:%s%s" % (hostname, port, uri)
#     data = simplejson.dumps({'method': method,
#                              'params': params,
#                              'jsonrpc': '2.0',
#                              'id': 1,
#                              })
#     req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
#     res = urllib2.urlopen(req).read()
#     return res


# def http_file_upload_post(host, uri, port=TASKFARM_MNG_PORT, params=None, files=None):
#     """Perform a plain HTTP file upload post (for task farming)"""
#     if params is None:
#         params = {}
#     if files is None:
#         files = []
#     content_type, body = https.client._encode_multipart_formdata(params, files)
#     h = httplib.HTTP(host, port)
#     h.putrequest('POST', uri)
#     h.putheader('content-type', content_type)
#     h.putheader('content-length', str(len(body)))
#     h.endheaders()
#     h.send(body)
#     _errcode, _errmsg, _headers = h.getreply()
#     return h.file.read()


# class TaskFarmCmd(ServiceCmd):

#     def __init__(self, parser, client):
#         self.initial_expected_state = 'RUNNING'
#         ServiceCmd.__init__(self, parser, client, "taskfarm", ['node'],
#                             "TaskFarm service sub-commands help")
#         self._add_get_mode()
#         self._add_set_mode()
#         self._add_upload()
#         self._add_select_schedule()

#     def call_manager(self, app_id, service_id, method, data=None):
#         """TaskFarm peculiarities:

#         1) it works via plain HTTP
#         2) it uses port 8475
#         3) the 'shutdown' method is called 'terminate_workers'
#         4) it accepts only POST requests
#         5) it does not have to be started or stopped
#         """
#         if data is None:
#             data = {}
#         if method == "shutdown":
#             method = "terminate_workers"


#         service = self.client.service_dict(app_id, service_id)
#         res = http_jsonrpc_post(service['application']['manager'], '/', method, params=data)

#         try:
#             data = simplejson.loads(res[1])
#         except ValueError:
#             data = simplejson.loads(res)

#         return data.get('result', data)

#     def _add_start(self):
#         """
#         TaskFarm does not have to be started.
#         Overrides ServiceCmd._add_start().
#         """
#         pass

#     def _add_stop(self):
#         """
#         TaskFarm does not have to be stopped.
#         Overrides ServiceCmd._add_stop()
#         """
#         pass

#     def _print_res(self, res):
#         resres = res['result']
#         if 'error' in resres:
#             self.client.error("%s" % resres['error'])
#         elif 'message' in resres:
#             print "%s" % resres['message']
#         else:
#             print "%s" % res



#     # ======= get_mode
#     def _add_get_mode(self):
#         subparser = self.add_parser('get_mode', help="get TaskFarm mode")
#         subparser.set_defaults(run_cmd=self.get_mode, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")

#     def get_mode(self, args):
#         app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)
#         mode = self.get_string_mode(app_id, service_id)
#         print "%s" % mode

#     def get_string_mode(self, app_id, service_id):
#         res = self.call_manager(app_id, service_id, "get_service_info")
#         return res['mode']

#     # ======= set_mode
#     def _add_set_mode(self):
#         subparser = self.add_parser('set_mode', help="set TaskFarm mode")
#         subparser.set_defaults(run_cmd=self.set_mode, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('mode', choices=MODES, help="mode")

#     def set_mode(self, args):
#         app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)
#         old_mode = self.get_string_mode(app_id, service_id)
#         if old_mode != 'NA':
#             res = {'result': {'error': 'ERROR: mode is already set to %s' % old_mode}}
#         else:
#             res = self.call_manager(app_id, service_id, "set_service_mode", [args.mode])
#         self._print_res(res)

#     # ========== upload bag of tasks
#     def _add_upload(self):
#         subparser = self.add_parser('upload_bot', help="upload bag of tasks")
#         subparser.set_defaults(run_cmd=self.upload_bag_of_tasks,
#                                parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('filename',
#                                help="file containing the bag of tasks")
#         subparser.add_argument('location',
#                                help="XtreemFS location, e.g., 192.168.122.1/uc3")

#     def upload_bag_of_tasks(self, args):
#         app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)
#         mode = self.get_string_mode(app_id, service_id)
#         if mode == 'NA':
#             res = {'result': {'error': 'ERROR: to upload bag of task, first specify run mode.'}}
#         else:
#             service = self.client.service_dict(app_id, service_id)
#             params = {'uriLocation': args.location,
#                       'method': 'start_sampling'}
#             filecontents = open(args.filename).read()
#             res = http_file_upload_post(service['application']['manager'], '/', params=params,
#                                         files=[('botFile', args.filename, filecontents)])
#             res = simplejson.loads(res)
#         self._print_res(res)

#     # ========= select_schedule
#     def _add_select_schedule(self):
#         subparser = self.add_parser('upload_bot', help="upload bag of tasks")
#         subparser.set_defaults(run_cmd=self.select_schedule, parser=subparser)
#         subparser.add_argument('app_name_or_id',
#                                help="Name or identifier of an application")
#         subparser.add_argument('serv_name_or_id',
#                                help="Name or identifier of a service")
#         subparser.add_argument('schedule', type=int, help="schedule identifier")

#     def _select_schedule(self, args):
#         app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)
#         mode = self.get_mode(app_id, service_id)
#         if mode == 'NA':
#             return {'result': {'error': 'ERROR: to select a schedule, first specify run mode DEMO or REAL, then upload a bag of tasks '}}
#         # check schedule availability
#         res = self.call_manager(app_id, service_id, "get_service_info")
#         if res['noCompletedTasks'] == 0:
#             return {'message': "No schedule available yet: try again later..."}
#         if res['state'] != 'RUNNING':
#             return {'message': "Busy %s: try again later..." % res['phase']}
#         sres = self.call_manager(app_id, service_id, "get_sampling_results")
#         sdata = simplejson.loads(sres)
#         if 'timestamp' in sdata:
#             # Sampling is ready, check if bag is ready, or if we have to choose a schedule
#             ts = sdata['timestamp']
#             print strftime("Bag sampled on %a %d %b %Y at %H:%M:%S %Z", localtime(ts / 1000))
#             if 'schedules' in sdata:
#                 #sch = sdata['schedules']
#                 #ss = simplejson.dumps(sch)
#                 # print "schedules: ", ss
#                 numscheds = len(sdata['schedules'])
#                 if numscheds == 0:
#                     return {'result': {'message': "Bag finished during sampling phase"}}
#                 if res['noTotalTasks'] == res['noCompletedTasks']:
#                     return {'result': {'message': "Taskfarm already finished"}}
#                 # check schedule selection
#                 if (args.schedule < 1) or (args.schedule > numscheds):
#                     return {'result': {'error': "ERROR: select schedule in interval [1..%d]" % numscheds}}

#         # start execution
#         # "{"method":"start_execution","params":["1371729870918","2"],"jsonrpc":"2.0","id":1}"
#         res = self.call_manager(app_id, service_id, "start_execution", [ts, args.schedule - 1])
#         return {'result': res}

#     def select_schedule(self, args):
#         res = self._select_schedule(args)
#         self._print_res(res)


# def main():
#     logger = logging.getLogger(__name__)
#     console = logging.StreamHandler()
#     formatter = logging.Formatter('%(levelname)s - %(message)s')
#     console.setFormatter(formatter)
#     logger.addHandler(console)

#     cmd_client = BaseClient(logger)

#     parser, argv = config('Manage ConPaaS PHP services.', logger)

#     _serv_cmd = TaskFarmCmd(parser, cmd_client)

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
