'''
Created on Mar 9, 2011

@author: ielhelw
@author: ales
'''

MYSQL_PORT = 3306

import time

iaas = None

class ServiceNode(object):
    def __init__(self, vmid, runMySQL=False):
        self.vmid = vmid
        self.ip = iaas.getVMInfo(vmid)['ip']
        self.isRunningMySQL = runMySQL
  
    def __repr__(self):
        return 'ServiceNode(vmid=%s, ip=%s, mysql=%s)' % (str(self.vmid), self.ip, str(self.isRunningMySQL))
  
    def __cmp__(self, other):
        if self.vmid == other.vmid: return 0
        elif self.vmid < other.vmid: return -1
        else: return 1

class MySQLConfiguration(object):
    def __init__(self, port=MYSQL_PORT, mysql=[]):
        self.port = port
        self.mysql_backends = mysql

class Configuration(object):
    '''Representation of the deployment configuration'''
    def __init__(self):
        self.mysql_count = 0
        self.serviceNodes = {}   
        self.mysql_config = MySQLConfiguration()
      
    def getMySQLServiceNodes(self):
        return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningMySQL ]
  
    def getMySQLTuples(self):
        return [ [serviceNode.ip, MYSQL_PORT] for serviceNode in self.serviceNodes.values() if serviceNode.isRunningMySQL ]
  
    def getMySQLIPs(self):
        return [ serviceNode.ip for serviceNode in self.serviceNodes.values() if serviceNode.isRunningMySQL ]
