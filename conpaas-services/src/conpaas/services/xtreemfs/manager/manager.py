"""
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
 3. Neither the name of the Contrail consortium nor the
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
"""

from threading import Thread

from conpaas.core.expose import expose
from conpaas.core.controller import Controller

from conpaas.core.manager import BaseManager
from conpaas.core.manager import ManagerException

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse
                         
from conpaas.core.log import create_logger
from conpaas.services.xtreemfs.agent import client

import subprocess

def invalid_arg(msg):
    return HttpErrorResponse(ManagerException(
        ManagerException.E_ARGS_INVALID, detail=msg).message)

class XtreemFSManager(BaseManager):
    
    # Manager states - Used by the frontend
    S_INIT = 'INIT'         # manager initialized but not yet started
    S_PROLOGUE = 'PROLOGUE' # manager is starting up
    S_RUNNING = 'RUNNING'   # manager is running
    S_ADAPTING = 'ADAPTING' # manager is in a transient stata: frontend will
                            # keep polling until manager out of transient state
    S_EPILOGUE = 'EPILOGUE' # manager is shutting down
    S_STOPPED = 'STOPPED'   # manager stopped
    S_ERROR = 'ERROR'       # manager is in error state

    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser

        BaseManager.__init__(self, config_parser)

        # node lists
        self.nodes = []    # all nodes         
        self.osdNodes = [] # only the OSD nodes  
        self.mrcNodes = [] # onle the MRC nodes
        self.dirNodes = [] # only the DIR nodes   

        # node counters
        self.dirCount = 0
        self.mrcCount = 0
        self.osdCount = 0

        # Setup the clouds' controller
        self.controller.generate_context('xtreemfs')
        self.state = self.S_INIT

    @expose('POST')
    def startup(self, kwargs):
        self.logger.debug("XtreemFSManager startup")
        if len(kwargs) != 0:
            return HttpErrorResponse(ManagerException(
                ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        if self.state != self.S_INIT and self.state != self.S_STOPPED:
            return HttpErrorResponse(ManagerException(
                ManagerException.E_STATE_ERROR).message)

        self.state = self.S_PROLOGUE
        Thread(target=self._do_startup, args=[]).start()
        return HttpJsonResponse({'state': self.S_PROLOGUE})

    
    def _start_dir(self, nodes):
        for node in nodes:
            try:
                client.createDIR(node.ip, 5555)
            except client.AgentException:
                self.logger.exception('Failed to start DIR at node %s' % node)
                self.state = self.S_ERROR
                raise

    def _start_mrc(self, nodes):
        for node in nodes:
            try:
                client.createMRC(node.ip, 5555, self.dirNodes[0].ip)
            except client.AgentException:
                self.logger.exception('Failed to start MRC at node %s' % node)
                self.state = self.S_ERROR
                raise

    def _start_osd(self, nodes):
        for node in nodes:
            try:
                client.createOSD(node.ip, 5555, self.dirNodes[0].ip)
            except client.AgentException:
                self.logger.exception('Failed to start OSD at node %s' % node)
                self.state = self.S_ERROR
                raise

    def _stop_osd(self, nodes):
        for node in nodes:
            try:
                client.stopOSD(node.ip, 5555)
            except client.AgentException:
                self.logger.exception('Failed to stop OSD at node %s' % node)
                self.state = self.S_ERROR
                raise

    def _do_startup(self):
        ''' Starts up the service. The firstnodes will contain all services
        '''
        try:
            # NOTE: The following service structure is enforce:
            #       - the first node contains a DIR, MRC and OSD,
            #         those services can not be removed
            #       - added DIR, MRC and OSD services will all run
            #         on exclusive nodes
            #       - all explicitly added services can be removed
            #
            # TODO: Currently, only OSDs can be removed, which might
            #       result in data loss depending on the replication
            #       policy. Removing a node in ConPaaS is the same to
            #       XtreemFS as node failure.

            # create 1 node
            node_instances = self.controller.create_nodes(1, \
                                           client.check_agent_process, 5555)
          
            # use this node for DIR, MRC and OSD
            self.nodes += node_instances
            self.dirNodes += node_instances
            self.mrcNodes += node_instances
            self.osdNodes += node_instances
            
            # start DIR, MRC, OSD
            self._start_dir(self.dirNodes)
            self._start_mrc(self.mrcNodes)
            self._start_osd(self.osdNodes)

            # at the startup the DIR node will have all the services
            self.dirCount = 1
            self.mrcCount = 1
            self.osdCount = 1

            self.logger.info('Created 1 node with DIR, MRC and OSD services')
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
        self.dirNodes = []          
        self.mrcNodes = []
        self.osdNodes = []   
    
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
        nr_osd = 0
        
        # Adding DIR Nodes
        if 'dir' in kwargs:
            if not isinstance(kwargs['dir'], int):
                return invalid_arg('Expected an integer value for "dir"')
            nr_dir = int(kwargs.pop('dir'))    
            if nr_dir < 0: 
                return invalid_arg('Expected a positive integer value for "dir"')

        # Adding MRC Nodes
        if 'mrc' in kwargs:
            if not isinstance(kwargs['mrc'], int):
                return invalid_arg('Expected an integer value for "mrc"')
            nr_mrc = int(kwargs.pop('mrc'))
            if nr_mrc < 0: 
                return invalid_arg('Expected a positive integer value for "mrc"')

        # TODO: 'osd' is no longer required, when adding other servives is supported
        if not 'osd' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['osd'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "osd"')

        nr_osd = int(kwargs.pop('osd'))
        if nr_osd < 0: 
            return invalid_arg('Expected a positive integer value for "nr osd"')

        self.state = self.S_ADAPTING
        Thread(target=self._do_add_nodes, args=[nr_dir, nr_mrc, nr_osd]).start()
        return HttpJsonResponse()
    
    # TODO: currently not used
    def KillOsd(self, nodes):
        for node in nodes:
            client.stopOSD(node.ip, 5555)
            self.osdNodes.remove(node)

    def _do_add_nodes(self, nr_dir, nr_mrc, nr_osd):
        totalNodes = nr_dir + nr_mrc + nr_osd

        # try to create totalNodes new nodes
        try:
            node_instances = self.controller.create_nodes(totalNodes, 
                client.check_agent_process, 5555)      
        except:
            self.logger.exception('_do_add_nodes: Failed to request a new node')
            self.state = self.S_STOPPED
            return

        self.nodes += node_instances 

        dirNodesAdded = node_instances[:nr_dir]
        self.dirNodes += dirNodesAdded

        mrcNodesAdded = node_instances[nr_dir:nr_mrc+nr_dir]
        self.mrcNodes += mrcNodesAdded

        osdNodesAdded = node_instances[nr_mrc+nr_dir:] 
        self.osdNodes += osdNodesAdded


        # TODO: maybe re-enable when OSD-removal moves data to another node before shutting down the service.
        #KilledOsdNodes = []
        # The first node will contain the OSD service so it will be removed
        # from there
        #if nr_osd > 0 and self.osdCount == 0:
        #    KilledOsdNodes.append(self.dirNodes[0])
        #self.KillOsd(KilledOsdNodes)
          
        # Startup DIR agents
        for node in dirNodesAdded:
            client.startup(node.ip, 5555)
            data = client.createDIR(node.ip, 5555)
            self.logger.info('Received %s from %s', data, node.id)
            self.dirCount += 1

        # Startup MRC agents
        for node in mrcNodesAdded:
            client.startup(node.ip, 5555)
            data = client.createMRC(node.ip, 5555, self.dirNodes[0].ip)
            self.logger.info('Received %s from %s', data, node.id)
            self.mrcCount += 1

        # Startup OSD agents
        for node in osdNodesAdded:
            client.startup(node.ip, 5555)
            data = client.createOSD(node.ip, 5555, self.dirNodes[0].ip)
            self.logger.info('Received %s from %s', data, node.id)         
            self.osdCount += 1

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
        nr_osd = 0
            
        # Removing DIR Nodes
        if 'dir' in kwargs:
            if not isinstance(kwargs['dir'], int):
                return invalid_arg('Expected an integer value for "dir"')
            nr_dir = int(kwargs.pop('dir'))    
            if nr_dir < 0: 
                return invalid_arg('Expected a positive integer value for "dir"')
            if nr_dir > self.dirCount - 1: # we need at least 1 DIR
                return invalid_arg('Cannot remove_nodes that many DIR nodes')
     
        # Removing MRC nodes
        if 'mrc' in kwargs:
            if not isinstance(kwargs['mrc'], int):
                return invalid_arg('Expected an integer value for "mrc"')
            nr_mrc = int(kwargs.pop('mrc'))
            if nr_mrc < 0: 
                return invalid_arg('Expected a positive integer value for "mrc"')
            if nr_mrc > self.mrcCount - 1: # we need at least 1 MRC
                return invalid_arg('Cannot remove_nodes that many MRC nodes')

        # TODO: 'osd' is no longer required, when removing other services is supported
        if not 'osd' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['osd'], int):
            return HttpErrorResponse(
                'ERROR: Expected an integer value for "osd"')

        nr_osd = int(kwargs.pop('osd'))
        if nr_osd < 0: 
            return invalid_arg('Expected a positive integer value for "osd"')
        if nr_osd > self.osdCount - 1: # we need at least 1 OSD
            return invalid_arg('Cannot remove_nodes that many OSD nodes')

        self.state = self.S_ADAPTING
        Thread(target=self._do_remove_nodes, args=[nr_dir, nr_mrc, nr_osd]).start()
        return HttpJsonResponse()

    def _do_remove_nodes(self, nr_dir, nr_mrc, nr_osd):
        
        # NOTE: the logically unremovable first node which contains all
        #       services is ignored by using 1 instead of 0 in:
        #   for _ in range(1, nr_[dir|mrc|osd]):
        #        node = self.[dir|mrc|osd]Nodes.pop(1)

        if nr_dir > 0:
            for _ in range(0, nr_dir):
                node = self.dirNodes.pop(1)
                self.controller.delete_nodes([node])
                self.nodes.remove(node)
            self.dirCount -= nr_osd

        if nr_mrc > 0:
            for _ in range(0, nr_mrc):
                node = self.mrcNodes.pop(1)
                self.controller.delete_nodes([node])
                self.nodes.remove(node)
            self.mrcCount -= nr_mrc

        if nr_osd > 0:
            for _ in range(0, nr_osd):
                node = self.osdNodes.pop(1)
                self._stop_osd([node])
                self.controller.delete_nodes([node])
                self.nodes.remove(node)
            self.osdCount -= nr_osd

        self.state = self.S_RUNNING

        # TODO: maybe re-enable when OSD-removal moves data to another node before shutting down the service.
        # if there are no more OSD nodes we need to start OSD service on the
        # DIR node
        #if self.osdCount == 0:
        #    self.osdNodes.append(self.dirNodes[0])
        #    self._start_osd(self.dirNodes)

        return HttpJsonResponse()


    @expose('POST')
    def createMRC(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to create MRC service')
        # Just get_helloworld from all the agents
        for node in self.nodes:
            data = client.createMRC(node.ip, 5555, self.dirNodes[0].ip)
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
            data = client.createOSD(node.ip, 5555, self.dirNodes[0].ip)
            self.logger.info('Received %s from %s', data, node.id)
        return HttpJsonResponse({
            'xtreemfs': [ node.id for node in self.nodes ],
            }) 
    
    @expose('POST') 
    def createVolume(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to create Volume')

        if not 'volumeName' in kwargs:
            return HttpErrorResponse(
                'ERROR: Required argument (volumeName) doesn\'t exist')

        volumeName = kwargs.pop('volumeName')

        # Get the value of 'owner', if specified. 'xtreemfs' otherwise
        owner = kwargs.pop('owner', 'xtreemfs')

        args = [ 'mkfs.xtreemfs',
                 '%s:32636/%s' % (self.mrcNodes[0].ip, volumeName),
                 "-u", owner,
                 "-g", owner,
                 "-m", "744" ]

        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        (stdout, stderr) = process.communicate()
        process.poll()

        if process.returncode == 1:
            self.logger.info('Failed to create volume:%s;%s', stdout, stderr)
            return HttpErrorResponse("The volume could not be created")

        self.logger.info('Creating Volume:%s;%s', stdout, stderr)
        return HttpJsonResponse()

    @expose('POST') 
    def deleteVolume(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to delete Volume')

        if not 'volumeName' in kwargs:
            return HttpErrorResponse(
                'ERROR: Required argument (volumeName) doesn\'t exist')

        volumeName = kwargs.pop('volumeName')

        args = [ 'rmfs.xtreemfs',
                 '%s:32636/%s' % (self.mrcNodes[0].ip, volumeName) ]

        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        (stdout, stderr) = process.communicate()
        process.poll()

        if process.returncode == 1:
            self.logger.info('Failed to delete volume:%s;%s', stdout, stderr)
            return HttpErrorResponse("The volume could not be deleted")

        self.logger.info('Deleting Volume:%s;%s', stdout, stderr)
        return HttpJsonResponse()

    @expose('GET')
    def viewVolumes(self, kwargs):
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpetced')

        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to view volumes')

        args = [ 'lsfs.xtreemfs', self.mrcNodes[0].ip + ':32636' ]

        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        (stdout, stderr) = process.communicate()
        process.poll()

        if process.returncode == 1:
            self.logger.info('Failed to view volume:%s;%s', stdout, stderr)
            return HttpErrorResponse("The volume list cannot be accessed")

        return HttpJsonResponse({ 'volumes': stdout })
