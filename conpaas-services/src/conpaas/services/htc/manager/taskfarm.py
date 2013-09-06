'''
Created on Jul 4, 2013

@author: Vlad & Bert
'''
from threading import Thread
from collections import deque
import os
import sys
import time
import submit_a_task
import get_run_time
import xmltodict
import pprint 
pp = pprint.PrettyPrinter(indent=4,stream=sys.stderr)


class Error(Exception):
    pass

class UnknownHtcTypeError(Error):
    """Exception raised for unknown tf_type or mode

    Attributes:
        tf_type     -- NOT Either batch, online or workflow
        mode        -- NOT Either real or demo
    """
    def __init__(self, tf_type,mode):
        self.tf_type = tf_type
        self.mode = mode
    def __str__(self):
        return "Unknown HTC start value: type %s and/or mode %s" % (self.tf_type, self.mode)
    
class UnimplementedHtcCombinationError(Error):
    """Exception raised for unimplemented combinations

    Attributes:
        tf_type     -- Either batch, online or workflow
        mode        -- Either real or demo
    """
    def __init__(self, tf_type,mode):
        self.tf_type = tf_type
        self.mode = mode
    def __str__(self):
        return "Unimplemented HTC start combination: type %s, mode %s" % (self.tf_type, self.mode)
        

class TaskFarm:
    
    M_REAL = 'real'
    M_DEMO = 'demo'
    
    T_ONLINE = 'online'
    T_WF = 'workflow'
    T_BATCH= 'batch'
    
    def add_worker(self, worker, worker_id):
        self.registered_workers[worker_id]=worker
        self.s_registered_workers[worker_id]=str(worker)
    
    def remove_worker(self, worker_id):
        del self.registered_workers[worker_id]
        del self.s_registered_workers[worker_id]
    
    def get_worker(self,worker_id):
        return self.registered_workers[worker_id]
    
 
    def get_worker_id(self,m_type):
        for k in self.registered_workers:
            if self.registered_workers[k].type==m_type:
                return k
        return None


 

    def __init__(self, mode, tf_type):
        self.jobs = {} # every entry is a       job_id : [ list of bags ]
        self.bags = {} # every entry is a       job_id : num_of_executed_bags
        self.counter = len(self.jobs) 
        self.registered_workers = {}
        self.s_registered_workers = {}
        self.mode = mode
        if tf_type not in ('batch', 'online', 'workflow') and mode not in ('demo', 'real'):
            raise UnknownHtcTypeError(tf_type, mode)
        if tf_type in ('batch', 'workflow') or mode == 'demo':
            raise UnimplementedHtcCombinationError(tf_type, mode)
            
        self.type = tf_type
        self.tf_job_dict = {}  # contains simple info per job, per bag, i.e. job.bag : { TotalTasks:x, CompletedTasks:x, ReplicatedTasks:x, ReplicationFactor:x }
        self.tf_job_info = {}   # contains info on completed tasks i.e. job.bag: [ job.bag.task: [ task_dict 1, ... , task_dict_n ] ]
        self.tf_dict = {'jobs':0,'bags':0,'submitted_tasks':0,'completed_tasks':0,'job_dict':self.tf_job_dict}
        
    def __str__(self):
        return 'TaskFarm: mode = ' + self.mode + ' , type = ' + self.type + "\n, workers:" + str(self.registered_workers) + "\n bots:" +str(self.jobs) 
    
    def add_bot(self, fullpath):
        self.tf_dict['jobs'] += 1
        job_id = self.counter = len(self.jobs)
        self.jobs[self.counter] = deque([])
        self.jobs[self.counter].append(fullpath)
        jb_key = "%d.%d" % (job_id,0)
        if not self.tf_job_dict.has_key(jb_key):
            self.tf_job_dict[jb_key] = {}
        self.tf_job_dict[jb_key]['SamplingStarted'] = False
        self.bags[job_id] = 0
        return job_id

    def add_on(self, fullpath, jid, atend=True):
        self.tf_dict['bags'] += 1       # count the total number of bags in the service
        if atend:
            self.jobs[jid].append(fullpath)
        else:
            self.jobs[jid].appendleft(fullpath)
	return jid

    def execute_job(self, job_id):  # TODO  need to specify which bag??
        if job_id not in self.jobs:
            return -1
        # TODO check if this job has been sampled, and sampling is finished. Refuse to execute otherwise
        Thread(target=self._do_execute_job, args=[job_id]).start()

    def _do_execute_job(self, jid):  # TODO  need to specify which bag??
        job_id = int(jid)
        while True:
            if len(self.jobs[job_id]) == 0:
                time.sleep(2)
            else:
                while len(self.jobs[job_id]) > 0:
                    self.bags[job_id] += 1
                    bag_id = self.bags[job_id]
                    jb_key = "%d.%d" % (job_id,bag_id)
                    self.tf_job_dict[jb_key] = {}
                    bag_path = self.jobs[job_id].popleft()
                    lines = open(bag_path,'r').readlines()
                    line = 0
                    for l in lines:
                        submit_a_task.submit_a_task( job_id, bag_id, line, l, [] )
                        line += 1
                        #callback function that needs to state whether a task is done
                        print l
                    self.tf_job_dict[jb_key]['SamplingReady'] = False
                    self.tf_job_dict[jb_key]['CompletedTasks'] = 0
                    self.tf_job_dict[jb_key]['TotalTasks'] = line
                    self.tf_job_dict[jb_key]['SubmittedTasks'] = line 
                    self.tf_dict['submitted_tasks'] += self.tf_job_dict[jb_key]['SubmittedTasks'] 
                    self.tf_dict['job_dict'] = self.tf_job_dict
                    Thread(target=self._do_poll, args=[job_id,self.bags[job_id]]).start()

    def job_exists(self, job_id):
        return job_id in self.jobs

    def sample_job(self, job_id):
        # TODO  set up a thread for collecting all info when all tasks are finished
        if job_id not in self.jobs:
            return -1
        # TODO check if a bag has already been sampled, and refuse to sample it again
        bag_id = 0 # ALWAYS when sampling
        jb_key = "%d.%d" % (job_id,bag_id)
        if self.tf_job_dict[jb_key]['SamplingStarted'] == True:
            if self.tf_job_dict[jb_key]['SamplingReady'] == True:
                return -3
            return -2
        self.tf_dict['bags'] += 1
        if not self.tf_job_dict.has_key(jb_key):
                self.tf_job_dict[jb_key] = {}
        replication_size = 7
        print job_id
        bag_path = self.jobs[job_id].popleft()
        lines = open(bag_path,'r').read().splitlines()
        N = len(lines)
        print N
        size = int((N* 1.96*1.96)//((1.96*1.96)+(2*(N-1))*(0.2*0.2)))

        # def submit_a_task(jobnr, bagnr, tasknr, commandline, workerlist, thedict={}):

        # first: find all available workertypes
        type_list=[] 
        for w in self.registered_workers:
            workertype = self.registered_workers[w].type
            if workertype not in type_list:
                type_list.append(workertype)
        # second: submit all tasks in separate commands
        self.tf_job_dict[jb_key]['SamplingReady'] = False
        # TODO  to use condor more efficiently, create just one ClassAd file
        for i in range(0,size):
            #function that submits on each worker type
            print >> sys.stderr, 'sample_job sampling ', job_id, i, lines[i]
            if i < replication_size:   # to replicate job on all worker types, use type_list
                submit_a_task.submit_a_task( job_id, bag_id, i, lines[i], type_list ) 
            else:
                submit_a_task.submit_a_task( job_id, bag_id, i, lines[i], [] ) 

        # TODO  Put all lines that were not yet submitted in a file for later execution, and put the filename "in front of" the queue
        filename_leftovers = "%s/lo-j%d-b%d" % ( os.path.dirname(bag_path), job_id, bag_id )
        print >> sys.stderr, "leftovers go in ", filename_leftovers
        fd = open ( filename_leftovers, "w" )
        for i in range(size, N):
            fd.write(lines[i] + "\n")
        fd.close()
        self.add_on( filename_leftovers, job_id, False )
                
        # some administration
        self.tf_job_dict[jb_key]['SamplingStarted'] = True
        self.tf_job_dict[jb_key]['SamplingReady'] = False
        self.tf_job_dict[jb_key]['CompletedTasks'] = 0
        self.tf_job_dict[jb_key]['TotalTasks'] = size
        self.tf_job_dict[jb_key]['SubmittedTasks'] = size + replication_size * ( len ( type_list ) - 1 )
        self.tf_dict['submitted_tasks'] += self.tf_job_dict[jb_key]['SubmittedTasks'] 
        self.tf_dict['job_dict'] = self.tf_job_dict
        # TODO  wait for all jobs to complete and return the run-times
        Thread(target=self._do_poll, args=[job_id,bag_id]).start()
        #       should return list of leftover tasks
        return size

    def callback_time(self, task_id):
        self.timers[task_id] = 0               

    def _do_poll(self, job_id, bag_id):
        _try = 0
        jb_key = "%d.%d" % (job_id,bag_id)
        filename = "hist-%d-%d.xml" % ( job_id, bag_id )
        command = "condor_history -constraint 'HtcJob == %d && HtcBag == %d' -xml > %s" % ( job_id, bag_id, filename )
        while True:
            _try += 1
            _trystr = "Try %d (%s) :" % (_try, jb_key)
            # get condor_history and analyse
            ret_val = os.system( command )
            if ret_val != 0:
                # wait a little until the first results come in
                print >> sys.stderr, _trystr, "wait a little until the first results come in on", filename
                time.sleep(1)
                continue
            # now we have created a file, check if it has any classads
            xml = open(filename).read()
            xmldict = xmltodict.parse(xml)

            print >> sys.stderr, "type(xmldict) = ", type(xmldict)
            if not ( type(xmldict) == dict and xmldict.has_key('classads') ):
                print >> sys.stderr, _trystr, "No classads, wait a little until the first results come in"
                time.sleep(4)
                continue

            print >> sys.stderr, "type(xmldict['classads']) = ", type(xmldict['classads'])
            if not ( type(xmldict['classads']) == dict and xmldict['classads'].has_key('c') ) :
                print >> sys.stderr, _trystr, "No classads <c> entries, wait a little until the first results come in"
                time.sleep(4)
                continue

            print >> sys.stderr, "type(xmldict['classads']['c']) = ", type(xmldict['classads']['c'])
            if not ( type(xmldict['classads']['c']) == list and xmldict['classads']['c'][0].has_key('a') ) :
                print >> sys.stderr, _trystr, "No classads attributes, wait a little until the first results come in"
                time.sleep(4)
                continue

            print >> sys.stderr, _trystr, "start polling", filename
            poll_dict = get_run_time.get_poll_dict(xmldict)
            print >> sys.stderr, _trystr, "polling done", filename
            completed_tasks = 0
            for _ in poll_dict.keys():
                completed_tasks += len(poll_dict[_])
            completed_task_sets = poll_dict.keys().__len__()
            self.tf_dict['completed_tasks'] += ( completed_tasks - self.tf_job_dict[jb_key]['CompletedTasks'] )
            self.tf_job_dict[jb_key]['CompletedTasks'] = completed_tasks
            self.tf_job_dict[jb_key]['CompletedTaskSets'] = completed_task_sets
            
            print >> sys.stderr, "polling %s, try %d: SubmittedTasks = %d, CompletedTasks = %d" % ( jb_key, _try, self.tf_job_dict[jb_key]['SubmittedTasks'], self.tf_job_dict[jb_key]['CompletedTasks'] )
            #if _try == 50:
            #    self.tf_job_dict[jb_key]['SamplingReady'] = True

            if self.tf_job_dict[jb_key]['CompletedTasks'] == self.tf_job_dict[jb_key]['SubmittedTasks']:
                self.tf_job_info[jb_key] = poll_dict
                self.tf_job_dict[jb_key]['SamplingReady'] = True

            if self.tf_job_dict[jb_key]['SamplingReady'] == True:
                pp.pprint(poll_dict)
                return
            time.sleep(4)
