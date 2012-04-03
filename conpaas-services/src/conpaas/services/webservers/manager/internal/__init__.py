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

from threading import Thread, Lock, Timer, Event
import memcache, tempfile, os, os.path, tarfile, time, stat, json, urlparse

from conpaas.core.log import create_logger
from conpaas.services.webservers.agent import client
from conpaas.services.webservers.manager.config import WebServiceNode, CodeVersion
from conpaas.services.webservers.misc import archive_open, archive_get_members, archive_close,\
  archive_get_type
from conpaas.core.http import HttpJsonResponse, HttpErrorResponse,\
                         HttpFileDownloadResponse, HttpRequest,\
                         FileUploadField, HttpError, _http_post
from conpaas.core.expose import expose
from conpaas.core.controller import Controller


class ManagerException(Exception):

    E_CONFIG_READ_FAILED = 0
    E_CONFIG_COMMIT_FAILED = 1
    E_ARGS_INVALID = 2
    E_ARGS_UNEXPECTED = 3
    E_ARGS_MISSING = 4
    E_IAAS_REQUEST_FAILED = 5
    E_STATE_ERROR = 6
    E_CODE_VERSION_ERROR = 7
    E_NOT_ENOUGH_CREDIT = 8
    E_UNKNOWN = 9

    E_STRINGS = [
      'Failed to read configuration',
      'Failed to commit configuration',
      'Invalid arguments',
      'Unexpected arguments %s', # 1 param (a list)
      'Missing argument "%s"', # 1 param
      'Failed to request resources from IAAS',
      'Cannot perform requested operation in current state',
      'No code version selected',
      'Not enough credits',
      'Unknown error',
    ]

    def __init__(self, code, *args, **kwargs):
      self.code = code
      self.args = args
      if 'detail' in kwargs:
        self.message = '%s DETAIL:%s' \
                       % ( (self.E_STRINGS[code] % args), str(kwargs['detail']))
      else:
        self.message = self.E_STRINGS[code] % args


class BasicWebserversManager(object):
  # memcache keys
  CONFIG = 'config'
  DEPLOYMENT_STATE = 'deployment_state'
  
  S_INIT = 'INIT'
  S_PROLOGUE = 'PROLOGUE'
  S_RUNNING = 'RUNNING'
  S_ADAPTING = 'ADAPTING'
  S_EPILOGUE = 'EPILOGUE'
  S_STOPPED = 'STOPPED'
  S_ERROR = 'ERROR'
  
  def __init__(self, config_parser):
    self.logger = create_logger(__name__)  
    self.controller = Controller(config_parser)
    self.controller.generate_context('web')
    self.memcache = memcache.Client([config_parser.get('manager', 'MEMCACHE_ADDR')])

    from conpaas.services.webservers.manager import config
    config.memcache = self.memcache

    self.code_repo = config_parser.get('manager', 'CODE_REPO') 
    self.logfile = config_parser.get('manager', 'LOG_FILE')
    self.state_log = []
    self.config_parser = config_parser
     
  def _state_get(self):
    return self.memcache.get(self.DEPLOYMENT_STATE)

  def _state_set(self, target_state, msg=''):
    self.memcache.set(self.DEPLOYMENT_STATE, target_state)
    self.state_log.append({'time': time.time(), 'state': target_state, 'reason': msg})
    self.logger.debug('STATE %s: %s' % (target_state, msg))
  
  def _configuration_get(self):
    return self.memcache.get(self.CONFIG)
  
  def _configuration_set(self, config):
    self.memcache.set(self.CONFIG, config)
  
  def _adapting_set_count(self, count):
    self.memcache.set('adapting_count', count)
  
  def _adapting_get_count(self):
    return self.memcache.get('adapting_count')
  
  def _stop_proxy(self, config, nodes):
    for serviceNode in nodes:
      try: client.stopHttpProxy(serviceNode.ip, 5555)
      except client.AgentException:
          self.logger.exception('Failed to stop proxy at node %s' % str(serviceNode))
          self._state_set(self.S_ERROR, msg='Failed to stop proxy at node %s' % str(serviceNode))
          raise

  def _start_web(self, config, nodes):
    if config.prevCodeVersion == None:
      code_versions = [config.currentCodeVersion]
    else:
      code_versions = [config.currentCodeVersion, config.prevCodeVersion]
    for serviceNode in nodes:
      try:
        client.createWebServer(serviceNode.ip, 5555,
                               config.web_config.port,
                               code_versions)
      except client.AgentException:
          self.logger.exception('Failed to start web at node %s' % str(serviceNode))
          self._state_set(self.S_ERROR, msg='Failed to start web at node %s' % str(serviceNode))
          raise
  
  def _update_web(self, config, nodes):
    if config.prevCodeVersion == None:
      code_versions = [config.currentCodeVersion]
    else:
      code_versions = [config.currentCodeVersion, config.prevCodeVersion]
    for webNode in nodes:
        try: client.updateWebServer(webNode.ip, 5555,
                                    config.web_config.port,
                                    code_versions)
        except client.AgentException:
          self.logger.exception('Failed to update web at node %s' % str(webNode))
          self._state_set(self.S_ERROR, msg='Failed to update web at node %s' % str(webNode))
          raise
  
  def _stop_web(self, config, nodes):
    for serviceNode in nodes:
      try: client.stopWebServer(serviceNode.ip, 5555)
      except client.AgentException:
          self.logger.exception('Failed to stop web at node %s' % str(serviceNode))
          self._state_set(self.S_ERROR, msg='Failed to stop web at node %s' % str(serviceNode))
          raise
  
  @expose('POST')
  def startup(self, kwargs):
    
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    config = self._configuration_get()
    
    dstate = self._state_get()
    if dstate != self.S_INIT and dstate != self.S_STOPPED:
      return HttpErrorResponse(ManagerException(ManagerException.E_STATE_ERROR).message)
    
    if config.proxy_count == 1 \
    and (config.web_count == 0 or config.backend_count == 0):# at least one is packed
      if config.web_count == 0 and config.backend_count == 0:# packed
        serviceNodeKwargs = [ {'runProxy':True, 'runWeb':True, 'runBackend':True} ]
      elif config.web_count == 0 and config.backend_count > 0:# web packed, backend separated
        serviceNodeKwargs = [ {'runBackend':True} for _ in range(config.backend_count) ]
        serviceNodeKwargs.append({'runProxy':True, 'runWeb':True})
      elif config.web_count > 0 and config.backend_count == 0:# proxy separated, backend packed
        serviceNodeKwargs = [ {'runWeb':True} for _ in range(config.web_count) ]
        serviceNodeKwargs.append({'runProxy':True, 'runBackend':True})
    else:
      if config.web_count < 1: config.web_count = 1 # have to have at least one web
      if config.backend_count < 1: config.backend_count = 1 # have to have at least one backend
      serviceNodeKwargs = [ {'runProxy':True} for _ in range(config.proxy_count) ]
      serviceNodeKwargs.extend([ {'runWeb':True} for _ in range(config.web_count) ])
      serviceNodeKwargs.extend([ {'runBackend':True} for _ in range(config.backend_count) ])
    
    #if not self._deduct_credit(len(serviceNodeKwargs)):
    #  return HttpErrorResponse(ManagerException(ManagerException.E_NOT_ENOUGH_CREDIT).message)
    
    self._state_set(self.S_PROLOGUE, msg='Starting up')
    Thread(target=self.do_startup, args=[config, serviceNodeKwargs]).start()
    return HttpJsonResponse({'state': self.S_PROLOGUE})
  
  @expose('POST')
  def shutdown(self, kwargs):
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    
    dstate = self._state_get()
    if dstate != self.S_RUNNING:
      return HttpErrorResponse(ManagerException(ManagerException.E_STATE_ERROR).message)
    
    config = self._configuration_get()
    self._state_set(self.S_EPILOGUE, msg='Shutting down')
    Thread(target=self.do_shutdown, args=[config]).start()
    return HttpJsonResponse({'state': self.S_EPILOGUE})
  
  def do_startup(self, config, serviceNodeKwargs):
    self.logger.debug('do_startup: Going to request %d new nodes' % len(serviceNodeKwargs))
    
    try:
      self._adapting_set_count(len(serviceNodeKwargs))
      node_instances = self.controller.create_nodes(len(serviceNodeKwargs),
                                                    client.checkAgentState, 5555)
    except:
      self.logger.exception('do_startup: Failed to request new nodes. Needed %d' % (len(serviceNodeKwargs)))
      self._state_set(self.S_STOPPED, msg='Failed to request new nodes')
      return
    finally:
      self._adapting_set_count(0)
    
    config.serviceNodes.clear()
    i = 0
    for kwargs in serviceNodeKwargs:
      config.serviceNodes[node_instances[i].vmid] = WebServiceNode(node_instances[i], **kwargs)
      i += 1
    config.update_mappings()
    
    # issue orders to agents to start PHP inside
    self._start_backend(config, config.getBackendServiceNodes())
    
    # stage the code files
    # NOTE: Code update is done after starting the backend
    #       because tomcat-create-instance complains if its
    #       directory exists when it is run and placing the
    #       code can only be done after creating the instance
    if config.currentCodeVersion != None:
      self._update_code(config, config.serviceNodes.values())
    
    # issue orders to agents to start web servers inside
    self._start_web(config, config.getWebServiceNodes())
    
    # issue orders to agents to start proxy inside
    self._start_proxy(config, config.getProxyServiceNodes())
    
    self._configuration_set(config) # update configuration
    self._state_set(self.S_RUNNING)
    self.memcache.set('nodes_additional', [])
  
  def do_shutdown(self, config):
    self._stop_proxy(config, config.getProxyServiceNodes())
    self._stop_web(config, config.getWebServiceNodes())
    self._stop_backend(config, config.getBackendServiceNodes())
    self.controller.delete_nodes(config.serviceNodes.values())
    config.serviceNodes = {}
    self._state_set(self.S_STOPPED)
    self._configuration_set(config)
  
  @expose('POST')
  def add_nodes(self, kwargs):
    config = self._configuration_get()
    dstate = self._state_get()
    if dstate != self.S_RUNNING:
      return HttpErrorResponse(ManagerException(ManagerException.E_STATE_ERROR).message)
    
    backend = 0
    web = 0
    proxy = 0
    if 'backend' in kwargs:
      if not isinstance(kwargs['backend'], int):
        return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected an integer value for "backend"').message)
      backend = int(kwargs.pop('backend'))
      if backend < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "backend"').message)
    if 'web' in kwargs:
      if not isinstance(kwargs['web'], int):
        return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected an integer value for "web"').message)
      web = int(kwargs.pop('web'))
      if web < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "web"').message)
    if 'proxy' in kwargs:
      if not isinstance(kwargs['proxy'], int):
        return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected an integer value for "proxy"').message)
      proxy = int(kwargs.pop('proxy'))
      if proxy < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "proxy"').message)
    if (backend + web + proxy) < 1:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING, ['backend', 'web', 'proxy'], detail='Need a positive value for at least one').message)
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    
    if (proxy + config.proxy_count) > 1 and ( (web + config.web_count) == 0 or (backend + config.backend_count) == 0 ):
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Cannot add more proxy servers without at least one "web" and one "backend"').message)
    
    self._state_set(self.S_ADAPTING, msg='Going to add proxy=%d, web=%d, backend=%d' % (proxy, web, backend))
    Thread(target=self.do_add_nodes, args=[config, proxy, web, backend]).start()
    return HttpJsonResponse()
  
  def do_add_nodes(self, config, proxy, web, backend):
    webNodesNew = []
    proxyNodesNew = []
    backendNodesNew = []
    
    webNodesKill = []
    backendNodesKill = []
    
    if backend > 0 and config.backend_count == 0:
      backendNodesKill.append(config.getBackendServiceNodes()[0])
    if web > 0 and config.web_count == 0:
      webNodesKill.append(config.getWebServiceNodes()[0])
    
    for _ in range(backend): backendNodesNew.append({'runBackend':True})
    for _ in range(web): webNodesNew.append({'runWeb':True})
    for _ in range(proxy): proxyNodesNew.append({'runProxy':True})
    
    for i in webNodesKill: i.isRunningWeb = False
    for i in backendNodesKill: i.isRunningBackend = False
    
    newNodes = []
    try:
      self._adapting_set_count(len(proxyNodesNew) + len(webNodesNew) + len(backendNodesNew))
      node_instances = self.controller.create_nodes(len(proxyNodesNew) + len(webNodesNew) + len(backendNodesNew),
                                                    client.checkAgentState, 5555)
    except:
      self.logger.exception('do_add_nodes: Failed to request new nodes. Needed %d' % (len(proxyNodesNew + webNodesNew + backendNodesNew)))
      self._state_set(self.S_RUNNING, msg='Failed to request new nodes. Reverting to old configuration')
      return
    finally:
      self._adapting_set_count(0)
    
    i = 0
    for kwargs in proxyNodesNew + webNodesNew + backendNodesNew:
      config.serviceNodes[node_instances[i].vmid] = WebServiceNode(node_instances[i], **kwargs)
      newNodes += [ config.serviceNodes[node_instances[i].vmid] ]
      i += 1
    config.update_mappings()
    
    # create new service nodes
    self._start_backend(config, [ node for node in newNodes if node.isRunningBackend ])
    # stage code files in all new VMs
    # NOTE: Code update is done after starting the backend
    #       because tomcat-create-instance complains if its
    #       directory exists when it is run and placing the
    #       code can only be done after creating the instance
    if config.currentCodeVersion != None:
      self._update_code(config, [ node for node in newNodes if node not in config.serviceNodes ])
    
    self._start_web(config, [ node for node in newNodes if node.isRunningWeb ])
    self._start_proxy(config, [ node for node in newNodes if node.isRunningProxy ])
    
    # update services
    if webNodesNew or backendNodesNew:
      self._update_proxy(config, [ i for i in config.serviceNodes.values() if i.isRunningProxy and i not in newNodes ])
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
    
    self._state_set(self.S_RUNNING)
    self._configuration_set(config)
    self.memcache.set('nodes_additional', [])
  
  @expose('POST')
  def remove_nodes(self, kwargs):
    config = self._configuration_get()
    backend = 0
    web = 0
    proxy = 0
    
    if 'backend' in kwargs:
      if not isinstance(kwargs['backend'], int):
        return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected an integer value for "backend"').message)
      backend = int(kwargs.pop('backend'))
      if backend < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "backend"').message)
    if 'web' in kwargs:
      if not isinstance(kwargs['web'], int):
        return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected an integer value for "web"').message)
      web = int(kwargs.pop('web'))
      if web < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "web"').message)
    if 'proxy' in kwargs:
      if not isinstance(kwargs['proxy'], int):
        return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected an integer value for "proxy"').message)
      proxy = int(kwargs.pop('proxy'))
      if proxy < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Expected a positive integer value for "proxy"').message)
    if (backend + web + proxy) < 1:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING, ['backend', 'web', 'proxy'], detail='Need a positive value for at least one').message)
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    
    if config.proxy_count - proxy < 1: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Not enough proxy nodes  will be left').message)
    
    if config.web_count - web < 1 and config.proxy_count - proxy > 1:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Not enough web nodes will be left').message)
    if config.web_count - web < 0: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Cannot remove_nodes that many web nodes').message)
    
    if config.backend_count - backend < 1 and config.proxy_count - proxy > 1:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Not enough backend nodes will be left').message)
    if config.backend_count - backend < 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Cannot remove_nodes that many backend nodes').message)
    
    dstate = self._state_get()
    if dstate != self.S_RUNNING:
      return HttpErrorResponse(ManagerException(ManagerException.E_STATE_ERROR).message)
    
    self._state_set(self.S_ADAPTING, msg='Going to remove_nodes proxy=%d, web=%d, backend=%d' %(proxy, web, backend))
    Thread(target=self.do_remove_nodes, args=[config, proxy, web, backend]).start()
    return HttpJsonResponse()
  
  def do_remove_nodes(self, config, proxy, web, backend):
    packBackend = False
    packWeb = False
    packingNode = None
    
    backendNodesKill = []
    webNodesKill = []
    proxyNodesKill = []
    
    if web > 0:
      webNodesKill += config.getWebServiceNodes()[-web:]
      if config.web_count - web == 0:
        packWeb = True
    
    if backend > 0:
      backendNodesKill += config.getBackendServiceNodes()[-backend:]
      if config.backend_count - backend == 0:
        packBackend = True
    
    if proxy > 0:
      proxyNodesKill += config.getProxyServiceNodes()[-proxy:]
    
    packingNode = config.getProxyServiceNodes()[0]
    for i in webNodesKill: i.isRunningWeb = False
    for i in backendNodesKill: i.isRunningBackend = False
    for i in proxyNodesKill: i.isRunningProxy = False
    if packBackend: packingNode.isRunningBackend = True
    if packWeb: packingNode.isRunningWeb = True
    
    config.update_mappings()
    
    # new nodes
    if packBackend:
      # NOTE: Code update is done after starting the backend
      #       because tomcat-create-instance complains if its
      #       directory exists when it is run and placing the
      #       code can only be done after creating the instance
      self._start_backend(config, [packingNode])
      self._update_code(config, [packingNode])
    if packWeb: self._start_web(config, [packingNode])
    
    if webNodesKill or backendNodesKill:
      self._update_proxy(config, [ i for i in config.serviceNodes.values() if i.isRunningProxy and i not in proxyNodesKill ])
    
    # remove_nodes nodes
    self._stop_backend(config, backendNodesKill)
    self._stop_web(config, webNodesKill)
    self._stop_proxy(config, proxyNodesKill)
    
    for i in config.serviceNodes.values():
      if not i.isRunningBackend and not i.isRunningWeb and not i.isRunningProxy:
        del config.serviceNodes[i.vmid]
        self.controller.delete_nodes([i])
    
    
    config.proxy_count = len(config.getProxyServiceNodes())
    config.backend_count = len(config.getBackendServiceNodes())
    if config.backend_count == 1 and config.getBackendServiceNodes()[0] in config.getProxyServiceNodes():
      config.backend_count = 0
    config.web_count = len(config.getWebServiceNodes())
    if config.web_count == 1 and config.getWebServiceNodes()[0] in config.getProxyServiceNodes():
      config.web_count = 0
    
    self._state_set(self.S_RUNNING)
    self._configuration_set(config)
  
  @expose('GET')
  def list_nodes(self, kwargs):
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    
    dstate = self._state_get()
    if dstate != self.S_RUNNING and dstate != self.S_ADAPTING:
      return HttpErrorResponse(ManagerException(ManagerException.E_STATE_ERROR).message)
    
    config = self._configuration_get()
    return HttpJsonResponse({
            'proxy': [ serviceNode.vmid for serviceNode in config.getProxyServiceNodes() ],
            'web': [ serviceNode.vmid for serviceNode in config.getWebServiceNodes() ],
            'backend': [ serviceNode.vmid for serviceNode in config.getBackendServiceNodes() ]
            })
  
  @expose('GET')
  def get_node_info(self, kwargs):
    if 'serviceNodeId' not in kwargs: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING, 'serviceNodeId').message)
    serviceNodeId = kwargs.pop('serviceNodeId')
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    
    config = self._configuration_get()
    if serviceNodeId not in config.serviceNodes: return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Invalid "serviceNodeId"').message)
    serviceNode = config.serviceNodes[serviceNodeId]
    return HttpJsonResponse({
            'serviceNode': {
                            'id': serviceNode.vmid,
                            'ip': serviceNode.ip,
                            'isRunningProxy': serviceNode.isRunningProxy,
                            'isRunningWeb': serviceNode.isRunningWeb,
                            'isRunningBackend': serviceNode.isRunningBackend,
                            }
            })

  @expose('GET')  
  def list_code_versions(self, kwargs):
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    config = self._configuration_get()
    versions = []
    for version in config.codeVersions.values():
      item = {'codeVersionId': version.id, 'filename': version.filename, 'description': version.description, 'time': version.timestamp}
      if version.id == config.currentCodeVersion: item['current'] = True
      versions.append(item)
    versions.sort(cmp=(lambda x, y: cmp(x['time'], y['time'])), reverse=True)
    return HttpJsonResponse({'codeVersions': versions})
  
  @expose('GET')
  def download_code_version(self, kwargs):
    if 'codeVersionId' not in kwargs:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING, 'codeVersionId').message)
    if isinstance(kwargs['codeVersionId'], dict):
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='codeVersionId should be a string').message)
    codeVersion = kwargs.pop('codeVersionId')
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    
    config = self._configuration_get()
    
    if codeVersion not in config.codeVersions:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Invalid codeVersionId').message)
    
    filename = os.path.abspath(os.path.join(self.code_repo, codeVersion))
    if not filename.startswith(self.code_repo + '/') or not os.path.exists(filename):
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Invalid codeVersionId').message)
    return HttpFileDownloadResponse(config.codeVersions[codeVersion].filename, filename)
  
  @expose('UPLOAD')
  def upload_code_version(self, kwargs):
    if 'code' not in kwargs:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING, 'code').message)
    code = kwargs.pop('code')
    if 'description' in kwargs: description = kwargs.pop('description')
    else: description = ''
    
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    if not isinstance(code, FileUploadField):
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='codeVersionId should be a file').message)
    
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
    if arch == None:
      os.remove(name)
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Invalid archive format').message)
    
    for fname in archive_get_members(arch):
      if fname.startswith('/') or fname.startswith('..'):
        archive_close(arch)
        os.remove(name)
        return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Absolute file names are not allowed in archive members').message)
    archive_close(arch)
    config.codeVersions[codeVersionId] = CodeVersion(codeVersionId, os.path.basename(code.filename), archive_get_type(name), description=description)
    self._configuration_set(config)
    return HttpJsonResponse({'codeVersionId': os.path.basename(codeVersionId)})
  
  @expose('GET')
  def get_service_performance(self, kwargs):
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    return HttpJsonResponse({
            'request_rate': 0,
            'error_rate': 0,
            'throughput': 0,
            'response_time': 0,
            })
  
  @expose('GET')
  def getLog(self, kwargs):
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    try:
      fd = open(self.logfile)
      ret = ''
      s = fd.read()
      while s != '':
        ret += s
        s = fd.read()
      if s != '':
        ret += s
      return HttpJsonResponse({'log': ret})
    except:
      return HttpErrorResponse('Failed to read log')
  
  @expose('GET')
  def get_service_history(self, kwargs):
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    return HttpJsonResponse({'state_log': self.state_log})
  
  @expose('GET')
  def getSummerSchool(self, kwargs):
    pac = self.memcache.get_multi([self.DEPLOYMENT_STATE, self.CONFIG, 'adapting_count', 'nodes_additional'])
    ret = [pac[self.DEPLOYMENT_STATE], len(pac[self.CONFIG].serviceNodes)]
    if 'adapting_count' in pac: ret += [pac['adapting_count']]
    else: ret += [0]
    nodes = [ i.vmid for i in pac[self.CONFIG].serviceNodes.values() ]
    if 'nodes_additional' in pac: nodes += pac['nodes_additional']
    ret += [str(nodes)]
    return ret
