'''
Created on Jun 8, 2011

@author: ales
'''
from conpaas.web.http import _http_get, _http_post
import httplib, json
import sys

class AgentException(Exception): pass

def __check_reply(body):
    try:
        ret = json.loads(body)
    except Exception as e: raise AgentException(*e.args)
    if not isinstance(ret, dict): raise AgentException('Response not a JSON object')
    if 'opState' not in ret: raise AgentException('Response does not contain "opState"')
    if ret['opState'] != 'OK':
        if 'ERROR' in ret['opState']: raise AgentException(ret['opState'], ret['error'])
    else: raise AgentException(ret['opState'])
    return True

def getMySQLServerState(host, port):
    params = {'action': 'getMySQLServerState'}
    code, body = _http_get(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

def createMySQLServer(host, port, mysql_port):
    params = {
              'action': 'createMySQLServer',
              'port': mysql_port,
    }
    code, body = _http_post(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

def printUsage():
    print 'TODO: Usage of agent_client.py.'
    pass

def stopMySQLServer(host, port):
    params = {'action': 'stopMySQLServer'}
    code, body = _http_post(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

if __name__ == '__main__':
    #host = '172.16.117.228'
    host = '127.0.0.1'
    port = 60000
    if sys.argv.__len__() in (2, 3):
        if sys.argv[1] in ("getMySQLServerState", "status"):
            getMySQLServerState(host, port)    
        if sys.argv[1] in ("createMySQLServer", "create"):
            if sys.argv.__len__() == 3:
                _port = int(sys.argv[2])
            else: 
                raise Exception('Please provide a port number')
                printUsage()
                exit()
            createMySQLServer(host, port, _port)
        if sys.argv[1] in ("stopMySQLServer", "stop"):
            stopMySQLServer(host, port)          
    else:
        printUsage()