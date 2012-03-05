'''
Created on Feb 22, 2012

@author: ales
'''
import threading
import time
from conpaas.mysql.utils.log import get_logger_plus
from conpaas.web.http import _jsonrpc_get

logger, flog, mlog = get_logger_plus(__name__)

class MaintainAgentConnections( threading.Thread ):   
    '''
    Maintains connection to the manager.
    '''

    poll_interval = 30
    manager = None
    dummy = None
    
    def __init__(self, manager = None, dummy = None):
        '''
        Constructor
        '''
        self.manager = manager
        threading.Thread.__init__(self)
        self.poll_interval = float(self.manager.configuration.poll_agents_timer)
        self.dummy = dummy
        logger.debug('setting poll interval to %s' % str(self.poll_interval))

    def run ( self ):
        """
        It tries to call a function of the agent from the list of agents. If exception
        is thrown, it removes the agent from the list.
        
        :param poll_intervall: how many seconds to wait. 10 secods is default value.
        :type poll_interfvall: int
        """
        logger.debug('maintain nodes list: going to start polling')
        if self.dummy:
            pass
        else:
            while True:
                logger.debug("Starting the poll.")       
                nodes = self.manager.configuration.getMySQLServiceNodes()
                logger.debug("The list : %s " % nodes)
                for node in nodes:
                    logger.debug("Trying node %s:%s " % (node.ip, node.port))
                    try:
                        method = "get_server_state"
                        result = _jsonrpc_get(node.ip, node.port, '/', method)
                        logger.debug("node %s:%s is up with returned value %s" % (node.ip, node.port, str(result)))
                    except Exception as e:
                        logger.error('Exception: ' + str(e)) 
                        logger.debug("Node %s:%s is down. Removing from the list. " % (node.ip, node.port))
                        self.manager.configuration.removeMySQLServiceNode(node.vmid)
                time.sleep(self.poll_interval)