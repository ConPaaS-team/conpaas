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
    return ret

def getMySQLServerState(host, port):
    params = {'action': 'getMySQLServerState'}
    code, body = _http_get(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

def createMySQLServer(host, port):
    params = {'action': 'createMySQLServer'}
    code, body = _http_post(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

def printUsage():
    print 'Usage: agent_ip agent_port function function_params\n\
Functions:  getMySQLServerState - no params\n \
            createMySQLServer - no params\n \
            restartMySQLServer - no params\n \
            stopMySQLServer - no params\n \
            configure_user - username, port \n \
            get_all_users - no params\n \
            remove_user - name \n \
            setMySQLServerConfiguration - paramid value\n \
            send_mysqldump -  location on disc\n'
    pass

def restartMySQLServer(host, port):
    params = {'action': 'restartMySQLServer'}
    code, body = _http_post(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)
    
def stopMySQLServer(host, port):
    params = {'action': 'stopMySQLServer'}
    code, body = _http_post(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)
    
def configure_user(host, port, username, password):
    params = {'action': "createNewMySQLuser",
              'username': username,
              'password': password}
    code, body = _http_post(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)
        
def get_all_users(host, port):
    params = {'action': 'listAllMySQLusers'}
    code, body = _http_get(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

def remove_user(host,port,name):
    params = {'action': 'removeMySQLuser',
            'username': name
            }
    code, body = _http_post(host, port, '/', params=params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

def setMySQLServerConfiguration(host,port, param_id, val):
    params = {'action': 'setMySQLServerConfiguration',
              'id_param': param_id,
              'value': val
              }
    code, body = _http_post(host, port, '/', params= params)
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

def send_mysqldump(host,port,location):
    params = {
              'action': 'create_with_MySQLdump'}
    code, body = _http_post(host, port, '/', params= params, files={'mysqldump':location})
    if code != httplib.OK: raise Exception('Received HTTP response code %d' % (code))
    return __check_reply(body)

if __name__ == '__main__':
    if sys.argv.__len__() > 3:
        host = sys.argv[1]
        port = sys.argv[2]
        if sys.argv[3] == 'getMySQLServerState':
            ret = getMySQLServerState(host, port)
            print ret
        if sys.argv[3] == 'createMySQLServer':
            ret = createMySQLServer(host, port)
            print ret
        if sys.argv[3] == 'restartMySQLServer':
            ret = restartMySQLServer(host, port)
            print ret
        if sys.argv[3] == 'stopMySQLServer':
            ret = stopMySQLServer(host, port)
            print ret
        if sys.argv[3] == 'configure_user':
            if sys.argv.__len__ == 6:
                ret = configure_user(host, port, sys.argv[4], sys.argv[5])
                print ret
            else:
                print 'additional parameters required'
        if sys.argv[3] == 'get_all_users':
            ret =get_all_users(host, port)
            print ret
        if sys.argv[3] == 'remove_user':
            if sys.argv.__len__ == 5:               
                ret = remove_user(host,port,sys.argv[4])
                print ret
            else:
                print 'additional parameters required'
        if sys.argv[3] == 'setMySQLServerConfiguration':
            if sys.argv.__len__ == 6:
                ret = setMySQLServerConfiguration(host,port, sys.argv[4], sys.argv[5])
                print ret
            else:
                print 'additional parameters required'                
        if sys.argv[3] == 'send_mysqldump':
            if sys.argv.__len__ == 5:
                ret = send_mysqldump(host,port,sys.argv[4])
                print ret
            else:
                print 'additional parameters required' 
    else:
        printUsage()
        #setMySQLServerConfiguration('127.0.0.1', 60000, "/home/danaia/Desktop/bla.txt")
        
        #createMySQLServer('127.0.0.1', 60000)
        #print configure_user('127.0.0.1', 60000, "janez", "rekar")        
        #print remove_user('127.0.0.1', 60000, "janez")
        
        #stopMySQLServer("127.0.0.1", 60000)
        #createMySQLServer('127.0.0.1', 60000)
        #print restartMySQLServer("127.0.0.1", 60000)
        #print getMySQLServerState('127.0.0.1', 60000)
        #print get_all_users("127.0.0.1", 60000)
        #ret = get_all_users('127.0.0.1', 60000)
        #for a in ret:
            #if a != 'opState':
                #print "username: " + ret[a]['username'] + " location: " + ret[a]["location"]
        #print send_mysqldump('127.0.0.1', 60000, "/home/danaia/Desktop/mysqldump")
        #printUsage()
        #print setMySQLServerConfiguration('127.0.0.1', 60000, "port", 40000)