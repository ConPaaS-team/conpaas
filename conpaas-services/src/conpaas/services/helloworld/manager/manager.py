from threading import Thread

from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse

from conpaas.services.helloworld.agent import client

class HelloWorldManager(BaseManager):

    # Manager states - Used by the Director
    S_INIT = 'INIT'         # manager initialized but not yet started
    S_PROLOGUE = 'PROLOGUE' # manager is starting up
    S_RUNNING = 'RUNNING'   # manager is running
    S_ADAPTING = 'ADAPTING' # manager is in a transient state - frontend will keep
                            # polling until manager out of transient state
    S_EPILOGUE = 'EPILOGUE' # manager is shutting down
    S_STOPPED = 'STOPPED'   # manager stopped
    S_ERROR = 'ERROR'       # manager is in error state

    AGENT_PORT = 5555

    def __init__(self, config_parser, **kwargs):
        BaseManager.__init__(self, config_parser)
        self.nodes = []
        # Setup the clouds' controller
        # self.controller.generate_context('helloworld')
        self.state = self.S_INIT


    def get_service_type(self):
        return 'helloworld'

    def get_context_replacement(self):
        return dict(STRING='helloworld')


    def on_start(self, nodes):
        return self.on_new_nodes(nodes)

    def on_stop(self):
        self.logger.info("Removing nodes: %s" %[ node.id for node in self.nodes ])
        return self.nodes[:]

    def on_add_nodes(self, nodes):
        return self.on_new_nodes(nodes)

    def on_remove_nodes(self, noderoles):
        count = sum(noderoles.values())
        del_nodes = []
        cp_nodes = self.nodes[:]
        for _ in range(0, count):
            node = cp_nodes.pop()
            del_nodes += [ node ]
        if not cp_nodes:         
            self.state = self.S_STOPPED
        else:
            self.state = self.S_RUNNING

        self.logger.info("Removing nodes: %s" %[ node.id for node in del_nodes ])
        return del_nodes

    def on_new_nodes(self, nodes):
        try:
            for node in nodes:
                client.startup(node.ip, self.AGENT_PORT)
            return True
        except Exception, err:
            self.logger.exception('_do_startup: Failed to create node: %s' % err)
            return False


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

    

    @expose('GET')
    def get_helloworld(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to get_helloworld')

        messages = []

        # Just get_helloworld from all the agents
        for node in self.nodes:
            data = client.get_helloworld(node.ip, self.AGENT_PORT)
            message = 'Received %s from %s' % (data['result'], node.id)
            self.logger.info(message)
            messages.append(message)

        return HttpJsonResponse({ 'helloworld': "\n".join(messages) })
