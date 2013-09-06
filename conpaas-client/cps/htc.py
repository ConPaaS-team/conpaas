import sys

import os
import sys
import httplib
import urllib2
import simplejson
from time import strftime, localtime

from cps.base import BaseClient

from conpaas.core import https
from cps import taskfarm



# TODO: as this file was created from a BLUEPRINT file,
# 	you may want to change ports, paths and/or methods (e.g. for hub)
#	to meet your specific service/server needs


class Client(BaseClient):

    
    
    def create(self, service_type, application_id=None):
        # TaskFarm's initial state is not INIT but RUNNING
        BaseClient.create(self, service_type, application_id, 
            initial_state='RUNNING')

    def start(self, service_id, cloud="default"):
        # TaskFarm does not have to be started
        mode = ''
        ht_type= ''
        #m_type= 'default_m_type'
        
        while mode not in ['real', 'demo']:
            mode = raw_input("insert HTC mode('real' or 'demo'):")
        while ht_type not in ['batch', 'workflow', 'online']:
            ht_type = raw_input("insert HTC type('batch', 'workflow', 'online'):")
        data = {'cloud': cloud}
        data["mode"]= mode
        data["type"]= ht_type
        #data["m_type"]= m_type
        print str(data)
        res = self.callmanager(service_id, "startup", True, data)
        if 'error' in res:
            print res['error']
        else:
            print "Your service is starting up."
            
            
    def hosts(self, service_id):
        res = self.callmanager(service_id, "list_nodes", False, {})
        return res
        
    #def create_worker(self,service_id, machine_type, count, cloud):
    def create_worker(self,service_id, count, cloud):
        #res = self.callmanager(service_id, "add_nodes", True, {"type":machine_type, "count":count, "cloud":cloud})
        res = self.callmanager(service_id, "add_nodes", True, {"count":count, "cloud":cloud})
        return res

    def remove_worker(self,service_id, worker_id,cloud):
        res = self.callmanager(service_id, "remove_nodes", True, {"id":worker_id, "count":1, "cloud":cloud})
        return res
    
    def create_job(self, service_id, filename=None) :
        if filename:
            contents = open(filename).read()
            files = [ ( filename, filename, contents) ]
            res = self.callmanager(service_id, "/", True,{'method':'create_job', },files)
        else:
            res = self.callmanager(service_id, "/", True,{'method':'create_job', },[])
        if 'error' in res:
            return res['error']
        
        return res['id']
        
    def upload_file(self, service_id, filename) :
        contents = open(filename).read()
        files = [ ( filename, filename, contents) ]
        res = self.callmanager(service_id, "/", True,{'method':'upload_file', },files)
        if 'error' in res:
            return res['error']

        return res['id']

    def add(self, service_id, job_id,filename=None):
        if filename:
            contents = open(filename).read()
            files = [ ( filename, filename, contents) ]
            res = self.callmanager(service_id, "/", True,{'method':'add', 'job_id': job_id},files)
            if 'error' in res:
                return res['error']
            return res["id"]
        else:
            return "No file specified"


    
    def remove(self, service_id, job_id,filename=None, xtreemfs_location=None):
        return self.upload_bag_of_tasks(service_id,filename, xtreemfs_location)
    
    def sample(self, service_id, job_id):
        res = self.callmanager(service_id, "sample", True, {'job_id':job_id})
        if 'error' in res:
            return res['error']
        return res["out"]
    
    #def submit(self, service_id, job_id, option):
    #    res = self.callmanager(service_id, "execute", True, {'id':job_id, 'opt':option})
    def submit(self, service_id, job_id):
        res = self.callmanager(service_id, "execute", True, {'job_id':job_id})
        if 'error' in res:
            return res['error']
        return res['out']

    def stat (self, service_id, job_id):
        res = self.callmanager(service_id, "stat", True, {'id':job_id})
        print res
        return res

    def get_mode (self, service_id):
        res = self.callmanager(service_id, "get_service_mode", False, {})
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
            return { 'result' : { 'error' : 'ERROR: to upload bag of task, first specify run mode DEMO or REAL \n\tcpsclient.py serviceid set_mode [ DEMO | REAL ] ' }}
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
        nodes = self.callmanager(service['sid'], "list_nodes", False, {})
    	print type(nodes)    
        for n in nodes:
            print n + "	:	" +str(nodes[n])


    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print " == HTC specific commands == "
        print "    hosts            serviceid "
        print "    create_job       serviceid   bot_file"
        print "    upload_file      serviceid   file"
        #print "    create_worker    serviceid    type [cloud]"
        print "    create_worker    serviceid   [cloud]"
        print "    remove_worker    serviceid   worker_id"
        print "    configuration    serviceid"
        print "    throughput       serviceid"
        print "    add              serviceid   job_id   bot_file"
        print "    remove           serviceid   job_id   bot_file"
        print "    sample           serviceid   job_id"
        print "    submit           serviceid   job_id"
        print "    stat             serviceid"

    def main(self, argv):
        command = argv[1]
        
        if command == "create_worker":
            #if len(argv) < 4:
            if len(argv) < 3:
                self.usage(argv[0])
                sys.exit(0)
            try:
                sid = int(argv[2])
                
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
            self.check_service_id(sid)
            #machine_type = argv[3]
            try:
                #if len(argv)==4:
                if len(argv)==3:
                    cloud = 'default'
                else:
                    #cloud = argv[4]
                    cloud = argv[3]
                if cloud not in self.available_clouds():
                    raise IndexError
            except IndexError:
                print "Cloud %s not in %s" % (cloud, self.available_clouds())
                sys.exit(0)
            #res = self.create_worker(sid, machine_type, 1, cloud)
            res = self.create_worker(sid, 1, cloud)
            if 'error' in res:
                print res['error']
            else:
                print "Service %d is performing the requested operation (%s)" % (sid, command)
        
        if command == "remove_worker":
            if len(argv) < 4:
                self.usage(argv[0])
                sys.exit(0)
            try:
                sid = int(argv[2])
                worker_id= int(argv[3])                
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
            self.check_service_id(sid)
            try:
                if len(argv)==4:
                    cloud = 'default'
                else:
                    cloud = argv[4]
                if cloud not in self.available_clouds():
                    raise IndexError
            except IndexError:
                print 'Cloud '+cloud+' not in '+ self.available_clouds()
                sys.exit(0)
            res = self.remove_worker(sid, worker_id,cloud)
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command        

        if command in ["create_job",'upload_file']:
            try:
                sid = int(argv[2])
                
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
            if len(argv) > 3:
                if command == 'create_job':
                    print self.create_job(sid,argv[3])
                else:
                    self.upload_file(sid,argv[3])
            else:
                self.usage(argv[0])
                sys.exit(0)

        if command in ["add", "sample", "submit"]:
            try:
                sid = int(argv[2])
                jid = int(argv[3])
                
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
            if len(argv) < 5:
                if command == "add":
                    self.usage(argv[0])
                    sys.exit(0)
                elif command=="sample":
                    print self.sample(sid, jid)
                else:
                    print self.submit(sid, jid)
            else:
                print self.add(sid, jid, argv[4])
        
        if command in ("configuration", "throughput", 'select'):
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
            
            t = raw_input("insert a target throughput:")
            if command == 'configuration':
                res = self.callmanager(sid, "get_config", True, {'t':t})
            elif command=='throughput':
                res = self.callmanager(sid, "get_m", True, {'t':t})
            else:
                res = self.callmanager(sid, "select", True, {'t':t})

            
            print res
            
        if command in ( 'add_nodes', 'remove_nodes' ):
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
                
            self.check_service_id(sid)

            try:
                count = int(argv[3])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            # call the methods
            try:
                if len(argv)==4:
                    cloud = 'default'
                else:
                    cloud = argv[4]
                if cloud not in self.available_clouds():
                    raise IndexError
            except IndexError:
                print 'Cloud '+cloud+' not in '+ self.available_clouds()
                sys.exit(0)
            res = self.callmanager(sid, command, True, {'count': count,
                'cloud': cloud})
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command
                

