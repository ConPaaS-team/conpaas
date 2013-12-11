# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread, Lock, Event, Timer
import os
import tempfile
import string
from random import choice
import collections

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse, \
                                      FileUploadField
from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager, ManagerException

from conpaas.services.galera.agent import client
from conpaas.services.galera.manager.config import Configuration, E_ARGS_INVALID, \
                              E_ARGS_MISSING, E_STATE_ERROR, E_ARGS_UNEXPECTED


class GaleraManager(BaseManager):
    """
    Initializes :py:attr:`config` using Config and sets :py:attr:`state` to :py:attr:`S_INIT`

    :param conf: Configuration file.
    :type conf: str
    :type conf: boolean

    """

    def __init__(self, conf, **kwargs):
        BaseManager.__init__(self, conf)

        self.logger.debug("Entering GaleraServerManager initialization")
        self.controller.generate_context('galera')
        self.controller.config_clouds({ "mem" : "512", "cpu" : "1" })
        self.state = self.S_INIT
        self.config = Configuration(conf)
        self.logger.debug("Leaving GaleraServer initialization")
        # The unique id that is used to start the master/slave
        self.id = 0

    # TODO: move to BaseManager
    def _check_state(self, expected_states):
        if self.state not in expected_states:
            raise Exception("ERROR: wrong state, was expecting one of %s"\
                            " but current state is %s" \
                            % (expected_states, self.state))

    # TODO: move to BaseManager
    def _check_arguments(self, kwargs, expected_args):
        for param, ptype in expected_args:
            if param not in kwargs:
                raise Exception("ERROR: missing required parameter %s" % param)
            arg_value = kwargs[param]
        # TODO: finish this generic argument checker, including ptype checks

    @expose('POST')
    def startup(self, kwargs):
        """ Starts the service - it will start and configure a Galera master """
        self.logger.debug("Entering GaleraServerManager startup")

        if self.state != self.S_INIT and self.state != self.S_STOPPED:
            return HttpErrorResponse(ManagerException(E_STATE_ERROR).message)

        self.state = self.S_PROLOGUE
        Thread(target=self._do_startup, kwargs=kwargs).start()
        return HttpJsonResponse({'state': self.S_PROLOGUE})

    def _do_startup(self, cloud):
        """ Starts up the galera service. """

        start_cloud = self._init_cloud(cloud)
        #TODO: Get any existing configuration (if the service was stopped and restarted)
        self.logger.debug('do_startup: Going to request one new node')

        # Generate a password for root
        # TODO: send a username?
        self.root_pass = ''.join([choice(string.letters + string.digits) for i in range(10)])
        self.controller.add_context_replacement(dict(mysql_username='mysqldb',
                                                     mysql_password=self.root_pass),
                                                cloud=start_cloud)
        try:
            node_instances = self.controller.create_nodes(1,
                                                          client.check_agent_process,
                                                          self.config.AGENT_PORT,
                                                          start_cloud)
            self._start_master(node_instances)
            self.config.addMySQLServiceNodes(nodes=node_instances,
                                             isMaster=True)
        except Exception, ex:
            # rollback
            self.controller.delete_nodes(node_instances)
            self.logger.exception('do_startup: Failed to request a new node on cloud %s: %s.' % (cloud, ex))
            self.state = self.S_STOPPED
            return
        self.state = self.S_RUNNING

    def _start_master(self, nodes):
        for serviceNode in nodes:
            try:
                client.create_master(serviceNode.ip,
                                     self.config.AGENT_PORT,
                                     self._get_server_id())
            except client.AgentException, ex:
                self.logger.exception('Failed to start Galera node %s: %s' % (str(serviceNode), ex))
                self.state = self.S_ERROR
                raise

    def _start_slave(self, nodes, master):
        slaves = {}
        for serviceNode in nodes:
            slaves[str(self._get_server_id())] = {'ip': serviceNode.ip,
                                                  'port': self.config.AGENT_PORT}
        try:
            self.logger.debug('create_slave for master.ip  = %s' % master)
            client.create_slave(master.ip, self.config.AGENT_PORT, slaves)
        except client.AgentException:
            self.logger.exception('Failed to start Galera Slave at node %s' % str(serviceNode))
            self.state = self.S_ERROR
            raise
            
    def _start_glb_node(self, nodes, master):
        slaves = {}
        for serviceNode in nodes:
            slaves[str(self._get_server_id())] = {'ip': serviceNode.ip,
                                                  'port': self.config.AGENT_PORT}
        try:
            galera_nodes = [{"host": node.ip, "port": self.config.AGENT_PORT} for node in self.getMySQLServiceNodes()]
            self.logger.debug('create_glb_node all galera nodes = %s' % str(galera_nodes))
            self.logger.debug('create_glb_node for master.ip  = %s' % master)
            client.create_glb_node(master.ip, self.config.AGENT_PORT, slaves, galera_nodes)
        except client.AgentException:
            self.logger.exception('Failed to start Galera GLB Node at node %s' % str(serviceNode))
            self.state = self.S_ERROR
            raise

    @expose('GET')
    def list_nodes(self, kwargs):
        """
        HTTP GET method.
        Uses :py:meth:`IaaSClient.listVMs()` to get list of
        all Service nodes. For each service node it gets it
        checks if it is in servers list. If some of them are missing
        they are removed from the list. Returns list of all service nodes.

        :returns: HttpJsonResponse - JSON response with the list of services
        :raises: HttpErrorResponse

        """
        if len(kwargs) != 0:
            return HttpErrorResponse(ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message)

        return HttpJsonResponse({
            'masters': [ node.id for node in self.config.getMySQLmasters() ],
            'glb_nodes': [ node.id for node in self.config.get_glb_nodes() ],
            'slaves': [ node.id for node in self.config.getMySQLslaves() ]
            })

    @expose('GET')
    def get_node_info(self, kwargs):
        """
        HTTP GET method. Gets info of a specific node.

        :param param: serviceNodeId is a VMID of an existing service node.
        :type param: str
        :returns: HttpJsonResponse - JSON response with details about the node.
        :raises: ManagerException

        """
        if 'serviceNodeId' not in kwargs:
            return HttpErrorResponse(ManagerException(E_ARGS_MISSING, 'serviceNodeId').message)
        serviceNodeId = kwargs.pop('serviceNodeId')
        if len(kwargs) != 0:
            return HttpErrorResponse(ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
        if serviceNodeId not in self.config.serviceNodes:
            return HttpErrorResponse('Unknown "serviceNodeId" %s, should be one of %s.'\
                                     % (serviceNodeId, self.config.serviceNodes.keys()))
        serviceNode = self.config.getMySQLNode(serviceNodeId)
        return HttpJsonResponse({
            'serviceNode': {
                            'id': serviceNode.id,
                            'ip': serviceNode.ip,
                            'isMaster': serviceNode.isMaster,
                            'isSlave': serviceNode.isSlave,
                            'cloud_name': serviceNode.cloud_name,
                            }
            })

    @expose('POST')
    def add_nodes(self, kwargs):
        """
        HTTP POST method. Creates new node and adds it to the list of existing nodes in the manager. Makes internal call to :py:meth:`createServiceNodeThread`.

        :param kwargs: number of nodes to add.
        :type param: str
        :returns: HttpJsonResponse - JSON response with details about the node.
        :raises: ManagerException

        """

        if self.state != self.S_RUNNING:
            return HttpErrorResponse('ERROR: Wrong state to add_nodes')
        if (not 'slaves' in kwargs) and (not 'glb_nodes' in kwargs):
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if (not isinstance(kwargs['slaves'], int)) and (not isinstance(kwargs['glb_nodes'], int)):
            return HttpErrorResponse('ERROR: Expected an integer value for "count"')
        self.state = self.S_ADAPTING

        # TODO: check if argument "cloud" is an known cloud
        if 'slaves' in kwargs:
            count = int(kwargs.pop('slaves'))
            Thread(target=self._do_add_nodes, args=['slaves', count, kwargs['cloud']]).start()
        if 'glb_nodes' in kwargs:
            count = int(kwargs.pop('glb_nodes'))
            Thread(target=self._do_add_nodes, args=['glb_nodes', count, kwargs['cloud']]).start()
        return HttpJsonResponse()

    # TODO: also specify the master for which to add slaves
    def _do_add_nodes(self, node_type, count, cloud):
        # Get the master
        masters = self.config.getMySQLmasters()
        start_cloud = self._init_cloud(cloud)
        # Configure the nodes as slaves
        try:
            self.controller.add_context_replacement(
                                        dict(mysql_username='mysqldb',
                                             mysql_password=self.root_pass),
                                        cloud=start_cloud)
            node_instances = self.controller.create_nodes(count,
                                           client.check_agent_process,
                                           self.config.AGENT_PORT, start_cloud)
            for master in masters:
                if node_type == 'slaves':
                    self._start_slave(node_instances, master)
                    self.config.addMySQLServiceNodes(nodes=node_instances, isSlave=True)
                elif node_type == 'glb_nodes':
                    self._start_glb_node(node_instances, master)
                    self.config.addGLBServiceNodes(nodes=node_instances)
        except Exception, ex:
            # rollback
            self.controller.delete_nodes(node_instances)
            self.logger.exception('_do_add_nodes: Could not start slave: %s' % ex)
            self.state = self.S_ERROR
            return
        self.state = self.S_RUNNING

    def _get_server_id(self):
        self.id = self.id + 1
        return self.id

    @expose('GET')
    def get_service_performance(self, kwargs):
        """HTTP GET method. Placeholder for obtaining performance metrics.

        :param kwargs: Additional parameters.
        :type kwargs: dict
        :returns:  HttpJsonResponse -- returns metrics

        """

        if len(kwargs) != 0:
            return HttpErrorResponse(ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
        return HttpJsonResponse({
                'request_rate': 0,
                'error_rate': 0,
                'throughput': 0,
                'response_time': 0,
        })

    @expose('POST')
    def remove_nodes(self, kwargs):
        if self.state != self.S_RUNNING:
            self.logger.debug('Wrong state to remove nodes')
            return HttpErrorResponse('ERROR: Wrong state to remove_nodes')
        if not 'slaves' in kwargs:
            return HttpErrorResponse('ERROR: Required argument doesn\'t exist')
        if not isinstance(kwargs['slaves'], int):
            return HttpErrorResponse('ERROR: Expected an integer value for "count"')
        count = int(kwargs.pop('slaves'))
        if count > len(self.config.getMySQLslaves()):
            return HttpErrorResponse('ERROR: Cannot remove so many nodes')
        self.state = self.S_ADAPTING
        Thread(target=self._do_remove_nodes, args=[count]).start()
        return HttpJsonResponse()

    def _do_remove_nodes(self, count):
        nodes = self.config.getMySQLslaves()[:count]
        self.controller.delete_nodes(nodes)
        self.config.remove_nodes(nodes)
        self.state = self.S_RUNNING
        return HttpJsonResponse()

    @expose('POST')
    def migrate_nodes(self, kwargs):
        """
        Migrate nodes from one cloud to another.

        Parameters:
         *  'nodes' is a comma-separated list of colon-separated triplets
                    origin_cloud:vmid:destination_cloud. For example:
                    "default:1:mycloud,default:3:mycloud,mycloud:i-728af315:default"
                    will migrate three nodes: nodes 1 and 3 of cloud 'default'
                    to cloud 'mycloud' and node i-728af315 of mycloud to cloud
                    'default'.

         * 'delay' (optional with default value to 0) time in seconds to delay
                    the removal of the old node. 0 means "remove old node as
                    soon as the new node is up", 60 means "remove old node
                    after 60 seconds after the new node is up". Useful to keep
                    the old node active while the DNS and its caches that
                    still have the IP address of the old node are updated
                    to the IP address of the new node.
        """
        try:
            self._check_state([self.S_RUNNING])
        except Exception, ex:
            return HttpErrorResponse('%s' % ex)

        if not 'nodes' in kwargs:
            return HttpErrorResponse('ERROR: Missing required "nodes" argument.')
        migrate_nodes_str = kwargs.pop('nodes').split(',')
        service_nodes = self.config.getMySQLServiceNodes()
        self.logger.debug("While migrate_nodes, service_nodes = %s." % service_nodes)
        migration_plan = []
        for migrate_node in migrate_nodes_str:
            try:
                from_cloud_name, node_id, dest_cloud_name = migrate_node.split(':')
                # TODO: check that cloud name cannot contain a column ':'
                if from_cloud_name == '' or dest_cloud_name == '':
                    raise Exception('Missing cloud name in parameter "nodes".' \
                                    % migrate_nodes_str)
            except Exception, ex:
                return HttpErrorResponse('ERROR: argument "nodes" does not' \
                    ' respect the expected format, a comma-separated list of'\
                    ' "from_cloud:node_id:dest_cloud": %s\n%s' % (migrate_nodes_str, ex))
            try:
                candidate_nodes = [node for node in service_nodes
                                   if node.cloud_name == from_cloud_name
                                       and node.id == node_id]
                if candidate_nodes == []:
                    avail_nodes = ', '.join([node.cloud_name + ':' + node.id
                                             for node in service_nodes])
                    raise Exception("Node %s in cloud %s is not a valid node" \
                                    " of this service. It should be one of %s" \
                                    % (node_id, from_cloud_name, avail_nodes))
#                node = self.controller.get_node(node_id, from_cloud_name)
#                if node not in service_nodes:
#                    raise Exception("Node %s from cloud %s is not a MySQL service node." \
#                                    % (node.id, node.cloud_name))
                node = candidate_nodes[0]
                dest_cloud = self.controller.get_cloud_by_name(dest_cloud_name)
            except Exception, ex:
                return HttpErrorResponse('ERROR: %s' % (ex))
            migration_plan.append((node, dest_cloud))

        if migration_plan == []:
            return HttpErrorResponse('ERROR: argument is missing the nodes to migrate.')

        # optional 'delay' argument: time in seconds to delay the removing of old nodes
        if 'delay' not in kwargs:
            delay = 0
        else:
            delay = kwargs.pop('delay')
            try:
                delay = int(delay)
            except ValueError, ex:
                return HttpErrorResponse('ERROR: argument "delay" must be an integer,' \
                                         'it cannot be %s.' % delay)
            if delay < 0:
                return HttpErrorResponse('ERROR: argument "delay" must be a positive or null integer,' \
                                         'it cannot be %s.' % delay)

        if len(kwargs) > 0:
            return HttpErrorResponse('ERROR: Unknown arguments %s' % kwargs)

        self.state = self.S_ADAPTING
        Thread(target=self._do_migrate_nodes, args=[migration_plan, delay]).start()
        return HttpJsonResponse()

    def _do_migrate_nodes(self, migration_plan, delay):
        self.logger.info("Migration: starting with plan %s and delay %s." \
                          % (migration_plan, delay))
        # TODO: use instead collections.Counter with Python 2.7
        clouds = [dest_cloud for (_node, dest_cloud) in migration_plan]
        new_vm_nb = collections.defaultdict(int)
        for cloud in clouds:
            new_vm_nb[cloud] += 1
        try:
            new_nodes = []
            # TODO: make it parallel
            masters = self.config.getMySQLmasters()
            for cloud, count in new_vm_nb.iteritems():
                self.controller.add_context_replacement(
                                        dict(mysql_username='mysqldb',
                                             mysql_password=self.root_pass),
                                        cloud=cloud)

                new_nodes.extend(
                    self.controller.create_nodes(count,
                                                 client.check_agent_process,
                                                 self.config.AGENT_PORT,
                                                 cloud))
                # TODO: no masters anymore in Galera
                for master in masters:
                    self._start_slave(new_nodes, master)
                self.config.addMySQLServiceNodes(nodes=new_nodes, isSlave=True)
        except Exception, ex:
            # error happened: rolling back...
            self.controller.delete_nodes(new_nodes)
            self.config.remove_nodes(new_nodes)
            self.logger.exception('_do_migrate_nodes: Could not' \
                                  ' start nodes: %s' % ex)
            self.state = self.S_RUNNING
            raise ex

        self.logger.debug("Migration: new nodes %s created and" \
                          " configured successfully." % (new_nodes))

        # TODO: wait for SYNCED state
        #    mysql -h 10.144.0.2 -u mysqldb -pwQe6KxqJvk -B -N -e 'SHOW global STATUS LIKE "wsrep_local_state_comment";'
        #  ==> better in services.galera.agent.role.MySQLServer.start()

        # New nodes successfully created
        # Now scheduling the removing of old nodes
        old_nodes = [node for node, _dest_cloud in migration_plan]
        if delay == 0:
            self.logger.debug("Migration: removing immediately" \
                              " the old nodes: %s." % old_nodes)
            self._do_migrate_finalize(old_nodes)
        else:
            self.logger.debug("Migration: setting a timer to remove" \
                              " the old nodes %s after %d seconds." \
                              % (old_nodes, delay))
            self._start_timer(delay, self._do_migrate_finalize, old_nodes)

    def _do_migrate_finalize(self, old_nodes):
        self.controller.delete_nodes(old_nodes)
        self.config.remove_nodes(old_nodes)
        self.state = self.S_RUNNING
        self.logger.info("Migration: old nodes %s have been removed." \
                         " END of migration." % old_nodes)

    def _start_timer(self, delay, callback, nodes):
        timer = Timer(delay, callback, args=[nodes])
        timer.start()

    @expose('GET')
    def get_service_info(self, kwargs):
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        return HttpJsonResponse({'state': self.state, 'type': 'galera'})

    @expose('POST')
    def shutdown(self, kwargs):
        """
        HTTP POST method. Shuts down the manager service.

        :returns: HttpJsonResponse - JSON response with details about the status of a manager node: . ManagerException if something went wrong.
        :raises: ManagerException

        """
        if len(kwargs) != 0:
            return HttpErrorResponse(ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message)

        if self.state != self.S_RUNNING:
            return HttpErrorResponse(ManagerException(E_STATE_ERROR).message)

        self.state = self.S_EPILOGUE
        Thread(target=self._do_shutdown, args=[]).start()
        return HttpJsonResponse({'state': self.S_EPILOGUE})


    def _do_shutdown(self):
        ''' Shuts down the service. '''
        #self._stop_slaves( config.getProxyServiceNodes())
        #self._stop_masters(config, config.getWebServiceNodes())
        self.controller.delete_nodes(self.config.serviceNodes.values())
        self.config.serviceNodes = {}
        self.state = self.S_STOPPED


    @expose('POST')
    def set_password(self, kwargs):
        self.logger.debug('Setting password')
        if self.state != self.S_RUNNING:
            self.logger.debug('Service not runnning')
            return HttpErrorResponse('ERROR: Service not running')
        if not 'user' in kwargs:
            return HttpErrorResponse('ERROR: Required argument \'user\' doesn\'t exist')
        if not 'password' in kwargs:
            return HttpErrorResponse('ERROR: Required argument \'password\' doesn\'t exist')

        # Get the master
        masters = self.config.getMySQLmasters()

        #TODO: modify this when multiple masters
        try:
            for master in masters:
                client.set_password(master.ip, self.config.AGENT_PORT, kwargs['user'], kwargs['password'])
        except:
            self.logger.exception('set_password: Could not set password')
            self.state = self.S_ERROR
            return HttpErrorResponse('Failed to set password')
        else:
            return HttpJsonResponse()

    @expose('UPLOAD')
    def load_dump(self, kwargs):
        self.logger.debug('Uploading mysql dump')
        if 'mysqldump_file' not in kwargs:
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING, \
                                                                     'mysqldump_file').message)
        mysqldump_file = kwargs.pop('mysqldump_file')
        if len(kwargs) != 0:
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, \
                                               detail='invalid number of arguments ').message)
        if not isinstance(mysqldump_file, FileUploadField):
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, \
                                               detail='mysqldump_file should be a file').message)
        fd, filename = tempfile.mkstemp(dir='/tmp')
        fd = os.fdopen(fd, 'w')
        upload = mysqldump_file.file
        bytes = upload.read(2048)
        while len(bytes) != 0:
            fd.write(bytes)
            bytes = upload.read(2048)
        fd.close()

        # Get master
        # TODO: modify this when multiple masters
        masters = self.config.getMySQLmasters()
        try:
            for master in masters:
                client.load_dump(master.ip, self.config.AGENT_PORT, filename)
        except:
            self.logger.exception('load_dump: could not upload mysqldump_file ')
            self.state = self.S_ERROR
            return
        return HttpJsonResponse()
