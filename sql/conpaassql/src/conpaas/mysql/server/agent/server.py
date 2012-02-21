'''
Created on Jun 01, 2011

@author: ales
'''
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

from conpaas.web.http import AbstractRequestHandler
from conpaas.mysql.server.agent.internals import MySQLServer
from ConfigParser import ConfigParser
from conpaas.mysql.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

agentServer = None
'''
    Holds configuration for the Agent.
'''

'''
    Class AgentServer
'''
class AgentServer(HTTPServer, ThreadingMixIn):
    
    @mlog
    def __init__(self, server_address, mysql_agent, RequestHandlerClass=AbstractRequestHandler):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.callback_dict = {'GET': {}, 'POST': {}, 'UPLOAD': {}}
             
        from conpaas.mysql.server.agent import internals
        
        self.whitelist_addresses = []
        
        internals.agent = mysql_agent
        for http_method in internals.exposed_functions:
            for func_name in internals.exposed_functions[http_method]:
                logger.debug( 'Going to register ' + " " + http_method + " " +func_name)
                self.register_method(http_method, func_name, getattr(internals, func_name))
  
    @mlog
    def register_method(self, http_method, func_name, callback):
        self.callback_dict[http_method][func_name] = callback

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-p', '--port', type='int', default=60000, dest='port')
    parser.add_option('-b', '--bind', type='string', default='0.0.0.0', dest='address')
    parser.add_option('-c', '--config', type='string', default='./configuration.cnf', dest='config')    
    options, args = parser.parse_args()
    config_parser = ConfigParser()
    config_parser.read(options.config)
    mysql_agent = MySQLServer(config_parser)
    logger.debug( 'Starting the MySQL server at ', options.address, options.port)
    agentServer = AgentServer((options.address, options.port), mysql_agent)
    agentServer.serve_forever()
    
if __name__ == '__main__':
    main()        