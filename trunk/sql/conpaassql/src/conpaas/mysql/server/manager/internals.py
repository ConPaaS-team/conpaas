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

'''
    For each of the node from the list of the manager check that it is alive (in the list
    returned by the ONE).
'''
@expose('GET')
def listServiceNodes(kwargs):
    logger.debug("Entering listServiceNode")
    if len(kwargs) != 0:
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
    #dstate = memcache.get(DEPLOYMENT_STATE)    
    vms = iaas.listVMs()
    vms_mysql = config.getMySQLServiceNodes()
    for vm in vms_mysql:
        if not(vm['id'] in vms.keys()):
            logger.debug('Removing instance ' + str(vm['id']) + ' since it is not in the list returned by the listVMs().')
            config.removeMySQLServiceNode(vm['id'])         
    #if dstate != S_RUNNING and dstate != S_ADAPTING:
    #    return {'opState': 'ERROR', 'error': ManagerException(E_STATE_ERROR).message}    
    #config = memcache.get(CONFIG)
    logger.debug("Exiting listServiceNode")
    return {
          'opState': 'OK',
          #'sql': [ serviceNode.vmid for serviceNode in managerServer.config.getMySQLServiceNodes() ]
          #'sql': [ vms.keys() ]
          'sql': [ serviceNode.vmid for serviceNode in config.getMySQLServiceNodes() ]
    }

'''Creates a new service node. 
@param function: None, "manager" or "agent". If None, empty image is provisioned. If "manager"
new manager is awaken and if the function equals "agent", new instance of the agent is 
provisioned.     
'''
@expose('POST')
def createServiceNode(kwargs):
    if not(len(kwargs) in (0,1)):
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}    
    if len(kwargs) == 0:
        new_vm=iaas.newInstance(None)
        Thread(target=createServiceNodeThread(None, new_vm)).start()
    else:
        new_vm=iaas.newInstance(kwargs['function'])
        Thread(target=createServiceNodeThread(kwargs['function'], new_vm)).start()
    return {
          'opState': 'OK',
          'sql': [ new_vm['id'] ]
    }

@expose('POST')
def deleteServiceNode(kwargs):
    if len(kwargs) != 1:
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
    logger.debug('deleteServiceNode ' + str(kwargs['id']))
    if iaas.killInstance(kwargs['id']):
        config.removeMySQLServiceNode(kwargs['id'])
    '''TODO: If false, return false response.
    '''
    return {
          'opState': 'OK'    
    }

'''
    Waits for new VMs to awake. 
    @param function: None, agent or manager.
    @param new_vm: new VM's details.  
'''
def createServiceNodeThread (function, new_vm):
    node_instances = []    
    vm=iaas.listVMs()[new_vm['id']]
    node_instances.append(vm)    
    wait_for_nodes(node_instances)
    config.addMySQLServiceNode(new_vm['id'], new_vm)

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
    Wait for nodes to get ready. It tries to call a function of the agent. If exception
    is thrown, wait for poll_interval seconds.
    @param nodes: a list of nodes
    @param poll_intervall: how many seconds to wait. 
'''
def wait_for_nodes(nodes, poll_interval=10):
    logger.debug('wait_for_nodes: going to start polling')
    done = []
    while len(nodes) > 0:
        for i in nodes:
            up = True
            try:
                if i['ip'] != '':
                    logger.debug('Probing ' + i['ip'] + ' for state.')
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