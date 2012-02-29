"""
Created on September, 2011

   This module gives a client methods to trigger a manager methods. See module :py:mod:`conpaas.mysql.server.manager.internals`.

   :platform: Linux, Debian
   :synopsis: Internals of ConPaaS MySQL Servers.
   :moduleauthor: Ales Cernivec <ales.cernivec@xlab.si> 

"""

from conpaas.web.http import _http_get, _http_post, HttpError, _jsonrpc_get,\
    _jsonrpc_post
import httplib, json
import sys
from threading import Thread
from conpaas.mysql.server.manager.internals import get_node_info

class ManagerException(Exception): pass

class ClientError(Exception): pass

def _check(response):
    code, body = response
    if code != httplib.OK: raise HttpError('Received http response code %d' % (code))
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
            get_node_info - no params\n \
            get_service_info - no params\n \
            add_nodes - no params\n \
            remove_nodes - username, port \n \
            get_service_performance - no params\n'
    pass

def list_nodes(host, port):
    method = 'list_nodes'
    return _check(_jsonrpc_get(host, port, '/', method))

def get_node_info(host, port, serviceNodeId):
    method = 'get_node_info'
    params = {'serviceNodeId': serviceNodeId}
    return _check(_jsonrpc_get(host, port, '/', method, params=params))

def get_service_info(host, port):
    method = 'get_service_info'
    return _check(_jsonrpc_get(host, port, '/', method))

def add_nodes(host, port, function):
    params = {}
    params['function'] = function
    method = 'add_nodes'
    return _check(_jsonrpc_post(host, port, '/', method, params=params))
    
#===============================================================================
# def getMySQLServerState(host, port):
#    params = {'action': 'getMySQLServerManagerState'}
#    code, body = _http_get(host, port, '/', params=params)
#    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
#    return __check_reply(body)
# 
# def addServiceNode(host, port, function):
#    params = {'action': 'createServiceNode', 'function':function}
#    #Thread(target=wait_for_reply(params)).start()
#    code, body = _http_post(host, port, '/', params=params)
#    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
#    return __check_reply(body)
#===============================================================================



#def wait_for_reply(prms):
#    code, body = _http_post(host, port, '/', params=prms)
#    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
#    return __check_reply(body)

#===============================================================================
# def deleteServiceNode(host, port, id):
#    params = {'action': 'deleteServiceNode','id':str(id)}
#    code, body = _http_post(host, port, '/', params=params)
#    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
#    return __check_reply(body)
#===============================================================================

def remove_nodes(host, port, serviceNodeId):
    method = 'remove_nodes'
    params={}
    params['serviceNodeId'] = serviceNodeId
    return _check(_jsonrpc_post(host, port, '/', method, params=params))

def get_service_performance(host, port):
    method = 'get_service_performance'
    return _check(_jsonrpc_get(host, port, '/', method))

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
    else:
        printUsage()