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
        self.context = {'FIRST': 'true', 'MGMT_SERVER': '', 'KNOWN_HOSTS': ''}
        # Setup the clouds' controller
        self.controller.generate_context('scalaris')
        self.cloud_groups = CloudGroups(self.controller.get_clouds(), self.controller.get_default_cloud().get_cloud_name())
        self.logger.info('Cloud-Groups: %s', self.cloud_groups.groups)

    def _do_startup(self, cloud):
        """Starts up the service. At least one node should be running scalaris when the service is started."""

        startCloud = self._init_cloud(cloud)
        try:
            # create node
            self.controller.add_context_replacement(self.context, startCloud)
            reg_key = self.cloud_groups.register_node(cloud)
            self.logger.info('Creating node in cloud: %s (cloud group %s)', cloud, self.cloud_groups.number(cloud))
            [instance] = self.controller.create_nodes(1, client.check_agent_process, 5555, startCloud)

            # startup agent
            first_in_group = self.cloud_groups.complete_registration(instance, reg_key, cloud)
            cloud_number = self.cloud_groups.number(cloud)
            client.startup(instance.ip, 5555, instance.ip, cloud_number, self.cloud_groups.no_of_groups, first_in_group)

            self.logger.info('Started node %s in cloud %s (cloud group: %s)', instance.id, cloud, cloud_number)
            self.logger.info('%s was first node in cloud group: %s', instance.id, first_in_group)
            self.context['FIRST'] = 'false'
            self.context['MGMT_SERVER'] = self._render_node(instance, 'mgmt_server')
            self.logger.info('Finished first node')
            self.controller.add_context_replacement(self.context, startCloud)
        except:
            self.logger.exception('do_startup: Failed to request a new node')
            self.state = self.S_STOPPED
            return
        self.state = self.S_RUNNING

    def _do_stop(self):
        self.controller.delete_nodes(self.cloud_groups.nodes)
        # TODO: solve race condition wih get_service_info?
        self.cloud_groups = CloudGroups(self.controller.get_clouds(), self.controller.get_default_cloud().get_cloud_name())
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
        if kwargs['cloud'] not in self.cloud_groups.clouds:
            return HttpErrorResponse("A cloud named '%s' could not be found" % kwargs['cloud'])
        self.state = self.S_ADAPTING
        Thread(target=self._do_add_nodes, args=[count, kwargs['cloud'], kwargs.get('auto_placement', False)]).start()
        return HttpJsonResponse()

    def _do_add_nodes(self, count, cloud, auto_placement):

        self.context['KNOWN_HOSTS'] = self._render_known_hosts()
        try:
            queue = Queue(maxsize=count)
            for i in range(count):
                if auto_placement:
                    (cloud, reg_id) = self.cloud_groups.next()
                    Thread(target=self._do_create_node, args=[cloud, queue, reg_id]).start()
                else:
                    reg_id = self.cloud_groups.register_node(cloud)
                    Thread(target=self._do_create_node, args=[cloud, queue, reg_id]).start()

            node_instances = []
            for i in range(queue.maxsize):
                node_instances.append(queue.get(True))

            # Startup agents
            for ([service_node], reg_id, cloud) in node_instances:
                self.logger.info('node: %s, reg_key: %s, cloud: %s', service_node, reg_id, cloud)
                cloud_group = self.cloud_groups.number(cloud)
                first_in_group = self.cloud_groups.complete_registration(service_node, reg_id, cloud)
                client.startup(service_node.ip, 5555, service_node.ip, cloud_group, self.cloud_groups.no_of_groups, first_in_group)
                self.logger.info('Started node %s on cloud %s (cloud group: %s)', service_node.id, cloud, cloud_group)
                self.logger.info('%s was first node in cloud group: %s', service_node.id, first_in_group)

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

    def _do_create_node(self, cloud, queue, reg_id):
        self.logger.info('Creating node in cloud: %s (cloud group %s)', cloud, self.cloud_groups.number(cloud))
        startCloud = self._init_cloud(cloud)
        self.controller.add_context_replacement(self.context, startCloud)
        node_instances = self.controller.create_nodes(1, client.check_agent_process, 5555, startCloud)
        queue.put((node_instances, reg_id, cloud), True)

    def _render_node(self, node, role):
        ip = node.ip.replace('.', ',')
        return '{{' + ip + '},14195,' + role + '}'

    def _render_known_hosts(self):
        rendered_nodes = [self._render_node(node, 'service_per_vm') for node in self.cloud_groups.nodes]
        return '[' + ', '.join(rendered_nodes) + ']'

    @expose('GET')
    def list_nodes(self, kwargs):
        self.logger.info('called list_nodes')
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to list_nodes')
        return HttpJsonResponse({
            'scalaris': [node.id for node in self.cloud_groups.nodes],
        })

    @expose('GET')
    def get_service_info(self, kwargs):
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        result = {'state': self.state, 'type': 'scalaris'}
        nodes = self.cloud_groups.nodes
        if len(nodes) > 0:
            result['mgmt_location'] = 'http://' + nodes[0].ip + ':8000'
            try:
                result['service_info'] = client.get_service_info(nodes[0].ip, 5555)
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
        for node in self.cloud_groups.nodes:
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
        nodes = self.cloud_groups.nodes
        if count > len(nodes) - 1:
            self.state = self.S_RUNNING
            self.logger.info('Cannot delete so many workers')
            return HttpErrorResponse('ERROR: Cannot delete so many workers')
        else:
            for i in range(0, count):
                node = self.cloud_groups.remove_node()
                self.logger.info('graceful leave on %s', node)
                res = client.graceful_leave(node.ip, 5555)
                self.logger.info('graceful leave: %s', res)
                self.controller.delete_nodes([node])
            self.state = self.S_RUNNING
            return HttpJsonResponse()





