'''
Created on Mar 9, 2011

@author: ielhelw
'''

from conpaas.web.http import _http_get, _http_post
import httplib, json

class AgentException(Exception): pass

def __check_reply(body):
  try:
    ret = json.loads(body)
  except Exception as e: raise AgentException(*e.args)
  if not isinstance(ret, dict): raise AgentException('Response not a JSON object')
  if 'opState' not in ret: raise AgentException('Response does not contain "opState"')
  if ret['opState'] != 'OK':
    if 'ERROR' in ret: raise AgentException(ret['opState'], ret['ERROR'])
    else: raise AgentException(ret['opState'])
  return True

def getWebServerState(host, port):
  params = {'action': 'getWebServerState'}
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def createWebServer(host, port, doc_root, web_port, php):
  params = {
    'action': 'createWebServer',
    'doc_root': doc_root,
    'port': web_port,
  }
  i = 0
  for pair in php:
    params['php.%d.ip' % i], params['php.%d.port' % i] = pair
    i += 1
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def updateWebServer(host, port, doc_root, web_port, php):
  params = {
    'action': 'updateWebServer',
    'doc_root': doc_root,
    'port': web_port,
  }
  i = 0
  for pair in php:
    params['php.%d.ip' % i], params['php.%d.port' % i] = pair
    i += 1
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def stopWebServer(host, port):
  params = {'action': 'stopWebServer'}
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def getHttpProxyState(host, port):
  params = {'action': 'getHttpProxyState'}
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def createHttpProxy(host, port, proxy_port, backends, codeversion):
  params = {
    'action': 'createHttpProxy',
    'port': proxy_port,
    'codeversion': codeversion,
  }
  i = 0
  for pair in backends:
    params['backends.%d.ip' % i], params['backends.%d.port' % i] = pair
    i += 1
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def updateHttpProxy(host, port, proxy_port, backends, codeversion):
  params = {
    'action': 'updateHttpProxy',
    'port': proxy_port,
    'codeversion': codeversion,
  }
  i = 0
  for pair in backends:
    params['backends.%d.ip' % i], params['backends.%d.port' % i] = pair
    i += 1
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def stopHttpProxy(host, port):
  params = {'action': 'stopHttpProxy'}
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def getPHPState(host, port):
  params = {'action': 'getPHPState'}
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def createPHP(host, port, php_port, scalaris, php_conf):
  params = {
    'action': 'createPHP',
    'port': php_port,
    'scalaris': scalaris,
  }
  
  i = 0
  for key in php_conf:
    params['configuration.%d.key' % (i)] = key
    params['configuration.%d.value' % (i)] = php_conf[key]
    i += 1
  
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def updatePHP(host, port, php_port, scalaris, php_conf):
  params = {
    'action': 'updatePHP',
    'port': php_port,
    'scalaris': scalaris,
  }
  
  i = 0
  for key in php_conf:
    params['configuration.%d.key' % (i)] = key
    params['configuration.%d.value' % (i)] = php_conf[key]
    i += 1
  
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def stopPHP(host, port):
  params = {'action': 'stopPHP'}
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

def updateCode(host, port, codeVersionId, filetype, filepath):
  params = {'action': 'updateCode',
            'codeVersionId': codeVersionId,
            'filetype': filetype}
  files = {'file': filepath}
  code, body = _http_post(host, port, '/', params, files)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return __check_reply(body)

if __name__ == '__main__':
  host = 'localhost'
  port = 5555
#  print getWebServerState(host, port)
#  print createWebServer(host, port, '/', 5588, [])
#  print updateWebServer(host, port, '/', 5590, [])
  print stopWebServer(host, port)


