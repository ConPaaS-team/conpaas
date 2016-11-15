from threading import Thread
from shutil import rmtree
import pickle
import zipfile
import tarfile
import tempfile
import stat
import os.path
import time

from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager, ManagerException

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse,\
    HttpFileDownloadResponse, FileUploadField

from conpaas.services.flink.agent import client

from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file

class FlinkManager(BaseManager):

    # Flink node types
    ROLE_MASTER  = 'master'  # master node (running a JobManager)
    ROLE_WORKER  = 'worker'  # worker node (running a TaskManager)

    # Packed node types
    ROLE_MASTER_WORKER = 'master_worker'    # JobManager + TaskManager

    def __init__(self, config_parser, **kwargs):
        """Initialize a Flink Manager.

        'config_parser' represents the manager config file.
        **kwargs holds anything that can't be sent in config_parser."""
        BaseManager.__init__(self, config_parser)

        self.master = None

    def get_service_type(self):
        return 'flink'

    def get_node_roles(self):
        return [ self.ROLE_MASTER, self.ROLE_WORKER ]

    def get_default_role(self):
        return self.ROLE_WORKER

    def get_starting_nodes(self):
        return { self.ROLE_MASTER_WORKER: 1 }

    def get_role_logs(self, role, add_default=True):
        if add_default:
            logs = BaseManager.get_role_logs(self, role)
        else:
            logs = []

        if role == self.ROLE_MASTER:
            logs.extend([{'filename': 'flink-jobmanager.log',
                          'description': 'JobManager log',
                          'path': '/var/cache/cpsagent/flink-jobmanager.log'},
                         {'filename': 'flink-jobmanager.out',
                          'description': 'JobManager out',
                          'path': '/var/cache/cpsagent/flink-jobmanager.out'}]);
        elif role == self.ROLE_WORKER:
            logs.extend([{'filename': 'flink-taskmanager.log',
                          'description': 'TaskManager log',
                          'path': '/var/cache/cpsagent/flink-taskmanager.log'},
                         {'filename': 'flink-taskmanager.out',
                          'description': 'TaskManager out',
                          'path': '/var/cache/cpsagent/flink-taskmanager.out'}]);
        elif role == self.ROLE_MASTER_WORKER:
            logs.extend(self.get_role_logs(self.ROLE_MASTER, False))
            logs.extend(self.get_role_logs(self.ROLE_WORKER, False))

        return logs

    def on_start(self, nodes):
        """Start up the service. The first node will be the master node."""

        nr_instances = 1
        vals = { 'action': '_do_startup', 'count': nr_instances }
        self.logger.debug(self.ACTION_REQUESTING_NODES % vals)

        try:
            self.master = nodes[0]
            self.logger.debug("Master's private IP address: %s" % self.master.private_ip)
            self._init_agents(nodes, self.master.private_ip)
            self._start_master(self.master)
            return True
        except Exception, err:
            self.logger.exception('_do_startup: Failed to create agents: %s' % err)
            return False

    def _init_agents(self, nodes, master_ip):
        self.logger.info("Initializing agents %s" %
                [ node.id for node in nodes ])

        for serviceNode in nodes:
            try:
                client.init_agent(serviceNode.ip, self.AGENT_PORT, master_ip)
            except client.AgentException:
                self.logger.exception('Failed to initialize agent at node %s'
                        % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to initialize agent at node %s'
                        % str(serviceNode))
                raise

    def _start_master(self, master):
        self.logger.info("Starting JobManager and TaskManager on agent %s" % master.id)

        try:
            client.start_master(master.ip, self.AGENT_PORT)
        except client.AgentException:
            self.logger.exception('Failed to start JobManager or TaskManager at node %s'
                    % str(serviceNode))
            self.state_set(self.S_ERROR, msg='Failed to start JobManager or TaskManager at node %s'
                    % str(serviceNode))
            raise

    def _start_workers(self, nodes):
        self.logger.info("Starting TaskManager on agents %s" %
                [ node.id for node in nodes ])

        for serviceNode in nodes:
            try:
                client.start_worker(serviceNode.ip, self.AGENT_PORT)
            except client.AgentException:
                self.logger.exception('Failed to start TaskManager at node %s'
                        % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to start TaskManager at node %s'
                        % str(serviceNode))
                raise

    def _stop_workers(self, nodes):
        self.logger.info("Stopping TaskManager on agents %s" %
                [ node.id for node in nodes ])

        for serviceNode in nodes:
            try:
                client.stop_worker(serviceNode.ip, self.AGENT_PORT)
            except client.AgentException:
                self.logger.warning('Failed to stop TaskManager at node %s'
                        % str(serviceNode))

    def on_stop(self):
        """Delete all nodes and switch to status STOPPED"""

        self.logger.info("Removing nodes %s" %
                [ node.id for node in self.nodes ])
        del_nodes = self.nodes[:]
        self.master = None
        return del_nodes

    def on_add_nodes(self, node_instances):
        nodes_before = filter(lambda n: n not in node_instances, self.nodes)

        self._init_agents(node_instances, self.master.private_ip)
        self._start_workers(node_instances)

        return True

    def check_remove_nodes(self, node_roles):
        BaseManager.check_remove_nodes(self, node_roles)

        if node_roles.get(self.ROLE_MASTER, 0) > 0:
            raise Exception("Cannot remove the master node.")

    def on_remove_nodes(self, node_roles):
        count = sum(node_roles.values())
        del_nodes = []
        cp_nodes = self.nodes[:]
        for _ in range(0, count):
            node = cp_nodes.pop()
            del_nodes += [ node ]
            self.logger.info("Removing node %s" % node.id)

        if not cp_nodes:
            self.master = None
            self.state_set(self.S_STOPPED)
        else:
            self._stop_workers(del_nodes)
            try:
                client.wait_unregister(self.master.ip, self.AGENT_PORT)
                self.logger.info('TaskManager unregistered')
            except client.AgentException:
                self.logger.warning('Failed to unregister TaskManager at node %s'
                        % str(serviceNode))
            self.state_set(self.S_RUNNING)

        return del_nodes

    @expose('GET')
    def list_nodes(self, kwargs):
        """Return a list of running nodes"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        try:
            self.check_state([self.S_RUNNING, self.S_ADAPTING])
        except:
            return HttpJsonResponse({})

        return HttpJsonResponse({
            self.ROLE_MASTER: [ self.master.id ],
            self.ROLE_WORKER: [ node.id for node in self.nodes ]
        })

    @expose('GET')
    def get_service_info(self, kwargs):
        """Return the service state and type"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({'state': self.state_get(), 'type': 'flink'})

    @expose('GET')
    def get_node_info(self, kwargs):
        """Return information about the node identified by the given
        kwargs['serviceNodeId']"""

        node_ids = [ str(node.id) for node in self.nodes ]
        exp_params = [('serviceNodeId', is_in_list(node_ids))]
        try:
            serviceNodeId = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        serviceNode = None
        for node in self.nodes:
            if serviceNodeId == node.id:
                serviceNode = node
                break

        return HttpJsonResponse({
            'serviceNode': {
                'id': serviceNode.id,
                'ip': serviceNode.ip,
                'vmid': serviceNode.vmid,
                'cloud': serviceNode.cloud_name,
                'is_master': serviceNode.id == self.master.id,
                'role': serviceNode.role,
                'logs': self.get_role_logs(serviceNode.role)
            }
        })
