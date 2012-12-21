from threading import Thread

from conpaas.core.expose import expose
from conpaas.core.controller import Controller
from conpaas.core.manager import BaseManager

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse

from conpaas.core.log import create_logger
from conpaas.services.helloworld.agent import client

class HelloWorldManager(BaseManager):

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
        BaseManager.__init__(self, config_parser)
        self.nodes = []
        # Setup the clouds' controller
        self.controller.generate_context('helloworld')
        self.state = self.S_INIT

    @expose('POST')
    def startup(self, kwargs):
        self.logger.info('Manager started up')
        self.state = self.S_RUNNING
        return HttpJsonResponse()

    @expose('POST')
    def shutdown(self, kwargs):
        self.state = self.S_EPILOGUE
        Thread(target=self._do_shutdown, args=[]).start()
        return HttpJsonResponse()

    def _do_shutdown(self):
        self.controller.delete_nodes(self.nodes)
        self.state = self.S_STOPPED
        return HttpJsonResponse()

    @expose('POST')
    def add_nodes(self, kwargs):
        self.controller.update_context(dict(STRING='helloworld'))
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to add_nodes')
        if not 'count' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['count'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "count"')
        count = int(kwargs.pop('count'))
        self.state = self.S_ADAPTING
        Thread(target=self._do_add_nodes, args=[count]).start()
        return HttpJsonResponse()

    def _do_add_nodes(self, count):
        node_instances = self.controller.create_nodes(count, \
                                           client.check_agent_process, 5555)
        self.nodes += node_instances
        # Startup agents
        for node in node_instances:
           client.startup(node.ip, 5555)
        self.state = self.S_RUNNING
        return HttpJsonResponse()

    @expose('GET')
    def list_nodes(self, kwargs):
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to list_nodes')
        return HttpJsonResponse({
              'helloworld': [ node.id for node in self.nodes ],
              })

    @expose('GET')
    def get_service_info(self, kwargs):
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        return HttpJsonResponse({'state': self.state, 'type': 'helloworld'})

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
                            'ip': serviceNode.ip
                            }
            })

    @expose('POST')
    def remove_nodes(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to remove_nodes')
        if not 'count' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['count'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "count"')
        count = int(kwargs.pop('count'))
        self.state = self.S_ADAPTING
        Thread(target=self._do_remove_nodes, args=[count]).start()
        return HttpJsonResponse()

    def _do_remove_nodes(self, count):
        for i in range(0, count):
            self.controller.delete_nodes([self.nodes.pop(0)])
        self.state = self.S_RUNNING
        return HttpJsonResponse()

    @expose('GET')
    def get_helloworld(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to get_helloworld')
        # Just get_helloworld from all the agents
        for node in self.nodes:
            data = client.get_helloworld(node.ip, 5555)
            self.logger.info('Received %s from %s', data, node.id)
        return HttpJsonResponse({
            'helloworld': [ node.id for node in self.nodes ],
            })
