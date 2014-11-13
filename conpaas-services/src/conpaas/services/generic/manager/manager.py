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

from threading import Thread
import memcache
from shutil import rmtree
import pickle
import zipfile
import tarfile
import tempfile
import stat
import os.path
import time

from conpaas.core.expose import expose
from conpaas.core.controller import Controller
from conpaas.core.manager import BaseManager

from conpaas.core import git
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse, FileUploadField
from conpaas.services.generic.misc import archive_open, archive_get_members, archive_close, archive_get_type, archive_extract_file

from conpaas.core.log import create_logger
from conpaas.services.generic.agent import client
from conpaas.services.generic.manager.config import CodeVersion, ServiceConfiguration

class GenericManager(BaseManager):
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

    DEPLOYMENT_STATE = 'deployment_state'

    # String template for error messages returned when performing actions in
    # the wrong state
    WRONG_STATE_MSG = "ERROR: cannot perform %(action)s in state %(curstate)s"

    # String template for error messages returned when a required argument is
    # missing
    REQUIRED_ARG_MSG = "ERROR: %(arg)s is a required argument"

    # String template for debugging messages logged on nodes creation
    ACTION_REQUESTING_NODES = "requesting %(count)s nodes in %(action)s"

    AGENT_PORT = 5555

    # memcache keys
    CONFIG = 'config'

    def __init__(self, config_parser, **kwargs):
        """Initialize a Generic Manager.

        'config_parser' represents the manager config file.
        **kwargs holds anything that can't be sent in config_parser."""
        BaseManager.__init__(self, config_parser)
        self.controller.generate_context('generic')

        memcache_addr = config_parser.get('manager', 'MEMCACHE_ADDR')
        self.memcache = memcache.Client([memcache_addr])
        self.code_repo = config_parser.get('manager', 'CODE_REPO')

        self.state_log = []
        if kwargs['reset_config']:
            self._create_initial_configuration()

        self.nodes = []
        self.agents_info = []
        self.master_ip = None
        self._state_set(self.S_INIT)

    @expose('POST')
    def startup(self, kwargs):
        """Start the Generic service"""
        self.logger.info('Manager starting up')

        # Starting up the service makes sense only in the INIT or STOPPED
        # states
        dstate = self._state_get()
        if dstate != self.S_INIT and dstate != self.S_STOPPED:
            ex = ManagerException(ManagerException.E_STATE_ERROR)
            return HttpErrorResponse(ex.message)

        self._state_set(self.S_PROLOGUE, msg='Starting up')

        Thread(target=self._do_startup, args=[kwargs]).start()

        return HttpJsonResponse({ 'state': self._state_get() })

    def _do_startup(self, kwargs):
        """Start up the service. The first node will be the master node."""

        nr_instances = 1
#        nr_instances = 0
#        if kwargs and kwargs.get('manifest'):
#            instances = kwargs.get('manifest').get('StartupInstances')
#            tar_path =  kwargs.get('manifest').get('Archive')
#            for role in instances:
#                nr_instances += int(instances[role])

        vals = { 'action': '_do_startup', 'count': nr_instances }
        self.logger.debug(self.ACTION_REQUESTING_NODES % vals)

        try:
            #nodes = []
            #for i in range(1, nr_instances):
            #    nodes.append( self.controller.create_nodes(1, client.check_agent_process, self.AGENT_PORT))
            nodes = self.controller.create_nodes(nr_instances, client.check_agent_process, self.AGENT_PORT)

            config = self._configuration_get()

            roles = {'master':'1'}

            agents_info = self._update_agents_info(nodes, roles)

            self._init_agents(config, nodes, agents_info)

            self._update_code(config, nodes)

            # Extend the nodes list with the newly created one
            self.nodes += nodes
            self.agents_info += agents_info
            self.master_ip = nodes[0].ip
            self._state_set(self.S_RUNNING)
        except Exception, err:
            self.logger.exception('_do_startup: Failed to create agents: %s' % err)
            self._state_set(self.S_ERROR)

    def _update_agents_info(self, nodes, roles):
        id_ip = []
        for node in nodes:
            id_ip.append( { 'id': node.id, 'ip': node.ip })

        id_ip_role = []
        for role in roles:
            if len(id_ip):
                node_ip_id = id_ip.pop()
                node_ip_id.update({'role':role})
                id_ip_role.append(node_ip_id)

        return id_ip_role

    def _init_agents(self, config, nodes, agents_info):
        self._extract_init(config)
        for serviceNode in nodes:
            try:
                initpath = os.path.join(self.code_repo, 'init.sh')
                client.init_agent(serviceNode.ip, 5555, initpath, agents_info)
            except client.AgentException:
                self.logger.exception('Failed initialize agent at node %s' % str(serviceNode))
                self._state_set(self.S_ERROR, msg='Failed to initialize agent at node %s' % str(serviceNode))
                raise

    def _extract_init(self, config):
        #current_code = config.codeVersions[config.currentCodeVersion]
        filepath = os.path.join(self.code_repo, config.currentCodeVersion)
        arch = archive_open(filepath)

        archive_extract_file(arch, self.code_repo, 'init.sh')

    @expose('POST')
    def run(self, kwargs):

        if self._state_get() != self.S_RUNNING:
            vals = { 'curstate': self._state_get(), 'action': 'run' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        #self._state_set(self.S_EPILOGUE)
        Thread(target=self._do_run, args=[]).start()

        return HttpJsonResponse({ 'state': self._state_get() })

    def _do_run(self):
        for node in self.nodes:
            try:
                client.run(node.ip, 5555)
            except client.AgentException:
                self.logger.exception('Failed to start run at node %s' % str(node))
                self._state_set(self.S_ERROR, msg='Failed to run code at node %s' % str(node))
                raise

    @expose('POST')
    def shutdown(self, kwargs):
        """Switch to EPILOGUE and call a thread to delete all nodes"""
        # Shutdown only if RUNNING
        if self._state_get() != self.S_RUNNING:
            vals = { 'curstate': self._state_get(), 'action': 'shutdown' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        self._state_set(self.S_EPILOGUE)
        Thread(target=self._do_shutdown, args=[]).start()

        return HttpJsonResponse({ 'state': self._state_get() })

    def _do_shutdown(self):
        """Delete all nodes and switch to status STOPPED"""
        self.controller.delete_nodes(self.nodes)
        self.nodes = []        # Not only delete the nodes, but clear the list too
        self.agents_info = []
        self.master_ip = None
        self._state_set(self.S_STOPPED)

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
        #self.controller.update_context(dict(STRING='generic'))

        # Adding nodes makes sense only in the RUNNING state
        if self._state_get() != self.S_RUNNING:
            vals = { 'curstate': self._state_get(), 'action': 'add_nodes' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        # Ensure 'count' is valid
        #count_or_err = self.__check_count_in_args(kwargs)
        #if isinstance(count_or_err, HttpErrorResponse):
        #    return count_or_err

        if 'nodes' in kwargs:
            nodes = kwargs['nodes']
        else:
            return HttpErrorResponse(self.REQUIRED_ARG_MSG % { 'arg': 'count' })

        #TODO: sanitize
        start_role = kwargs['start_role']
        #count = count_or_err

        self._state_set(self.S_ADAPTING)
        Thread(target=self._do_add_nodes, args=[nodes, start_role]).start()

        return HttpJsonResponse({ 'state': self._state_get() })

    def _do_add_nodes(self, nodes, start_role):
        """Add 'count' Generic Nodes to this deployment"""
        count = 0
        for node in nodes:
                count += int(nodes[node])

        if count:
            node_instances = self.controller.create_nodes(count,
                client.check_agent_process, self.AGENT_PORT)

            config = self._configuration_get()
            agents_info = self._update_agents_info(node_instances, nodes)
            self._init_agents(config, node_instances, agents_info)
            self._update_code(config, node_instances)

            # Startup agents
            #for node in node_instances:
            #    client.create_node(node.ip, self.AGENT_PORT, self.master_ip)
            #config = self._configuration_get()
            #self._update_code(config, node_instances)

            self.nodes += node_instances
            self.agents_info += agents_info

        self._state_set(self.S_RUNNING)

    @expose('POST')
    def remove_nodes(self, kwargs):
        """Remove kwargs['count'] nodes from this deployment"""

        # Removing nodes only if RUNNING
        if self._state_get()!= self.S_RUNNING:
            vals = { 'curstate': self._state_get(), 'action': 'remove_nodes' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        # Ensure 'count' is valid
        count_or_err = self.__check_count_in_args(kwargs)
        if isinstance(count_or_err, HttpErrorResponse):
            return count_or_err

        count = count_or_err

        if count > len(self.nodes) - 1:
            return HttpErrorResponse("ERROR: Cannot remove so many nodes")

        self._state_set(self.S_ADAPTING)

        Thread(target=self._do_remove_nodes, args=[count]).start()

        return HttpJsonResponse({ 'state': self._state_get() })

    def _do_remove_nodes(self, count):
        """Remove 'count' nodes, starting from the end of the list. This way
        the Generic master gets removed last."""
        for _ in range(count):
            node = self.nodes.pop()
            self.agents_info.pop()
            self.logger.info("Removing node with IP %s" % node.ip)
            self.controller.delete_nodes([ node ])
        if not self.nodes:
            self.master_ip = None
            self._state_set(self.S_STOPPED)
        else:
            self._state_set(self.S_RUNNING)

    def __is_master(self, node):
        """Return True if the given node is the Generic master"""
        return node.ip == self.master_ip

    @expose('GET')
    def list_nodes(self, kwargs):
        """Return a list of running nodes"""
        if self._state_get() != self.S_RUNNING:
            vals = { 'curstate': self._state_get(), 'action': 'list_nodes' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        generic_nodes = [
            node.id for node in self.nodes if not self.__is_master(node)
        ]
        generic_master = [
            node.id for node in self.nodes if self.__is_master(node)
        ]

        return HttpJsonResponse({
            'master': generic_master,
            'node': generic_nodes
        })

    def _create_initial_configuration(self):
        print 'CREATING INIT CONFIG'

        config = ServiceConfiguration()

        if len(config.codeVersions) > 0:
            return

        if not os.path.exists(self.code_repo):
            os.makedirs(self.code_repo)

        tfile = tarfile.TarFile(name=os.path.join(self.code_repo, 'code-default'), mode='w')

        fileno, path = tempfile.mkstemp()
        fd = os.fdopen(fileno, 'w')
        fd.write('''#/bin/bash
echo "Initializing Generic Service!" >> /root/generic.out
echo "My IP is $MY_IP" >> /root/generic.out
echo "My role is $MY_ROLE" >> /root/generic.out
echo "My master IP is $MASTER_IP" >> /root/generic.out
echo "Inofrmation about other agents is stored at /var/cache/cpsagent/agents.json" >> /root/generic.out
cat /var/cache/cpsagent/agents.json >> /root/generic.out
echo "" >> /root/generic.out
''')
        fd.close()
        os.chmod(path, stat.S_IRWXU | stat.S_IROTH | stat.S_IXOTH)
        tfile.add(path, 'init.sh')

        fileno, path = tempfile.mkstemp()
        fd = os.fdopen(fileno, 'w')
        fd.write('''#/bin/bash
echo "Starting Generic Service!" >> /root/generic.out
echo "My IP is $MY_IP" >> /root/generic.out
echo "My role is $MY_ROLE" >> /root/generic.out
echo "My master IP is $MASTER_IP" >> /root/generic.out
echo "Inofrmation about other agents is stored at /var/cache/cpsagent/agents.json" >> /root/generic.out
cat /var/cache/cpsagent/agents.json >> /root/generic.out
echo "" >> /root/generic.out
''')
        fd.close()
        os.chmod(path, stat.S_IRWXU | stat.S_IROTH | stat.S_IXOTH)
        tfile.add(path, 'start.sh')

        tfile.close()
        os.remove(path)
        config.codeVersions['code-default'] = CodeVersion('code-default', 'code-default.tar', 'tar', description='Initial version')
        config.currentCodeVersion = 'code-default'
        self._configuration_set(config)

    @expose('UPLOAD')
    def upload_code_version(self, kwargs):
        if 'code' not in kwargs:
            ex = ManagerException(ManagerException.E_ARGS_MISSING, 'code')
            return HttpErrorResponse(ex.message)
        code = kwargs.pop('code')
        if 'description' in kwargs:
            description = kwargs.pop('description')
        else:
            description = ''

        if len(kwargs) != 0:
            ex = ManagerException(ManagerException.E_ARGS_UNEXPECTED,
                                  kwargs.keys())
            return HttpErrorResponse(ex.message)
        if not isinstance(code, FileUploadField):
            ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                  detail='codeVersionId should be a file')
            return HttpErrorResponse(ex.message)

        config = self._configuration_get()
        fd, name = tempfile.mkstemp(prefix='code-', dir=self.code_repo)
        fd = os.fdopen(fd, 'w')
        upload = code.file
        codeVersionId = os.path.basename(name)

        bytes = upload.read(2048)
        while len(bytes) != 0:
            fd.write(bytes)
            bytes = upload.read(2048)
        fd.close()

        arch = archive_open(name)
        if arch is None:
            os.remove(name)
            ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                  detail='Invalid archive format')
            return HttpErrorResponse(ex.message)

        for fname in archive_get_members(arch):
            if fname.startswith('/') or fname.startswith('..'):
                archive_close(arch)
                os.remove(name)
                ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                      detail='Absolute file names are not allowed in archive members')
                return HttpErrorResponse(ex.message)
        archive_close(arch)
        config.codeVersions[codeVersionId] = CodeVersion(
            codeVersionId, os.path.basename(code.filename), archive_get_type(name), description=description)
        self._configuration_set(config)
        return HttpJsonResponse({'codeVersionId': os.path.basename(codeVersionId)})

    @expose('GET')
    def get_service_info(self, kwargs):
        """Return the service state and type"""
        return HttpJsonResponse({'state': self._state_get(), 'type': 'generic'})

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
                'is_master': self.__is_master(serviceNode)
            }
        })

    @expose('GET')
    def list_code_versions(self, kwargs):
        if len(kwargs) != 0:
            ex = ManagerException(ManagerException.E_ARGS_UNEXPECTED,
                                  kwargs.keys())
            return HttpErrorResponse(ex.message)
        config = self._configuration_get()
        versions = []
        for version in config.codeVersions.values():
            item = {'codeVersionId': version.id, 'filename': version.filename,
                    'description': version.description, 'time': version.timestamp}
            if version.id == config.currentCodeVersion:
                item['current'] = True
            versions.append(item)
        versions.sort(
            cmp=(lambda x, y: cmp(x['time'], y['time'])), reverse=True)
        return HttpJsonResponse({'codeVersions': versions})

    @expose('POST')
    def enable_code(self, kwargs):
        codeVersionId = None
        if 'codeVersionId' in kwargs:
            codeVersionId = kwargs.pop('codeVersionId')
        config = self._configuration_get()
        phpconf = {}

        if len(kwargs) != 0:
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        if codeVersionId is None:
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING, '"codeVersionId" is not specified').message)

        if codeVersionId and codeVersionId not in config.codeVersions:
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Unknown code version identifier "%s"' % codeVersionId).message)

        dstate = self._state_get()
        if dstate == self.S_INIT or dstate == self.S_STOPPED:
            if codeVersionId:
                config.currentCodeVersion = codeVersionId
            self._configuration_set(config)
        elif dstate == self.S_RUNNING:
            self._state_set(self.S_ADAPTING, msg='Updating configuration')
            Thread(target=self.do_enable_code, args=[config, codeVersionId]).start()
        else:
            return HttpErrorResponse(ManagerException(ManagerException.E_STATE_ERROR).message)
        return HttpJsonResponse()

    def do_enable_code(self, config, codeVersionId):
        if codeVersionId is not None:
            self.prevCodeVersion = config.currentCodeVersion
            config.currentCodeVersion = codeVersionId
            self._update_code(config, self.nodes)
        self._state_set(self.S_RUNNING)
        self._configuration_set(config)

    def _update_code(self, config, nodes):
        for node in nodes:
            # Push the current code version via GIT if necessary
            #if config.codeVersions[config.currentCodeVersion].type == 'git':
            #    _, err = git.git_push(git.DEFAULT_CODE_REPO, node.ip)
            #    if err:
            #        self.logger.debug('git-push to %s: %s' % (node.ip, err))
            try:
                client.update_code(node.ip, 5555, config.currentCodeVersion,
                                     config.codeVersions[config.currentCodeVersion].type,
                                     os.path.join(self.code_repo, config.currentCodeVersion))
            except client.AgentException:
                self.logger.exception('Failed to update code at node %s' % str(node))
                self._state_set(self.S_ERROR, msg='Failed to update code at node %s' % str(node))
                raise

    def _configuration_get(self):
        return self.memcache.get(self.CONFIG)

    def _configuration_set(self, config):
        self.memcache.set(self.CONFIG, config)

    def _state_get(self):
        return self.memcache.get(self.DEPLOYMENT_STATE)

    def _state_set(self, target_state, msg=''):
        self.memcache.set(self.DEPLOYMENT_STATE, target_state)
        self.state_log.append({'time': time.time(),
                               'state': target_state,
                               'reason': msg})
        self.logger.debug('STATE %s: %s' % (target_state, msg))

