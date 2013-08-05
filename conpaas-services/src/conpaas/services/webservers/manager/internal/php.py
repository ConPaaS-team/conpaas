# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread
import re, tarfile, tempfile, stat, os.path

from conpaas.services.webservers.manager.config import CodeVersion, PHPServiceConfiguration
from conpaas.services.webservers.agent import client
from conpaas.core.https.server import HttpErrorResponse, HttpJsonResponse
from . import BasicWebserversManager, ManagerException
from conpaas.core.expose import expose

from conpaas.core import git
from conpaas.services.webservers.manager.autoscaling.scaler import ProvisioningManager 
from multiprocessing.pool import ThreadPool

class PHPManager(BasicWebserversManager):
  
    def __init__(self, config_parser, **kwargs):
      BasicWebserversManager.__init__(self, config_parser)
      if kwargs['reset_config']:
        self._create_initial_configuration()
      self._register_scalaris(kwargs['scalaris'])
      
      try:
          self.scaler = ProvisioningManager(config_parser)
      except Exception as ex:
          self.logger.exception('Failed to initialize the Provisioning Manager %s' % str(ex))
  
    def _update_code(self, config, nodes):
      for serviceNode in nodes:
        # Push the current code version via GIT if necessary
        if config.codeVersions[config.currentCodeVersion].type == 'git':
          _, err = git.git_push(git.DEFAULT_CODE_REPO, serviceNode.ip)
          if err:
            self.logger.debug('git-push to %s: %s' % (serviceNode.ip, err))
        
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
                'cdn': config.cdn,
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
                'cdn': config.cdn
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
  
    @expose('GET')
    def get_service_info(self, kwargs):
      if len(kwargs) != 0:
        return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      return HttpJsonResponse({'state': self._state_get(), 'type': 'PHP'})

    @expose('GET')
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
      return HttpJsonResponse({
              'codeVersionId': config.currentCodeVersion,
              'phpconf': phpconf,
              'cdn': config.cdn,
              'autoscaling':config.autoscaling
              })

    @expose('POST')
    def on_autoscaling(self, kwargs):
      self.logger.info('on_autoscaling entering')  
      try:
         self.autoscaling_threads = ThreadPool(processes=1)
         if isinstance(int(kwargs['cool_down']), int) and isinstance(int(kwargs['response_time']), int) and kwargs['strategy']:
            self.autoscaling_threads.apply_async(self.scaler.do_provisioning, (int(kwargs.pop('response_time')), int(kwargs.pop('cool_down')), kwargs.pop('strategy')))
            #self.logger.info('on_autoscaling passed %s' % str( int(kwargs.pop('response_time')) ) )
            config = self._configuration_get()
            config.autoscaling = True
            self._configuration_set(config)
         return HttpJsonResponse({'autoscaling': config.autoscaling})   
      except Exception as ex:
        self.logger.critical('Error when trying to start the autoscaling mechanism ')
        return HttpErrorResponse(str(ex)) 

    @expose('POST')
    def off_autoscaling(self, kwargs):
      self.logger.info('off_autoscaling entering')  
      try:
        self.autoscaling_threads.terminate()
        self.scaler.stop_provisioning()
        config = self._configuration_get()
        config.autoscaling = False
        self._configuration_set(config)
        
        self.logger.info('off_autoscaling done.')
        return HttpJsonResponse({'autoscaling': config.autoscaling})
      except Exception as ex:
        self.logger.critical('Error when trying to stop the autoscaling mechanism ')
        return HttpErrorResponse(str(ex)) 

    @expose('POST')
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
      config.cdn = False
      config.autoscaling = False
    
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

    @expose('POST')
    def cdn_enable(self, params):
        '''
        Enable/disable CDN offloading.
        The changes must be reflected on the load balancer a.k.a proxy
        '''
        try:
            enable = params['enable']
            if enable:
                cdn = params['address']
                self.logger.info('Enabling CDN hosted at "%s"' %(cdn))
            else:
                cdn = False
                self.logger.info('Disabling CDN')
            config = self._configuration_get()
            config.cdn = cdn
            self._update_proxy(config, config.getProxyServiceNodes())
            self._configuration_set(config)
            return HttpJsonResponse({'cdn': config.cdn})
        except Exception as e:
            self.logger.exception(e)
            return HttpErrorResponse(str(e))

