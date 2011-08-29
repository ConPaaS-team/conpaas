'''
Created on Jun 7, 2011

@author: ales
'''
from conpaas.log import create_logger
from conpaas.mysql.server.manager.config import Configuration, ManagerException,\
    E_ARGS_UNEXPECTED, ServiceNode
from threading import Thread

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
    
    def __init__(self, config):        
        logger.debug("Entering MySQLServerManager initialization")
        self.config = Configuration(config)                        
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
    sn.ip="127.0.0.1"    
    managerServer.config.addMySQLServiceNode(1,sn)
    return {
          'opState': 'OK',
          'sql': [ sn.vmid ]
    }
    
def createServiceNodeThread ():
    pass

