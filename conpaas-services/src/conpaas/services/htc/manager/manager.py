# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread

from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse

from conpaas.services.htc.agent import client
from conpaas.services.htc.manager.worker import Worker
from conpaas.services.htc.manager.taskfarm import TaskFarm, UnknownHtcTypeError, UnimplementedHtcCombinationError
from conpaas.services.htc.manager.configuration import Configuration
import node_info
import os
import sys
import time
import pprint 
pp = pprint.PrettyPrinter(indent=4,stream=sys.stderr)
#import json
#import random
class HTCManager(BaseManager):
    """Manager class with the following exposed methods:

    shutdown() -- POST
    add_nodes(count) -- POST
    remove_nodes(count) -- POST
    list_nodes() -- GET
    get_service_info() -- GET
    get_node_info(serviceNodeId) -- GET
    """
    RWCT = 'RemoteWallClockTime'
    MT = 'MATCH_EXP_MachineCloudMachineType'

    def __init__(self, config_parser, **kwargs):
        """Initialize a HTC Manager. 

        'config_parser' represents the manager config file. 
        **kwargs holds anything that can't be sent in config_parser."""
        BaseManager.__init__(self, config_parser)

        self.nodes = []

        # Setup the clouds' controller
        self.controller.generate_context('htc')

        self.con = True
        self.hub_ip = None
        types = []
        costs = []
        limits = []
	
        types.append(self.config_parser.get('iaas', 'INST_TYPE'))
        cpt = self.config_parser.get('iaas', 'COST_PER_TIME')
        i = cpt.index('/')
        s = cpt.index('$')
        c = cpt[s+2:i]
        costs.append(float(c))
        limits.append(int(self.config_parser.get('iaas', 'MAX_VMS')))
	      

        for cloud in self.controller.get_clouds():
            types.append(self.config_parser.get(cloud.cloud_name, 'INST_TYPE'))
            cpt = self.config_parser.get(cloud.cloud_name, 'COST_PER_TIME')
            i = cpt.index('/')
            s = cpt.index('$')
            c = cpt[s+2:i]
            costs.append(float(c))
            limits.append(int(self.config_parser.get(cloud.cloud_name, 'MAX_VMS')))
        self.configuration = Configuration(types,costs,limits)
        self.logger.info(self.configuration.costs)
        self.logger.info(self.configuration.keys)
        self.logger.info(self.configuration.limits)
#        random.seed()
#        for t in types:
#            self.configuration.set_average(t, 2 * random.uniform(0,1))        
#        self.configuration.relevant_time_unit(20)
#        self.configuration.compute_throughput()
#        self.configuration.dynamic_configuration()
	self.pool={}
        self.files=[]


    @expose('POST')
    def startup(self, kwargs):
        self.logger.info("HTC Manager starting up")
        self.logger.info(str(kwargs))
        if self.state != self.S_INIT and self.state != self.S_STOPPED:
            vals = { 'curstate': self.state, 'action': 'startup' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        if 'cloud' in kwargs:
            try:
                self._init_cloud(kwargs['cloud'])
            except Exception:
                return HttpErrorResponse(
                    "A cloud named '%s' could not be found" % kwargs['cloud'])        
        #self.logger.info('Get service TaskFarm')
        try:
            self.service = TaskFarm(kwargs['mode'], kwargs['type'])
        except (UnknownHtcTypeError, UnimplementedHtcCombinationError) as e:
            return HttpErrorResponse({ 'error': e.__str__() })
        #self.logger.info('Got service TaskFarm, delete some kwargs entries')
        self.state = self.S_PROLOGUE
        del kwargs['type']
        del kwargs['mode']
        #del kwargs['m_type']
        #self.logger.info('Show leftover kwargs entries')
        self.logger.info(str(kwargs))
        #self.logger.info('Starting Thread for startup')
        Thread(target=self._do_startup, kwargs=kwargs).start()
        
        self.logger.info(str(self.service))

        return HttpJsonResponse({ 'state': self.state })


    #def _do_startup(self, cloud, m_type):
    def _do_startup(self, cloud):
        """Start up the service. The first node will be an agent running a
        HTC Hub and a HTC Node."""

        #self.logger.info("_do_startup(%s)" % cloud)
        startCloud = self._init_cloud(cloud)
        m_type = self.config_parser.get(startCloud.cloud_name, 'INST_TYPE')  # 'default' may have been replaced by 'iaas'
        #self.logger.info("_do_startup(%s)" % cloud)
        self.logger.info(str(self.controller.get_clouds()))
        vals = { 'action': '_do_startup', 'count': 1 }
        self.logger.debug(self.ACTION_REQUESTING_NODES % vals)

        try:
            nodes = self.controller.create_nodes(1,
                client.check_agent_process, self.AGENT_PORT, startCloud)

            hub_node = nodes[0]

            # The first agent is a HTC Hub and a HTC Node
            client.create_hub(hub_node.ip, self.AGENT_PORT)

            client.create_node(hub_node.ip, self.AGENT_PORT, hub_node.ip)
            self.logger.info("Added node %s: %s " % (hub_node.id, hub_node.ip))
            node_info.add_node_info('/etc/hosts', hub_node.ip, hub_node.id)

            node = hub_node
            worker = Worker(node.id, node.ip, node.private_ip, node.cloud_name, m_type)
            self.service.add_worker(worker, int(node.id))

            self.hub_ip = hub_node.ip

            # Extend the nodes list with the newly created one
            self.nodes += nodes
	    if m_type in self.pool:
		    self.pool[m_type]+=1
            else:
		    self.pool[m_type]=1
            self.state = self.S_RUNNING
        except Exception, err:
            self.logger.exception('_do_startup: Failed to create hub: %s' % err)
            self.state = self.S_ERROR

    @expose('POST')
    def shutdown(self, kwargs):
        """Switch to EPILOGUE and call a thread to delete all nodes"""
        # Shutdown only if RUNNING
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'shutdown' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        
        self.state = self.S_EPILOGUE
        Thread(target=self._do_shutdown, args=[]).start()

        return HttpJsonResponse({ 'state': self.state })

    def _do_shutdown(self):
        """Delete all nodes and switch to status STOPPED"""
        self.controller.delete_nodes(self.nodes)
        self.logger.info(self.nodes)
        self.nodes = []
        self.logger.info("All nodes deleted")
        self.state = self.S_STOPPED

    def __check_count_in_args(self, kwargs):
        """Return 'count' if all is good. HttpErrorResponse otherwise."""
        # The frontend sends count under 'node'.
        if 'node' in kwargs:
            kwargs['count'] = kwargs['node']

        if not 'count' in kwargs:
            return HttpErrorResponse(self.REQUIRED_ARG_MSG % { 'arg': 'count' })

        if not isinstance(kwargs['count'], int):
            return HttpErrorResponse(
                "ERROR: Expected an integer value for 'count'")

        return int(kwargs['count'])

    @expose('POST')
    def add_nodes(self, kwargs):
        """Add kwargs['count'] nodes to this deployment"""
        self.controller.add_context_replacement(dict(STRING='htc'))

        # Adding nodes makes sense only in the RUNNING state
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'add_nodes' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        # Ensure 'count' is valid
        count_or_err = self.__check_count_in_args(kwargs)        
        if isinstance(count_or_err, HttpErrorResponse):
            return count_or_err

        count = count_or_err

        self.state = self.S_ADAPTING
        #Thread(target=self._do_add_nodes, args=[count, kwargs['cloud'], kwargs['type']]).start()
        Thread(target=self._do_add_nodes, args=[count, kwargs['cloud']]).start()
        self.logger.info(str(kwargs))
        return HttpJsonResponse({ 'state': self.state })

    #TODO remove hack!!!
    #def _do_add_nodes(self, count, cloud, m_type):
    def _do_add_nodes(self, count, cloud):
        """Add 'count' HTC Nodes to this deployment"""
        #if m_type in ['small', 'medium'] and cloud=='default':
        #    cloud = "cloud.amsterdam."+m_type
        startCloud = self._init_cloud(cloud)

        self.logger.info(str(self.controller.get_clouds()))
        vals = { 'action': '_do_add_nodes', 'count': count }
        self.logger.debug(self.ACTION_REQUESTING_NODES % vals)
        node_instances = self.controller.create_nodes(count, 
            client.check_agent_process, self.AGENT_PORT, startCloud)

        # Startup agents
        for node in node_instances:
            self.logger.info("Adding node %s: " % (node.id))

            client.create_node(node.ip, self.AGENT_PORT, self.hub_ip)
            self.logger.info("Added node %s: %s " % (node.id, node.ip))
            node_info.add_node_info('/etc/hosts', node.ip, node.id)

            m_type = self.config_parser.get(cloud, 'INST_TYPE')
            worker = Worker(node.id, node.ip, node.private_ip, node.cloud_name, m_type)
            self.service.add_worker(worker, int(node.id))

            self.logger.info(str(self.service))
        self.nodes += node_instances
        self.state = self.S_RUNNING
        if m_type in self.pool:
            self.pool[m_type]+=count
        else:
            self.pool[m_type]=count

    @expose('POST')
    def remove_nodes(self, kwargs):
        """Remove kwargs['count'] nodes from this deployment"""

        # Removing nodes only if RUNNING
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'remove_nodes' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        # Ensure 'count' is valid
        count_or_err = self.__check_count_in_args(kwargs)
        if isinstance(count_or_err, HttpErrorResponse):
            return count_or_err

        count = count_or_err

        if count > len(self.nodes) - 1:
            return HttpErrorResponse("ERROR: Cannot remove so many nodes")
        self.logger.info(type(kwargs["id"]))
        if kwargs["id"] not in self.service.registered_workers.keys():
            return HttpErrorResponse("ERROR: This worker does not exist")
        id=kwargs["id"]
        self.state = self.S_ADAPTING
        Thread(target=self._do_remove_nodes, args=[id]).start()


        return HttpJsonResponse({ 'state': self.state })


    def _do_remove_nodes(self, worker_id):
        """Remove 'count' nodes, starting from the end of the list. This way
        the HTC Hub gets removed last."""
        self.logger.info(str(self.controller.get_clouds()))
        node = self.service.get_worker(worker_id)
        client.condor_off(node.ip, self.AGENT_PORT)     # sign off with condor
        self.logger.info("Removing node with IP %s" % node)
        self.controller.delete_nodes([ node ])
        node_info.remove_node_info('/etc/hosts', node.ip)
        self.service.remove_worker(worker_id)
        self.nodes.remove(node)
        self.logger.info(str(self.service))
        self.state = self.S_RUNNING
        self.pool[node.type]-=1

    @expose('UPLOAD')
    def create_job(self, kwargs):
        fileobject = kwargs.popitem()
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'create_job' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
        fullpath = os.path.join(basedir, fileobject[0])

        # Write the uploaded script to filesystem
        open(fullpath, 'w').write(fileobject[1].file.read())

        key = self.service.add_bot(fullpath)
        self.logger.debug("create_job with args=%s" % kwargs)
        self.logger.info(str(self.service))

        return HttpJsonResponse({ 'id': key })

    @expose('UPLOAD')
    def upload_file(self, kwargs):
        fileobject = kwargs.popitem()
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'upload_file' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
        fullpath = os.path.join(basedir, fileobject[0])

        # Write the uploaded script to filesystem
        open(fullpath, 'w').write(fileobject[1].file.read())
        self.files.append(fullpath)
        self.logger.info(str(self.files))


    @expose('UPLOAD')
    def add(self, kwargs):
        job_id = int(kwargs.pop('job_id'))
        fileobject = kwargs.popitem()
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'add' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
        fullpath = os.path.join(basedir, fileobject[0])

        # Write the uploaded script to filesystem
        open(fullpath, 'w').write(fileobject[1].file.read())

        key = self.service.add_on(fullpath, job_id)
        self.logger.debug("add with args=%s" % kwargs)
        self.logger.debug(type(key))
        self.logger.info(str(self.service))

        return HttpJsonResponse({ 'id': job_id })

    @expose('POST')
    def sample(self,kwargs):
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'sample' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        job_id = int(kwargs.pop('job_id'))
        if not self.service.job_exists(job_id):
            return HttpErrorResponse("wrong job_id: "+ str(job_id))            
        size = self.service.sample_job(job_id)
        if size == -2:
            return HttpErrorResponse("sampling already started for job_id: "+ str(job_id))            
        if size == -3:
            return HttpErrorResponse("sampling already finished for job_id: "+ str(job_id))            
        self.logger.info(size)
        Thread(target=self._do_check_jobs, args=[]).start()
        return HttpJsonResponse({ 'out': "sampling started" })

    @expose('POST')
    def execute(self,kwargs):
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'execute' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        job_id = int(kwargs.pop('job_id'))
        if not self.service.job_exists(job_id):
            return HttpErrorResponse("wrong job_id: "+ str(job_id))            
        jb_key = "%d.0" % job_id
        if self.service.tf_job_dict[jb_key]['SamplingStarted'] == False:
            return HttpErrorResponse("Sampling not started for job id: "+ str(job_id))
        if self.service.tf_job_dict[jb_key]['SamplingReady'] == False:
            return HttpErrorResponse("Sampling not ready for job id: "+ str(job_id))
        size = self.service.execute_job(job_id)
        if size == -1:
            return HttpErrorResponse("wrong job_id: "+ str(job_id))            
        return HttpJsonResponse({ 'out': "execution started, feel free to add more bags" })

    @expose('POST')
    def callback_time(self,kwargs):
        task_id = kwargs.pop('task_id')
        self.service.callback_time(task_id)

    @expose('POST')
    def get_config(self,kwargs):
#        self.logger.info(self.configuration.conf_dict )
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'get_config' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        t = int(kwargs['t'])
        if t not in self.configuration.conf_dict:
            return HttpErrorResponse("manager not configured yet for throughput = "+ str(t))
        return HttpJsonResponse({"conf":self.configuration.conf_dict[t]})
    
    @expose('POST')
    def get_m(self,kwargs):
#        self.logger.info(self.configuration.m ) 
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'get_cost' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        t = int(kwargs['t'])
        if t not in self.configuration.m:
            return HttpErrorResponse("manager not configured yet for throughput = "+ str(t))
        return HttpJsonResponse({"conf":self.configuration.m[t]})

    @expose('POST')
    def select(self,kwargs):
#        self.logger.info(self.configuration.m ) 
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'select' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        t = int(kwargs['t'])
        if t not in self.configuration.m:
            return HttpErrorResponse("manager not configured yet for throughput = "+ str(t))
        for k in self.pool:
            while self.pool[k] > self.configuration.conf_dict[t][self.configuration.keys[k]]:
                wid=self.service.get_worker_id(k)
                self._do_remove_nodes(wid)
            if self.pool[k] < self.configuration.conf_dict[t][self.configuration.keys[k]]:
                count = self.configuration.conf_dict[t][self.configuration.keys[k]] - self.pool[k]  
		self.state = self.S_ADAPTING
                Thread(target=self._do_add_nodes, args=[count, 'cloud.amsterdam.'+ str(k)]).start()
	self.logger.info(str(self.service))
        return HttpJsonResponse({"conf:":self.configuration.m[t]})

    def update_configuration(self, tasks_dict):
        f1 = open('t1','a')
        f2 = open('t2','a')
        tot = {}
        num = {}
        for k in tasks_dict:
            for t in tasks_dict[k]:
                if t[self.MT] in tot:
                    tot[t[self.MT]] += t[self.RWCT]
                    num[t[self.MT]] += 1
                else:
                    tot[t[self.MT]] = t[self.RWCT]
                    num[t[self.MT]] = 1
        for k in tot:

	    print >>f1, k ,tot[k]/num[k]
	    self.logger.info(k +" "+str(tot[k]/num[k]))
            av = self.configuration.averages[self.configuration.keys[k]]
            no = self.configuration.notasks[self.configuration.keys[k]]
            newtot = tot[k] + (no*av)
            newno = num[k] + no
            newav = 0
	    if av == 0:
		newav = newtot/newno
	    else:
		newav = 0.6*av + 0.4*tot[k]/num[k] 
            self.configuration.set_average(k,newav,newno)
	    print >>f2, k,newav
	    self.logger.info(k +" "+str(newav))
        f1.close()
        f2.close()
        self.configuration.relevant_time_unit()
        self.configuration.relevant_time_unit()
        self.configuration.dynamic_configuration()
	self.logger.info(self.configuration.averages)
    def _do_check_jobs(self):
        size=0
        while True:
            if len(self.service.tf_job_info)>size:
                for k in self.service.tf_job_info:
                    if 'complete' not in self.service.tf_job_info[k]:
                        self.update_configuration(self.service.tf_job_info[k])
                        self.service.tf_job_info[k]['complete']=0
                size = len(self.service.tf_job_info)
            else:
                time.sleep(2)

    def __is_hub(self, node):
        """Return True if the given node is the HTC Hub"""
        return node.ip == self.hub_ip        

    @expose('GET')
    def list_nodes(self, kwargs):
        """Return a list of running nodes"""
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'list_nodes' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        
        print str(self.service.registered_workers)

        return HttpJsonResponse(self.service.s_registered_workers)
        

    @expose('GET')
    def get_service_info(self, kwargs):
        """Return the service state and type"""
        if self.state == self.S_RUNNING: # service is present
            fn = "job_info@%d" % time.time()
            fd = open(fn, "w")
            pp = pprint.PrettyPrinter(indent=4,width=160,stream=fd)
            pp.pprint(self.service.tf_job_info)
            fd.close
            self.service.tf_dict['file'] = fn
            self.service.tf_dict['dir'] = os.getcwd()
            self.logger.info(str(self.service))
            return HttpJsonResponse({'state': self.state, 'type': 'htc', 'dict': self.service.tf_dict})
        else:
            return HttpJsonResponse({'state': self.state, 'type': 'htc'})

    @expose('GET')
    def get_node_info(self, kwargs):
        """Return information about the node identified by the given
        kwargs['serviceNodeId']"""

        # serviceNodeId is a required parameter
        if 'serviceNodeId' not in kwargs:
            vals = { 'arg': 'serviceNodeId' }
            return HttpErrorResponse(self.REQUIRED_ARG_MSG % vals)

        serviceNodeId = kwargs.pop('serviceNodeId')

        serviceNode = None
        for node in self.nodes:
            if serviceNodeId == node.id:
                serviceNode = node
                break

        if serviceNode is None:
            return HttpErrorResponse(
                'ERROR: Cannot find node with serviceNode=%s' % serviceNodeId)

        return HttpJsonResponse({
            'serviceNode': { 
                'id': serviceNode.id, 
                'ip': serviceNode.ip, 
                'is_hub': self.__is_hub(serviceNode)
            }
        })
