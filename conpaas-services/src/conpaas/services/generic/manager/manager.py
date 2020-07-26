"""
Copyright (c) 2010-2015, Contrail consortium.
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

from conpaas.core import git
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse,\
    HttpFileDownloadResponse, FileUploadField
from conpaas.services.generic.misc import archive_open, archive_get_members,\
    archive_close, archive_get_type, archive_extract_file

from conpaas.services.generic.agent import client
from conpaas.services.generic.manager.config import CodeVersion,\
    ServiceConfiguration, VolumeInfo

from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file

class GenericManager(BaseManager):

    # Generic node types
    ROLE_MASTER  = 'main'  # main node (the first one started)
    # a regular node (the role used by any other node) is defined in base class

    # String used as an error message when 'interrupt' is called when no
    # scripts are currently running
    NO_SCRIPTS_ARE_RUNNING_MSG = "ERROR: No scripts are currently running inside "\
                                "agents. Nothing to interrupt."

    # String used as an error message when scripts are running inside agents
    SCRIPTS_ARE_RUNNING_MSG = "ERROR: Scripts are still running inside at "\
                                "least one agent. Please wait for them to "\
                                "finish execution or call 'interrupt' first."

    def __init__(self, config_parser, **kwargs):
        """Initialize a Generic Manager.

        'config_parser' represents the manager config file.
        **kwargs holds anything that can't be sent in config_parser."""
        BaseManager.__init__(self, config_parser)

        self.code_repo = config_parser.get('manager', 'CODE_REPO')

        if kwargs['reset_config']:
            self._create_initial_configuration()

        self.agents_info = []
        self.main_ip = None

    def _prepare_default_config_script(self, script_name):
        fileno, path = tempfile.mkstemp()
        fd = os.fdopen(fileno, 'w')
        fd.write('''#!/bin/bash
date >> /root/generic.out
echo "Executing script ${0##*/}" >> /root/generic.out
echo "Parameters ($#): $@" >> /root/generic.out
echo "My IP is $MY_IP" >> /root/generic.out
echo "My role is $MY_ROLE" >> /root/generic.out
echo "My main IP is $MASTER_IP" >> /root/generic.out
echo "Information about other agents is stored at /var/cache/cpsagent/agents.json" >> /root/generic.out
cat /var/cache/cpsagent/agents.json >> /root/generic.out
echo "" >> /root/generic.out
echo "" >> /root/generic.out
''')
        fd.close()
        os.chmod(path, stat.S_IRWXU | stat.S_IROTH | stat.S_IXOTH)
        return path

    def get_service_type(self):
        return 'generic'

    def get_node_roles(self):
        return [ self.ROLE_MASTER, self.ROLE_REGULAR ]

    def get_starting_nodes(self):
        return { self.ROLE_MASTER: 1 }

    def get_role_logs(self, role):
        logs = BaseManager.get_role_logs(self, role)

        logs.extend([{'filename': 'agent.out',
                      'description': 'agent output',
                      'path': '/root/agent.out'},
                     {'filename': 'agent.err',
                      'description': 'agent error',
                      'path': '/root/agent.err'}]);

        return logs

    def _create_initial_configuration(self):
        self.logger.info("Creating initial configuration")

        config = ServiceConfiguration()

        if len(config.codeVersions) > 0:
            return

        if not os.path.exists(self.code_repo):
            os.makedirs(self.code_repo)

        tfile = tarfile.TarFile(name=os.path.join(self.code_repo, 'code-default'),
                mode='w')

        scripts = ['init.sh', 'notify.sh', 'run.sh', 'interrupt.sh', 'cleanup.sh']
        for script in scripts:
            path = self._prepare_default_config_script(script)
            tfile.add(path, script)
            os.remove(path)

        tfile.close()
        config.codeVersions['code-default'] = CodeVersion('code-default',
                'code-default.tar', 'tar', description='Initial version')
        config.currentCodeVersion = 'code-default'
        self._configuration_set(config)

    def on_start(self, nodes):
        """Start up the service. The first node will be the main node."""

        nr_instances = 1

        vals = { 'action': '_do_startup', 'count': nr_instances }
        self.logger.debug(self.ACTION_REQUESTING_NODES % vals)
        try:
            config = self._configuration_get()

            roles = { self.ROLE_MASTER: '1' }

            agents_info = self._update_agents_info(nodes, roles)

            self._init_agents(config, nodes, agents_info)
            self._update_code(config, nodes)

            # Extend the nodes list with the newly created one

            self.agents_info += agents_info
            self.main_ip = nodes[0].ip
            return True
        except Exception, err:
            self.logger.exception('_do_startup: Failed to create agents: %s' % err)
            return False

    def _update_agents_info(self, nodes, roles):
        id_ip = []
        for node in nodes:
            id_ip.append( { 'id': node.id, 'ip': node.ip })

        id_ip_role = []
        for role in roles:
            for _ in range(int(roles[role])):
                if len(id_ip):
                    node_ip_id = id_ip.pop(0)
                    node_ip_id.update({'role':role})
                    id_ip_role.append(node_ip_id)

        return id_ip_role

    def _init_agents(self, config, nodes, agents_info):
        self.logger.info("Initializing agents %s" %
                [ node.id for node in nodes ])

        for serviceNode in nodes:
            try:
                client.init_agent(serviceNode.ip, self.AGENT_PORT, agents_info)
            except client.AgentException:
                self.logger.exception('Failed initialize agent at node %s'
                        % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to initialize agent at node %s'
                        % str(serviceNode))
                raise

    def on_stop(self):
        """Delete all nodes and switch to status STOPPED"""

        self.logger.info("Removing nodes: %s" %
                [ node.id for node in self.nodes ])
        # self.controller.delete_nodes(self.nodes)
        del_nodes = self.nodes[:]
        self.agents_info = []
        self.main_ip = None
        return del_nodes

    def on_add_nodes(self, node_instances):
        # (genc): i have to figure out how to deal with the roles
        start_role = self.ROLE_REGULAR
        roles = {start_role: str(len(node_instances))}
        # Startup agents
        agents_info = self._update_agents_info(node_instances, roles)

        nodes_before = filter(lambda n: n not in node_instances, self.nodes)
        self.agents_info += agents_info

        config = self._configuration_get()
        self._init_agents(config, node_instances, self.agents_info)
        self._update_code(config, node_instances)

        self._do_execute_script('notify', nodes_before)
        return True

    def check_remove_nodes(self, node_roles):
        BaseManager.check_remove_nodes(self, node_roles)

        if node_roles.get(self.ROLE_MASTER, 0) > 0:
            raise Exception("Cannot remove the main node.")

    def on_remove_nodes(self, node_roles):
        count = sum(node_roles.values())
        del_nodes = []
        cp_nodes = self.nodes[:]
        for _ in range(0, count):
            node = cp_nodes.pop()
            del_nodes += [ node ]
            self.agents_info.pop()
            self.logger.info("Removing node with IP %s" % node.ip)
        if not cp_nodes:
            self.main_ip = None
            self.state_set(self.S_STOPPED)
        else:
            self._do_execute_script('notify', cp_nodes)
            self.state_set(self.S_RUNNING)

        return del_nodes

    def __is_main(self, node):
        """Return True if the given node is the Generic main"""
        return node.ip == self.main_ip

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

        generic_nodes = [
            node.id for node in self.nodes if not self.__is_main(node)
        ]
        generic_main = [
            node.id for node in self.nodes if self.__is_main(node)
        ]

        return HttpJsonResponse({
            self.ROLE_MASTER: generic_main,
            self.ROLE_REGULAR: generic_nodes
        })

    @expose('GET')
    def get_service_info(self, kwargs):
        """Return the service state and type"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({'state': self.state_get(), 'type': 'generic'})

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
                'is_main': self.__is_main(serviceNode),
                'role': serviceNode.role,
                'logs': self.get_role_logs(serviceNode.role)

            }
        })

    @expose('GET')
    def list_code_versions(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

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

    @expose('GET')
    def list_authorized_keys(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({'authorizedKeys' : git.get_authorized_keys()})

    @expose('UPLOAD')
    def upload_authorized_key(self, kwargs):
        exp_params = [('key', is_uploaded_file)]
        try:
            key = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        key_lines = key.file.readlines()
        num_added = git.add_authorized_keys(key_lines)

        return HttpJsonResponse({'outcome': "%s keys added to authorized_keys" % num_added})

    def on_git_push(self):
        config = self._configuration_get()

        repo = git.DEFAULT_CODE_REPO
        revision = git.git_code_version(repo)
        codeVersionId = "git-%s" % revision

        config.codeVersions[codeVersionId] = CodeVersion(id=codeVersionId,
                                                         filename=revision,
                                                         atype="git",
                                                         description=git.git_last_description(repo))

        self._configuration_set(config)

    @expose('UPLOAD')
    def upload_code_version(self, kwargs):
        exp_params = [('code', is_uploaded_file),
                      ('description', is_string, '')]
        try:
            code, description = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

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
            return HttpErrorResponse("%s" % ex)

        for fname in archive_get_members(arch):
            if fname.startswith('/') or fname.startswith('..'):
                archive_close(arch)
                os.remove(name)
                ex = ManagerException(ManagerException.E_ARGS_INVALID,
                    detail='Absolute file names are not allowed in archive members')
                return HttpErrorResponse("%s" % ex)
        archive_close(arch)
        config.codeVersions[codeVersionId] = CodeVersion(
            codeVersionId, os.path.basename(code.filename), archive_get_type(name),
            description=description)
        self._configuration_set(config)
        return HttpJsonResponse({'codeVersionId': os.path.basename(codeVersionId)})

    @expose('GET')
    def download_code_version(self, kwargs):
        config = self._configuration_get()
        exp_params = [('codeVersionId',
                       is_in_list(config.codeVersions),
                       config.currentCodeVersion)]
        try:
            codeVersionId = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        if config.codeVersions[codeVersionId].type == 'git':
            return HttpErrorResponse(
                'ERROR: To download this code, please clone the git repository');

        filename = os.path.abspath(os.path.join(self.code_repo, codeVersionId))
        if not filename.startswith(self.code_repo + '/') or not os.path.exists(filename):
            ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                  detail='Invalid codeVersionId')
            return HttpErrorResponse("%s" % ex)
        return HttpFileDownloadResponse(config.codeVersions[codeVersionId].filename,
                filename)

    @expose('POST')
    def enable_code(self, kwargs):
        config = self._configuration_get()
        exp_params = [('codeVersionId', is_in_list(config.codeVersions))]
        try:
            codeVersionId = check_arguments(exp_params, kwargs)
            self.check_state([self.S_INIT, self.S_STOPPED, self.S_RUNNING])
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        state = self.state_get()
        if state == self.S_INIT or state == self.S_STOPPED:
            config.currentCodeVersion = codeVersionId
            self._configuration_set(config)
        elif state == self.S_RUNNING:
            if self._are_scripts_running():
                self.logger.info("Code activation is disabled when scripts are "\
                        "running")
                return HttpErrorResponse(self.SCRIPTS_ARE_RUNNING_MSG);
            self.state_set(self.S_ADAPTING, msg='Updating configuration')
            Thread(target=self._do_enable_code, args=[config, codeVersionId]).start()

        return HttpJsonResponse()

    def _do_enable_code(self, config, codeVersionId):
        config.currentCodeVersion = codeVersionId
        self._update_code(config, self.nodes)
        self.state_set(self.S_RUNNING)
        self._configuration_set(config)

    def _update_code(self, config, nodes):
        self.logger.info("Updating code to version '%s' at agents %s" %
                (config.currentCodeVersion, [ node.id for node in nodes ]))

        for node in nodes:
            # Push the current code version via GIT if necessary
            if config.codeVersions[config.currentCodeVersion].type == 'git':
                filepath = config.codeVersions[config.currentCodeVersion].filename
                _, err = git.git_push(git.DEFAULT_CODE_REPO, node.ip)
                if err:
                    self.logger.debug('git-push to %s: %s' % (node.ip, err))
            else:
                filepath = os.path.join(self.code_repo, config.currentCodeVersion)
            try:
                client.update_code(node.ip, self.AGENT_PORT, config.currentCodeVersion,
                                     config.codeVersions[config.currentCodeVersion].type,
                                     filepath)
            except client.AgentException:
                self.logger.exception('Failed to update code at node %s' % str(node))
                self.state_set(self.S_ERROR, msg='Failed to update code at node %s' % str(node))
                raise

    @expose('POST')
    def delete_code_version(self, kwargs):
        config = self._configuration_get()
        exp_params = [('codeVersionId', is_in_list(config.codeVersions))]
        try:
            codeVersionId = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        if codeVersionId == config.currentCodeVersion:
            ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                  detail='Cannot remove the active code version')
            return HttpErrorResponse("%s" % ex)

        if not config.codeVersions[codeVersionId].type == 'git':
            filename = os.path.abspath(os.path.join(self.code_repo, codeVersionId))
            if not filename.startswith(self.code_repo + '/') or not os.path.exists(filename):
                ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                      detail='Invalid codeVersionId')
                return HttpErrorResponse("%s" % ex)

            os.remove(filename)

        config.codeVersions.pop(codeVersionId)
        self._configuration_set(config)

        return HttpJsonResponse()

    def check_create_volume(self, volume_name, volume_size, agent_id):
        if self._are_scripts_running():
            self.logger.info("Volume creation is disabled when scripts "
                             "are running")
            raise Exception(self.SCRIPTS_ARE_RUNNING_MSG)

    def on_create_volume(self, node, volume):
        client.mount_volume(node.ip, self.AGENT_PORT, volume['dev_name'],
                            volume['vol_name'])

    def check_delete_volume(self, node, volume):
        if self._are_scripts_running():
            self.logger.info("Volume removal is disabled when scripts "
                             "are running")
            raise Exception(self.SCRIPTS_ARE_RUNNING_MSG)

    def on_delete_volume(self, node, volume):
        client.unmount_volume(node.ip, self.AGENT_PORT, volume['vol_name'])

    @expose('POST')
    def execute_script(self, kwargs):
        valid_commands = [ 'run', 'interrupt', 'cleanup' ]
        exp_params = [('command', is_in_list(valid_commands)),
                      ('parameters', is_string, '')]
        try:
            command, parameters = check_arguments(exp_params, kwargs)
            self.check_state([self.S_RUNNING])
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.logger.info("Received request for executing the '%s' command "
                "with parameters '%s'" % (command, parameters))

        # if command is 'interrupt' and no scripts are running, return an error
        if command == 'interrupt' and not self._are_scripts_running():
            self.logger.info("No scripts are currently running inside agents")
            return HttpErrorResponse(self.NO_SCRIPTS_ARE_RUNNING_MSG)

        # for the other commands, if scripts are already running, return an error
        elif command != 'interrupt' and self._are_scripts_running():
            self.logger.info("Scripts are already running inside at least "
                    "one agent")
            return HttpErrorResponse(self.SCRIPTS_ARE_RUNNING_MSG)

        Thread(target=self._do_execute_script, args=[command,
                                                        self.nodes,
                                                        parameters]).start()

        return HttpJsonResponse({ 'state': self.state_get() })

    def _is_script_running(self, command):
        script_name = "%s.sh" % command
        for node in self.nodes:
            try:
                res = client.get_script_status(node.ip, self.AGENT_PORT)
                if res['scripts'][script_name] == "RUNNING":
                    return True
            except client.AgentException:
                message = ("Failed to obtain script status at node %s" % str(node));
                self.logger.exception(message)
        return False

    def _are_scripts_running(self):
        for node in self.nodes:
            try:
                res = client.get_script_status(node.ip, self.AGENT_PORT)
                if "RUNNING" in res['scripts'].values():
                    return True
            except client.AgentException:
                message = ("Failed to obtain script status at node %s" % str(node));
                self.logger.exception(message)
        return False

    def _do_execute_script(self, command, nodes, parameters=''):
        self.logger.info("Executing the '%s' command at agents %s" %
                (command, [ node.id for node in nodes ]))

        for node in nodes:
            try:
                client.execute_script(node.ip, self.AGENT_PORT, command,
                        parameters, self.agents_info)
            except client.AgentException:
                message = ("Failed to execute the '%s' command at node %s" %
                        (command, str(node)));
                self.logger.exception(message)
                self.state_set(self.S_ERROR, msg=message)
                raise

    @expose('GET')
    def get_script_status(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
            self.check_state([self.S_RUNNING])
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        agents = {}
        for node in self.nodes:
            try:
                res = client.get_script_status(node.ip, self.AGENT_PORT)
                agents[node.id] = res['scripts']
            except client.AgentException as ex:
                message = ("Failed to obtain script status at node %s" % str(node));
                self.logger.exception(message)
                self.state_set(self.S_ERROR, msg=message)
                return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({ 'agents' : agents })

    def _configuration_get(self):
        return self.service_config

    def _configuration_set(self, config):
        self.service_config = config
