'''
Copyright (c) 2010-2012, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the <ORGANIZATION> nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

Created May, 2012

@author Dragos Diaconescu

'''
from threading import Thread, Lock, Timer, Event

from conpaas.core.expose import expose
from conpaas.core.controller import Controller
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse,\
                         HttpFileDownloadResponse, HttpRequest,\
                         FileUploadField, HttpError
from conpaas.core.log import create_logger
from conpaas.services.xtreemfs.agent import client
import subprocess
import time
class ManagerException(Exception):

    E_CONFIG_READ_FAILED = 0
    E_CONFIG_COMMIT_FAILED = 1
    E_ARGS_INVALID = 2
    E_ARGS_UNEXPECTED = 3
    E_ARGS_MISSING = 4
    E_IAAS_REQUEST_FAILED = 5
    E_STATE_ERROR = 6
    E_CODE_VERSION_ERROR = 7
    E_NOT_ENOUGH_CREDIT = 8
    E_UNKNOWN = 9

    E_STRINGS = [
      'Failed to read configuration',
      'Failed to commit configuration',
      'Invalid arguments',
      'Unexpected arguments %s', # 1 param (a list)
      'Missing argument "%s"', # 1 param
      'Failed to request resources from IAAS',
      'Cannot perform requested operation in current state',
      'No code version selected',
      'Not enough credits',
      'Unknown error',
    ]

    def __init__(self, code, *args, **kwargs):
      self.code = code
      self.args = args
      if 'detail' in kwargs:
        self.message = '%s DETAIL:%s' \
                       % ( (self.E_STRINGS[code] % args), str(kwargs['detail']))
      else:
        self.message = self.E_STRINGS[code] % args



class XtreemFSManager(object):

    
    # Manager states - Used by the frontend
    S_INIT = 'INIT'         # manager initialized but not yet started
    S_PROLOGUE = 'PROLOGUE' # manager is starting up
    S_RUNNING = 'RUNNING'   # manager is running
    S_ADAPTING = 'ADAPTING' # manager is in a transient state - frontend will keep
                            # polling until manager out of transient state 
    S_EPILOGUE = 'EPILOGUE' # manager is shutting down
    S_STOPPED = 'STOPPED'   # manager stopped
    S_ERROR = 'ERROR'       # manager is in error state

    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser
                                # (hopefully the new service won't need anything extra)

        self.config_parser = config_parser
        self.logger = create_logger(__name__)
        self.logfile = config_parser.get('manager', 'LOG_FILE')
        self.nodes = []         
        self.osdNodes = []   
        self.mrcNodes = []
        self.dirNodes = []    

        self.dirCount = 0
        self.mrcCount = 0
        self.osdCount = 0
        # Setup the clouds' controller
        self.controller = Controller(config_parser)
        self.controller.generate_context('xtreemfs')
        self.state = self.S_INIT

    @expose('POST')
    def startup(self, kwargs):
        self.logger.debug("XtreemFSManager startup")
        if len(kwargs) != 0:
            return HttpErrorResponse(ManagerException \
                                      (E_ARGS_UNEXPECTED, \
                                       kwargs.keys()).message)

        if self.state != self.S_INIT and self.state != self.S_STOPPED:
            return HttpErrorResponse(ManagerException(E_STATE_ERROR).message)
        self.state = self.S_PROLOGUE
        Thread(target=self._do_startup, args=[]).start()
        return HttpJsonResponse({'state': self.S_PROLOGUE})

    
    def _start_dir(self,nodes):
        for node in nodes:
            try:
                data = client.createDIR(node.ip,5555)
            except client.AgentException:
                self.logger.exception('Failed to start DIR at node %s' % \
                                str(node))
                self.state = self.S_ERROR
                raise

    def _start_mrc(self,nodes):
        for node in nodes:
            try:
                data = client.createMRC(node.ip,5555,self.dirNodes[0].ip)
            except client.AgentException:
                self.logger.exception('Failed to start MRC at node %s' % \
                                str(node))
                self.state = self.S_ERROR
                raise
    def _start_osd(self,nodes):
        for node in nodes:
            try:
                client.createOSD(node.ip,5555,self.dirNodes[0].ip)
            except client.AgentException:
                self.logger.exception('Failed to start OSD at node %s' % \
                                str(node))
                self.state = self.S_ERROR
                raise

    def _stop_osd(self,nodes):
        for node in nodes:
            try:
                data = client.stopOSD(node.ip,5555)
            except client.AgentException:
                self.logger.exception('Failed to stop OSD at node %s' % \
                                str(node))
                self.state = self.S_ERROR
                raise

    def _do_startup(self):
        ''' Starts up the service. The firstnodes will contain all services
        '''
        try:
            node_instances = self.controller.create_nodes(1, \
                                           client.check_agent_process, 5555)

            self.logger.info('Created 1 node with DIR, MRC and OSD services')
            self.nodes += node_instances
            self.dirNodes += node_instances
            self.osdNodes += node_instances
            self.mrcNodes += node_instances
            
            self._start_dir(node_instances)
            self._start_osd(node_instances)
            self._start_mrc(node_instances)
            #at the startup the DIR node will have all the services
            self.dirCount = 1
            self.mrcCount = 0
            self.osdCount = 0
        except:
            self.logger.exception('do_startup: Failed to request a new node')
            self.state = self.S_STOPPED
            return

        self.logger.info('XtreemFS service was started up')    
        self.state = self.S_RUNNING
    @expose('POST')
    def shutdown(self, kwargs):
        self.state = self.S_EPILOGUE
        Thread(target=self._do_shutdown, args=[]).start()
        return HttpJsonResponse()

    def _do_shutdown(self):
        self.controller.delete_nodes(self.nodes)
        self.nodes = []
        self.osdNodes = []   
        self.mrcNodes = []
        self.dirNodes = []   	   
	
        self.dirCount = 0
        self.mrcCount = 0
        self.osdCount = 0

        self.state = self.S_STOPPED
        return HttpJsonResponse()

    @expose('POST')
    def add_nodes(self, kwargs):
        #self.controller.update_context(dict(STRING='xtreemfs'))
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to add_nodes')

        nr_dir = 0
        nr_mrc = 0 
        
        if 'dir' in kwargs:
            if not isinstance(kwargs['dir'], int):
                return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected an integer value for "dir"').message)
            nr_dir = int(kwargs.pop('dir'))    
        if nr_dir < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "dir"').message)

        if 'mrc' in kwargs:
            if not isinstance(kwargs['mrc'], int):
                return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected an integer value for "mrc"').message)
            nr_mrc = int(kwargs.pop('mrc'))
        if nr_mrc < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "mrc"').message)

        if not 'osd' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['osd'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "osd"')

        osd = int(kwargs.pop('osd'))
        if osd < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "nr osd"').message)

        self.state = self.S_ADAPTING
        Thread(target=self._do_add_nodes, args=[nr_dir,nr_mrc,osd]).start()
        return HttpJsonResponse()

    
    def KillOsd(self,nodes):
        for node in nodes:
            data = client.stopOSD(node.ip, 5555)
            self.osdNodes.remove(node)

    def _do_add_nodes(self,nr_dir,nr_mrc,nr_osd):
        totalNodes = nr_dir + nr_mrc + nr_osd

        try:
            node_instances = self.controller.create_nodes(totalNodes, \
                                           client.check_agent_process, 5555)      
        except:
            self.logger.exception('_do_add_nodes: Failed to request a new node')
            self.state = self.S_STOPPED
            return

        self.nodes += node_instances 
        self.dirNodes += node_instances[:nr_dir]
        dirNodes = node_instances[:nr_dir]

        self.mrcNodes += node_instances[nr_dir:nr_mrc+nr_dir]
        mrcNodes = node_instances[nr_dir:nr_mrc+nr_dir]

        self.osdNodes += node_instances[nr_mrc+nr_dir:]
        osdNodes = node_instances[nr_mrc+nr_dir:] 


        KilledOsdNodes = []
        # The first node will contain the OSD service so it will be removed from there
        if nr_osd > 0 and self.osdCount == 0:
            KilledOsdNodes.append(self.dirNodes[0])
        self.KillOsd(KilledOsdNodes)
          
        # Startup DIR agents
        # The DIR node is the first node from the list. It is the only one
        for node in dirNodes:
            client.startup(node.ip, 5555)
            data = client.createDIR(node.ip, 5555)
            self.logger.info('Received %s from %s', data, node.id)
            self.dirCount +=1

        # Startup MRC agents
        for node in mrcNodes:
            client.startup(node.ip, 5555)
            data = client.createMRC(node.ip, 5555,self.dirNodes[0].ip)
            self.logger.info('Received %s from %s', data, node.id)
            self.mrcCount +=1

        # Startup OSD agents
        for node in osdNodes:
            client.startup(node.ip, 5555)
            data = client.createOSD(node.ip, 5555,self.dirNodes[0].ip)
            self.logger.info('Received %s from %s', data, node.id)         
            self.osdCount += 1

        KilledOsdNodes = []
        #The first node will contain the osd service so it will be removed from there
        if nr_osd > 0 and self.osdCount == 0:
            KilledOsdNodes.append(self.dirNodes[0])
        self.KillOsd(KilledOsdNodes)

        self.state = self.S_RUNNING
        return HttpJsonResponse()

    @expose('GET')
    def list_nodes(self, kwargs):
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to list_nodes')
        return HttpJsonResponse({
              'dir': [node.id for node in self.dirNodes ],
              'mrc': [node.id for node in self.mrcNodes],
              'osd': [node.id for node in self.osdNodes]
              })

    @expose('GET')
    def get_service_info(self, kwargs):
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        return HttpJsonResponse({'state': self.state, 'type': 'xtreemfs'})

    @expose('GET')
    def get_node_info(self, kwargs):
        if 'serviceNodeId' not in kwargs:
            return HttpErrorResponse('ERROR: Missing arguments')
        serviceNodeId = kwargs.pop('serviceNodeId')
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        serviceNode = None
        for node in self.nodes:
            if serviceNodeId == node.id:
                serviceNode = node
                break
        if serviceNode is None:
            return HttpErrorResponse('ERROR: Invalid arguments')
        return HttpJsonResponse({
            'serviceNode': {
                            'id': serviceNode.id,
                            'ip': serviceNode.ip,
                            'dir': serviceNode in self.dirNodes,
                            'mrc': serviceNode in self.mrcNodes,
                            'osd': serviceNode in self.osdNodes
                            }
            })

    @expose('POST')
    def remove_nodes(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to remove_nodes')
        nr_dir = 0
        nr_mrc = 0 
            
        if 'dir' in kwargs:
            if not isinstance(kwargs['dir'], int):
                return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected an integer value for "dir"').message)
            nr_dir = int(kwargs.pop('dir'))    
        if nr_dir < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "dir"').message)
        if nr_dir > self.dirCount:
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Cannot remove_nodes that many DIR nodes').message)
     
        if 'mrc' in kwargs:
            if not isinstance(kwargs['mrc'], int):
                return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected an integer value for "mrc"').message)
            nr_mrc = int(kwargs.pop('mrc'))
        if nr_mrc < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "mrc"').message)
        if nr_mrc > self.mrcCount:
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Cannot remove_nodes that many MRC nodes').message)

        if not 'osd' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['osd'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "osd"')

        osd = int(kwargs.pop('osd'))
        if osd < 0: 
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "nr osd"').message)
        if osd > self.osdCount:
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Cannot remove_nodes that many OSD nodes').message)

        self.state = self.S_ADAPTING
        Thread(target=self._do_remove_nodes, args=[nr_dir,nr_mrc,osd]).start()
        return HttpJsonResponse()

    def _do_remove_nodes(self, nr_dir,nr_mrc,nr_osd):
        
        if nr_osd > 0:
            for i in range(0, nr_osd):
                node = self.osdNodes.pop(0)
                self.controller.delete_nodes([node])
                self.nodes.remove(node)
            self.osdCount -= nr_osd
        if nr_mrc > 0:
            for i in range(0, nr_mrc):
                node = self.mrcNodes.pop(0)
                self.controller.delete_nodes([node])
                self.nodes.remove(node)
            self.mrcCount -= nr_mrc
        if nr_dir > 0:
            for i in range(0, nr_dir):
                node = self.dirNode.pop(0)
                self.controller.delete_nodes([node])
                self.nodes.remove(node)
            self.dirCount -= nr_osd
        self.state = self.S_RUNNING

        # if there are no more OSD nodes we need to start OSD service on the DIR node
        if self.osdCount == 0:
            self.osdNodes.append(self.dirNodes[0])
            self._start_osd(self.dirNodes)
        return HttpJsonResponse()


    @expose('POST')
    def createMRC(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to create MRC service')
        # Just get_helloworld from all the agents
        for node in self.nodes:
            data = client.createMRC(node.ip, 5555,self.dirNodes[0].ip)
            self.logger.info('Received %s from %s', data, node.id)
        return HttpJsonResponse({
            'xtreemfs': [ node.id for node in self.nodes ],
            })   

    @expose('POST')
    def createDIR(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to create DIR service')
        # Just get_helloworld from all the agents
        for node in self.nodes:
            data = client.createDIR(node.ip, 5555)
            self.logger.info('Received %s from %s', data, node.id)
        return HttpJsonResponse({
            'xtreemfs': [ node.id for node in self.nodes ],
            })   

    @expose('POST')
    def createOSD(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to create OSD service')
        # Just get_helloworld from all the agents
        for node in self.nodes:
            data = client.createOSD(node.ip, 5555)
            self.logger.info('Received %s from %s', data, node.id)
        return HttpJsonResponse({
            'xtreemfs': [ node.id for node in self.nodes ],
            }) 
    
    @expose('POST') 
    def createVolume(self,kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to create Volume')
        if not 'volumeName' in kwargs:
            return HttpErrorResponse('ERROR: Required argument (volume Name) doesn\'t exist')

        volumeName = kwargs.pop('volumeName')
        if not 'owner' in kwargs:
            owner = "xtreemfs"
        else:
            owner = kwargs.pop('owner')
        args = ['mkfs.xtreemfs',self.mrcNodes[0].ip + ':32636/'+volumeName,"-u", owner,
                        "-g", owner,"-m", "744"]
        process = subprocess.Popen(args, \
                        stdout = subprocess.PIPE)
        (stdout,stderr) = process.communicate()
        process.poll()
        if process.returncode == 1:
            self.logger.info('Failed to create volume:%s;%s',stdout,stderr)
            return HttpErrorResponse("The volume could not be created");
        self.logger.info('Creating Volume:%s;%s',stdout,stderr)
        return HttpJsonResponse()

    @expose('POST') 
    def deleteVolume(self,kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to delete Volume')
        if not 'volumeName' in kwargs:
            return HttpErrorResponse('ERROR: Required argument (volume Name) doesn\'t exist')
        volumeName = kwargs.pop('volumeName')
        args = ['rmfs.xtreemfs',self.mrcNodes[0].ip + ':32636/'+volumeName]
        process = subprocess.Popen(args, \
                        stdout = subprocess.PIPE)
        (stdout,stderr) = process.communicate()
        process.poll()
        if process.returncode == 1:
            self.logger.info('Failed to delete volume:%s;%s',stdout,stderr)
            return HttpErrorResponse("The volume could not be deleted");
        self.logger.info('Deleting Volume:%s;%s',stdout,stderr)
        return HttpJsonResponse()

    @expose('GET')
    def viewVolumes(self,kwargs):
        if len(kwargs) !=0:
            return HttpErrorResponse('ERROR: Arguments unexpetced')
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to view volumes')
        args = ['lsfs.xtreemfs',self.mrcNodes[0].ip + ':32636']
        process = subprocess.Popen(args, \
                        stdout = subprocess.PIPE)
        (stdout,stderr) = process.communicate()
        process.poll()
        if process.returncode == 1:
            self.logger.info('Failed to view volume:%s;%s',stdout,stderr)
            return HttpErrorResponse("The volume list cannot be accessed");i
        return HttpJsonResponse({'volumes':stdout})

    @expose('GET')
    def getLog(self, kwargs):
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        try:
            fd = open(self.logfile)
            ret = ''
            s = fd.read()
            while s != '':
              ret += s
              s = fd.read()
              if s != '':
                  ret += s
            return HttpJsonResponse({'log': ret})
        except:
            return HttpErrorResponse('Failed to read log')
