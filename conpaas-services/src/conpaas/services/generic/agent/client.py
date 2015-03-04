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

from conpaas.core import https
from conpaas.core.misc import file_get_contents

class AgentException(Exception):
    pass


def _check(response):
    """Check the given HTTP response, returning the result if everything went
    fine"""
    code, body = response
    if code != httplib.OK:
        raise Exception('Received http response code %d' % (code))

    data = json.loads(body)
    if data['error']:
        raise Exception(data['error'])

    return data['result']

def check_agent_process(host, port):
    """GET () check_agent_process"""
    method = 'check_agent_process'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def init_agent(host, port, agents_info):
    """POST (agents_info, ip) init_agent"""
    method = 'init_agent'
    params = {
        'agents_info': json.dumps(agents_info),
        'ip' : host
    }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params))

def update_code(host, port, codeVersionId, filetype, filepath):
    """UPLOAD (filetype, codeVersionId, file) update_code"""
    params = {
        'method': 'update_code',
        'codeVersionId': codeVersionId,
        'filetype': filetype
    }

    if filetype != 'git':
        # File-based code uploads
        files = [('file', filepath, file_get_contents(filepath))]
        return _check(https.client.https_post(host, port, '/', params, files=files))

    # git-based code uploads do not need a FileUploadField.
    # Pass filepath as a dummy value for the 'file' parameter.
    params['file'] = filepath
    return _check(https.client.https_post(host, port, '/', params))

def mount_volume(host, port, dev_name, vol_name):
    """POST (dev_name, vol_name) mount_volume"""
    method = 'mount_volume'
    params = { 'dev_name': dev_name, 'vol_name': vol_name }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params))

def unmount_volume(host, port, dev_name):
    """POST (dev_name) unmount_volume"""
    method = 'unmount_volume'
    params = { 'dev_name': dev_name }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params))

def execute_script(host, port, command, parameters, agents_info):
    """POST (command, parameters, agents_info) execute_script"""
    method = 'execute_script'
    params = {
        'command' : command,
        'parameters' : parameters,
        'agents_info': json.dumps(agents_info)
    }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params))

def get_script_status(host, port):
    """GET () get_script_status"""
    method = 'get_script_status'
    return _check(https.client.jsonrpc_get(host, port, '/', method))
