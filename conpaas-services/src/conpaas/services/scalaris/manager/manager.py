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

Created February, 2012

@author tschuett

'''

from threading import Thread

from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager
from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse, HttpError
from conpaas.services.scalaris.agent import client

class ScalarisManager(BaseManager):

    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser
                                # (hopefully the new service won't need anything extra)
        BaseManager.__init__(self, config_parser)
        self.nodes = []
        self.context = {'FIRST': 'true', 'MGMT_SERVER': '', 'KNOWN_HOSTS': ''}
        # Setup the clouds' controller
        self.controller.generate_context('scalaris')

    def _do_startup(self, cloud):
        ''' Starts up the service. At least one node should be running scalaris
            when the service is started.
        '''
        startCloud = self._init_cloud(cloud)
        try:
          self.controller.update_context(self.context, startCloud)
          instance = self.controller.create_nodes(1, \
            client.check_agent_process, 5555, startCloud)
          self.nodes += instance
          self.logger.info('Created node: %s', instance[0])
          client.startup(instance[0].ip, 5555, instance[0].ip)
          self.logger.info('Called startup: %s', instance[0])
          self.context['FIRST'] = 'false'
          self.context['MGMT_SERVER']=self._render_node(instance[0], 'mgmt_server')
          self.logger.info('Finished first node')
          self.controller.update_context(self.context, startCloud)
        except:
            self.logger.exception('do_startup: Failed to request a new node')
            self.state = self.S_STOPPED
            return
        self.state = self.S_RUNNING

    @expose('POST')
    def shutdown(self, kwargs):
        self.state = self.S_EPILOGUE
        Thread(target=self._do_shutdown, args=[]).start()
        return HttpJsonResponse()

    def _do_shutdown(self):
      self.controller.delete_nodes(self.nodes)
      #TODO: solve race condition wih get_service_info?
      self.nodes = []
      self.state = self.S_STOPPED
      self.context['FIRST'] = 'true'
      self.context['MGMT_SERVER']= ''
      self.context['KNOWN_HOSTS']= ''
      return HttpJsonResponse()

    @expose('POST')
    def add_nodes(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to add_nodes')
        if not 'scalaris' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['scalaris'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "count"')
        count = int(kwargs.pop('scalaris'))
        # create at least one node
        if count < 1:
            return HttpErrorResponse('ERROR: Expected a positive integer value for "count"')
        self.state = self.S_ADAPTING
        Thread(target=self._do_add_nodes, args=[count, kwargs['cloud']]).start()
        return HttpJsonResponse()

    def _do_add_nodes(self, count, cloud):
        startCloud = self._init_cloud(cloud)
        try:
            self.logger.info('Starting nodes: %d', count)
            self.context['KNOWN_HOSTS']=self._render_known_hosts()
            self.controller.update_context(self.context, startCloud)
            node_instances = self.controller.create_nodes(count,
                client.check_agent_process, 5555, startCloud)
            self.logger.info('Create nodes: %s', node_instances)
            self.nodes += node_instances
            # Startup agents
            for node in node_instances:
                client.startup(node.ip, 5555, node.ip)
            self.state = self.S_RUNNING
            self.logger.info('Started nodes: %d %s', count, self.state)
        except HttpError as e:
            self.logger.info('exception in _do_add_nodes2: %s', e)
            return HttpJsonResponse()
        except Exception as e:
            self.logger.info('exception in _do_add_nodes1: %s', e)
            return HttpJsonResponse()
        finally:
            self.logger.info('finished _do_add_nodes')
            return HttpJsonResponse()

    def _render_node(self, node, role):
        ip = node.ip.replace('.', ',')
        return '{{' + ip + '},14195,' + role + '}'

    def _render_known_hosts(self):
        rendered_nodes = [self._render_node(node, 'service_per_vm') for node in self.nodes]
        return '[' + ', '.join(rendered_nodes) + ']'

    @expose('GET')
    def list_nodes(self, kwargs):
        self.logger.info('called list_nodes')
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to list_nodes')
        return HttpJsonResponse({
              'scalaris': [ node.id for node in self.nodes ],
              })

    @expose('GET')
    def get_service_info(self, kwargs):
        self.logger.info('called get_service_info: %s', self.state)
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        result = {'state': self.state, 'type': 'scalaris'}
        if len(self.nodes) > 0:
            result['mgmt_location'] = 'http://' + self.nodes[0].ip + ':8000'
            try:
                result['service_info'] = client.get_service_info(self.nodes[0].ip, 5555)
            except HttpError as e:
                self.logger.info('exception in get_service_info: %s', e)
            except:
                self.logger.info('unknown exception in get_service_info')

        return HttpJsonResponse(result)

    @expose('GET')
    def get_node_info(self, kwargs):
        self.logger.info('called get_node_info')
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
        self.logger.info('called remove_nodes')
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to remove_nodes')
        if not 'scalaris' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['scalaris'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "count"')
        count = int(kwargs.pop('scalaris'))
        self.state = self.S_ADAPTING
        Thread(target=self._do_remove_nodes, args=[count]).start()
        return HttpJsonResponse()

    def _do_remove_nodes(self, count):
        if count > len(self.nodes) - 1:
            self.state = self.S_RUNNING
            return HttpErrorResponse('ERROR: Cannot delete so many workers')
        if count == len(self.nodes):
            self.logger.info('killing the nodes')
            for i in range(0, count):
                self.controller.delete_nodes([self.nodes.pop(1)])
            self.state = self.S_RUNNING
            return HttpJsonResponse()
        else:
            for i in range(0, count):
                node = self.nodes.pop(1)
                self.logger.info('graceful leave on %s', node)
                res = client.graceful_leave(node.ip, 5555)
                self.logger.info('graceful leave: %s', res)
                self.controller.delete_nodes([node])
            self.state = self.S_RUNNING
            return HttpJsonResponse()
