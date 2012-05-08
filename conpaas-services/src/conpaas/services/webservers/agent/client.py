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


Created on Mar 9, 2011

@author: ielhelw
'''

from conpaas.core.http import _jsonrpc_get, _jsonrpc_post, _http_post
import httplib, json

class AgentException(Exception): pass

def _check(response):
  code, body = response
  if code != httplib.OK: raise AgentException('Received http response code %d' % (code))
  try: data = json.loads(body)
  except Exception as e: raise AgentException(*e.args)
  if data['error']: raise AgentException(data['error'])
  else: return True

def getWebServerState(host, port):
  method = 'getWebServerState'
  return _check(_jsonrpc_get(host, port, '/', method))

def createWebServer(host, port, web_port, code_versions):
  method = 'createWebServer'
  params = {
    'port': web_port,
    'code_versions': code_versions,
  }
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def updateWebServer(host, port, web_port, code_versions):
  method = 'updateWebServer'
  params = {
    'port': web_port,
    'code_versions': code_versions,
  }
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def stopWebServer(host, port):
  method = 'stopWebServer'
  return _check(_jsonrpc_post(host, port, '/', method))

def getHttpProxyState(host, port):
  method = 'getHttpProxyState'
  return _check(_jsonrpc_get(host, port, '/', method))

def createHttpProxy(host, port, proxy_port, code_version, web_list=[], fpm_list=[], tomcat_list=[], tomcat_servlets=[]):
  method = 'createHttpProxy'
  params = {
    'port': proxy_port,
    'code_version': code_version,
  }
  if web_list: params['web_list'] = web_list
  if fpm_list: params['fpm_list'] = fpm_list
  if tomcat_list: params['tomcat_list'] = tomcat_list
  if tomcat_servlets: params['tomcat_servlets'] = tomcat_servlets
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def updateHttpProxy(host, port, proxy_port, code_version, web_list=[], fpm_list=[], tomcat_list=[], tomcat_servlets=[]):
  method = 'updateHttpProxy'
  params = {
    'port': proxy_port,
    'code_version': code_version,
  }
  if web_list: params['web_list'] = web_list
  if fpm_list: params['fpm_list'] = fpm_list
  if tomcat_list: params['tomcat_list'] = tomcat_list
  if tomcat_servlets: params['tomcat_servlets'] = tomcat_servlets
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def stopHttpProxy(host, port):
  method = 'stopHttpProxy'
  return _check(_jsonrpc_post(host, port, '/', method))

def getPHPState(host, port):
  method = 'getPHPState'
  return _check(_jsonrpc_get(host, port, '/', method))

def checkAgentState(host, port):
  method = 'checkAgentState'
  return _check(_jsonrpc_get(host, port, '/', method))

def createPHP(host, port, php_port, scalaris, php_conf):
  method = 'createPHP'
  params = {
    'port': php_port,
    'scalaris': scalaris,
    'configuration': php_conf,
  }
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def updatePHP(host, port, php_port, scalaris, php_conf):
  method = 'updatePHP'
  params = {
    'port': php_port,
    'scalaris': scalaris,
    'configuration': php_conf
  }
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def stopPHP(host, port):
  method = 'stopPHP'
  return _check(_jsonrpc_post(host, port, '/', method))

def updatePHPCode(host, port, codeVersionId, filetype, filepath):
  params = {
    'method': 'updatePHPCode',
    'codeVersionId': codeVersionId,
    'filetype': filetype
  }

  if filetype != 'git':
    # File-based code uploads 
    files = {'file': filepath}
    return _check(_http_post(host, port, '/', params, files=files))

  # git-based code uploads do not need a FileUploadField.  
  # Pass filepath as a dummy value for the 'file' parameter.
  params['file'] = filepath
  return _check(_http_post(host, port, '/', params))

def getTomcatState(host, port):
  method = 'getTomcatState'
  return _check(_jsonrpc_get(host, port, '/', method))

def createTomcat(host, port, tomcat_port):
  method = 'createTomcat'
  params = {
    'tomcat_port': tomcat_port,
  }
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def stopTomcat(host, port):
  method = 'stopTomcat'
  return _check(_jsonrpc_post(host, port, '/', method))

def updateTomcatCode(host, port, codeVersionId, filetype, filepath):
  params = {
    'method': 'updateTomcatCode',
    'codeVersionId': codeVersionId,
    'filetype': filetype
  }

  if filetype != 'git':
    # File-based code uploads 
    files = {'file': filepath}
    return _check(_http_post(host, port, '/', params, files=files))

  # git-based code uploads do not need a FileUploadField.  
  # Pass filepath as a dummy value for the 'file' parameter.
  params['file'] = filepath
  return _check(_http_post(host, port, '/', params))
