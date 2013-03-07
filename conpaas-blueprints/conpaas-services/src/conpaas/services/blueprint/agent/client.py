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

# TODO: as this file was created from a BLUEPRINT file,
# 	you may want to change ports, paths and/or methods (e.g. for hub)
#	to meet your specific service/server needs

import json
import httplib

from conpaas.core import https 

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

def create_hub(host, port):
    """POST (my_ip) create_hub"""
    method = 'create_hub'
    params = { 'my_ip': host }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params))

def create_node(host, port, hub_ip):
    """POST (my_ip, hub_ip) create_node"""
    method = 'create_node'
    params = { 'my_ip': host, 'hub_ip': hub_ip }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params))
