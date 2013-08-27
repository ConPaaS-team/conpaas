import os
import sys
import httplib
import urllib2
import simplejson
from time import strftime, localtime

from cps.base import BaseClient

from conpaas.core import https

def http_jsonrpc_post(hostname, port, uri, method, params):
    """Perform a plain HTTP JSON RPC post (for task farming)"""
    url = "http://%s:%s%s" % (hostname, port, uri)

    data = simplejson.dumps({ 'method': method, 'params': params, 
        'jsonrpc': '2.0', 'id': 1 })

    req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    res = urllib2.urlopen(req).read()
    return res

def http_file_upload_post(host, port, uri, params={}, files=[]):
    """Perform a plain HTTP file upload post (for task farming)"""
    content_type, body = https.client._encode_multipart_formdata(params, files)
    h = httplib.HTTP(host, port)
    h.putrequest('POST', uri)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

class Client(BaseClient):

    def callmanager(self, service_id, method, post, data):
        """TaskFarm peculiarities:

        1) it works via plain http
        2) it uses port 8475
        3) the 'shutdown' method is called 'terminate_workers'
        """
        if method == "shutdown":
            method = "terminate_workers"

        service = self.service_dict(service_id)
        res = http_jsonrpc_post(service['manager'], 8475, '/', method, params=data)

        try:
            data = simplejson.loads(res[1])
        except ValueError:
            data = simplejson.loads(res)

        return data.get('result', data)

    def create(self, service_type, application_id=None):
        # TaskFarm's initial state is not INIT but RUNNING 
        BaseClient.create(self, service_type, application_id, 
            initial_state='RUNNING')

    def start(self, service_id):
        # TaskFarm does not have to be started
        pass

    def stop(self, service_id):
        # TaskFarm does not have to be stopped
        pass
    
    def terminate(self, service_id):
        # TaskFarm is never in 'STOPPED' state
        print "Terminating service... "
        sys.stdout.flush()

        res = self.callapi("stop/%s" % service_id, True, {})
        if res:
            print "done."
        else:
            print "failed."

    def get_mode (self, service_id):
        res = self.callmanager(service_id, "get_service_info", False, {})
        return res['mode'];

    def set_mode (self, service_id, new_mode):
        """
                new mode = DEMO or REAL
        """
        new_mode = new_mode.upper()
        if not (new_mode in ( "DEMO", "REAL" )):
            return { 'result' : { 'error' : 'ERROR: invalid mode %s: use DEMO or REAL' % new_mode }}
        old_mode = self.get_mode(service_id)
        if old_mode != 'NA':
            return { 'result' : { 'error' : 'ERROR: mode is already set to %s' % old_mode }}
        res = self.callmanager(service_id, "set_service_mode", True, [new_mode])
        return { 'result': res }

    def upload_bag_of_tasks(self, service_id, filename, xtreemfs_location):
        """eg: upload_bag_of_tasks(service_id=1, 
                                   filename="/var/lib/outsideTester/contrail3/test.bot", 
                                   xtreemfs_location="192.168.122.1/uc3")
        """
        mode = self.get_mode(service_id)
        if mode == 'NA':
            return { 'result' : { 'error' : 'ERROR: to upload bag of task, first specify run mode DEMO or REAL \n\tcpsclient.py set_mode serviceid [ DEMO | REAL ] ' }}
        service = self.service_dict(service_id)
        params = { 'uriLocation': xtreemfs_location, 'method': 'start_sampling' }
        filecontents = open(filename).read()
        res = http_file_upload_post(service['manager'], 8475, '/', params, 
            files=[('botFile', filename, filecontents)])
        return simplejson.loads(res)

    def select_schedule(self, service_id, schedule):
        mode = self.get_mode(service_id)
        if mode == 'NA':
            return { 'result' : { 'error' : 'ERROR: to select a schedule, first specify run mode DEMO or REAL, then upload a bag of tasks ' }}
        service = self.service_dict(service_id)
        # check schedule availability
        res = self.callmanager(service_id, "get_service_info", False, {})
        if res['noCompletedTasks'] == 0:     # 
            print "No schedule available, please wait..."
            return
        if res['state'] != 'RUNNING':
            print "Busy %s, please wait..." % res['phase']
            return
        sres = self.callmanager(service_id, "get_sampling_results", False, {}) # in json format
        sdata = simplejson.loads(sres)
        if 'timestamp' in sdata:        # Sampling is ready, check if bag is ready, or if we have to choose a schedule
            ts = sdata['timestamp']
            print strftime("Bag sampled on %a %d %b %Y at %H:%M:%S %Z", localtime(ts/1000))
            if 'schedules' in sdata:
                sch = sdata['schedules']
                ss = simplejson.dumps(sch)
                # print "schedules: ", ss
                numscheds = len(sdata['schedules']) 
                if numscheds == 0:
                    return { 'result': { 'message' : "Bag finished during sampling phase" }}
                if res['noTotalTasks'] == res['noCompletedTasks']:
                    return { 'result': { 'message' : "Taskfarm already finished" }}
                # check schedule selection
                if (schedule < 1) or (schedule > numscheds):
                    return { 'result': { 'error' : "ERROR: select schedule in [ 1 .. %d ]" % numscheds  }}

        # start execution
        # "{"method":"start_execution","params":["1371729870918","2"],"jsonrpc":"2.0","id":1}"
        res = self.callmanager(service_id, "start_execution", True, [ ts, schedule-1 ])
        return { 'result': res }

    def info(self, service_id):
        service = BaseClient.info(self, service_id)

        # This call gives a urllib2.URLError "Connection reset by peer" quite
        # often...
        res = self.callmanager(service['sid'], "get_service_info", False, {})

        data = simplejson.dumps(res);
        # print "data:", data 
        print "mode:", res['mode']
        print "phase:", res['phase']
        print "total tasks:", res['noTotalTasks']
        print "completed tasks:", res['noCompletedTasks']
        print "money spent sampling:", res['moneySpentSampling']
        print "money spent:", res['moneySpent']
        if res['noCompletedTasks'] > 0:     # 
            if res['state'] != 'RUNNING':
                print "Busy %s, please wait..." % res['phase']
                return
            sres = self.callmanager(service_id, "get_sampling_results", False, {}) # in json format
            sdata = simplejson.loads(sres)
            if 'timestamp' in sdata:        # Sampling is ready, check if bag is ready, or if we have to choose a schedule
                ts = sdata['timestamp']
                print strftime("Bag sampled on %a %d %b %Y at %H:%M:%S %Z", localtime(ts/1000))
                if 'schedules' in sdata:
                    sch = sdata['schedules']
                    ss = simplejson.dumps(sch)
                    # print "schedules: ", ss
                    if len(sdata['schedules']) == 0:
                        print "Bag finished during sampling phase"
                        return
                    if res['noTotalTasks'] == res['noCompletedTasks']:
                        print "Taskfarm finished"
                        return
                    count = 0
                    print "Schedules to choose from:"
                    print "%s\t%6.6s\t%6.6s" % ('Sched#','Time', 'Cost')
                    for sched in sdata['schedules']:
                        count = count + 1
                        print "%s:\t%6.6s\t%6.6s" % ( count, sched['time'], sched['cost'] )
                return
            print "error in samplingresults: ", sdata 


    def logs(self, service_id):
        """The getLog method is called get_log in TaskFarm"""
        res = self.callmanager(service_id, "get_log", False, {})
        print res['message']

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    set_mode   serviceid [ DEMO | REAL ]         # select run mode"
        print "    upload_bot serviceid filename xtreemfs_loc   # upload bag of tasks and set file location "
        print "    select_schedule serviceid schedule_number    # select one of the available schedules "

    def main(self, argv):
        command = argv[1]

        if command == "set_mode":
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            self.check_service_id(sid)

            try:
                mode = argv[3]
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            res = self.set_mode(sid, mode)
            if 'error' in res['result']:
                print res['result']['error']
            elif 'message' in res['result']:
                print res['result']['message']
            else:
                print res

        if command == "upload_bot":
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            self.check_service_id(sid)

            try:
                filename = argv[3]
                xtreemfs_location = argv[4]
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            if not os.path.isfile(filename):
                print "E: %s is not a file" % filename
                sys.exit(0)

            res = self.upload_bag_of_tasks(sid, filename, xtreemfs_location)
            if 'error' in res['result']:
                print res['result']['error']
            elif 'message' in res['result']:
                print res['result']['message']
            else:
                print res

        if command == "select_schedule":
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            self.check_service_id(sid)

            try:
                schedule = int(argv[3])
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            res = self.select_schedule(sid, schedule)
            if 'error' in res['result']:
                print res['result']['error']
            elif 'message' in res['result']:
                print res['result']['message']
            else:
                print res

