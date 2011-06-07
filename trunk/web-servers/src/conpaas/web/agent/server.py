'''
Created on Jan 24, 2011

@author: ielhelw
'''

from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

from conpaas.web.http import AbstractRequestHandler
from conpaas import log
from ConfigParser import ConfigParser

class AgentServer(HTTPServer, ThreadingMixIn):
  def __init__(self, server_address, RequestHandlerClass=AbstractRequestHandler):
    HTTPServer.__init__(self, server_address, RequestHandlerClass)
    config_parser = ConfigParser()
    config_parser.add_section('manager')
    config_parser.set('manager', 'LOG_FILE', '/var/log/conpaas.log')
    log.init(config_parser)
    self.callback_dict = {'GET': {}, 'POST': {}}
    
    from conpaas.web.agent import internals
    for http_method in internals.exposed_functions:
      for func_name in internals.exposed_functions[http_method]:
        # print 'Going to register ', http_method, func_name
        self.register_method(http_method, func_name, getattr(internals, func_name))
  
  def register_method(self, http_method, func_name, callback):
    self.callback_dict[http_method][func_name] = callback


if __name__ == '__main__':
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option('-p', '--port', type='int', default=5555, dest='port')
  parser.add_option('-b', '--bind', type='string', default='0.0.0.0', dest='address')
  options, args = parser.parse_args()
  print options.address, options.port
  a = AgentServer((options.address, options.port))
  a.serve_forever()
