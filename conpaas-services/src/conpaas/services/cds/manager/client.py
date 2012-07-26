import httplib, json
from conpaas.core.http import HttpError, _jsonrpc_get, _jsonrpc_post, _http_post, _http_get

def _check(response):
  code, body = response
  if code != httplib.OK: raise HttpError('Received http response code %d' % (code))
  data = json.loads(body)
  if data['error']: raise Exception(data['error'])
  else: return data['result']

def get_service_info(host, port):
  method = 'get_service_info'
  return _check(_jsonrpc_get(host, port, '/', method))

def get_helloworld(host, port):
  method = 'get_helloworld'
  return _check(_jsonrpc_get(host, port, '/', method))

def startup(host, port):
  method = 'startup'
  return _check(_jsonrpc_post(host, port, '/', method))

def add_nodes(host, port, count=0):
  method = 'add_nodes'
  params = {}
  params['count'] = count
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def remove_nodes(host, port, count=0):
  method = 'remove_nodes'
  params = {}
  params['count'] = count
  return _check(_jsonrpc_post(host, port, '/', method, params=params))

def list_nodes(host, port):
  method = 'list_nodes'
  return _check(_jsonrpc_get(host, port, '/', method))

