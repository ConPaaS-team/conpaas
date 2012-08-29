#!/usr/bin/python
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


Created on September, 2011

@author: ales

   This module gives a client methods to trigger the
   manager methods.
   See module :py:mod:`conpaas.mysql.server.manager.internals`.

   :platform: Linux, Debian
   :synopsis: Internals of ConPaaS MySQL Servers.
   :moduleauthor: Ales Cernivec <ales.cernivec@xlab.si> 

'''

import httplib, json
import sys
from threading import Thread

from conpaas.core import https
from conpaas.core.misc import file_get_contents

class ManagerException(Exception): pass

class ClientError(Exception): pass

def _check(response):
    code, body = response
    if code != httplib.OK: raise https.server.HttpError('Received http response code %d' % (code))
    try: data = json.loads(body)
    except Exception as e: raise ClientError(*e.args)
    if data['error']: raise ClientError(data['error'])
    else: return data['result']

def __check_reply(body):
    try:
        ret = json.loads(body)
    except Exception as e: raise ManagerException(*e.args)
    if not isinstance(ret, dict): raise ManagerException('Response not a JSON object')
    if 'opState' not in ret: raise ManagerException('Response does not contain "opState"')
    if ret['opState'] != 'OK':
        if 'ERROR' in ret['opState']: raise ManagerException(ret['opState'], ret['error'])
        else: raise ManagerException(ret['opState'])
    return ret

def printUsage():
    print 'Usage: service_ip service_port function function_params\n\
Functions:  list_nodes - no params\n \
            startup - no params\n \
            get_node_info - no params\n \
            get_service_info - no params\n \
            add_nodes - no params\n \
            remove_nodes - username, port \n \
            get_service_performance - no params\n \
            load_dump - mysqldump_file\n'
    pass

def startup(host, port):
    method = 'startup'
    return _check(https.client.jsonrpc_post(host, port, '/', method))

def list_nodes(host, port):
    method = 'list_nodes'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def get_node_info(host, port, serviceNodeId):
    method = 'get_node_info'
    params = {'serviceNodeId': serviceNodeId}
    return _check(https.client.jsonrpc_get(host, port, '/', method, params=params))

def set_password(host, port, username, password):
    method = 'set_password'
    params = {'user': username, 'password': password}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def get_service_info(host, port):
    method = 'get_service_info'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def add_nodes(host, port, count):
    params = {'slaves': count}
    method = 'add_nodes'
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def get_log(host, port):
    method = 'getLog'
    return _check(https.client.jsonrpc_get(host, port, '/', method))
    
def remove_nodes(host, port, serviceNodeId):
    method = 'remove_nodes'
    params={}
    params['serviceNodeId'] = serviceNodeId
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def get_service_performance(host, port):
    method = 'get_service_performance'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def load_dump(host, port, mysqldump_path):
    params = {'method': 'load_dump'}
    files = [('mysqldump_file', mysqldump_path, file_get_contents(mysqldump_path))]
    return _check(https.client.https_post(host, port, '/', params, files=files))

if __name__ == '__main__':
    if sys.argv.__len__() in (4, 5):
        host = sys.argv[1]
        port = sys.argv[2]
        if sys.argv[3] in ("list_nodes"):
            ret = list_nodes(host, port)
            print ret            
        if sys.argv[3] in ("add_nodes"):
            ret = add_nodes(host, port, sys.argv[4])
            print ret            
        if sys.argv[3] in ("get_service_info"):
            ret = get_service_info(host, port)
            print ret            
        if sys.argv[3] in ("remove_nodes"):            
            id = sys.argv[4]
            ret = remove_nodes(host, port, id)
            print ret            
        if sys.argv[3] in ("list_nodes"):            
            ret = list_nodes(host, port)
            print ret
        if sys.argv[3] in ("get_node_info"):   
            serviceNodeId = sys.argv[4]         
            ret = get_node_info(host, port, serviceNodeId)
            print ret    
        if sys.argv[3] in ("get_service_performance"):          
            ret = get_service_performance(host, port)
            print ret 
        if sys.argv[3] in ("load_dump"):          
            ret = load_dump(host, port, sys.argv[4])
            print ret
    else:
        printUsage()
