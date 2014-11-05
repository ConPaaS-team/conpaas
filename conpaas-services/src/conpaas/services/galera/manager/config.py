# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from conpaas.core.log import create_logger
from conpaas.core.node import ServiceNode

E_ARGS_UNEXPECTED = 0
E_CONFIG_READ_FAILED = 1
E_CONFIG_NOT_EXIST = 2
E_UNKNOWN = 3
E_ARGS_MISSING = 4
E_ARGS_INVALID = 5
E_STATE_ERROR = 6

E_STRINGS = ['Unexpected arguments %s',
             'Unable to open configuration file: %s',
             'Configuration file does not exist: %s',
             'Unknown error.',
             'Missing argument: %s',
             'Invalid argument: %s',
             'Service in wrong state'
             ]


class SQLServiceNode(ServiceNode):
    '''
    Holds information on service nodes.

    :param vm: Service node id
    :type vm: array
    :param runMySQL: Indicator if service node is running MySQL
    :type runMySQL: boolean

    '''
    isNode=True
    isGlb_node=False;
    def __init__(self, node):
        ServiceNode.__init__(self, node.vmid,
                             node.ip, node.private_ip,
                             node.cloud_name)
        self.port = 5555

    '''String representation of the ServiceNode.
    @return: returns service nodes information. Id ip and if mysql is running on this service node.'''

    def __repr__(self):
        return 'ServiceNode(ip=%s, port=%s)' % (self.ip, self.port)


class GLBServiceNode(ServiceNode):
    '''
    Holds information on Galera Balancer nodes.

    :param vm: Service node id
    :type vm: array
    :param runMySQL: Indicator if service node is running MySQL
    :type runMySQL: boolean

    '''
    isGlb_node=True
    isNode=False
    def __init__(self, node):
        ServiceNode.__init__(self, node.vmid,
                             node.ip, node.private_ip,
                             node.cloud_name)
        self.port = 5555

    '''String representation of the ServiceNode.
    @return: returns service nodes information. Id ip and if mysql is running on this service node.'''

    def __repr__(self):
        return 'GLBServiceNode(ip=%s, port=%s)' % (self.ip, self.port)


class Configuration(object):

    MYSQL_PORT = 3306
    GLB_PORT = 3307

    # The port on which the agent listens
    AGENT_PORT = 5555

    '''Galera Load Balancer Nodes'''
    glb_service_nodes = {}
    serviceNodes = {}

    def __init__(self, configuration):
        '''Representation of the deployment configuration'''
        self.logger = create_logger(__name__)
        self.mysql_count = 0
        self.serviceNodes = {}
        self.glb_service_nodes = {}

    def getMySQLTuples(self):
        '''Returns the list of service nodes as tuples <IP, PORT>.'''
        return [[serviceNode.ip, self.MYSQL_PORT]
                for serviceNode in self.serviceNodes.values()]

    ''' Returns the list of IPs of MySQL instances'''
    def get_nodes_addr(self):
        return [serviceNode.ip for serviceNode in self.serviceNodes.values()]

    def get_nodes(self):
        """ Returns the list of MySQL nodes."""
        return [serviceNode for serviceNode in self.serviceNodes.values()]

    def get_glb_nodes(self):
        ''' Returns the list of GLB nodes'''
        return [serviceNode for serviceNode in self.glb_service_nodes.values()]

    def getMySQLNode(self, id):
	self.logger.debug('Entering getMysqlNodes id= %s ' % id)
	if self.serviceNodes.has_key(id) :
        	node = self.serviceNodes[id]
	else:
		node = self.glb_service_nodes[id]
	self.logger.debug('Exit getMySQlNode node = %s' %node)
	return node

    def addGLBServiceNodes(self, nodes):
        '''
        Add new GLB Node to the server (configuration).
        '''
        self.logger.debug('Entering addGLBServiceNodes')
        for node in nodes:
            self.glb_service_nodes[node.id] = GLBServiceNode(node)
        self.logger.debug('Exiting addGLBServiceNodes')

    def removeGLBServiceNode(self, id):
        '''
          Remove GLB Node to the server (configuration).
        '''
        del self.glb_service_nodes[id]

    def remove_glb_nodes(self, nodes):
        for node in nodes:
            del self.glb_service_nodes[node.id]

    def addMySQLServiceNodes(self, nodes):
        '''
          Add new Service Node to the server (configuration).
        '''
        for node in nodes:
            self.serviceNodes[node.id] = SQLServiceNode(node)

    def removeMySQLServiceNode(self, id):
        '''
          Remove Service Node to the server (configuration).
        '''
        del self.serviceNodes[id]

    def remove_nodes(self, nodes):
         for node in nodes:
		self.logger.debug('RemoveNodes node.id=%s' % node.id )
         	self.logger.debug('RemoveNodes node=%s' % node )
         	self.logger.debug('RemoveNodes self.ServiceNodes=%s' % self.serviceNodes )
	    	if self.serviceNodes.has_key(node.id) :
			self.serviceNodes.pop(node.id, None)
	    	else : 
			self.glb_service_nodes.pop(node.id,None)
