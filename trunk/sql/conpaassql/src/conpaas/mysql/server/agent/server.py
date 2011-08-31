'''
Created on Jun 01, 2011

@author: ales
'''
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

from conpaas.web.http import AbstractRequestHandler
from conpaas.log import create_logger

logger = create_logger(__name__)
agentServer = None

'''
    Class AgentServer
'''
class AgentServer(HTTPServer, ThreadingMixIn):
    
    def __init__(self, server_address, RequestHandlerClass=AbstractRequestHandler):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.callback_dict = {'GET': {}, 'POST': {}}
    
        from conpaas.mysql.server.agent import internals
        for http_method in internals.exposed_functions:
            for func_name in internals.exposed_functions[http_method]:
                logger.debug( 'Going to register ' + " " + http_method + " " +func_name)
                self.register_method(http_method, func_name, getattr(internals, func_name))
  
    def register_method(self, http_method, func_name, callback):
        self.callback_dict[http_method][func_name] = callback

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-p', '--port', type='int', default=60000, dest='port')
    parser.add_option('-b', '--bind', type='string', default='0.0.0.0', dest='address')
    options, args = parser.parse_args()
    print 'Starting the MySQL server at ', options.address, options.port
    agentServer = AgentServer((options.address, options.port))
    agentServer.serve_forever()    