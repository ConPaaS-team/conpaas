'''
Created on Mar 9, 2011

    Holds configuration for the ConPaaS SQL Server Manager.

@author: ales
'''
from conpaas.log import create_logger

import ConfigParser
import os
from conpaas.iaas import DummyONEDriver

MYSQL_PORT = 3306
CONFIGURATION_FILE=os.getcwd() + "/sql_manager_configuration.cnf"

E_ARGS_UNEXPECTED = 0
E_CONFIG_READ_FAILED = 1
E_CONFIG_NOT_EXIST=2
E_UNKNOWN=3
E_ARGS_MISSING = 4
E_ARGS_INVALID=5
E_STATE_ERROR=6

E_STRINGS = [  
  'Unexpected arguments %s',
  'Unable to open configuration file: %s',
  'Configuration file does not exist: %s',
  'Unknown error.',
  'Missing argument: %s',
  'Invalid argument: %s',
  'Service in wrong state'
]

iaas = None

logger = create_logger(__name__)

class ManagerException(Exception):
    
    def __init__(self, code, *args, **kwargs):
        self.code = code
        self.args = args
        if 'detail' in kwargs:
            self.message = '%s DETAIL:%s' % ( (E_STRINGS[code] % args), str(kwargs['detail']) )
        else:
            self.message = E_STRINGS[code] % args

class ServiceNode(object):
    
    def __init__(self, vm, runMySQL=False):
        self.vmid = vm['id']
        self.ip = vm['ip']
        self.name = vm['name']
        self.state = vm['state']
        self.isRunningMySQL = runMySQL
        self.isRunningProxy = False
        self.isRunningBackend= False        
        self.isRunningWeb= False
        self.port = 60000
  
    def __repr__(self):
        return 'ServiceNode(vmid=%s, ip=%s, mysql=%s)' % (str(self.vmid), self.ip, str(self.isRunningMySQL))
  
    def __cmp__(self, other):
        if self.vmid == other.vmid: return 0
        elif self.vmid < other.vmid: return -1
        else: return 1

class Configuration(object):
    
    dummy_backend = False
    
    def __read_config(self,config, _dummy_backend = False):
        logger.debug("Entering read_config")
        try:
            logger.debug("Trying to get params from configuration file ")
            self.driver = config.get("iaas", "DRIVER")
            if self.driver == "OPENNEBULA_XMLRPC":
                self.xmlrpc_conn_location = config.get("iaas", "OPENNEBULA_URL")
                self.conn_password = config.get("iaas", "OPENNEBULA_USER")
                self.conn_username = config.get("iaas", "OPENNEBULA_PASSWORD")
            logger.debug("Got configuration parameters")
        except ConfigParser.Error, err:
            ex = ManagerException(E_CONFIG_READ_FAILED, str(err))
            logger.critical(ex.message)
        except IOError, err:
            ex = ManagerException(E_CONFIG_NOT_EXIST, str(err))
            logger.critical(ex.message)  
        logger.debug("Leaving read_config")
    
    '''Representation of the deployment configuration'''
    def __init__(self, configuration, _dummy_backend = False):        
        self.dummy_backend=_dummy_backend        
        self.mysql_count = 0
        self.serviceNodes = {}        
        self.__read_config(configuration, _dummy_backend)
      
    def getMySQLServiceNodes(self):
        return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningMySQL ]
        #return self.serviceNodes
  
    def getMySQLTuples(self):
        return [ [serviceNode.ip, MYSQL_PORT] for serviceNode in self.serviceNodes.values() if serviceNode.isRunningMySQL ]
  
    def getMySQLIPs(self):
        return [ serviceNode.ip for serviceNode in self.serviceNodes.values() if serviceNode.isRunningMySQL ]
    
    '''
      Add new Service Node to the server (configuration).
      @param accesspoint: new VM
    '''
    def addMySQLServiceNode(self, accesspoint):
        logger.debug('Entering addMySQLServiceNode') 
        self.serviceNodes[accesspoint['id']]=ServiceNode(accesspoint, True)
        self.mysql_count+=1
        logger.debug('Exiting addMySQLServiceNode')
        
    '''
      Remove Service Node to the server (configuration).
    '''
    def removeMySQLServiceNode(self, vmid):
        del self.serviceNodes[vmid]
        self.mysql_count-=1            