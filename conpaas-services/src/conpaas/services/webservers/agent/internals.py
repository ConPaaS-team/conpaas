'''
Copyright (c) 2010-2013, Contrail consortium.
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


Created on Mar 7, 2011

@author: ielhelw
'''

from os.path import exists, devnull, join
from subprocess import Popen
from os import remove, makedirs
from shutil import rmtree
from threading import Lock
import pickle, zipfile, tarfile

from conpaas.core.agent import BaseAgent, AgentException
from conpaas.services.webservers.agent import role 

from conpaas.core.https.server import HttpErrorResponse, HttpJsonResponse, FileUploadField
from conpaas.core.expose import expose
from conpaas.core import git

class WebServersAgent(BaseAgent):

    def __init__(self, config_parser):
      BaseAgent.__init__(self, config_parser)

      role.init(config_parser)

      self.VAR_TMP = config_parser.get('agent', 'VAR_TMP')
      self.VAR_CACHE = config_parser.get('agent', 'VAR_CACHE')
      self.VAR_RUN = config_parser.get('agent', 'VAR_RUN')

      self.webserver_file = join(self.VAR_TMP, 'web-php.pickle')
      self.webservertomcat_file = join(self.VAR_TMP, 'web-tomcat.pickle')
      self.httpproxy_file = join(self.VAR_TMP, 'proxy.pickle')
      self.php_file = join(self.VAR_TMP, 'php.pickle')
      self.tomcat_file = join(self.VAR_TMP, 'tomcat.pickle')

      self.web_lock = Lock()
      self.webservertomcat_lock = Lock()
      self.httpproxy_lock = Lock()
      self.php_lock = Lock()
      self.tomcat_lock = Lock()

      self.WebServer = role.NginxStatic
      self.HttpProxy = role.NginxProxy

      self.ganglia.add_modules(( 'nginx_mon', 'nginx_proxy_mon', 
        'php_fpm_mon' ))
 
    def _get(self, get_params, class_file, pClass):
      if not exists(class_file):
        return HttpErrorResponse(AgentException(
            AgentException.E_CONFIG_NOT_EXIST).message)
      try:
        fd = open(class_file, 'r')
        p = pickle.load(fd)
        fd.close()
      except Exception as e:
        ex = AgentException(
            AgentException.E_CONFIG_READ_FAILED, 
                pClass.__name__, class_file, detail=e)
        self.logger.exception(ex.message)
        return HttpErrorResponse(ex.message)
      else:
        return HttpJsonResponse({'return': p.status()})

    def _create(self, post_params, class_file, pClass):
      if exists(class_file):
        return HttpErrorResponse(AgentException(
            AgentException.E_CONFIG_EXISTS).message)
      try:
        if type(post_params) != dict: raise TypeError()
        p = pClass(**post_params)
      except (ValueError, TypeError) as e:
        ex = AgentException(AgentException.E_ARGS_INVALID, detail=str(e))
        return HttpErrorResponse(ex.message)
      except Exception as e:
        ex = AgentException(AgentException.E_UNKNOWN, detail=e)
        self.logger.exception(e)
        return HttpErrorResponse(ex.message)
      else:
        try:
          fd = open(class_file, 'w')
          pickle.dump(p, fd)
          fd.close()
        except Exception as e:
          ex = AgentException(AgentException.E_CONFIG_COMMIT_FAILED, detail=e)
          self.logger.exception(ex.message)
          return HttpErrorResponse(ex.message)
        else:
          return HttpJsonResponse()

    def _update(self, post_params, class_file, pClass):
      try:
        if type(post_params) != dict: raise TypeError()
        fd = open(class_file, 'r')
        p = pickle.load(fd)
        fd.close()
        p.configure(**post_params)
        p.restart()
      except (ValueError, TypeError) as e:
          self.logger.exception(e)
          ex = AgentException(AgentException.E_ARGS_INVALID)
          return HttpErrorResponse(ex.message)
      except Exception as e:
          self.logger.exception(e)
          ex = AgentException(AgentException.E_UNKNOWN, detail=e)
          return HttpErrorResponse(ex.message)
      else:
          try:
              fd = open(class_file, 'w')
              pickle.dump(p, fd)
              fd.close()
          except Exception as e:
              self.logger.exception(ex.message)
              ex = AgentException(AgentException.E_CONFIG_COMMIT_FAILED, detail=e)
              return HttpErrorResponse(ex.message)
          else:
              return HttpJsonResponse()

    def _stop(self, get_params, class_file, pClass):
      if not exists(class_file):
        return HttpErrorResponse(AgentException(
            AgentException.E_CONFIG_NOT_EXIST).message)
      try:
        try:
          fd = open(class_file, 'r')
          p = pickle.load(fd)
          fd.close()
        except Exception as e:
          ex = AgentException(
            AgentException.E_CONFIG_READ_FAILED, detail=e)
          self.logger.exception(ex.message)
          return HttpErrorResponse(ex.message)
        p.stop()
        remove(class_file)
        return HttpJsonResponse()
      except Exception as e:
        ex = AgentException(AgentException.E_UNKNOWN, detail=e)
        self.logger.exception(e)
        return HttpErrorResponse(ex.message)

    def _webserver_get_params(self, kwargs):
      ret = {}
  
      if 'port' not in kwargs:
        raise AgentException(AgentException.E_ARGS_MISSING, 'port')
      if not isinstance(kwargs['port'], int):
        raise AgentException(AgentException.E_ARGS_INVALID, detail='Invalid "port" value')
      ret['port'] = int(kwargs.pop('port'))
  
      if 'code_versions' not in kwargs:
        raise AgentException(AgentException.E_ARGS_MISSING, 'code_versions')
      ret['code_versions'] = kwargs.pop('code_versions')
  
      if len(kwargs) != 0:
        raise AgentException(AgentException.E_ARGS_UNEXPECTED, kwargs.keys())
      return ret

    @expose('GET')
    def getWebServerState(self, kwargs):
      """GET state of WebServer"""
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      with web_lock:
        return _get(kwargs, self.webserver_file, self.WebServer)

    @expose('POST')
    def createWebServer(self, kwargs):
      """Create the WebServer"""
      try: kwargs = self._webserver_get_params(kwargs)
      except AgentException as e:
        return HttpErrorResponse(e.message)
      else:
        with self.web_lock:
          return self._create(kwargs, self.webserver_file, self.WebServer)

    @expose('POST')
    def updateWebServer(self, kwargs):
      """UPDATE the WebServer"""
      try: kwargs = self._webserver_get_params(kwargs)
      except AgentException as e:
        return HttpErrorResponse(e.message)
      else:
        with self.web_lock:
          return self._update(kwargs, self.webserver_file, self.WebServer)

    @expose('POST')
    def stopWebServer(self, kwargs):
      """KILL the WebServer"""
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      with self.web_lock:
        return self._stop(kwargs, self.webserver_file, self.WebServer)

    def _httpproxy_get_params(self, kwargs):
      ret = {}
      if 'port' not in kwargs:
        raise AgentException(AgentException.E_ARGS_MISSING, 'port')
      if not isinstance(kwargs['port'], int):
        raise AgentException(
            AgentException.E_ARGS_INVALID, detail='Invalid "port" value')
      ret['port'] = int(kwargs.pop('port'))
  
      if 'code_version' not in kwargs:
        raise AgentException(
            AgentException.E_ARGS_MISSING, 'code_version')
      ret['code_version'] = kwargs.pop('code_version')
  
      if 'web_list' in kwargs:
        web_list = kwargs.pop('web_list')
      else:
        web_list = []
      if len(web_list) == 0:
        raise AgentException(
            AgentException.E_ARGS_INVALID, detail='At least one web_list is required')
      ret['web_list'] = web_list
  
      if 'fpm_list' in kwargs:
        ret['fpm_list'] = kwargs.pop('fpm_list')
  
      if 'tomcat_list' in kwargs:
        ret['tomcat_list'] = kwargs.pop('tomcat_list')
        if 'tomcat_servlets' in kwargs:
          ret['tomcat_servlets'] = kwargs.pop('tomcat_servlets')

      ret['cdn'] = kwargs.get('cdn', None)
      return ret

    @expose('GET')
    def getHttpProxyState(self, kwargs):
      """GET state of HttpProxy"""
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      with self.httpproxy_lock:
        return self._get(kwargs, self.httpproxy_file, self.HttpProxy)

    @expose('POST')
    def createHttpProxy(self, kwargs):
      """Create the HttpProxy"""
      try: kwargs = self._httpproxy_get_params(kwargs)
      except AgentException as e:
        return HttpErrorResponse(e.message)
      else:
        with self.httpproxy_lock:
          return self._create(kwargs, self.httpproxy_file, self.HttpProxy)

    @expose('POST')
    def updateHttpProxy(self, kwargs):
      try:
          kwargs = self._httpproxy_get_params(kwargs)
          with self.httpproxy_lock:
              return self._update(kwargs, self.httpproxy_file, self.HttpProxy)
      except AgentException as e:
          self.logger.exception(e)
          return HttpErrorResponse(e.message)
      except Exception as e:
          self.logger.exception(e)
          return HttpErrorResponse(str(e))

    @expose('POST')
    def stopHttpProxy(self, kwargs):
      """KILL the HttpProxy"""
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      with self.httpproxy_lock:
        return self._stop(kwargs, self.httpproxy_file, self.HttpProxy)


    def _php_get_params(self, kwargs):
      ret = {}
      if 'port' not in kwargs:
        raise AgentException(AgentException.E_ARGS_MISSING, 'port')
      if not isinstance(kwargs['port'], int):
        raise AgentException(
            AgentException.E_ARGS_INVALID, detail='Invalid "port" value')
      ret['port'] = int(kwargs.pop('port'))
      if 'scalaris' not in kwargs:
        raise AgentException(AgentException.E_ARGS_MISSING, 'scalaris')
      ret['scalaris'] = kwargs.pop('scalaris')
      if 'configuration' not in kwargs:
        raise AgentException(AgentException.E_ARGS_MISSING, 'configuration')
      if not isinstance(kwargs['configuration'], dict):
        raise AgentException(
            AgentException.E_ARGS_INVALID, detail='invalid "configuration" object')
      ret['configuration'] = kwargs.pop('configuration')
  
      if len(kwargs) != 0:
        raise AgentException(AgentException.E_ARGS_UNEXPECTED, kwargs.keys())
      return ret

    @expose('GET')
    def getPHPState(self, kwargs):
      """GET state of PHPProcessManager"""
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      with self.php_lock:
        return self._get(kwargs, self.php_file, role.PHPProcessManager)

    @expose('POST')
    def createPHP(self, kwargs):
      """Create the PHPProcessManager"""
      try: kwargs = self._php_get_params(kwargs)
      except AgentException as e:
        return HttpErrorResponse(e.message)
      else:
        with self.php_lock:
          return self._create(kwargs, self.php_file, role.PHPProcessManager)

    @expose('POST')
    def updatePHP(self, kwargs):
      """UPDATE the PHPProcessManager"""
      try: kwargs = self._php_get_params(kwargs)
      except AgentException as e:
        return HttpErrorResponse(e.message)
      else:
        with self.php_lock:
          return self._update(kwargs, self.php_file, role.PHPProcessManager)

    @expose('POST')
    def stopPHP(self, kwargs):
      """KILL the PHPProcessManager"""
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      with self.php_lock:
        return self._stop(kwargs, self.php_file, role.PHPProcessManager)

    def fix_session_handlers(self, dir):
      session_dir = join(self.VAR_CACHE, 'www')
      cmd_path = join(session_dir, 'phpsession.sh')
      script_path = join(session_dir, 'phpsession.php')
      devnull_fd = open(devnull, 'w')
      proc = Popen([cmd_path, dir, script_path], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
      proc.wait()
      #if proc.wait() != 0:
      #  self.logger.exception('Failed to start the script to fix the session handlers')
      #  raise OSError('Failed to start the script to fix the session handlers')

    @expose('UPLOAD')
    def updatePHPCode(self, kwargs):

        if 'filetype' not in kwargs:
          return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_MISSING, 'filetype').message)
        filetype = kwargs.pop('filetype')
      
        if 'codeVersionId' not in kwargs:
          return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_MISSING, 'codeVersionId').message)
        codeVersionId = kwargs.pop('codeVersionId')

        if 'file' not in kwargs:
          return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_MISSING, 'file').message)
        file = kwargs.pop('file')

        if filetype != 'git' and not isinstance(file, FileUploadField):
          return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_INVALID, detail='"file" should be a file').message)

        if len(kwargs) != 0:
          return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        if filetype == 'zip': source = zipfile.ZipFile(file.file, 'r')
        elif filetype == 'tar': source = tarfile.open(fileobj=file.file)
        elif filetype == 'git': source = git.DEFAULT_CODE_REPO
        else: return HttpErrorResponse('Unknown archive type ' + str(filetype))
  
        if not exists(join(self.VAR_CACHE, 'www')):
          makedirs(join(self.VAR_CACHE, 'www'))
  
        target_dir = join(self.VAR_CACHE, 'www', codeVersionId)
        if exists(target_dir):
          rmtree(target_dir)

        if filetype == 'git':
          target_dir = join(self.VAR_CACHE, 'www')
          self.logger.debug("git_enable_revision('%s', '%s', '%s')" % (target_dir, source, codeVersionId))
          git.git_enable_revision(target_dir, source, codeVersionId)
        else:
          source.extractall(target_dir)

        # Fix session handlers
        self.fix_session_handlers(target_dir)
      
        return HttpJsonResponse()

    @expose('GET')
    def getTomcatState(self, kwargs):
      """GET state of Tomcat6"""
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      with self.tomcat_lock:
        return self._get(kwargs, self.tomcat_file, role.Tomcat6)

    @expose('POST')
    def createTomcat(self, kwargs):
      """Create Tomcat6"""
      ret = {}
      if 'tomcat_port' not in kwargs:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_MISSING, 'tomcat_port').message)
      ret['tomcat_port'] = kwargs.pop('tomcat_port')
  
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
  
      with self.tomcat_lock:
        return self._create(ret, self.tomcat_file, role.Tomcat6)

    @expose('POST')
    def stopTomcat(self, kwargs):
      """KILL Tomcat6"""
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      with self.tomcat_lock:
        return self._stop(kwargs, self.tomcat_file, role.Tomcat6)

    @expose('UPLOAD')
    def updateTomcatCode(self, kwargs):
      if 'filetype' not in kwargs:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_MISSING, 'filetype').message)
      filetype = kwargs.pop('filetype')
  
      if 'codeVersionId' not in kwargs:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_MISSING, 'codeVersionId').message)
      codeVersionId = kwargs.pop('codeVersionId')

      if 'file' not in kwargs:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_MISSING, 'file').message)
      file = kwargs.pop('file')

      if filetype != 'git' and not isinstance(file, FileUploadField):
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_INVALID, detail='"file" should be a file').message)

      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
  
      if filetype == 'zip': source = zipfile.ZipFile(file.file, 'r')
      elif filetype == 'tar': source = tarfile.open(fileobj=file.file)
      elif filetype == 'git': source = git.DEFAULT_CODE_REPO
      else: return HttpErrorResponse('Unsupported archive type ' + str(filetype))
  
      target_dir = join(self.VAR_CACHE, 'tomcat_instance', 'webapps', codeVersionId)
      if exists(target_dir):
        rmtree(target_dir)

      if filetype == 'git':
        target_dir = join(self.VAR_CACHE, 'tomcat_instance', 'webapps')
        self.logger.debug("git_enable_revision('%s', '%s', '%s')" % (target_dir, source, codeVersionId))
        git.git_enable_revision(target_dir, source, codeVersionId)
      else:
        source.extractall(target_dir)

      return HttpJsonResponse()
