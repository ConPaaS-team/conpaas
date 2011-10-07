'''
Created on Jun 7, 2011

@author: ales
'''
from conpaas.log import create_logger
from conpaas.mysql.server.manager.config import Configuration, ManagerException,\
    E_ARGS_UNEXPECTED, ServiceNode, E_UNKNOWN, E_ARGS_MISSING
from threading import Thread
from conpaas.mysql.client import agent_client
import time
import conpaas
import conpaas.mysql.server.manager
from conpaas.web.http import HttpErrorResponse, HttpJsonResponse
from conpaas.mysql.server.agent.internals import E_ARGS_INVALID

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
dummy_backend = None

class MySQLServerManager():
    
    dummy_backend = False
    
    def __init__(self, conf, _dummy_backend=False):        
        logger.debug("Entering MySQLServerManager initialization")
        conpaas.mysql.server.manager.internals.config = Configuration(conf, _dummy_backend)         
        self.state = S_INIT
        self.dummy_backend = _dummy_backend
        conpaas.mysql.server.manager.internals.dummy_backend = _dummy_backend
        # TODO:
        self.__findAlreadyRunningInstances()
        logger.debug("Leaving MySQLServer initialization")

    '''
        Adds running instances of mysql agents to the list.
    '''
    def __findAlreadyRunningInstances(self):
        logger.debug("Entering __findAlreadyRunningInstances")
        list = iaas.listVMs()
        logger.debug('List obtained: ' + str(list))
        if self.dummy_backend:
            for i in list.values():
                conpaas.mysql.server.manager.internals.config.addMySQLServiceNode(i)
        else:
            for i in list.values():
                up = True
                try:
                    if i['ip'] != '':
                        logger.debug('Probing ' + i['ip'] + ' for state.')
                        ret = agent_client.getMySQLServerState(i['ip'], 60000)                    
                        logger.debug('Returned query:' + str(ret))
                    else:
                        up = False
                except agent_client.AgentException as e: logger.error('Exception: ' + str(e))
                except Exception as e:
                    logger.error('Exception: ' + str(e))                
                    up = False
                if up:
                    logger.debug('Adding service node ' + i['ip'])
                    conpaas.mysql.server.manager.internals.config.addMySQLServiceNode(i)
        logger.debug("Exiting __findAlreadyRunningInstances")        

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
        if not(vm.vmid in vms.keys()):
            logger.debug('Removing instance ' + str(vm.vmid) + ' since it is not in the list returned by the listVMs().')
            config.removeMySQLServiceNode(vm.vmid)         
    #if dstate != S_RUNNING and dstate != S_ADAPTING:
    #    return {'opState': 'ERROR', 'error': ManagerException(E_STATE_ERROR).message}    
    #config = memcache.get(CONFIG)
    logger.debug("Exiting listServiceNode")
    return {
          'opState': 'OK',
          #'sql': [ serviceNode.vmid for serviceNode in managerServer.config.getMySQLServiceNodes() ]
          #'sql': [ vms.keys() ]
          'sql': [ [serviceNode.vmid, serviceNode.ip, serviceNode.port, serviceNode.state ] for serviceNode in config.getMySQLServiceNodes() ]
    }

@expose('GET')
def list_nodes(kwargs):
    if len(kwargs) != 0:
        return HttpErrorResponse(ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
    vms = iaas.listVMs()
    vms_mysql = config.getMySQLServiceNodes()
    for vm in vms_mysql:
        if not(vm.vmid in vms.keys()):
            logger.debug('Removing instance ' + str(vm.vmid) + ' since it is not in the list returned by the listVMs().')
            config.removeMySQLServiceNode(vm.vmid)                 
    return HttpJsonResponse({
        'sql': [ [serviceNode.vmid] for serviceNode in config.getMySQLServiceNodes() ],
        })

'''Creates a new service node. 
@param function: None, "manager" or "agent". If None, empty image is provisioned. If "manager"
new manager is awaken and if the function equals "agent", new instance of the agent is 
provisioned.     
'''
@expose('POST')
def createServiceNode(kwargs):
    if not(len(kwargs) in (0,1, 3)):
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}    
    if len(kwargs) == 0:
        new_vm=iaas.newInstance(None)
        Thread(target=createServiceNodeThread(None, new_vm)).start()
    elif len(kwargs) == 1:
        new_vm=iaas.newInstance(kwargs['function'])
        Thread(target=createServiceNodeThread(kwargs['function'], new_vm)).start()
    else:
        pass
    return {
          'opState': 'OK',
          'sql': [ new_vm['id'] ]
    }

@expose('POST')
def add_nodes(kwargs):
    if not(len(kwargs) in (0,1, 3)):
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}    
    if len(kwargs) == 0:
        new_vm=iaas.newInstance(None)
        Thread(target=createServiceNodeThread(None, new_vm)).start()
    elif len(kwargs) == 1:
        new_vm=iaas.newInstance(kwargs['function'])
        Thread(target=createServiceNodeThread(kwargs['function'], new_vm)).start()
    else:
        pass
    return HttpJsonResponse()

'''Creating a service replication.
'''
@expose('POST')
def createReplica(kwargs):
    if not(len(kwargs) in (2)):
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}    
    new_vm=iaas.newInstance('agent')
    master_id=kwargs['master_id']
    createServiceNodeThread('agent', new_vm)    
    '''new_vm is a new replica instance
    '''
    '''TODO: insert code for initializing a replica master'''
    '''TODO: insert code for initializing a replica client'''
    
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

@expose('POST')
def delete_nodes(kwargs):
    if len(kwargs) != 1:
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
    logger.debug('deleteServiceNode ' + str(kwargs['id']))
    if iaas.killInstance(kwargs['id']):
        config.removeMySQLServiceNode(kwargs['id'])
    '''TODO: If false, return false response.
    '''
    return HttpJsonResponse()

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
    config.addMySQLServiceNode(new_vm)

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

#===============================================================================
# @expose('GET')
# def get_node_info( kwargs):
#    logger.debug("Entering get_node_info")
#    if 'serviceNodeId' not in kwargs: return HttpErrorResponse(ManagerException(E_ARGS_MISSING, 'serviceNodeId').message)
#    serviceNodeId = kwargs.pop('serviceNodeId')
#    if len(kwargs) != 0:
#        return HttpErrorResponse(ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
#    
#    config = self._configuration_get()
#    if serviceNodeId not in config.serviceNodes: return HttpErrorResponse(ManagerException(E_ARGS_INVALID, detail='Invalid "serviceNodeId"').message)
#    serviceNode = config.serviceNodes[serviceNodeId]
#    return HttpJsonResponse({
#            'serviceNode': {
#                            'id': serviceNode.vmid,
#                            'ip': serviceNode.ip,
#                            'isRunningProxy': serviceNode.isRunningProxy,
#                            'isRunningWeb': serviceNode.isRunningWeb,
#                            'isRunningBackend': serviceNode.isRunningBackend,
#                            'isRunningMySQL': serviceNode.isRunningBackend,
#                            }
#            })
#===============================================================================

'''
    Sets up a replica master node
    @param id: new replica master id.

'''
@expose('POST')
def set_up_replica_master(params):
    logger.debug("Entering set_up_replica_master")
    if len(params) != 1:
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, params.keys()).message}
    new_master_id = params['id']
    new_master_ip = ''
    new_master_port = ''
    for node in config.getMySQLServiceNodes():
        if new_master_id == node.id:
            new_master_ip=node.ip
            new_master_port=node.port
    agent_client.set_up_replica_master(new_master_ip, new_master_port)
    logger.debug("Exiting set_up_replica_master")
    pass

@expose('POST')
def set_up_replica_slave(params):
    logger.debug("Entering set_up_replica_slave")
    if len(params) != 5:
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, params.keys()).message}
    _id = params['id']
    _host = ''
    _port = ''
    for node in config.getMySQLServiceNodes():
        if _id == node.id:
            _host=node.ip
            _port=node.port
    master_host = params['master_host']
    master_log_file = params['master_log_file']
    master_log_pos = params['master_log_pos']
    slave_server_id = params['slave_server_id']
    agent_client.set_up_replica_slave(_host, _port, master_host, master_log_file, master_log_pos, slave_server_id)
    logger.debug("Exiting set_up_replica_slave")
    pass

'''
    Wait for nodes to get ready. It tries to call a function of the agent. If exception
    is thrown, wait for poll_interval seconds.
    @param nodes: a list of nodes
    @param poll_intervall: how many seconds to wait. 
'''
def wait_for_nodes(nodes, poll_interval=10):
    logger.debug('wait_for_nodes: going to start polling')
    if conpaas.mysql.server.manager.internals.dummy_backend:
        pass
    else:        
        done = []
        while len(nodes) > 0:
            for i in nodes:
                up = True
                try:
                    if i['ip'] != '':
                        logger.debug('Probing ' + i['ip'] + ' for state.')
                        agent_client.getMySQLServerState(i['ip'], 60000)
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