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


Created on Mar 29, 2011

@author: ielhelw
'''

import httplib, json

from conpaas.core.http import HttpError, _jsonrpc_get, _jsonrpc_post, _http_post, _http_get

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
