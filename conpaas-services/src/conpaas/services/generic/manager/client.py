"""
Copyright (c) 2010-2015, Contrail consortium.
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
"""

import json
import httplib

from conpaas.core.misc import file_get_contents
from conpaas.core import https

def _check(response):
    """Check the given HTTP response, returning the result if everything went
    fine"""
    code, body = response
    if code != httplib.OK:
        raise HttpError('Received http response code %d' % (code))

    data = json.loads(body)
    if data['error']:
        raise Exception(data['error'])

    return data['result']

def startup(host, port):
    """POST () startup"""
    method = 'startup'
    return _check(https.client.jsonrpc_post(host, port, '/', method))

def shutdown(host, port):
    """POST () shutdown"""
    method = 'shutdown'
    return _check(https.client.jsonrpc_post(host, port, '/', method))

def add_nodes(host, port, count):
    """POST (count) add_nodes"""
    method = 'add_nodes'
    params = { 'count' : count }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def remove_nodes(host, port, count):
    """POST (count) remove_nodes"""
    method = 'remove_nodes'
    params = { 'count' : count }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def list_nodes(host, port):
    """GET () list_nodes"""
    method = 'list_nodes'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def get_service_info(host, port):
    """GET () get_service_info"""
    method = 'get_service_info'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def get_node_info(host, port, serviceNodeId):
    """GET (serviceNodeId) get_node_info"""
    method = 'get_node_info'
    params = { 'serviceNodeId' : serviceNodeId }
    return _check(https.client.jsonrpc_get(host, port, '/', method, params=params))

def list_code_versions(host, port):
    """GET () list_code_versions"""
    method = 'list_code_versions'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def list_authorized_keys(host, port):
    """GET () list_authorized_keys"""
    method = 'list_authorized_keys'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def upload_authorized_key(host, port, filepath):
    """UPLOAD (key) upload_authorized_key"""
    params = {'method': 'upload_authorized_key'}
    files = [('key', filepath, file_get_contents(filepath))]
    return _check(https.client.https_post(host, port, '/', params, files=files))

def git_push_hook(host, port):
    """POST () git_push_hook"""
    method = 'git_push_hook'
    return _check(https.client.jsonrpc_post(host, port, '/', method))

def upload_code_version(host, port, filepath):
    """UPLOAD (code) upload_code_version"""
    params = { 'method' : 'upload_code_version' }
    files = [('code', filepath, file_get_contents(filepath))]
    return _check(https.client.https_post(host, port, '/', params, files=files))

def download_code_version(host, port, codeVersionId):
    """GET (codeVersionId) download_code_version"""
    method = 'download_code_version'
    params = { 'codeVersionId' : codeVersionId }
    return _check(https.client.jsonrpc_get(host, port, '/', method, params=params))

def enable_code(host, port, codeVersionId):
    """POST (codeVersionId) enable_code"""
    method = 'enable_code'
    params = { 'codeVersionId' : codeVersionId }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def delete_code_version(host, port, codeVersionId):
    """POST (codeVersionId) delete_code_version"""
    method = 'delete_code_version'
    params = { 'codeVersionId' : codeVersionId }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def list_volumes(host, port):
    """GET () list_volumes"""
    method = 'list_volumes'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def generic_create_volume(host, port, volumeName, volumeSize, agentId):
    """POST (volumeName, volumeSize, agentId) generic_create_volume"""
    method = 'generic_create_volume'
    params = { 'volumeName' : volumeName,
               'volumeSize' : volumeSize,
               'agentId' : agentId }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def generic_delete_volume(host, port, volumeName):
    """POST (volumeName) generic_delete_volume"""
    method = 'generic_delete_volume'
    params = { 'volumeName' : volumeName }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def execute_script(host, port, command, parameters=''):
    """POST (command) execute_script"""
    method = 'execute_script'
    params = {
        'command' : command,
        'parameters' : parameters
    }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def get_script_status(host, port):
    """GET () get_script_status"""
    method = 'get_script_status'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def get_agent_log(host, port, filename=None):
    """GET (filename) get_agent_log"""
    method = 'get_agent_log'
    params = {}
    if filename:
        params['filename'] = filename
    return _check(https.client.jsonrpc_get(host, port, '/', method, params=params))
