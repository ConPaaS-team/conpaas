# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread

from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse

from conpaas.services.selenium.agent import client

class SeleniumManager(BaseManager):
    """Manager class with the following exposed methods:

    shutdown() -- POST
    add_nodes(count) -- POST
    remove_nodes(count) -- POST
    list_nodes() -- GET
    get_service_info() -- GET
    get_node_info(serviceNodeId) -- GET
    """
    def __init__(self, config_parser, **kwargs):
        """Initialize a Selenium Manager. 

        'config_parser' represents the manager config file. 
        **kwargs holds anything that can't be sent in config_parser."""
        BaseManager.__init__(self, config_parser)

        self.nodes = []

        # Setup the clouds' controller
        self.controller.generate_context('selenium')

        self.hub_ip = None

    def _do_startup(self, cloud):
        """Start up the service. The first node will be an agent running a
        Selenium Hub and a Selenium Node."""

        startCloud = self._init_cloud(cloud)
        vals = { 'action': '_do_startup', 'count': 1 }
        self.logger.debug(self.ACTION_REQUESTING_NODES % vals)

        try:
            nodes = self.controller.create_nodes(1,
                client.check_agent_process, self.AGENT_PORT, startCloud)

            hub_node = nodes[0]

            # The first agent is a Selenium Hub and a Selenium Node
            client.create_hub(hub_node.ip, self.AGENT_PORT)
            client.create_node(hub_node.ip, self.AGENT_PORT, hub_node.ip)

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
        self.nodes = []      		# Not only delete the nodes, but clear the list too
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
        self.controller.add_context_replacement(dict(STRING='selenium'))

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
        startCloud = self._init_cloud(cloud)
        """Add 'count' Selenium Nodes to this deployment"""
        node_instances = self.controller.create_nodes(count, 
            client.check_agent_process, self.AGENT_PORT, startCloud)

        # Startup agents
        for node in node_instances:
            client.create_node(node.ip, self.AGENT_PORT, self.hub_ip)

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
        the Selenium Hub gets removed last."""
        for _ in range(count):
            node = self.nodes.pop()
            self.logger.info("Removing node with IP %s" % node.ip)
            self.controller.delete_nodes([ node ])

        self.state = self.S_RUNNING

    def __is_hub(self, node):
        """Return True if the given node is the Selenium Hub"""
        return node.ip == self.hub_ip        

    @expose('GET')
    def list_nodes(self, kwargs):
        """Return a list of running nodes"""
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'list_nodes' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        selenium_nodes = [ 
            node.id for node in self.nodes if not self.__is_hub(node) 
        ]
        selenium_hub = [ 
            node.id for node in self.nodes if self.__is_hub(node) 
        ]

        return HttpJsonResponse({
            'hub': selenium_hub,
            'node': selenium_nodes
        })

    @expose('GET')
    def get_service_info(self, kwargs):
        """Return the service state and type"""
        return HttpJsonResponse({'state': self.state, 'type': 'selenium'})

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
