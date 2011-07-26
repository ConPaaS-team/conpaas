'''
Created on Jul 11, 2011

@author: ielhelw
'''

from threading import Thread
from xml.dom import minidom
from tempfile import mkdtemp
from shutil import rmtree
import zipfile, tempfile, stat, os.path

from conpaas.web.manager.config import CodeVersion, JavaServiceConfiguration
from conpaas.web.agent import client
from conpaas.web.misc import archive_open, archive_get_members
from conpaas.web.http import HttpErrorResponse, HttpJsonResponse

from . import InternalsBase, ManagerException

class JavaInternal(InternalsBase):
  
  def __init__(self, memcache_in, iaas_in, code_repo_in, logfile_in, reset_config):
    InternalsBase.__init__(self, memcache_in, iaas_in, code_repo_in, logfile_in)
    self.exposed_functions['GET']['get_service_info'] = self.get_service_info
    self.exposed_functions['GET']['get_configuration'] = self.get_configuration
    self.exposed_functions['POST']['update_java_configuration'] = self.update_java_configuration
    if reset_config:
      self._create_initial_configuration()
  
  def _update_code(self, config, nodes):
    for serviceNode in nodes:
      try:
        if serviceNode.isRunningBackend:  ## UPLOAD TOMCAT CODE TO TOMCAT
          client.updateTomcatCode(serviceNode.ip, 5555, config.currentCodeVersion, config.codeVersions[config.currentCodeVersion].type, os.path.join(self.code_repo, config.currentCodeVersion))
        if serviceNode.isRunningProxy or serviceNode.isRunningWeb:
          client.updatePHPCode(serviceNode.ip, 5555, config.currentCodeVersion, config.codeVersions[config.currentCodeVersion].type, os.path.join(self.code_repo, config.currentCodeVersion))
      except client.AgentException:
        self.logger.exception('Failed to update code at node %s' % str(serviceNode))
        self._state_set(self.S_ERROR, msg='Failed to update code at node %s' % str(serviceNode))
        return
  
  def _start_backend(self, config, nodes):
    for serviceNode in nodes:
      try:
        client.createTomcat(serviceNode.ip, 5555, config.backend_config.port)
      except client.AgentException:
          self.logger.exception('Failed to start Tomcat at node %s' % str(serviceNode))
          self._state_set(self.S_ERROR, msg='Failed to start Tomcat at node %s' % str(serviceNode))
          return
  
  def _stop_backend(self, config, nodes):
    for serviceNode in nodes:
      try: client.stopTomcat(serviceNode.ip, 5555)
      except client.AgentException:
          self.logger.exception('Failed to stop Tomcat at node %s' % str(serviceNode))
          self._state_set(self.S_ERROR, msg='Failed to stop Tomcat at node %s' % str(serviceNode))
          return
  
  def _start_web(self, config, nodes):
    servlets_current = self._get_servlet_urls(config.currentCodeVersion)
    kwargs = {}
    if config.prevCodeVersion and config.prevCodeVersion != config.currentCodeVersion:
      kwargs['codeOld'] = config.prevCodeVersion
      kwargs['servletsOld'] = self._get_servlet_urls(config.prevCodeVersion)
    for serviceNode in nodes:
      try:
        client.createTomcatWebServer(serviceNode.ip, 5555,
                                     config.web_config.doc_root,
                                     config.web_config.port,
                                     config.web_config.backends,
                                     config.currentCodeVersion,
                                     servlets_current,
                                     **kwargs)
      except client.AgentException:
          self.logger.exception('Failed to start web at node %s' % str(serviceNode))
          self._state_set(self.S_ERROR, msg='Failed to start web at node %s' % str(serviceNode))
          return
  
  def _update_web(self, config, nodes):
    servlets_current = self._get_servlet_urls(config.currentCodeVersion)
    kwargs = {}
    if config.prevCodeVersion and config.prevCodeVersion != config.currentCodeVersion:
      kwargs['codeOld'] = config.prevCodeVersion
      kwargs['servletsOld'] = self._get_servlet_urls(config.prevCodeVersion)
    for webNode in nodes:
        try: client.updateTomcatWebServer(webNode.ip, 5555,
                                          config.web_config.doc_root,
                                          config.web_config.port,
                                          config.web_config.backends,
                                          config.currentCodeVersion,
                                          servlets_current,
                                          **kwargs)
        except client.AgentException:
          self.logger.exception('Failed to update web at node %s' % str(webNode))
          self._state_set(self.S_ERROR, msg='Failed to update web at node %s' % str(webNode))
          return
  
  def _stop_web(self, config, nodes):
    for serviceNode in nodes:
      try: client.stopTomcatWebServer(serviceNode.ip, 5555)
      except client.AgentException:
          self.logger.exception('Failed to stop web at node %s' % str(serviceNode))
          self._state_set(self.S_ERROR, msg='Failed to stop web at node %s' % str(serviceNode))
          return
  
  def get_service_info(self, kwargs):
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    return HttpJsonResponse({'state': self._state_get(), 'type': 'JAVA'})
  
  def get_configuration(self, kwargs):
#    try: check_nofiles(kwargs)
#    except ManagerException as e: return {'opState': 'ERROR', 'error': e.message}
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    config = self._configuration_get()
    return HttpJsonResponse({'codeVersionId': config.currentCodeVersion})
  
  def update_java_configuration(self, kwargs):
#    try: check_nofiles(kwargs)
#    except ManagerException as e: return {'opState': 'ERROR', 'error': e.message}
    
    if 'codeVersionId' not in kwargs:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING, 'at least one of "codeVersionId"').message)
    codeVersionId = kwargs.pop('codeVersionId')
    config = self._configuration_get()
    
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    
    dstate = self._state_get()
    if dstate == self.S_INIT or dstate == self.S_STOPPED:
      if codeVersionId: config.currentCodeVersion = codeVersionId
      self._configuration_set(config)
    elif dstate == self.S_RUNNING:
      self._state_set(self.S_ADAPTING, msg='Updating configuration')
      Thread(target=self.do_update_configuration, args=[config, codeVersionId]).start()
    else:
      return HttpErrorResponse(ManagerException(ManagerException.E_STATE_ERROR).message)
    return HttpJsonResponse()
  
  def _get_servlet_urls(self, codeVersionId):
    arch = archive_open(os.path.join(self.code_repo, codeVersionId))
    filelist = archive_get_members(arch)
    ret = []
    if 'WEB-INF/web.xml' in filelist:
      tmp_dir = mkdtemp()
      arch.extract('WEB-INF/web.xml', path=tmp_dir)
      doc = minidom.parse(tmp_dir + '/WEB-INF/web.xml')
      mappers = doc.getElementsByTagName('servlet-mapping')
      for m in mappers:
        url = m.getElementsByTagName('url-pattern')[0].firstChild.wholeText
        ret.append(url)
      rmtree(tmp_dir, ignore_errors=True)
    return ret
  
  def do_update_configuration(self, config, codeVersionId):
    if codeVersionId != None:
      config.prevCodeVersion = config.currentCodeVersion
      config.currentCodeVersion = codeVersionId
      self._update_code(config, config.serviceNodes.values())
      self._update_web(config, config.getWebServiceNodes())
      self._update_proxy(config, config.getProxyServiceNodes())
    
    self._state_set(self.S_RUNNING)
    self._configuration_set(config)
  
  def _create_initial_configuration(self):
    config = JavaServiceConfiguration()
    config.backend_count = 0
    config.web_count = 1
    config.proxy_count = 0
    
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
    zfile = zipfile.ZipFile(os.path.join(self.code_repo,'code-default'), mode='w')
    zfile.write(path, 'index.html')
    zfile.close()
    os.remove(path)
    config.codeVersions['code-default'] = CodeVersion('code-default', 'code-default.war', 'zip', description='Initial version')
    config.currentCodeVersion = 'code-default'
    self._configuration_set(config)
    self._state_set(self.S_INIT)
