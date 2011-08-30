'''
Created on Jun 8, 2011

@author: ales
'''
from conpaas.web.http import _http_get, _http_post
import httplib, json
import sys

class ManagerException(Exception): pass

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
    print 'TODO: Usage of agent_client.py.'
    pass

def getListServiceNodes(host, port):
    params = {'action': 'listServiceNodes'}
    code, body = _http_get(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

def addServiceNode(host, port):
    params = {'action': 'createServiceNode'}
    code, body = _http_post(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

if __name__ == '__main__':
    #host = '172.16.117.228'
    host = '0.0.0.0'
    #host = '172.16.118.185'
    port = 50000
    if sys.argv.__len__() in (2, 3):
        if sys.argv[1] in ("listServiceNodes"):
            ret = getListServiceNodes(host, port)
            print ret            
        if sys.argv[1] in ("createServiceNode"):
            ret = addServiceNode(host, port)
            print ret            
    else:
        printUsage()