import os
import sys
import httplib
import urllib2
import simplejson

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

    def create(self, service_type):
        # TaskFarm's initial state is not INIT but RUNNING 
        BaseClient.create(self, service_type, initial_state='RUNNING')

    def start(self, service_id):
        print "XXX: do we have to startup?"

    def upload_bag_of_tasks(self, service_id, filename, xtreemfs_location):
        """eg: upload_bag_of_tasks(service_id=1, 
                                   filename="/var/lib/outsideTester/contrail3/test.bot", 
                                   xtreemfs_location="192.168.122.1/uc3")
        """
        service = self.service_dict(service_id)
        params = { 'uriLocation': xtreemfs_location, 'method': 'start_sampling' }
        filecontents = open(filename).read()
        res = http_file_upload_post(service['manager'], 8475, '/', params, 
            files=[('botFile', filename, filecontents)])
        return simplejson.loads(res)

    def info(self, service_id):
        service = BaseClient.info(self, service_id)

        # This call gives a urllib2.URLError "Connection reset by peer" quite
        # often...
        res = self.callmanager(service['sid'], "get_service_info", False, {})
            
        print "total tasks:", res['noTotalTasks']
        print "completed tasks:", res['noCompletedTasks']

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    upload_bot serviceid filename xtreemfs_loc"

    def main(self, argv):
        command = argv[1]

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
            print res['result']['message']
