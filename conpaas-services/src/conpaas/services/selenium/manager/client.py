"""
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

from conpaas.core.http import HttpError, _jsonrpc_get, _jsonrpc_post

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
    return _check(_jsonrpc_post(host, port, '/', method))

def shutdown(host, port):
    """POST () shutdown"""
    method = 'shutdown'
    return _check(_jsonrpc_post(host, port, '/', method))

def get_service_info(host, port):
    """GET () get_service_info"""
    method = 'get_service_info'
    return _check(_jsonrpc_get(host, port, '/', method))

def add_nodes(host, port, count=0):
    """POST (count) add_nodes"""
    method = 'add_nodes'
    params = {}
    params['count'] = count
    return _check(_jsonrpc_post(host, port, '/', method, params=params))

def remove_nodes(host, port, count=0):
    """POST (count) remove_nodes"""
    method = 'remove_nodes'
    params = {}
    params['count'] = count
    return _check(_jsonrpc_post(host, port, '/', method, params=params))

def list_nodes(host, port):
    """GET () list_nodes"""
    method = 'list_nodes'
    return _check(_jsonrpc_get(host, port, '/', method))

def get_node_info(host, port, serviceNodeId):
    """GET (serviceNodeId) get_node_info"""
    method = 'get_node_info'
    params = { 'serviceNodeId': serviceNodeId }
    return _check(_jsonrpc_get(host, port, '/', method, params=params))
