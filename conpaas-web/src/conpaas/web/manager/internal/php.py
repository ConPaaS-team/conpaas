'''
Copyright (C) 2010-2011 Contrail consortium.

This file is part of ConPaaS, an integrated runtime environment 
for elastic cloud applications.

ConPaaS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ConPaaS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.


Created on Jul 11, 2011

@author: ielhelw
'''

from threading import Thread
import re, tarfile, tempfile, stat, os.path

from conpaas.web.manager.config import CodeVersion, PHPServiceConfiguration
from conpaas.web.agent import client
from conpaas.web.http import HttpErrorResponse, HttpJsonResponse

from . import InternalsBase, ManagerException

class PHPInternal(InternalsBase):
  
  def __init__(self, memcache_in, iaas_in, code_repo_in, logfile_in, scalaris_addr, reset_config, **kwargs):
    InternalsBase.__init__(self, memcache_in, iaas_in, code_repo_in, logfile_in, **kwargs)
    self.exposed_functions['GET']['get_service_info'] = self.get_service_info
    self.exposed_functions['GET']['get_configuration'] = self.get_configuration
    self.exposed_functions['POST']['update_php_configuration'] = self.update_php_configuration
    if reset_config:
      self._create_initial_configuration()
    self._register_scalaris(scalaris_addr)
  
  def _update_code(self, config, nodes):
    for serviceNode in nodes:
      try:
        client.updatePHPCode(serviceNode.ip, 5555, config.currentCodeVersion, config.codeVersions[config.currentCodeVersion].type, os.path.join(self.code_repo, config.currentCodeVersion))
      except client.AgentException:
        self.logger.exception('Failed to update code at node %s' % str(serviceNode))
        self._state_set(self.S_ERROR, msg='Failed to update code at node %s' % str(serviceNode))
        raise
  
  def _start_proxy(self, config, nodes):
    kwargs = {
              'web_list': config.getWebTuples(),
              'fpm_list': config.getBackendTuples(),
              }
    
    for proxyNode in nodes:
      try:
        if config.currentCodeVersion != None:
          client.createHttpProxy(proxyNode.ip, 5555,
                                 config.proxy_config.port,
                                 config.currentCodeVersion,
                                 **kwargs)
      except client.AgentException:
          self.logger.exception('Failed to start proxy at node %s' % str(proxyNode))
          self._state_set(self.S_ERROR, msg='Failed to start proxy at node %s' % str(proxyNode))
          raise
  
  def _update_proxy(self, config, nodes):
    kwargs = {
              'web_list': config.getWebTuples(),
              'fpm_list': config.getBackendTuples(),
              }
    
    for proxyNode in nodes:
        try:
          if config.currentCodeVersion != None:
            client.updateHttpProxy(proxyNode.ip, 5555,
                                 config.proxy_config.port,
                                 config.currentCodeVersion,
                                 **kwargs)
        except client.AgentException:
          self.logger.exception('Failed to update proxy at node %s' % str(proxyNode))
          self._state_set(self.S_ERROR, msg='Failed to update proxy at node %s' % str(proxyNode))
          raise
  
  def _start_backend(self, config, nodes):
    for serviceNode in nodes:
      try:
        client.createPHP(serviceNode.ip, 5555, config.backend_config.port, config.backend_config.scalaris, config.backend_config.php_conf.conf)
      except client.AgentException:
        self.logger.exception('Failed to start php at node %s' % str(serviceNode))
        self._state_set(self.S_ERROR, msg='Failed to start php at node %s' % str(serviceNode))
        raise
  
  def _update_backend(self, config, nodes):
    for serviceNode in nodes:
      try: client.updatePHP(serviceNode.ip, 5555, config.backend_config.port, config.backend_config.scalaris, config.backend_config.php_conf.conf)
      except client.AgentException:
        self.logger.exception('Failed to update php at node %s' % str(serviceNode))
        self._state_set(self.S_ERROR, msg='Failed to update php at node %s' % str(serviceNode))
        raise
  
  def _stop_backend(self, config, nodes):
    for serviceNode in nodes:
      try: client.stopPHP(serviceNode.ip, 5555)
      except client.AgentException:
        self.logger.exception('Failed to stop php at node %s' % str(serviceNode))
        self._state_set(self.S_ERROR, msg='Failed to stop php at node %s' % str(serviceNode))
        raise
  
  def get_service_info(self, kwargs):
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    return HttpJsonResponse({'state': self._state_get(), 'type': 'PHP'})
  
  def get_configuration(self, kwargs):
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    config = self._configuration_get()
    phpconf = {}
    for key in config.backend_config.php_conf.defaults:
      if key in config.backend_config.php_conf.conf:
        phpconf[key] = config.backend_config.php_conf.conf[key]
      else:
        phpconf[key] = config.backend_config.php_conf.defaults[key]
    return HttpJsonResponse({'codeVersionId': config.currentCodeVersion, 'phpconf': phpconf})
  
  def update_php_configuration(self, kwargs):
    codeVersionId = None
    if 'codeVersionId' in kwargs:
      codeVersionId = kwargs.pop('codeVersionId')
    config = self._configuration_get()
    phpconf = {}
    if 'phpconf' in kwargs:
      phpconf = kwargs.pop('phpconf')
      for key in phpconf.keys():
        if key not in config.backend_config.php_conf.defaults:
          return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, 'phpconf attribute "%s"' % (str(key))).message)
        if not re.match(config.backend_config.php_conf.format[key], phpconf[key]):
          return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID).message)
    
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    
    if codeVersionId == None and  not phpconf:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING, 'at least one of "codeVersionId" or "phpconf"').message)
    
    if codeVersionId and codeVersionId not in config.codeVersions:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Invalid codeVersionId').message)
    
    dstate = self._state_get()
    if dstate == self.S_INIT or dstate == self.S_STOPPED:
      if codeVersionId: config.currentCodeVersion = codeVersionId
      for key in phpconf:
        config.backend_config.php_conf.conf[key] = phpconf[key]
      self._configuration_set(config)
    elif dstate == self.S_RUNNING:
      self._state_set(self.S_ADAPTING, msg='Updating configuration')
      Thread(target=self.do_update_configuration, args=[config, codeVersionId, phpconf]).start()
    else:
      return HttpErrorResponse(ManagerException(ManagerException.E_STATE_ERROR).message)
    return HttpJsonResponse()
  
  def do_update_configuration(self, config, codeVersionId, phpconf):
    if phpconf:
      for key in phpconf:
        config.backend_config.php_conf.conf[key] = phpconf[key]
      self._update_backend(config, config.getBackendServiceNodes())
    if codeVersionId != None:
      self.prevCodeVersion = config.currentCodeVersion
      config.currentCodeVersion = codeVersionId
      self._update_code(config, config.serviceNodes.values())
      self._update_web(config, config.getWebServiceNodes())
      self._update_proxy(config, config.getProxyServiceNodes())
    self._state_set(self.S_RUNNING)
    self._configuration_set(config)
  
  def _create_initial_configuration(self):
    print 'CREATING INIT CONFIG'
    config = PHPServiceConfiguration()
    config.backend_count = 0
    config.web_count = 0
    config.proxy_count = 1
    
    if not os.path.exists(self.code_repo):
      os.makedirs(self.code_repo)
    
    fileno, path = tempfile.mkstemp()
    fd = os.fdopen(fileno, 'w')
    fd.write('''<html>
  <head>
  <title>Welcome to ConPaaS!</title>
  </head>
  <body bgcolor="white" text="black">
  <center><h1>Welcome to ConPaaS!</h1></center>
  </body>
  </html>''')
    fd.close()
    os.chmod(path, stat.S_IRWXU | stat.S_IROTH | stat.S_IXOTH)
    
    if len(config.codeVersions) > 0: return
    tfile = tarfile.TarFile(name=os.path.join(self.code_repo,'code-default'), mode='w')
    tfile.add(path, 'index.html')
    tfile.close()
    os.remove(path)
    config.codeVersions['code-default'] = CodeVersion('code-default', 'code-default.tar', 'tar', description='Initial version')
    config.currentCodeVersion = 'code-default'
    self._configuration_set(config)
    self._state_set(self.S_INIT)
  
  def _register_scalaris(self, scalaris):
    config = self._configuration_get()
    config.backend_config.scalaris = scalaris
    self._configuration_set(config)

