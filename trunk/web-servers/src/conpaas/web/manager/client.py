'''
Created on Mar 29, 2011

@author: ielhelw
'''

import httplib, json

from conpaas.web.http import HttpError, _jsonrpc_get, _jsonrpc_post, _http_post, _http_get

class ClientError(Exception): pass

def _check(response):
  code, body = response
  if code != httplib.OK: raise HttpError('Received http response code %d' % (code))
  try: data = json.loads(body)
  except Exception as e: raise ClientError(*e.args)
  if data['error']: raise ClientError(data['error'])
  else: return data['result']

def get_service_info(host, port):
  method = 'get_service_info'
  return _check(_jsonrpc_get(host, port, '/', method))

def get_service_history(host, port):
  method = 'get_service_history'
  return _check(_jsonrpc_get(host, port, '/', method))

def getLog(host, port):
  method = 'getLog'
  return _check(_jsonrpc_get(host, port, '/', method))

def startup(host, port):
  method = 'startup'
  return _check(_jsonrpc_post(host, port, '/', method))

def shutdown(host, port):
  method = 'shutdown'
  return _check(_jsonrpc_post(host, port, '/', method))

def add_nodes(host, port, proxy=None, web=None, backend=None):
  method = 'add_nodes'
  params = {}
  if proxy: params['proxy'] = proxy
  if web: params['web'] = web
  if backend: params['backend'] = backend
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def remove_nodes(host, port, proxy=None, web=None, backend=None):
  method = 'remove_nodes'
  params = {}
  if proxy: params['proxy'] = proxy
  if web: params['web'] = web
  if backend: params['backend'] = backend
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def list_nodes(host, port):
  method = 'list_nodes'
  return _check(_jsonrpc_get(host, port, '/', method))

def get_node_info(host, port, serviceNodeId):
  method = 'get_node_info'
  params = {'serviceNodeId': serviceNodeId}
  return _check(_jsonrpc_get(host, port, '/', method, params=params))

def list_code_versions(host, port):
  method = 'list_code_versions'
  return _check(_jsonrpc_get(host, port, '/', method))

def upload_code_version(host, port, filename):
  params = {'method': 'upload_code_version'}
  files = {'code': filename}
  return _check(_http_post(host, port, '/', params, files=files))

def get_configuration(host, port):
  method = 'get_configuration'
  return _check(_jsonrpc_get(host, port, '/', method))

def update_php_configuration(host, port, codeVersionId=None, phpconf={}):
  method = 'update_php_configuration'
  params = {}
  if codeVersionId != None:
    params['codeVersionId'] = codeVersionId
  if phpconf:
    params['phpconf'] = phpconf
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def update_java_configuration(host, port, codeVersionId):
  method = 'update_java_configuration'
  params = {'codeVersionId': codeVersionId}
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def get_service_performance(host, port):
  method = 'get_service_performance'
  return _check(_jsonrpc_get(host, port, '/', method))
