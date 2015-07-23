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


def create_node(host, port):
    """POST (my_ip) create_node"""
    method = 'create_node'
    params = { 'my_ip': host }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def test(host, port):
    """GET (my_ip) create_node"""
    method = 'test'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def make_worker(host, port):
    """GET (my_ip) make_worker"""
    method = 'make_worker'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def setup_node(host,port, master, naasbox, ismaster, isreducer,node):
    """GET (my_ip) setup_node"""
    method = 'setup_node'
    params = {'master':master,'naasbox':naasbox,'ismaster':ismaster,'isreducer':isreducer,'node':node}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def setup_naasbox(host,port,naasbox):
    """GET (my_ip) setup_naasbox"""
    method = 'setup_naasbox'
    params = {'naasbox':naasbox}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def enable_ssh(host,port,node):
    method = 'enable_ssh'
    params = {'node':node}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def append_slaves(host,port,nodes):
    method = 'append_slaves'
    params = {'nodes':nodes}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def fix_hosts(host,port,node):
    method = 'fix_hosts'
    params = {'node':node}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def start_all(host,port):
    method = 'start_all'
    return _check(https.client.jsonrpc_get(host, port, '/', method))


def update_host(host, port, node, nodes):
    method = 'update_host'
    params = {'me': node, 'nodes':nodes}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def update_code(host, port, codeVersionId, filetype, filepath):                   
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


def run(host, port, args):
    """POST run"""
    method = 'run'
    params = {}
    if args:
        params['args'] = args 
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))