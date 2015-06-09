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
"""

# TODO: as this file was created from a BLUEPRINT file,
# 	you may want to change ports, paths and/or methods (e.g. for hub)
#	to meet your specific service/server needs

from threading import Thread
import time, os
from conpaas.core.expose import expose
from conpaas.core.controller import Controller
from conpaas.core.manager import BaseManager

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse
                          
from conpaas.core.log import create_logger
from conpaas.services.hadoopnaas.agent import client

class HadoopNaasManager(BaseManager):
    """Manager class with the following exposed methods:

    startup() -- POST
    shutdown() -- POST
    add_nodes(count) -- POST
    remove_nodes(count) -- POST
    list_nodes() -- GET
    get_service_info() -- GET
    get_node_info(serviceNodeId) -- GET
    """
    # Manager states 
    S_INIT = 'INIT'         # manager initialized but not yet started
    S_PROLOGUE = 'PROLOGUE' # manager is starting up
    S_RUNNING = 'RUNNING'   # manager is running
    S_ADAPTING = 'ADAPTING' # manager is in a transient state - frontend will 
                            # keep polling until manager out of transient state
    S_EPILOGUE = 'EPILOGUE' # manager is shutting down
    S_STOPPED = 'STOPPED'   # manager stopped
    S_ERROR = 'ERROR'       # manager is in error state

    # String template for error messages returned when performing actions in
    # the wrong state
    WRONG_STATE_MSG = "ERROR: cannot perform %(action)s in state %(curstate)s"

    # String template for error messages returned when a required argument is
    # missing
    REQUIRED_ARG_MSG = "ERROR: %(arg)s is a required argument"

    # String template for debugging messages logged on nodes creation
    ACTION_REQUESTING_NODES = "requesting %(count)s nodes in %(action)s"

    AGENT_PORT = 5555

    INITIAL_NODES = 5


    def __init__(self, config_parser, **kwargs):
        """Initialize a BluePrint Manager. 

        'config_parser' represents the manager config file. 
        **kwargs holds anything that can't be sent in config_parser."""
        BaseManager.__init__(self, config_parser)

        self.reservation_ids = []
        self.nodes = []
        self.MAPPERS = []
        self.NAASBOX = None
        self.MASTER = None
        self.REDUCER = None

        # Setup the clouds' controller
        self.controller.generate_context('hadoopnaas')

        self.state = self.S_INIT
       


    @expose('POST')
    def startup(self, kwargs):
        """Start the BluePrint service"""
        self.logger.info('Manager starting up')

        # Starting up the service makes sense only in the INIT or STOPPED
        # states
        if self.state != self.S_INIT and self.state != self.S_STOPPED:
            vals = { 'curstate': self.state, 'action': 'startup' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        self.state = self.S_PROLOGUE
        Thread(target=self._do_startup, args=[]).start()

        return HttpJsonResponse({ 'state': self.state })


    def _do_startup(self):
        """Start up the service. The first node will be an agent running a
        BluePrint Hub and a BluePrint Node."""

        vals = { 'action': '_do_startup', 'count': 1 }
        self.logger.debug(self.ACTION_REQUESTING_NODES % vals)

        try:

            self.nodes = self.reserve(self.INITIAL_NODES)
            self.logger.debug('nodes: %s' % self.nodes)
            self.update_hosts()

            self.MASTER = self.nodes[0]
            self.NAASBOX = self.nodes[1]
            self.REDUCER = self.nodes[2]
            self.MAPPERS.append(self.nodes[3])
            self.MAPPERS.append(self.nodes[4])

            time.sleep(5)

            self.logger.debug('Setting master at %s [%s]' % (self.MASTER['Address'],self.MASTER['ID'] ))
            # Setup Master node
            client.setup_node(self.MASTER['Address'],self.AGENT_PORT,self.MASTER,self.NAASBOX,True,False,self.MASTER)

            self.logger.debug('Setting naasbox at %s [%s]' % (self.NAASBOX['Address'],self.NAASBOX['ID'] ))
            # Setup Naasbox
            client.setup_naasbox(self.NAASBOX['Address'],self.AGENT_PORT,self.NAASBOX)

            self.logger.debug('Setting reducer at %s [%s]' % (self.REDUCER['Address'],self.REDUCER['ID'] ))
            # Setup Reducer
            client.make_worker(self.REDUCER['Address'],self.AGENT_PORT)
            client.setup_node(self.REDUCER['Address'],self.AGENT_PORT,self.MASTER,self.NAASBOX,False,True,self.REDUCER)

            self.logger.debug('Setting mapper at %s [%s]' % (self.MAPPERS[0]['Address'],self.MAPPERS[0]['ID'] ))
            # Setup the first mapper
            client.make_worker(self.MAPPERS[0]['Address'],self.AGENT_PORT)
            client.setup_node(self.MAPPERS[0]['Address'],self.AGENT_PORT,self.MASTER,self.NAASBOX,False,False,self.MAPPERS[0])

            self.logger.debug('Setting mapper at %s [%s]' % (self.MAPPERS[1]['Address'],self.MAPPERS[1]['ID'] ))
            # Setup the first mapper
            client.make_worker(self.MAPPERS[1]['Address'],self.AGENT_PORT)
            client.setup_node(self.MAPPERS[1]['Address'],self.AGENT_PORT,self.MASTER,self.NAASBOX,False,False,self.MAPPERS[1])

            # Append slaves to slaves file on master
            client.append_slaves(self.MASTER['Address'],self.AGENT_PORT, [self.REDUCER, self.MAPPERS[0], self.MAPPERS[1]])
            # client.append_slave(self.MASTER['Address'],self.AGENT_PORT,)
            # client.append_slave(self.MASTER['Address'],self.AGENT_PORT,self.MAPPERS[1])

            
            self.state = self.S_RUNNING

            # # Enable ssh and fix hosts
            for node in self.nodes:
                client.enable_ssh(self.MASTER['Address'],self.AGENT_PORT,node)
                time.sleep(1)


            client.start_all(self.MASTER['Address'],self.AGENT_PORT)
            # for node in self.nodes:
            #     for inner_node in self.nodes:
            #         client.enable_ssh(inner_node['Address'],self.AGENT_PORT,node)
            #         time.sleep(1)

        except Exception, err:
            self.logger.exception('_do_startup: Failed to start agent: %s' % err)
            self.state = self.S_ERROR

    def createRandomID(self, size):
        import binascii
        return binascii.b2a_hex(os.urandom(size))
    
    def reserve(self, count):
        configuration = {'Resources' : [{'GroupID' : 'hdp-%s'%self.createRandomID(4), 'NumInstances' : count, 'Type' : 'Machine', 'Attributes' : {'Cores' : 1, 'Memory' : 1024}}]}
        reservation = self.controller.prepare_reservation(configuration)
        self.reservation_ids += reservation['ConfigID']
        reservation = self.controller.create_reservation_test(reservation, client.check_agent_process, self.AGENT_PORT)
        return reservation['Instances']

    def get_startup_nodes(self):
        return self.INITIAL_NODES
    
    def update_hosts(self):
        for node in self.nodes: 
            try:                                           
                client.update_host(node['Address'], 5555, node, self.nodes)            
            except Exception:                                                                
                self.logger.exception('Failed to update host at node %s' % str(node))             
                self.state = self.S_ERROR
                raise        
        self.logger.info('Instances %s' % self.nodes)

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
        for reservation_id in self.reservation_ids:
            self.controller.release_reservation(reservation_id)
        self.nodes = []     # Not only delete the nodes, but clear the list too
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

    # @expose('POST')
    # def add_nodes(self, kwargs):
    #     """Add kwargs['count'] nodes to this deployment"""
    #     #self.controller.update_context(dict(STRING='blueprint'))

    #     # Adding nodes makes sense only in the RUNNING state
    #     if self.state != self.S_RUNNING:
    #         vals = { 'curstate': self.state, 'action': 'add_nodes' }
    #         return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

    #     # Ensure 'count' is valid
    #     count_or_err = self.__check_count_in_args(kwargs)        
    #     if isinstance(count_or_err, HttpErrorResponse):
    #         return count_or_err

    #     count = count_or_err

    #     self.state = self.S_ADAPTING
    #     Thread(target=self._do_add_nodes, args=[count]).start()

    #     return HttpJsonResponse({ 'state': self.state })

    # def _do_add_nodes(self, count):
    #     """Add 'count' BluePrint Nodes to this deployment"""
    #     node_instances = self.controller.create_nodes(count, client.check_agent_process, self.AGENT_PORT)

    #     # Startup agents
    #     for node in node_instances:
    #         client.create_node(node['Address'], self.AGENT_PORT)
    #         client.make_worker(node['Address'],self.AGENT_PORT)
    #         client.setup_node(node['Address'],self.AGENT_PORT,self.MASTER,self.NAASBOX,False,False,node)
    #         client.append_slave(self.MASTER['Address'],self.AGENT_PORT,node)
    #         client.enable_ssh(self.MASTER['Address'],self.AGENT_PORT,node)
    #         self.MAPPERS.append(node)

    #     self.nodes += node_instances
    #     self.state = self.S_RUNNING

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

        self.state = self.S_ADAPTING
        Thread(target=self._do_remove_nodes, args=[count]).start()

        return HttpJsonResponse({ 'state': self.state })

    def _do_remove_nodes(self, count):
        """Remove 'count' nodes, starting from the end of the list. This way
        the BluePrint Hub gets removed last."""
        for _ in range(count):
            node = self.nodes.pop()
            self.logger.info("Removing node with IP %s" % node["Address"])
            self.controller.delete_nodes([ node ])

        self.state = self.S_RUNNING

    @expose('GET')
    def list_nodes(self, kwargs):
        """Return a list of running nodes"""
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'list_nodes' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        node_ids = [node["ID"] for node in self.MAPPERS ]
        return HttpJsonResponse({
            'master': self.MASTER["ID"],
            'nassbox': self.NAASBOX["ID"],
            'node': node_ids
        })

    @expose('GET')
    def get_service_info(self, kwargs):
        """Return the service state and type"""
        return HttpJsonResponse({'state': self.state, 'type': 'hadoopnaas'})

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
            if serviceNodeId == node['ID']:
                serviceNode = node
                break

        if serviceNode is None:
            return HttpErrorResponse(
                'ERROR: Cannot find node with serviceNode=%s' % serviceNodeId)

        return HttpJsonResponse({
            'serviceNode': { 
                'id': serviceNode['ID'], 
                'ip': serviceNode['IP']
            }
        })

    @expose('GET')
    def test(self, kwargs):
        """Return test messages from all the agents"""
        #msgsum = ''
        #for node in self.nodes:
        #    msgsum += client.test(node.ip, self.AGENT_PORT)['msg'] + '\n'

        for node in self.nodes:
            client.enable_ssh(self.MASTER.ip,self.AGENT_PORT,node.ip)

        return HttpJsonResponse({'msgs': 'done'})
