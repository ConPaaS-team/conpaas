# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import httplib, json
import sys

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

def startup(host, port, cloud, clustering):
    method = 'startup'
    params = {'cloud': cloud, 'clustering': clustering}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

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
