'''
Created on Feb 22, 2012

@author: ales
'''

import threading
import time
from conpaas.mysql.utils.log import get_logger_plus
from conpaas.web.http import _jsonrpc_post

logger, flog, mlog = get_logger_plus(__name__)

class MaintainAgentConnection( threading.Thread ):   
    '''
    Maintains connection to the manager.
    '''

    agent = None
    poll_interval = 30
    
    def __init__(self, agent=None, poll_interval = 30):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.poll_interval = poll_interval
        self.agent = agent

    def run ( self ):
        while True:
            logger.debug("Maintaining connection to %s " % self.agent.config.manager);
            params = {}
            params['state'] = self.agent.status()
            method = 'register_node'
            try:
                ret = _jsonrpc_post(self.agent.config.manager['ip'], self.agent.config.manager['port'], '/', method, params=params)
                logger.debug("Got answer from manager: %s" % str(ret))
            except Exception as e:
                logger.error('Exception: ' + str(e))
            time.sleep(self.poll_interval)