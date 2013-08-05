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

from conpaas.core import https
from conpaas.core.misc import file_get_contents

class ClientError(Exception): pass

def _check(response):
  code, body = response
  if code != httplib.OK: raise https.server.HttpError('Received http response code %d' % (code))
  try: data = json.loads(body)
  except Exception as e: raise ClientError(*e.args)
  if data['error']: raise ClientError(data['error'])
  else: return data['result']

def get_service_info(host, port):
  method = 'get_service_info'
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def get_service_history(host, port):
  method = 'get_service_history'
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def getLog(host, port):
  method = 'getLog'
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def startup(host, port):
  method = 'startup'
  return _check(https.client.jsonrpc_post(host, port, '/', method))

def shutdown(host, port):
  method = 'shutdown'
  return _check(https.client.jsonrpc_post(host, port, '/', method))

# MODIFIED SCALING V2:
def add_nodes(host, port, proxy=None, web=None, backend=None, cloud=None, vm_backend_instance=None, vm_web_instance=None):
  method = 'add_nodes'
  params = {}
  if proxy: params['proxy'] = proxy
  if web: params['web'] = web
  if backend: params['backend'] = backend
  
  ####### ADDED SCALING V2: ######################
  if vm_backend_instance != None: params['vm_backend_instance'] = vm_backend_instance
  if vm_web_instance !=None: params['vm_web_instance'] = vm_web_instance
  if cloud != None: params['cloud'] = cloud
  ################################################
  
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def remove_nodes(host, port, proxy=None, web=None, backend=None, node_ip=None):
  method = 'remove_nodes'
  params = {}
  if proxy: params['proxy'] = proxy
  if web: params['web'] = web
  if backend: params['backend'] = backend
  
  ####### ADDED SCALING V2: ######################
  if node_ip != None: params['node_ip'] = node_ip
  ################################################
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def update_nodes_weight(host, port, web=None, backend=None):
  method = 'update_nodes_weight'
  params = {}
  if web: params['web'] = web
  if backend: params['backend'] = backend
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def list_nodes(host, port):
  method = 'list_nodes'
  return _check(https.client.jsonrpc_get(host, port, '/', method))
  
def on_autoscaling(host, port, cool_down, response_time):
  method = 'on_autoscaling'
  params = {'cool_down': cool_down, 'response_time': response_time }
  return _check(https.client.jsonrpc_post(host, port, '/', method, params))

def off_autoscaling(host, port):
  method = 'off_autoscaling'
  params = {}
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def get_node_info(host, port, serviceNodeId):
  method = 'get_node_info'
  params = {'serviceNodeId': serviceNodeId}
  return _check(https.client.jsonrpc_get(host, port, '/', method, params=params))

def list_authorized_keys(host, port):
  method = 'list_authorized_keys'
  return _check(https.client.jsonrpc_get(host, port, '/', method))  

def list_code_versions(host, port):
  method = 'list_code_versions'
  return _check(https.client.jsonrpc_get(host, port, '/', method))
  
def on_autoscaling(host, port, cool_down, response_time):
  method = 'on_autoscaling'
  params = {'cool_down': cool_down, 'response_time': response_time }
  return _check(https.client.jsonrpc_post(host, port, '/', method, params))

def off_autoscaling(host, port):
  method = 'off_autoscaling'
  params = {}
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def upload_code_version(host, port, filepath):
  params = {'method': 'upload_code_version'}
  files = [('code', filepath, file_get_contents(filepath))]
  return _check(https.client.https_post(host, port, '/', params, files=files))

def upload_authorized_key(host, port, filepath):
  params = {'method': 'upload_authorized_key'}
  files = [('key', filepath, file_get_contents(filepath))]
  return _check(https.client.https_post(host, port, '/', params, files=files))

def get_configuration(host, port):
  method = 'get_configuration'
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def update_php_configuration(host, port, codeVersionId=None, phpconf={}):
  method = 'update_php_configuration'
  params = {}
  if codeVersionId != None:
    params['codeVersionId'] = codeVersionId
  if phpconf:
    params['phpconf'] = phpconf
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def update_java_configuration(host, port, codeVersionId):
  method = 'update_java_configuration'
  params = {'codeVersionId': codeVersionId}
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def get_service_performance(host, port):
  method = 'get_service_performance'
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def git_push_hook(host, port):
  method = 'git_push_hook'
  return _check(https.client.jsonrpc_post(host, port, '/', method))
