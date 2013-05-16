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

from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse

from conpaas.services.taskfarm.agent import client
# import node_info

class TaskFarmManager(BaseManager):
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

    def __init__(self, config_parser, **kwargs):
        """Initialize a TaskFarm Manager. 

        'config_parser' represents the manager config file. 
        **kwargs holds anything that can't be sent in config_parser."""
        BaseManager.__init__(self, config_parser)

        self.nodes = []

        # Setup the clouds' controller
        self.controller.generate_context('taskfarm')

        self.state = self.S_INIT
        self.hub_ip = None

    @expose('POST')
    def startup(self, kwargs):
        """Start the TaskFarm service"""
        self.logger.info('Manager starting up')

        # Starting up the service makes sense only in the INIT or STOPPED
        # states
        if self.state != self.S_INIT and self.state != self.S_STOPPED:
            vals = { 'curstate': self.state, 'action': 'startup' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        self.state = self.S_PROLOGUE
        Thread(target=self._do_startup, kwargs=kwargs).start()

        return HttpJsonResponse({ 'state': self.state })

    def _do_startup(self, cloud):
        """Start up the service. The first node will be an agent running a
        TaskFarm Hub and a TaskFarm Node."""

        startCloud = self._init_cloud(cloud)
        vals = { 'action': '_do_startup', 'count': 1 }
        self.logger.debug(self.ACTION_REQUESTING_NODES % vals)

        try:
            nodes = self.controller.create_nodes(1,
                client.check_agent_process, self.AGENT_PORT, startCloud)

            hub_node = nodes[0]

            # The first agent is a TaskFarm Hub and a TaskFarm Node
            client.create_hub(hub_node.ip, self.AGENT_PORT)
            client.create_node(hub_node.ip, self.AGENT_PORT, hub_node.ip)
            self.logger.info("Added node %s: %s " % (hub_node.id, hub_node.ip))
            # node_info.add_node_info('/etc/hosts', hub_node.ip, hub_node.id)

            self.hub_ip = hub_node.ip

            # Extend the nodes list with the newly created one
            self.nodes += nodes
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
        self.controller.update_context(dict(STRING='taskfarm'))

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
        Thread(target=self._do_add_nodes, args=[count, kwargs['cloud']]).start()

        return HttpJsonResponse({ 'state': self.state })

    def _do_add_nodes(self, count, cloud):
        """Add 'count' TaskFarm Nodes to this deployment"""
        startCloud = self._init_cloud(cloud)
        vals = { 'action': '_do_add_nodes', 'count': count }
        self.logger.debug(self.ACTION_REQUESTING_NODES % vals)
        node_instances = self.controller.create_nodes(count, 
            client.check_agent_process, self.AGENT_PORT, startCloud)

        # Startup agents
        for node in node_instances:
            client.create_node(node.ip, self.AGENT_PORT, self.hub_ip)
            self.logger.info("Added node %s: %s " % (node.id, node.ip))
            # node_info.add_node_info('/etc/hosts', node.ip, node.id)

        self.nodes += node_instances
        self.state = self.S_RUNNING

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
        the TaskFarm Hub gets removed last."""
        for _ in range(count):
            node = self.nodes.pop()
            self.logger.info("Removing node with IP %s" % node.ip)
            self.controller.delete_nodes([ node ])
            # node_info.remove_node_info('/etc/hosts', node.ip)

        self.state = self.S_RUNNING

    def __is_hub(self, node):
        """Return True if the given node is the TaskFarm Hub"""
        return node.ip == self.hub_ip        

    @expose('GET')
    def list_nodes(self, kwargs):
        """Return a list of running nodes"""
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'list_nodes' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        taskfarm_nodes = [ 
            node.id for node in self.nodes if not self.__is_hub(node) 
        ]
        taskfarm_hub = [ 
            node.id for node in self.nodes if self.__is_hub(node) 
        ]

        return HttpJsonResponse({
            'hub': taskfarm_hub,
            'node': taskfarm_nodes
        })

    @expose('GET')
    def get_service_info(self, kwargs):
        """Return the service state and type"""
        return HttpJsonResponse({'state': self.state, 'type': 'taskfarm'})

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
