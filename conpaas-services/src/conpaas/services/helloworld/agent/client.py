from conpaas.core.http import _jsonrpc_get, _jsonrpc_post, _http_post
import httplib, json

def _check(response):
  code, body = response
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  data = json.loads(body)
  if data['error']: raise Exception(data['error'])
  else: return data['result']

def check_agent_process(host, port):
  method = 'check_agent_process'
  return _check(_jsonrpc_get(host, port, '/', method))

def startup(host, port):
  method = 'startup'
  return _check(_jsonrpc_post(host, port, '/', method))

def get_helloworld(host, port):
  method = 'get_helloworld'
  return _check(_jsonrpc_get(host, port, '/', method))
