# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread

from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse, \
                                      HttpError
from conpaas.services.mapreduce.agent import client

class MapReduceManager(BaseManager):

    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser
                                # (hopefully the new service won't need anything extra)
        BaseManager.__init__(self, config_parser)

        self.nodes = []
        # Setup the clouds' controller
        self.controller.generate_context('mapreduce')
        self.controller.config_clouds({ "mem" : "1024", "cpu" : "1" })

    def _do_startup(self, cloud):
        ''' Starts up the service. The first node will be the job 
            main as well as an hadoop worker.
        '''
        startCloud = self._init_cloud(cloud)
        try:
          self.context = {'FIRST': 'true',
                          'MGMT_SERVER': ''}
          self.controller.add_context_replacement(self.context, cloud = startCloud)
          instance = self.controller.create_nodes(1,
            client.check_agent_process, 5555, startCloud)
          self.nodes += instance

          self.logger.info('Created node: %s', instance[0])
          client.startup(instance[0].ip, 5555,
                         instance[0].ip,
                         instance[0].private_ip)
          self.logger.info('Called startup: %s', instance[0])
          self.context = {'FIRST': 'false',
                          'MGMT_SERVER': instance[0].ip}
          self.controller.add_context_replacement(self.context, cloud = startCloud)
        except:
          self.logger.exception('do_startup: Failed to request a new node')
          self.state = self.S_STOPPED
          return
        self.state = self.S_RUNNING


    def _do_stop(self):
      self.controller.delete_nodes(self.nodes)
      self.nodes = []
      self.state = self.S_STOPPED
      return HttpJsonResponse()

    @expose('POST')
    def add_nodes(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to add_nodes')
        if not 'workers' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['workers'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "count"')
        count = int(kwargs.pop('workers'))
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
            node_instances = self.controller.create_nodes(count, \
                                client.check_agent_process, 5555, startCloud)
            self.logger.info('Create nodes: %s', node_instances)
            self.nodes += node_instances
            # Startup agents
            for node in node_instances:
                client.startup(node.ip, 5555, node.ip, node.private_ip)
            self.logger.info('Started nodes: %d %s', count, self.state)
            return HttpJsonResponse()
        except HttpError as e:
            self.logger.info('exception in _do_add_nodes2: %s', e)
            return HttpJsonResponse()
        except Exception as e:
            self.logger.info('exception in _do_add_nodes1: %s', e)
            return HttpJsonResponse()
        finally:
            #TODO error handling (propagte error to client, i.e. browser)
            self.state = self.S_RUNNING
            self.logger.info('finished _do_add_nodes')
            return HttpJsonResponse()

    @expose('GET')
    def list_nodes(self, kwargs):
        self.logger.info('called list_nodes')
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to list_nodes')
        return HttpJsonResponse({
          'mains' : [self.nodes[0].id],
          'workers': [ node.id for node in self.nodes[1:] ]
              })

    @expose('GET')
    def get_service_info(self, kwargs):
        self.logger.info('called get_service_info: %s', self.state)
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        return HttpJsonResponse({'state': self.state, 'type': 'mapreduce'})

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
        if not 'workers' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['workers'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "count"')
        count = int(kwargs.pop('workers'))
        self.state = self.S_ADAPTING
        Thread(target=self._do_remove_nodes, args=[count]).start()
        return HttpJsonResponse()

    def _do_remove_nodes(self, count):
        if count > len(self.nodes) - 1:
            self.state = self.S_RUNNING
            return HttpErrorResponse('ERROR: Cannot delete so many workers')
        for i in range(0, count):
            self.controller.delete_nodes([self.nodes.pop(1)])
        self.state = self.S_RUNNING
        return HttpJsonResponse()
