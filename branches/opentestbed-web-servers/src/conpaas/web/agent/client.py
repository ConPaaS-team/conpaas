'''
Created on Mar 9, 2011

@author: ielhelw
'''

from conpaas.web.http import _jsonrpc_get, _jsonrpc_post, _http_post
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
  files = {'file': filepath}
  return _check(_http_post(host, port, '/', params, files=files))

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
  files = {'file': filepath}
  return _check(_http_post(host, port, '/', params, files=files))

