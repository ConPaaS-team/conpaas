'''
Created on Jun 7, 2011

@author: ales
'''
from conpaas.log import create_logger
from conpaas.mysql.server.manager.config import Configuration, ManagerException,\
    E_ARGS_UNEXPECTED, ServiceNode, E_UNKNOWN
from threading import Thread
from conpaas.mysql.client import agent_client
import time
import conpaas

S_INIT = 'INIT'
S_PROLOGUE = 'PROLOGUE'
S_RUNNING = 'RUNNING'
S_ADAPTING = 'ADAPTING'
S_EPILOGUE = 'EPILOGUE'
S_STOPPED = 'STOPPED'
S_ERROR = 'ERROR'

memcache = None
dstate = None
exposed_functions = {}
config = None
logger = create_logger(__name__)
iaas = None
managerServer = None

class MySQLServerManager():
    
    def __init__(self, conf):        
        logger.debug("Entering MySQLServerManager initialization")
        conpaas.mysql.server.manager.internals.config = Configuration(conf)                                 
        self.state = S_INIT
        logger.debug("Leaving MySQLServer initialization")

def expose(http_method):
    def decorator(func):
        if http_method not in exposed_functions:
            exposed_functions[http_method] = {}
        exposed_functions[http_method][func.__name__] = func
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped
    return decorator

@expose('GET')
def listServiceNodes(kwargs):
    logger.debug("Entering listServiceNode")
    if len(kwargs) != 0:
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
    #dstate = memcache.get(DEPLOYMENT_STATE)    
    vms = iaas.listVMs()
    #if dstate != S_RUNNING and dstate != S_ADAPTING:
    #    return {'opState': 'ERROR', 'error': ManagerException(E_STATE_ERROR).message}
    
    #config = memcache.get(CONFIG)
    logger.debug("Exiting listServiceNode")
    return {
          'opState': 'OK',
          #'sql': [ serviceNode.vmid for serviceNode in managerServer.config.getMySQLServiceNodes() ]
          'sql': [ vms.keys() ]
    }

@expose('POST')
def createServiceNode(kwargs):
    if len(kwargs) != 0:
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
    Thread(target=createServiceNodeThread).start()
    sn=ServiceNode(1, True)
    #sn.ip="127.0.0.1"    
    #managerServer.config.addMySQLServiceNode(1,sn)
    return {
          'opState': 'OK'
          #'sql': [ sn.vmid ]
    }
  
def createServiceNodeThread ():
    node_instances = []
    new_vm=iaas.newInstance()
    vm=iaas.listVMs()[new_vm['id']]
    node_instances.append(vm)
    config.addMySQLServiceNode(new_vm['id'], new_vm)
    #wait_for_nodes(node_instances)

@expose('GET')
def getMySQLServerManagerState(params):
    logger.debug("Entering getMySQLServerManagerState")
    try: 
        logger.debug("Leaving getMySQLServerManagerState")
        return {'opState':'OK', 'return': managerServer.state}
    except Exception as e:
        ex = ManagerException(E_UNKNOWN, detail=e)
        logger.exception(e)
        logger.debug('Leaving getMySQLServerManagerState')
        return {'opState': 'ERROR', 'error': ex.message}

'''
    Wait for nodes to get ready.
'''
def wait_for_nodes(nodes, poll_interval=10):
    logger.debug('wait_for_nodes: going to start polling')
    done = []
    while len(nodes) > 0:
        for i in nodes:
            up = True
            try:
                if i['ip'] != '':
                    agent_client.getMySQLServerState((i['ip'], 60000))
                else:
                    up = False
            except agent_client.AgentException: pass
            except: up = False
            if up:
                done.append(i)
        nodes = [ i for i in nodes if i not in done]
        if len(nodes):
            logger.debug('wait_for_nodes: waiting for %d nodes' % len(nodes))
            time.sleep(poll_interval)
            no_ip_nodes = [ i for i in nodes if i['ip'] == '' ]
            if no_ip_nodes:
                logger.debug('wait_for_nodes: refreshing %d nodes' % len(no_ip_nodes))
                refreshed_list = iaas.listVMs()
                for i in no_ip_nodes:
                    i['ip'] = refreshed_list[i['id']]['ip']
        logger.debug('wait_for_nodes: All nodes are ready %s' % str(done))