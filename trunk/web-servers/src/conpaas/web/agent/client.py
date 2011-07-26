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

def createWebServer(host, port, doc_root, web_port, codeVersion, php, prevCodeVersion=None):
  method = 'createWebServer'
  params = {
    'doc_root': doc_root,
    'port': web_port,
    'codeVersion': codeVersion,
    'backends': php,
  }
  if prevCodeVersion:
    params['prevCodeVersion'] = prevCodeVersion;
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def updateWebServer(host, port, doc_root, web_port, codeVersion, php, prevCodeVersion=None):
  method = 'updateWebServer'
  params = {
    'doc_root': doc_root,
    'port': web_port,
    'codeVersion': codeVersion,
    'backends': php,
  }
  if prevCodeVersion:
    params['prevCodeVersion'] = prevCodeVersion;
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def stopWebServer(host, port):
  method = 'stopWebServer'
  return _check(_jsonrpc_post(host, port, '/', method))

def getTomcatWebServerState(host, port):
  method = 'getTomcatWebServerState'
  return _check(_jsonrpc_get(host, port, '/', method))

def createTomcatWebServer(host, port, doc_root, web_port, php, codeCurrent,
               servletsCurrent, codeOld=None, servletsOld=[]):
  method = 'createTomcatWebServer'
  params = {
    'doc_root': doc_root,
    'port': web_port,
    'backends': php,
    'codeCurrent': codeCurrent,
    'servletsCurrent': servletsCurrent,
  }
  if codeOld:
    params['codeOld'] = codeOld
    params['servletsOld'] = servletsOld
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def updateTomcatWebServer(host, port, doc_root, web_port, php, codeCurrent,
               servletsCurrent, codeOld=None, servletsOld=[]):
  method = 'updateTomcatWebServer'
  params = {
    'doc_root': doc_root,
    'port': web_port,
    'backends': php,
    'codeCurrent': codeCurrent,
    'servletsCurrent': servletsCurrent,
  }
  if codeOld:
    params['codeOld'] = codeOld
    params['servletsOld'] = servletsOld
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def stopTomcatWebServer(host, port):
  method = 'stopTomcatWebServer'
  return _check(_jsonrpc_post(host, port, '/', method))

def getHttpProxyState(host, port):
  method = 'getHttpProxyState'
  return _check(_jsonrpc_get(host, port, '/', method))

def createHttpProxy(host, port, proxy_port, backends, codeversion):
  method = 'createHttpProxy'
  params = {
    'port': proxy_port,
    'codeversion': codeversion,
    'backends': backends,
  }
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def updateHttpProxy(host, port, proxy_port, backends, codeversion):
  method = 'updateHttpProxy'
  params = {
    'port': proxy_port,
    'codeversion': codeversion,
    'backends': backends,
  }
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

