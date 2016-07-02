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


Created on Feb 8, 2011

@author: ielhelw

- What is a deployment?
  A set of VMs logically grouped into 3 roles; web servers, php and load balancers.

- What is the configuration?
  web servers:    port, list of php (ip, port)
  php:           port
  load balancer:  port, list of web servers (ip, port)
  CODE to be placed at doc_root of all webserver VMs. Any file ending with
  '.php' is considered a dynamic script and will be passed to an php process.
  CODE should be located at the same directory path at all web servers and
  phps.

- How is a deployment started?
  A VM is created by the cloud front-end to host the MANAGER. The manager reads
  the initial configuration (from cloud storage or service?) and starts
  requesting VMs as needed by the configuration. Each VM will host an AGENT
  that is responsible for starting processes in it. The MANAGER will assign
  roles to each VM by instructing their AGENTs to run certain processes.
'''

from threading import Thread, Timer
import collections
import tempfile
import os
import os.path
import time

from conpaas.services.webservers.agent import client
from conpaas.services.webservers.manager.config import WebServiceNode, CodeVersion
from conpaas.services.webservers.misc import archive_open, archive_get_members, archive_close,\
    archive_get_type
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse,\
    HttpFileDownloadResponse, FileUploadField
from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager
from conpaas.core.manager import ManagerException

from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file

from conpaas.core import git


class BasicWebserversManager(BaseManager):

    # Default load balancing weight for nodes.
    DEFAULT_NODE_WEIGHT = 100

    def __init__(self, config_parser):
        BaseManager.__init__(self, config_parser)

        # self.controller.generate_context('web')

        self.code_repo = config_parser.get('manager', 'CODE_REPO')

    def get_service_type(self):
        return 'web'

    def _configuration_get(self):
        return self.service_config

    def _configuration_set(self, config):
        self.service_config = config

    # def _adapting_set_count(self, count):
    #     self.memcache.set('adapting_count', count)

    # def _adapting_get_count(self):
    #     return self.memcache.get('adapting_count')

    def _start_scalaris(self, config, nodes, first_start):
        # If needed, must be overridden by extending classes
        pass

    def _start_proxy(self, config, nodes):
        raise Exception("BasicWebservicesManager._start_proxy(...) must be overridden by extending classes.")

    def _update_proxy(self, config, nodes):
        raise Exception("BasicWebservicesManager._update_proxy(...) must be overridden by extending classes.")

    def _stop_proxy(self, config, nodes):
        for serviceNode in nodes:
            try:
                client.stopHttpProxy(serviceNode.ip, self.AGENT_PORT)
            except client.AgentException:
                self.logger.exception(
                    'Failed to stop proxy at node %s' % str(serviceNode))
                self.state_set(
                    self.S_ERROR, msg='Failed to stop proxy at node %s' % str(serviceNode))
                raise

    def _start_web(self, config, nodes):
        if config.prevCodeVersion is None:
            code_versions = [config.currentCodeVersion]
        else:
            code_versions = [config.currentCodeVersion, config.prevCodeVersion]
        for serviceNode in nodes:
            try:
                client.createWebServer(serviceNode.ip, self.AGENT_PORT,
                                       config.web_config.port,
                                       code_versions)
            except client.AgentException:
                self.logger.exception(
                    'Failed to start web at node %s' % str(serviceNode))
                self.state_set(
                    self.S_ERROR, msg='Failed to start web at node %s' % str(serviceNode))
                raise

    def _update_web(self, config, nodes):
        if config.prevCodeVersion is None:
            code_versions = [config.currentCodeVersion]
        else:
            code_versions = [config.currentCodeVersion, config.prevCodeVersion]
        for webNode in nodes:
            try:
                client.updateWebServer(webNode.ip, self.AGENT_PORT,
                                       config.web_config.port,
                                       code_versions)
            except client.AgentException:
                self.logger.exception(
                    'Failed to update web at node %s' % str(webNode))
                self.state_set(
                    self.S_ERROR, msg='Failed to update web at node %s' % str(webNode))
                raise

    def _stop_web(self, config, nodes):
        for serviceNode in nodes:
            try:
                client.stopWebServer(serviceNode.ip, self.AGENT_PORT)
            except client.AgentException:
                self.logger.exception('Failed to stop web at node %s'
                                      % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to stop web at node %s'
                                % str(serviceNode))
                raise

    def _start_backend(self, config, nodes):
        raise Exception("BasicWebservicesManager._start_backend(...) must be overridden by extending classes.")

    def _stop_backend(self, config, nodes):
        raise Exception("BasicWebservicesManager._stop_backend(...) must be overridden by extending classes.")

    def get_starting_nodes(self):
        config = self._configuration_get()
        nr_agents = config.proxy_count + config.web_count + config.backend_count
        if nr_agents == 0:
            nr_agents = 1

        # (genc): maybe not neccessary at this moment
        # self._adapting_set_count(nr_agents)
        return [{'cloud':None} for _ in range(nr_agents)]

    def on_start(self, nodes):
        config = self._configuration_get()

        if config.proxy_count == 1 \
                and (config.web_count == 0 or config.backend_count == 0):  # at least one is packed
            if config.web_count == 0 and config.backend_count == 0:  # packed
                serviceNodeKwargs = [
                    {'runProxy': True, 'runWeb': True, 'runBackend': True}]
            # web packed, backend separated
            elif config.web_count == 0 and config.backend_count > 0:
                serviceNodeKwargs = [{'runBackend': True}
                                     for _ in range(config.backend_count)]
                serviceNodeKwargs.append({'runProxy': True, 'runWeb': True})
            # proxy separated, backend packed
            elif config.web_count > 0 and config.backend_count == 0:
                serviceNodeKwargs = [{'runWeb': True}
                                     for _ in range(config.web_count)]
                serviceNodeKwargs.append(
                    {'runProxy': True, 'runBackend': True})
        else:
            if config.web_count < 1:
                config.web_count = 1  # have to have at least one web
            if config.backend_count < 1:
                config.backend_count = 1  # have to have at least one backend
            serviceNodeKwargs = [{'runProxy': True}
                                 for _ in range(config.proxy_count)]
            serviceNodeKwargs.extend([{'runWeb': True}
                                     for _ in range(config.web_count)])
            serviceNodeKwargs.extend([{'runBackend': True}
                                     for _ in range(config.backend_count)])

        node_instances = nodes
        config.serviceNodes.clear()
        i = 0
        for kwargs in serviceNodeKwargs:
            config.serviceNodes[node_instances[i].id] = WebServiceNode(
                node_instances[i], **kwargs)
            i += 1
        config.update_mappings()

        # start the Scalaris process to keep the session data
        self._start_scalaris(config, nodes, True)

        # issue orders to agents to start PHP inside
        self._start_backend(config, config.getBackendServiceNodes())

        # stage the code files
        # NOTE: Code update is done after starting the backend
        #       because tomcat-create-instance complains if its
        #       directory exists when it is run and placing the
        #       code can only be done after creating the instance
        if config.currentCodeVersion is not None:
            self._update_code(config, config.serviceNodes.values())

        # issue orders to agents to start web servers inside
        self._start_web(config, config.getWebServiceNodes())

        # issue orders to agents to start proxy inside
        self._start_proxy(config, config.getProxyServiceNodes())

        self._configuration_set(config)  # update configuration

        # self.memcache.set('nodes_additional', [])
        return True

    def on_stop(self):
        config = self._configuration_get()
        self._stop_proxy(config, config.getProxyServiceNodes())
        self._stop_web(config, config.getWebServiceNodes())
        self._stop_backend(config, config.getBackendServiceNodes())
        del_nodes = config.serviceNodes.values()
        # self.controller.delete_nodes(config.serviceNodes.values())
        config.serviceNodes = {}
        self._configuration_set(config)
        return del_nodes

    # @expose('POST')
    # def startup(self, kwargs):

    #     config = self._configuration_get()

    #     state = self.state_get()
    #     if state != self.S_INIT and state != self.S_STOPPED:
    #         ex = ManagerException(ManagerException.E_STATE_ERROR)
    #         return HttpErrorResponse("%s" % ex)

    #     if config.proxy_count == 1 \
    #             and (config.web_count == 0 or config.backend_count == 0):  # at least one is packed
    #         if config.web_count == 0 and config.backend_count == 0:  # packed
    #             serviceNodeKwargs = [
    #                 {'runProxy': True, 'runWeb': True, 'runBackend': True}]
    #         # web packed, backend separated
    #         elif config.web_count == 0 and config.backend_count > 0:
    #             serviceNodeKwargs = [{'runBackend': True}
    #                                  for _ in range(config.backend_count)]
    #             serviceNodeKwargs.append({'runProxy': True, 'runWeb': True})
    #         # proxy separated, backend packed
    #         elif config.web_count > 0 and config.backend_count == 0:
    #             serviceNodeKwargs = [{'runWeb': True}
    #                                  for _ in range(config.web_count)]
    #             serviceNodeKwargs.append(
    #                 {'runProxy': True, 'runBackend': True})
    #     else:
    #         if config.web_count < 1:
    #             config.web_count = 1  # have to have at least one web
    #         if config.backend_count < 1:
    #             config.backend_count = 1  # have to have at least one backend
    #         serviceNodeKwargs = [{'runProxy': True}
    #                              for _ in range(config.proxy_count)]
    #         serviceNodeKwargs.extend([{'runWeb': True}
    #                                  for _ in range(config.web_count)])
    #         serviceNodeKwargs.extend([{'runBackend': True}
    #                                  for _ in range(config.backend_count)])

    #     # if not self._deduct_credit(len(serviceNodeKwargs)):
    #     # return
    #     # HttpErrorResponse(ManagerException(ManagerException.E_NOT_ENOUGH_CREDIT).message)

    #     self.state_set(self.S_PROLOGUE, msg='Starting up')
    #     Thread(target=self.do_startup, args=[
    #            config, serviceNodeKwargs, kwargs['cloud']]).start()
    #     return HttpJsonResponse({'state': self.S_PROLOGUE})

    # @expose('POST')
    # def stop(self, kwargs):
    #     if len(kwargs) != 0:
    #         ex = ManagerException(ManagerException.E_ARGS_UNEXPECTED,
    #                               kwargs.keys())
    #         return HttpErrorResponse("%s" % ex)

    #     state = self.state_get()
    #     if state != self.S_RUNNING:
    #         ex = ManagerException(ManagerException.E_STATE_ERROR)
    #         return HttpErrorResponse("%s" % ex)

    #     self.state_set(self.S_EPILOGUE, msg='Shutting down')
    #     Thread(target=self._do_stop, args=[]).start()
    #     return HttpJsonResponse({'state': self.S_EPILOGUE})

    def _update_code(self, config, nodes):
        raise Exception("BasicWebservicesManager._update_code(...) must be overridden by extending classes.")


    # def do_startup(self, config, serviceNodeKwargs, cloud):
    #     self.logger.debug(
    #         'do_startup: Going to request %d new nodes' % len(serviceNodeKwargs))
    #     cloud = self._init_cloud(cloud)
    #     try:
    #         self._adapting_set_count(len(serviceNodeKwargs))
    #         node_instances = self.controller.create_nodes(
    #             len(serviceNodeKwargs),
    #             client.check_agent_process, self.AGENT_PORT, cloud)
    #     except:
    #         self.logger.exception(
    #             'do_startup: Failed to request new nodes. Needed %d' % (len(serviceNodeKwargs)))
    #         self.state_set(self.S_STOPPED, msg='Failed to request new nodes')
    #         return
    #     finally:
    #         self._adapting_set_count(0)

    #     config.serviceNodes.clear()
    #     i = 0
    #     for kwargs in serviceNodeKwargs:
    #         config.serviceNodes[node_instances[i].id] = WebServiceNode(
    #             node_instances[i], **kwargs)
    #         i += 1
    #     config.update_mappings()

    #     # issue orders to agents to start PHP inside
    #     self._start_backend(config, config.getBackendServiceNodes())

    #     # stage the code files
    #     # NOTE: Code update is done after starting the backend
    #     #       because tomcat-create-instance complains if its
    #     #       directory exists when it is run and placing the
    #     #       code can only be done after creating the instance
    #     if config.currentCodeVersion is not None:
    #         self._update_code(config, config.serviceNodes.values())

    #     # issue orders to agents to start web servers inside
    #     self._start_web(config, config.getWebServiceNodes())

    #     # issue orders to agents to start proxy inside
    #     self._start_proxy(config, config.getProxyServiceNodes())

    #     self._configuration_set(config)  # update configuration
    #     self.state_set(self.S_RUNNING)
    #     self.memcache.set('nodes_additional', [])

    # def _do_stop(self):
    #     config = self._configuration_get()
    #     self._stop_proxy(config, config.getProxyServiceNodes())
    #     self._stop_web(config, config.getWebServiceNodes())
    #     self._stop_backend(config, config.getBackendServiceNodes())
    #     self.controller.delete_nodes(config.serviceNodes.values())
    #     config.serviceNodes = {}
    #     self.state_set(self.S_STOPPED)
    #     self._configuration_set(config)

    def on_add_nodes(self, nodes):
        config = self._configuration_get()
        backend = len(filter(lambda n: n.role=='backend', nodes))
        web = len(filter(lambda n: n.role=='web', nodes))
        proxy = len(filter(lambda n: n.role=='proxy', nodes))

        webNodesNew = []
        proxyNodesNew = []
        backendNodesNew = []

        webNodesKill = []
        backendNodesKill = []

        if backend > 0 and config.backend_count == 0:
            backendNodesKill.append(config.getBackendServiceNodes()[0])
        if web > 0 and config.web_count == 0:
            webNodesKill.append(config.getWebServiceNodes()[0])

        for _ in range(backend):
            backendNodesNew.append({'runBackend': True})
        for _ in range(web):
            webNodesNew.append({'runWeb': True})
        for _ in range(proxy):
            proxyNodesNew.append({'runProxy': True})

        for i in webNodesKill:
            i.isRunningWeb = False
        for i in backendNodesKill:
            i.isRunningBackend = False

        node_instances = nodes
        # node_instances = []
        # try:
        #     self._adapting_set_count(
        #         len(proxyNodesNew) + len(webNodesNew) + len(backendNodesNew))
        #     if proxy > 0:
        #         node_instances += self.controller.create_nodes(
        #             len(proxyNodesNew), client.check_agent_process, self.AGENT_PORT, cloud)
        #     if web > 0 and vm_web_type is None:
        #         node_instances += self.controller.create_nodes(
        #             len(webNodesNew), client.check_agent_process, self.AGENT_PORT, cloud)
        #     elif web > 0:
        #         node_instances += self.controller.create_nodes(
        #             len(webNodesNew), client.check_agent_process, self.AGENT_PORT, cloud, inst_type=vm_web_type)

        #     if backend > 0 and vm_backend_type is None:
        #         node_instances += self.controller.create_nodes(
        #             len(backendNodesNew), client.check_agent_process, self.AGENT_PORT, cloud)
        #     elif backend > 0:
        #         node_instances += self.controller.create_nodes(
        #             len(backendNodesNew), client.check_agent_process, self.AGENT_PORT, cloud, inst_type=vm_backend_type)
        # except:
        #     self.logger.exception(
        #         'do_add_nodes: Failed to request new nodes. Needed %d' %
        #         (len(proxyNodesNew + webNodesNew + backendNodesNew)))
        #     self.state_set(
        #         self.S_RUNNING, msg='Failed to request new nodes. Reverting to old configuration')
        #     return
        # finally:
        #     self._adapting_set_count(0)

        i = 0
        newNodes = []
        for kwargs in proxyNodesNew + webNodesNew + backendNodesNew:
            config.serviceNodes[node_instances[i].id] = WebServiceNode(
                node_instances[i], self.DEFAULT_NODE_WEIGHT, self.DEFAULT_NODE_WEIGHT, **kwargs)
            newNodes += [config.serviceNodes[node_instances[i].id]]
            i += 1
        config.update_mappings()

        # start the Scalaris process to keep the session data
        self._start_scalaris(config, nodes, False)

        # add new service nodes
        self._start_backend(
            config, [node for node in newNodes if node.isRunningBackend])
        # stage code files in all new VMs
        # NOTE: Code update is done after starting the backend
        #       because tomcat-create-instance complains if its
        #       directory exists when it is run and placing the
        #       code can only be done after creating the instance
        if config.currentCodeVersion is not None:
            self._update_code(
                config, [node for node in newNodes
                         if node not in config.serviceNodes])  # FIXME: ? rather be config.serviceNodes.values ?

        self._start_web(config,
                        [node for node in newNodes if node.isRunningWeb])
        self._start_proxy(config,
                          [node for node in newNodes if node.isRunningProxy])

        # update services
        if webNodesNew or backendNodesNew:
            self._update_proxy(
                config, [i for i in config.serviceNodes.values()
                         if i.isRunningProxy and i not in newNodes])
        # remove_nodes old ones

        self._stop_backend(config, backendNodesKill)
        self._stop_web(config, webNodesKill)

        config.proxy_count = len(config.getProxyServiceNodes())
        config.backend_count = len(config.getBackendServiceNodes())
        if config.backend_count == 1 and config.getBackendServiceNodes()[0] in config.getProxyServiceNodes():
            config.backend_count = 0
        config.web_count = len(config.getWebServiceNodes())
        if config.web_count == 1 and config.getWebServiceNodes()[0] in config.getProxyServiceNodes():
            config.web_count = 0


        self._configuration_set(config)
        # self.memcache.set('nodes_additional', [])
        return True

    # @expose('POST')
    # def add_nodes(self, kwargs):
    #     """
    #     Add nodes to this web service.
    #     At least one of the three types of nodes must be positive:
    #     backend > 0 or web > 0 or proxy > 0.

    #     POST parameters:
    #     ----------------
    #     backend : int
    #         Optional
    #         number of new backend nodes to create
    #     web : int
    #         Optional
    #         number of new web nodes to create
    #     proxy : int
    #         Optional
    #         number of new proxy nodes to create
    #     vm_backend_instance : string
    #         Optional
    #         type of cloud instance to create as backend node.
    #         Values depend on the cloud provider (for example "t1.micro" for Amazon
    #         EC2, or "small" for OpenNebula, etc.). Default is the instance type
    #         specified in the director configuration file (INST_TYPE in OpenNebula
    #         configuration, SIZE_ID in Amazon EC2 configuration).
    #     vm_web_instance : string
    #         Optional
    #         type of cloud instance to create as web node.
    #         Values are similar to the vm_backend_instance argument.
    #     cloud : string
    #         Optional
    #         name of the cloud where the nodes will be created
    #     """
    #     config = self._configuration_get()
    #     state = self.state_get()
    #     if state != self.S_RUNNING:
    #         ex = ManagerException(ManagerException.E_STATE_ERROR)
    #         return HttpErrorResponse("%s" % ex)

    #     backend = 0
    #     web = 0
    #     proxy = 0

    #     vm_backend_type = None
    #     vm_web_type = None

    #     if 'backend' in kwargs:
    #         if not isinstance(kwargs['backend'], int):
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected an integer value for "backend"')
    #             return HttpErrorResponse("%s" % ex)
    #         backend = int(kwargs.pop('backend'))
    #         if backend < 0:
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a positive integer value for "backend"')
    #             return HttpErrorResponse("%s" % ex)

    #     if 'web' in kwargs:
    #         if not isinstance(kwargs['web'], int):
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected an integer value for "web"')
    #             return HttpErrorResponse("%s" % ex)
    #         web = int(kwargs.pop('web'))
    #         if web < 0:
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a positive integer value for "web"')
    #             return HttpErrorResponse("%s" % ex)

    #     if 'proxy' in kwargs:
    #         if not isinstance(kwargs['proxy'], int):
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected an integer value for "proxy"')
    #             return HttpErrorResponse("%s" % ex)
    #         proxy = int(kwargs.pop('proxy'))
    #         if proxy < 0:
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a positive integer value for "proxy"')
    #             return HttpErrorResponse("%s" % ex)

    #     if (backend + web + proxy) < 1:
    #         ex = ManagerException(ManagerException.E_ARGS_MISSING, ['backend', 'web', 'proxy'],
    #                               detail='Need a positive value for at least one')
    #         return HttpErrorResponse("%s" % ex)

    #     cloud = kwargs.pop('cloud', 'iaas')
    #     try:
    #         cloud = self._init_cloud(cloud)
    #     except Exception as ex:
    #         # unknown cloud
    #         return HttpErrorResponse("%s" % ex)

    #     if 'vm_backend_instance' in kwargs:
    #         self.logger.info('VM BACKEND INSTANCE: %s' %
    #                          str(kwargs['vm_backend_instance']))
    #         if not isinstance(str(kwargs['vm_backend_instance']), basestring):
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a string value for "vm_backend_instance"')
    #             return HttpErrorResponse("%s" % ex)
    #         vm_backend_type = kwargs.pop('vm_backend_instance')
    #         if len(vm_backend_type) <= 0:
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a string value for "vm_backend_instance"')
    #             return HttpErrorResponse("%s" % ex)

    #     if 'vm_web_instance' in kwargs:
    #         self.logger.info('VM WEB INSTANCE: %s' %
    #                          str(kwargs['vm_web_instance']))
    #         if not isinstance(str(kwargs['vm_web_instance']), basestring):
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a string value for "vm_web_instance"')
    #             return HttpErrorResponse("%s" % ex)
    #         vm_web_type = kwargs.pop('vm_web_instance')
    #         if len(vm_web_type) <= 0:
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a string value for "vm_web_instance"')
    #             return HttpErrorResponse("%s" % ex)

    #     if (proxy + config.proxy_count) > 1 and ((web + config.web_count) == 0 or (backend + config.backend_count) == 0):
    #         ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                               detail='Cannot add more proxy servers without at least one "web" and one "backend"')
    #         return HttpErrorResponse("%s" % ex)

    #     self.state_set(
    #         self.S_ADAPTING, msg='Going to add proxy=%d, web=%d, backend=%d, vm_backend_type=%s, vm_web_type=%s, cloud=%s' %
    #         (proxy, web, backend, str(vm_backend_type), str(vm_web_type), cloud.get_cloud_name()))
    #     Thread(target=self.do_add_nodes, args=[
    #            config, proxy, web, backend, cloud, vm_backend_type, vm_web_type]).start()
    #     return HttpJsonResponse()

    # def do_add_nodes(self, config, proxy, web, backend, cloud, vm_backend_type, vm_web_type):
    #     webNodesNew = []
    #     proxyNodesNew = []
    #     backendNodesNew = []

    #     webNodesKill = []
    #     backendNodesKill = []

    #     if backend > 0 and config.backend_count == 0:
    #         backendNodesKill.append(config.getBackendServiceNodes()[0])
    #     if web > 0 and config.web_count == 0:
    #         webNodesKill.append(config.getWebServiceNodes()[0])

    #     for _ in range(backend):
    #         backendNodesNew.append({'runBackend': True})
    #     for _ in range(web):
    #         webNodesNew.append({'runWeb': True})
    #     for _ in range(proxy):
    #         proxyNodesNew.append({'runProxy': True})

    #     for i in webNodesKill:
    #         i.isRunningWeb = False
    #     for i in backendNodesKill:
    #         i.isRunningBackend = False

    #     node_instances = []
    #     try:
    #         self._adapting_set_count(
    #             len(proxyNodesNew) + len(webNodesNew) + len(backendNodesNew))
    #         if proxy > 0:
    #             node_instances += self.controller.create_nodes(
    #                 len(proxyNodesNew), client.check_agent_process, self.AGENT_PORT, cloud)
    #         if web > 0 and vm_web_type is None:
    #             node_instances += self.controller.create_nodes(
    #                 len(webNodesNew), client.check_agent_process, self.AGENT_PORT, cloud)
    #         elif web > 0:
    #             node_instances += self.controller.create_nodes(
    #                 len(webNodesNew), client.check_agent_process, self.AGENT_PORT, cloud, inst_type=vm_web_type)

    #         if backend > 0 and vm_backend_type is None:
    #             node_instances += self.controller.create_nodes(
    #                 len(backendNodesNew), client.check_agent_process, self.AGENT_PORT, cloud)
    #         elif backend > 0:
    #             node_instances += self.controller.create_nodes(
    #                 len(backendNodesNew), client.check_agent_process, self.AGENT_PORT, cloud, inst_type=vm_backend_type)
    #     except:
    #         self.logger.exception(
    #             'do_add_nodes: Failed to request new nodes. Needed %d' %
    #             (len(proxyNodesNew + webNodesNew + backendNodesNew)))
    #         self.state_set(
    #             self.S_RUNNING, msg='Failed to request new nodes. Reverting to old configuration')
    #         return
    #     finally:
    #         self._adapting_set_count(0)

    #     i = 0
    #     newNodes = []
    #     for kwargs in proxyNodesNew + webNodesNew + backendNodesNew:
    #         config.serviceNodes[node_instances[i].id] = WebServiceNode(
    #             node_instances[i], self.DEFAULT_NODE_WEIGHT, self.DEFAULT_NODE_WEIGHT, **kwargs)
    #         newNodes += [config.serviceNodes[node_instances[i].id]]
    #         i += 1
    #     config.update_mappings()

    #     # add new service nodes
    #     self._start_backend(
    #         config, [node for node in newNodes if node.isRunningBackend])
    #     # stage code files in all new VMs
    #     # NOTE: Code update is done after starting the backend
    #     #       because tomcat-create-instance complains if its
    #     #       directory exists when it is run and placing the
    #     #       code can only be done after creating the instance
    #     if config.currentCodeVersion is not None:
    #         self._update_code(
    #             config, [node for node in newNodes
    #                      if node not in config.serviceNodes])  # FIXME: ? rather be config.serviceNodes.values ?

    #     self._start_web(config,
    #                     [node for node in newNodes if node.isRunningWeb])
    #     self._start_proxy(config,
    #                       [node for node in newNodes if node.isRunningProxy])

    #     # update services
    #     if webNodesNew or backendNodesNew:
    #         self._update_proxy(
    #             config, [i for i in config.serviceNodes.values()
    #                      if i.isRunningProxy and i not in newNodes])
    #     # remove_nodes old ones

    #     self._stop_backend(config, backendNodesKill)
    #     self._stop_web(config, webNodesKill)

    #     config.proxy_count = len(config.getProxyServiceNodes())
    #     config.backend_count = len(config.getBackendServiceNodes())
    #     if config.backend_count == 1 and config.getBackendServiceNodes()[0] in config.getProxyServiceNodes():
    #         config.backend_count = 0
    #     config.web_count = len(config.getWebServiceNodes())
    #     if config.web_count == 1 and config.getWebServiceNodes()[0] in config.getProxyServiceNodes():
    #         config.web_count = 0

    #     self.state_set(self.S_RUNNING)
    #     self._configuration_set(config)
    #     self.memcache.set('nodes_additional', [])

    def on_remove_nodes(self, node_roles):
        # no checks on parameters here (should be done in base class)
        # no remove from ip supported
        backend = web = proxy = 0
        if 'backend' in node_roles:
            backend = node_roles['backend']

        if 'web' in node_roles:
            web = node_roles['web']

        if 'proxy' in node_roles:
            proxy = node_roles['proxy']

        node_ip = None

        config = self._configuration_get()

        packBackend = False
        packWeb = False
        packingNode = None

        backendNodesKill = []
        webNodesKill = []
        proxyNodesKill = []

        if web > 0:
            if node_ip is not None:
                for serviceNode in config.getWebServiceNodes():
                    if(serviceNode.ip == node_ip):
                        webNodesKill.append(serviceNode)
            else:
                webNodesKill += config.getWebServiceNodes()[-web:]
            if config.web_count - web == 0:
                packWeb = True

        if backend > 0:
            if node_ip is not None:
                for serviceNode in config.getBackendServiceNodes():
                    if(serviceNode.ip == node_ip):
                        backendNodesKill.append(serviceNode)
            else:
                backendNodesKill += config.getBackendServiceNodes()[-backend:]
            if config.backend_count - backend == 0:
                packBackend = True

        if proxy > 0:
            proxyNodesKill += config.getProxyServiceNodes()[-proxy:]

        packingNode = config.getProxyServiceNodes()[0]
        for i in webNodesKill:
            i.isRunningWeb = False
        for i in backendNodesKill:
            i.isRunningBackend = False
        for i in proxyNodesKill:
            i.isRunningProxy = False
        if packBackend:
            packingNode.isRunningBackend = True
        if packWeb:
            packingNode.isRunningWeb = True

        config.update_mappings()
        self.logger.info("Remove_nodes " + str(config.serviceNodes))
        # new nodes
        if packBackend:
            # NOTE: Code update is done after starting the backend
            #       because tomcat-create-instance complains if its
            #       directory exists when it is run and placing the
            #       code can only be done after creating the instance
            self._start_backend(config, [packingNode])
            self._update_code(config, [packingNode])
        if packWeb:
            self._start_web(config, [packingNode])

        if webNodesKill or backendNodesKill:
            self._update_proxy(config, [i for i in config.serviceNodes.values()
                                        if i.isRunningProxy and i not in proxyNodesKill])

        try:
            # remove_nodes nodes
            self._stop_backend(config, backendNodesKill)
            self._stop_web(config, webNodesKill)
            self._stop_proxy(config, proxyNodesKill)
            del_nodes = []
            #   self.logger.info("Internal php: service nodes "+str(config.serviceNodes.values()))
            for i in config.serviceNodes.values():
                if not i.isRunningBackend and not i.isRunningWeb and not i.isRunningProxy:
                    del_nodes += [i]
                    del config.serviceNodes[i.id]
                    # self.controller.delete_nodes([i])
                    #  self.logger.info("Internal php: Removing_node "+str(i.id))

            config.proxy_count = len(config.getProxyServiceNodes())
            config.backend_count = len(config.getBackendServiceNodes())
            if config.backend_count == 1 and config.getBackendServiceNodes()[0] in config.getProxyServiceNodes():
                config.backend_count = 0
            config.web_count = len(config.getWebServiceNodes())
            if config.web_count == 1 and config.getWebServiceNodes()[0] in config.getProxyServiceNodes():
                config.web_count = 0

            #  config.update_mappings()
            self.logger.info("Remove_nodes " + str(config.serviceNodes))

        except Exception:
            self.logger.critical('Error when trying to remove ')

        self._configuration_set(config)
        self.state_set(self.S_RUNNING)
        return del_nodes


    # @expose('POST')
    # def remove_nodes(self, kwargs):
    #     config = self._configuration_get()
    #     backend = 0
    #     web = 0
    #     proxy = 0

    #     node_ip = None

    #     if 'backend' in kwargs:
    #         if not isinstance(kwargs['backend'], int):
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected an integer value for "backend"')
    #             return HttpErrorResponse("%s" % ex)
    #         backend = int(kwargs.pop('backend'))
    #         if backend < 0:
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a positive integer value for "backend"')
    #             return HttpErrorResponse("%s" % ex)

    #     if 'web' in kwargs:
    #         if not isinstance(kwargs['web'], int):
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected an integer value for "web"')
    #             return HttpErrorResponse("%s" % ex)
    #         web = int(kwargs.pop('web'))
    #         if web < 0:
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a positive integer value for "web"')
    #             return HttpErrorResponse("%s" % ex)

    #     if 'proxy' in kwargs:
    #         if not isinstance(kwargs['proxy'], int):
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected an integer value for "proxy"')
    #             return HttpErrorResponse("%s" % ex)
    #         proxy = int(kwargs.pop('proxy'))
    #         if proxy < 0:
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a positive integer value for "proxy"')
    #             return HttpErrorResponse("%s" % ex)

    #     if (backend + web + proxy) < 1:
    #         ex = ManagerException(ManagerException.E_ARGS_MISSING, ['backend', 'web', 'proxy'],
    #                               detail='Need a positive value for at least one')
    #         return HttpErrorResponse("%s" % ex)

    #     if 'node_ip' in kwargs:
    #         self.logger.info('IP Node to remove: %s' % str(kwargs['node_ip']))
    #         if not isinstance(str(kwargs['node_ip']), basestring):
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a string value for "node_ip"')
    #             return HttpErrorResponse("%s" % ex)
    #         node_ip = kwargs.pop('node_ip')
    #         if len(node_ip) <= 0:
    #             ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                                   detail='Expected a string value for "node_ip"')
    #             return HttpErrorResponse("%s" % ex)

    #     if len(kwargs) != 0:
    #         ex = ManagerException(ManagerException.E_ARGS_UNEXPECTED,
    #                               kwargs.keys())
    #         return HttpErrorResponse("%s" % ex)

    #     if config.proxy_count - proxy < 1:
    #         ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                               detail='Not enough proxy nodes  will be left')
    #         return HttpErrorResponse("%s" % ex)

    #     if config.web_count - web < 1 and config.proxy_count - proxy > 1:
    #         ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                               detail='Not enough web nodes will be left')
    #         return HttpErrorResponse("%s" % ex)

    #     if config.web_count - web < 0:
    #         ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                               detail='Cannot remove_nodes that many web nodes')
    #         return HttpErrorResponse("%s" % ex)

    #     if config.backend_count - backend < 1 and config.proxy_count - proxy > 1:
    #         ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                               detail='Not enough backend nodes will be left')
    #         return HttpErrorResponse("%s" % ex)

    #     if config.backend_count - backend < 0:
    #         ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                               detail='Cannot remove_nodes that many backend nodes')
    #         return HttpErrorResponse("%s" % ex)

    #     #state = self.state_get()
    #     # FIXME: Problem with the states
    #     #  if state != self.S_RUNNING:
    #     # return
    #     # HttpErrorResponse(ManagerException(ManagerException.E_STATE_ERROR).message)

    #     self.state_set(
    #         self.S_ADAPTING, msg='Going to remove_nodes proxy=%d, web=%d, backend=%d' %
    #         (proxy, web, backend))
    #     Thread(target=self.do_remove_nodes, args=[
    #            config, proxy, web, backend, node_ip]).start()
    #     return HttpJsonResponse()

    # def do_remove_nodes(self, config, proxy, web, backend, node_ip=None):
    #     packBackend = False
    #     packWeb = False
    #     packingNode = None

    #     backendNodesKill = []
    #     webNodesKill = []
    #     proxyNodesKill = []

    #     if web > 0:
    #         if node_ip is not None:
    #             for serviceNode in config.getWebServiceNodes():
    #                 if(serviceNode.ip == node_ip):
    #                     webNodesKill.append(serviceNode)
    #         else:
    #             webNodesKill += config.getWebServiceNodes()[-web:]
    #         if config.web_count - web == 0:
    #             packWeb = True

    #     if backend > 0:
    #         if node_ip is not None:
    #             for serviceNode in config.getBackendServiceNodes():
    #                 if(serviceNode.ip == node_ip):
    #                     backendNodesKill.append(serviceNode)
    #         else:
    #             backendNodesKill += config.getBackendServiceNodes()[-backend:]
    #         if config.backend_count - backend == 0:
    #             packBackend = True

    #     if proxy > 0:
    #         proxyNodesKill += config.getProxyServiceNodes()[-proxy:]

    #     packingNode = config.getProxyServiceNodes()[0]
    #     for i in webNodesKill:
    #         i.isRunningWeb = False
    #     for i in backendNodesKill:
    #         i.isRunningBackend = False
    #     for i in proxyNodesKill:
    #         i.isRunningProxy = False
    #     if packBackend:
    #         packingNode.isRunningBackend = True
    #     if packWeb:
    #         packingNode.isRunningWeb = True

    #     config.update_mappings()
    #     self.logger.info("Remove_nodes " + str(config.serviceNodes))
    #     # new nodes
    #     if packBackend:
    #         # NOTE: Code update is done after starting the backend
    #         #       because tomcat-create-instance complains if its
    #         #       directory exists when it is run and placing the
    #         #       code can only be done after creating the instance
    #         self._start_backend(config, [packingNode])
    #         self._update_code(config, [packingNode])
    #     if packWeb:
    #         self._start_web(config, [packingNode])

    #     if webNodesKill or backendNodesKill:
    #         self._update_proxy(config, [i for i in config.serviceNodes.values()
    #                                     if i.isRunningProxy and i not in proxyNodesKill])

    #     try:
    #         # remove_nodes nodes
    #         self._stop_backend(config, backendNodesKill)
    #         self._stop_web(config, webNodesKill)
    #         self._stop_proxy(config, proxyNodesKill)

    #         #   self.logger.info("Internal php: service nodes "+str(config.serviceNodes.values()))
    #         for i in config.serviceNodes.values():
    #             if not i.isRunningBackend and not i.isRunningWeb and not i.isRunningProxy:
    #                 del config.serviceNodes[i.id]
    #                 self.controller.delete_nodes([i])
    #                 #  self.logger.info("Internal php: Removing_node "+str(i.id))

    #         config.proxy_count = len(config.getProxyServiceNodes())
    #         config.backend_count = len(config.getBackendServiceNodes())
    #         if config.backend_count == 1 and config.getBackendServiceNodes()[0] in config.getProxyServiceNodes():
    #             config.backend_count = 0
    #         config.web_count = len(config.getWebServiceNodes())
    #         if config.web_count == 1 and config.getWebServiceNodes()[0] in config.getProxyServiceNodes():
    #             config.web_count = 0

    #         #  config.update_mappings()
    #         self.logger.info("Remove_nodes " + str(config.serviceNodes))

    #     except Exception:
    #         self.logger.critical('Error when trying to remove ')

    #     self._configuration_set(config)
    #     self.state_set(self.S_RUNNING)

    @expose('POST')
    def update_nodes_weight(self, kwargs):
        exp_params = [('web', is_dict),
                      ('backend', is_dict)]
        try:
            web_weights, backend_weights = check_arguments(exp_params, kwargs)
            self.check_state([self.S_RUNNING])
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.logger.debug('Received request to update nodes weight...')

        config = self._configuration_get()

        for web_id in web_weights:
            if web_id not in config.serviceNodes:
                ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                      detail='The web node ID does not exist')
                return HttpErrorResponse("%s" % ex)
            self.logger.debug('Updating web weight for node: %s to: %s ' %
                              (str(web_id), str(web_weights[web_id])))
            config.serviceNodes[web_id].weightWeb = int(web_weights[web_id])

        for backend_id in backend_weights:
            if backend_id not in config.serviceNodes:
                ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                      detail='The backend node ID does not exist')
                return HttpErrorResponse("%s" % ex)
            self.logger.debug('Updating backend weight for node: %s to: %s ' %
                              (str(backend_id), str(backend_weights[backend_id])))
            config.serviceNodes[backend_id].weightBackend = int(
                backend_weights[backend_id])

        self.logger.debug("Result of updating node weights: %s" %
                          str(config.serviceNodes))

        for web_id in web_weights:
            if web_id not in config.serviceNodes:
                ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                      detail='The web node ID does not exist')
                return HttpErrorResponse("%s" % ex)
            config.serviceNodes[web_id].webWeight = int(web_weights[web_id])

        config.update_mappings()
        self._update_proxy(config, [i for i in config.serviceNodes.values()
                                    if i.isRunningProxy])
        self._configuration_set(config)

        return HttpJsonResponse()

    @expose('GET')
    def list_nodes(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        try:
            self.check_state([self.S_RUNNING, self.S_ADAPTING])
        except:
            return HttpJsonResponse({})

        config = self._configuration_get()
        return HttpJsonResponse({
            'proxy': [serviceNode.id for serviceNode in config.getProxyServiceNodes()],
            'web': [serviceNode.id for serviceNode in config.getWebServiceNodes()],
            'backend': [serviceNode.id for serviceNode in config.getBackendServiceNodes()]
        })

    @expose('GET')
    def get_node_info(self, kwargs):
        config = self._configuration_get()
        exp_params = [('serviceNodeId', is_in_list(config.serviceNodes))]
        try:
            serviceNodeId = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        serviceNode = config.serviceNodes[serviceNodeId]
        return HttpJsonResponse({
            'serviceNode': {'id': serviceNode.id,
                            'ip': serviceNode.ip,
                            'vmid': serviceNode.vmid,
                            'cloud': serviceNode.cloud_name,
                            'isRunningProxy': serviceNode.isRunningProxy,
                            'isRunningWeb': serviceNode.isRunningWeb,
                            'isRunningBackend': serviceNode.isRunningBackend,
                            'weightWeb': serviceNode.weightWeb,
                            'weightBackend': serviceNode.weightBackend
                            }
        })

    @expose('POST')
    def migrate_nodes(self, kwargs):
        """
        Migrate nodes of this service from a cloud to another.

        Parameters
            migration_plan : list
                Description of migration: list of mappings with the following
                keys:
                    * 'from_cloud': cloud name
                    * 'vmid': a VM identifier
                    * 'to_cloud': cloud name
                For examples:
                    * migration_plan=[{'from_cloud': 'mycloud',
                                       'vmid': '2',
                                       'to_cloud': 'mycloud2'}]
                    * migration_plan=[{'from_cloud': 'mycloud2',
                                       'vmid': '42',
                                       'to_cloud': 'mycloud1'},
                                      {'from_cloud': 'mycloud2',
                                       'vmid': '43',
                                       'to_cloud': 'mycloud1'}]
            delay : int
                time in seconds to delay the removal of the old nodes.
                Optional with 0 as default.
                0 means "remove the old nodes as soon as the new nodes are up",
                60 means "remove the old nodes after 60 seconds after the new nodes
                are up". Useful to keep the old node active while the DNS and its
                caches that still have the IP address of the old node are updated
                to the IP address of the new node.

        Note
            the new node on the destination cloud will use the default VM
            instance type. For example, migrating an Amazon EC2 "t2.medium" to a
            private OpenNebula cloud, will create a VM in the OpenNebula cloud
            with default instance type which can be "small" for example.
        """
        try:
            exp_keys = ['from_cloud', 'vmid', 'to_cloud']
            exp_params = [('migration_plan', is_list_dict2(exp_keys)),
                          ('delay', is_pos_nul_int, 0)]
            migration_plan, delay = check_arguments(exp_params, kwargs)
            migration_plan = self._check_migrate_args(migration_plan)
            self.check_state([self.S_RUNNING])
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.state_set(self.S_ADAPTING, msg='Going to migrate nodes %s' % migration_plan)
        Thread(target=self._do_migrate_nodes, args=[migration_plan, delay]).start()
        return HttpJsonResponse()

    def _check_migrate_args(self, migration_plan):
        """Check that given cloud names and VM identifiers exist."""
        checked_migration_plan = []
        config = self._configuration_get()
        for migr in migration_plan:
            serv_nodes = [serv_node for serv_node in config.serviceNodes.values()
                          if serv_node.cloud_name == migr['from_cloud']
                          and serv_node.vmid == migr['vmid']]
            if len(serv_nodes) == 0:
                raise Exception("Unknown node from cloud %s with VM identifier %s"
                                % (migr['from_cloud'], migr['vmid']))
            if len(serv_nodes) > 1:
                raise Exception("Internal error: found %s nodes from cloud %s with VM identifier %s!"
                                % (len(serv_nodes), migr['from_cloud'], migr['vmid']))
            to_cloud = self._init_cloud(migr['to_cloud'])
            checked_migration_plan.append({'node': serv_nodes[0], 'to_cloud': to_cloud})
        return checked_migration_plan

    def _do_migrate_nodes(self, migration_plan, delay):
        self.logger.info("Migration: starting with plan %s and delay %s."
                         % (migration_plan, delay))
        config = self._configuration_get()
        new_nodes = {}
        added_new_nodes = []
        try:
            # (1) create all new nodes on each destination cloud
            # TODO: make it parallel
            clouds = [migr['to_cloud'] for migr in migration_plan]
            # TODO: use collections.Counter with Python 2.7 instead
            new_vm_nb = collections.defaultdict(int)
            for cloud in clouds:
                new_vm_nb[cloud] += 1
            for cloud, count in new_vm_nb.iteritems():
                new_nodes[cloud] = self.controller.create_nodes(count,
                                                                client.check_agent_process,
                                                                self.AGENT_PORT,
                                                                cloud)
            # (2) configure new nodes according the initial corresponding node configuration
            for migr in migration_plan:
                src_node = migr['node']
                dest_node = new_nodes[migr['to_cloud']].pop()
                added_new_nodes.append(dest_node)
                if src_node.isRunningProxy:
                    self._start_proxy(config, [dest_node])
                if src_node.isRunningWeb:
                    self._start_web(config, [dest_node])
                if src_node.isRunningBackend:
                    self._start_backend(config, [dest_node])
                if config.currentCodeVersion is not None:
                    self._update_code(config, [dest_node])
                config.serviceNodes[dest_node.id] = \
                    WebServiceNode(dest_node,
                                   weightWeb=src_node.weightWeb,
                                   weightBackend=src_node.weightBackend,
                                   runProxy=src_node.isRunningProxy,
                                   runWeb=src_node.isRunningWeb,
                                   runBackend=src_node.isRunningBackend)
                self._update_proxy(config,
                                   [node for node in config.serviceNodes.values()
                                    if node.isRunningProxy])
        except Exception, ex:
            self.logger.exception('Could not start nodes: %s. Rolled back.' % ex)
            # error happened: rolling back...
            rm_nodes = reduce(lambda acc, ele: acc + ele,
                              new_nodes.values(), [])
            rm_nodes.extend(added_new_nodes)
            self.controller.delete_nodes(rm_nodes)
            for node in rm_nodes:
                if rm_nodes.id in config.serviceNodes:
                    del config.serviceNodes[node.id]
            raise ex
        finally:
            config.update_mappings()
            config.proxy_count = len(config.getProxyServiceNodes())
            config.backend_count = len(config.getBackendServiceNodes())
            if config.backend_count == 1 and config.getBackendServiceNodes()[0] in config.getProxyServiceNodes():
                config.backend_count = 0
            config.web_count = len(config.getWebServiceNodes())
            if config.web_count == 1 and config.getWebServiceNodes()[0] in config.getProxyServiceNodes():
                config.web_count = 0
            self.state_set(self.S_RUNNING)

        self._configuration_set(config)
        self.logger.debug("Migration: new nodes %s created and"
                          " configured successfully." % (new_nodes))

        # New nodes successfully created
        # Now scheduling the removing of old nodes
        old_nodes = [migr['node'] for migr in migration_plan]
        if delay == 0:
            self.logger.debug("Migration: removing immediately"
                              " the old nodes: %s." % old_nodes)
            self._do_migrate_finalize(old_nodes)
        else:
            self.logger.debug("Migration: setting a timer to remove"
                              " the old nodes %s after % seconds."
                              % (old_nodes, delay))
            self._start_timer(delay, self._do_migrate_finalize, old_nodes)
            self.state_set(self.S_RUNNING)

    def _do_migrate_finalize(self, old_nodes):
        self.state_set(self.S_ADAPTING)

        config = self._configuration_get()
        for node in old_nodes:
            webserv_node = config.serviceNodes[node.id]
            if webserv_node.isRunningProxy:
                self._stop_proxy(config, [webserv_node])
            if webserv_node.isRunningWeb:
                self._stop_web(config, [webserv_node])
            if webserv_node.isRunningBackend:
                self._stop_backend(config, [webserv_node])
            del config.serviceNodes[node.id]
            self.controller.delete_nodes([node])

        config.proxy_count = len(config.getProxyServiceNodes())
        config.backend_count = len(config.getBackendServiceNodes())
        if config.backend_count == 1 and config.getBackendServiceNodes()[0] in config.getProxyServiceNodes():
            config.backend_count = 0
        config.web_count = len(config.getWebServiceNodes())
        if config.web_count == 1 and config.getWebServiceNodes()[0] in config.getProxyServiceNodes():
            config.web_count = 0

        self._configuration_set(config)
        self.state_set(self.S_RUNNING)
        self.logger.info("Migration: old nodes %s have been removed."
                         " END of migration." % old_nodes)

    def _start_timer(self, delay, callback, nodes):
        timer = Timer(delay, callback, args=[nodes])
        timer.start()

    @expose('GET')
    def list_authorized_keys(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({'authorizedKeys': git.get_authorized_keys()})

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
    def download_code_version(self, kwargs):
        config = self._configuration_get()
        exp_params = [('codeVersionId', is_in_list(config.codeVersions))]
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
        return HttpFileDownloadResponse(config.codeVersions[codeVersionId].filename, filename)

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
            codeVersionId, os.path.basename(code.filename), archive_get_type(name), description=description)
        self._configuration_set(config)
        return HttpJsonResponse({'codeVersionId': os.path.basename(codeVersionId)})

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

    @expose('GET')
    def get_service_performance(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({
            'request_rate': 0,
            'error_rate': 0,
            'throughput': 0,
            'response_time': 0,
        })

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

    # @expose('GET')
    # def getSummerSchool(self, kwargs):
    #     pac = self.memcache.get_multi(
    #         [self.DEPLOYMENT_STATE, self.CONFIG, 'adapting_count', 'nodes_additional'])
    #     ret = [pac[self.DEPLOYMENT_STATE], len(pac[self.CONFIG].serviceNodes)]
    #     if 'adapting_count' in pac:
    #         ret += [pac['adapting_count']]
    #     else:
    #         ret += [0]
    #     nodes = [i.id for i in pac[self.CONFIG].serviceNodes.values()]
    #     if 'nodes_additional' in pac:
    #         nodes += pac['nodes_additional']
    #     ret += [str(nodes)]
    #     return ret

    # def upload_script(self, kwargs, filename):
    #     """Write the file uploaded in kwargs['script'] to filesystem.

    #     Return the script absoulte path on success, HttpErrorResponse on
    #     failure.
    #     """
    #     self.logger.debug("upload_script: called with filename=%s" % filename)

    #     # Check if the required argument 'script' is present
    #     if 'script' not in kwargs:
    #         ex = ManagerException(ManagerException.E_ARGS_MISSING, 'script')
    #         return HttpErrorResponse("%s" % ex)

    #     script = kwargs.pop('script')

    #     # Check if any trailing parameter has been submitted
    #     if len(kwargs) != 0:
    #         ex = ManagerException(ManagerException.E_ARGS_UNEXPECTED,
    #                               kwargs.keys())
    #         return HttpErrorResponse("%s" % ex)

    #     # Script has to be a FileUploadField
    #     if not isinstance(script, FileUploadField):
    #         ex = ManagerException(ManagerException.E_ARGS_INVALID,
    #                               detail='script should be a file')
    #         return HttpErrorResponse("%s" % ex)

    #     basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
    #     fullpath = os.path.join(basedir, filename)

    #     # Write the uploaded script to filesystem
    #     open(fullpath, 'w').write(script.file.read())

    #     self.logger.debug("upload_script: script uploaded successfully to '%s'"
    #                       % fullpath)

    #     # Return the script absolute path
    #     return fullpath

    # @expose('UPLOAD')
    # def upload_startup_script(self, kwargs):
    #     ret = self.upload_script(kwargs, 'startup.sh')

    #     if type(ret) is HttpErrorResponse:
    #         # Something went wrong. Return the error
    #         return ret

    #     # (genc): why rebuilding the context?
    #     # Rebuild context script
    #     # self.controller.generate_context("web")

    #     # All is good. Return the filename of the uploaded script
    #     return HttpJsonResponse({'filename': ret})

    # @expose('GET')
    # def get_startup_script(self, kwargs):
    #     """Return contents of the currently defined startup script, if any"""
    #     basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
    #     fullpath = os.path.join(basedir, 'startup.sh')

    #     try:
    #         return HttpJsonResponse(open(fullpath).read())
    #     except IOError:
    #         return HttpErrorResponse('No startup script')
