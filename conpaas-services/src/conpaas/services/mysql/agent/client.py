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


Created on Jun 8, 2011

@author: ales, aaasz
'''
from conpaas.core.http import _http_get, _http_post, _jsonrpc_get, _jsonrpc_post
import httplib, json
import sys
from conpaas.core.log import create_logger


class AgentException(Exception): pass

def _check(response):
    code, body = response
    if code != httplib.OK:
        raise AgentException('Received http response code %d' % (code))
    try:
        data = json.loads(body)
    except Exception as e:
        raise AgentException(*e.args)
    if data['error']:
        raise AgentException(data['error'])
    else:
        return True

def get_master_state(host, port):
    method = 'get_master_state'
    result = _jsonrpc_get(host, port, '/', method)
    if _check(result):
        return result
    else:
        return False

def get_slave_state(host, port):
    method = 'get_slave_state'
    result = _jsonrpc_get(host, port, '/', method)
    if _check(result):
        return result
    else:
        return False

# TODO: with dump ?
def create_master(host, port, master_server_id):
    method = 'create_master'
    params = {
        'master_server_id': master_server_id
    }
    return _check(_jsonrpc_post(host, port, '/', method, params=params))

'''
   Method called by the manager and executed on a master agent
'''
def create_slave(host, port, slaves):
    method = 'create_slave'
    params = {'slaves': slaves}
    return _check(_jsonrpc_post(host, port, '/', method, params=params))

def configure_user(host, port, username, password):
    method = 'configure_user'
    params = {'username': username,
              'password': password}
    return _check(_jsonrpc_post(host, port, '/', method, params=params))
        
def get_all_users(host, port):
    method = 'get_all_users'
    result = _jsonrpc_get(host, port, '/', method)
    if _check(result):
        return result
    else:
        return False

def set_password(host, port, username, password):
    method = 'set_password'
    params = {'username': username,
              'password': password}
    return _check(_jsonrpc_post(host, port, '/', method, params=params))

def remove_user(host,port,name):
    method = 'remove_user'
    params = {'username': name}
    return _check(_jsonrpc_get(host, port, '/', method, params=params))

def check_agent_process(host, port):
    method = 'check_agent_process'
    return _check(_jsonrpc_get(host, port, '/', method))

def load_dump(host, port, mysqldump_path):
    params = {'method': 'load_dump'}
    files = {'mysqldump_file': mysqldump_path} 
    return _check(_http_post(host, port, '/', params, files=files))
'''

    Method called by a master agent to configure a slave agent
    (is executed inside the slave)
'''
def setup_slave(host, port, slave_server_id, master_host, \
                 master_log_file, master_log_pos, \
                 mysqldump_path):
    params = {
        'method': 'setup_slave',
        'master_host': master_host,
        'master_log_file': master_log_file,
        'master_log_pos': master_log_pos,
        'slave_server_id': slave_server_id
    }
    files = {'mysqldump_file': mysqldump_path} 
    return _check(_http_post(host, port, '/', params, files=files))
