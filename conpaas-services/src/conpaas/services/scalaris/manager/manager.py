# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread
from Queue import Queue
from cloudgroups import CloudGroups

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
        self.cloud_groups = CloudGroups(self.controller.get_clouds())
        self.logger.info('Cloud-Groups: %s', self.cloud_groups.get_groups())


    def _do_startup(self, cloud):
        ''' Starts up the service. At least one node should be running scalaris
            when the service is started.
        '''
        startCloud = self._init_cloud(cloud)
        try:
            self.controller.add_context_replacement(self.context, startCloud)
            instance = self.controller.create_nodes(1, client.check_agent_process, 5555, startCloud)
            self.nodes += instance
            self.logger.info('Created node: %s', instance[0])
            cloud_number = self.cloud_groups.number(cloud)
            self.cloud_groups.added_node(cloud)
            client.startup(instance[0].ip, 5555, instance[0].ip, cloud_number, self.cloud_groups.no_of_groups,
                           self.cloud_groups.first_in_group(cloud))
            self.logger.info('Started node %s in cloud %s (cloud group: %s)', instance[0].id, cloud, cloud_number)
            self.context['FIRST'] = 'false'
            self.context['MGMT_SERVER'] = self._render_node(instance[0], 'mgmt_server')
            self.logger.info('Finished first node')
            self.controller.add_context_replacement(self.context, startCloud)
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
        # TODO: solve race condition wih get_service_info?
        self.nodes = []
        self.state = self.S_STOPPED
        self.context['FIRST'] = 'true'
        self.context['MGMT_SERVER'] = ''
        self.context['KNOWN_HOSTS'] = ''
        return HttpJsonResponse()

    @expose('POST')
    def add_nodes(self, kwargs):
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to add_nodes')
        if not 'scalaris' in kwargs:
            return HttpErrorResponse('ERROR: Required argument "scalaris" doesn\'t exist')
        if not isinstance(kwargs['scalaris'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "scalaris"')
        count = int(kwargs.pop('scalaris'))
        # create at least one node
        if count < 1:
            return HttpErrorResponse('ERROR: Expected a positive integer value for "count"')
        if kwargs['cloud'] not in self.cloud_groups.get_clouds():
            return HttpErrorResponse("A cloud named '%s' could not be found" % kwargs['cloud'])
        self.state = self.S_ADAPTING
        Thread(target=self._do_add_nodes, args=[count, kwargs['cloud'], kwargs.get('auto_placement', False)]).start()
        return HttpJsonResponse()

    def _do_add_nodes(self, count, cloud, auto_placement):

        self.context['KNOWN_HOSTS'] = self._render_known_hosts()
        try:
            if auto_placement:
                queue = Queue(maxsize=count)
                for i in range(count):
                    cloud = self.cloud_groups.next()
                    Thread(target=self._do_create_node, args=[cloud, queue]).start()
                count = 1
            else:
                queue = Queue(maxsize=1)
                self.cloud_groups.added_node(cloud, count)
                self._do_create_node(cloud, queue, count)

            # wait for the completion of the node creation
            node_instances = []
            for i in range(queue.maxsize):
                node_instances.append(queue.get(True))

            # Startup agents
            for (nodes, cloud) in node_instances:
                for node in nodes:
                    cloud_group = self.cloud_groups.number(cloud)
                    first_in_group = self.cloud_groups.first_in_group(cloud)
                    self.nodes.append(node)
                    client.startup(node.ip, 5555, node.ip, cloud_group, self.cloud_groups.no_of_groups, first_in_group)
                    self.logger.info('Started node %s on cloud %s (cloud group: %s)', node.id, cloud, cloud_group)
                    self.logger.info('%s was first node in cloud group: %s', node.id, first_in_group)
            self.state = self.S_RUNNING


        except HttpError as e:
            self.logger.info('exception in _do_add_nodes2: %s', e)
            return HttpJsonResponse()
        except Exception as e:
            self.logger.info('exception in _do_add_nodes1: %s', e)
            return HttpJsonResponse()
        finally:
            self.logger.info('finished _do_add_nodes')
            return HttpJsonResponse()

    def _do_create_node(self, cloud, queue, count=1):
        self.logger.info('Starting %d nodes in cloud: %s (cloud group %s)',
                         count, cloud, self.cloud_groups.number(cloud))
        startCloud = self._init_cloud(cloud)
        self.controller.add_context_replacement(self.context, startCloud)
        node_instances = self.controller.create_nodes(count, client.check_agent_process, 5555, startCloud)
        queue.put((node_instances, cloud), True)

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
            'scalaris': [node.id for node in self.nodes],
        })

    @expose('GET')
    def get_service_info(self, kwargs):
        # self.logger.info('called get_service_info: %s', self.state)
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
            return HttpErrorResponse('ERROR: too many arguments')
        serviceNode = None
        for node in self.nodes:
            if serviceNodeId == node.id:
                serviceNode = node
                break

        if serviceNode is None:
            return HttpErrorResponse('ERROR: node does not exist')
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
            return HttpErrorResponse('ERROR: Required argument "scalaris" doesn\'t exist')
        if not isinstance(kwargs['scalaris'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "scalaris"')
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





