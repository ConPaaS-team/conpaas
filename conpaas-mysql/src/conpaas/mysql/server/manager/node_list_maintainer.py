'''
Created on Feb 22, 2012

@author: ales
'''
import threading
import time
from conpaas.mysql.utils.log import get_logger_plus
from conpaas.web.http import _jsonrpc_post, _jsonrpc_get
from conpaas.mysql.client import agent_client
import conpaas.mysql.server.manager.internals

logger, flog, mlog = get_logger_plus(__name__)

class MaintainAgentConnections( threading.Thread ):   
    '''
    Maintains connection to the manager.
    '''

    config = None
    poll_interval = 30
    
    def __init__(self, config=None, poll_interval = 30):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.poll_interval = poll_interval
        self.config = config

    def run ( self ):
        """
        It tries to call a function of the agent from the list of agents. If exception
        is thrown, it removes the agent from the list.
        
        :param poll_intervall: how many seconds to wait. 10 secods is default value.
        :type poll_interfvall: int
        """
        logger.debug('maintain nodes list: going to start polling')
        if conpaas.mysql.server.manager.internals.dummy_backend:
            pass
        else:
            while True:
                logger.debug("Starting the poll.")       
                nodes = self.config.getMySQLServiceNodes()
                logger.debug("The list : %s " % nodes)
                for node in nodes:
                    logger.debug("Trying node %s " % node)
                    try:
                        method = "get_server_state"
                        result = _jsonrpc_get(node.ip, node.port, '/', method)
                        logger.debug("node %s:%s is up with returned value %s" % (node.ip, node.port, str(result)))
                    except Exception as e:
                        logger.error('Exception: ' + str(e)) 
                        logger.debug("Node %s:%s is down. Removing from the list. " % (node.ip, node.port))
                        self.config.removeMySQLServiceNode(node.vmid)
                time.sleep(self.poll_interval)