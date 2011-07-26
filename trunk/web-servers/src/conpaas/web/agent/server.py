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
    self.callback_dict = {'GET': {}, 'POST': {}, 'UPLOAD': {}}
    
    from conpaas.web.agent import internals
    for http_method in internals.exposed_functions:
      for func_name in internals.exposed_functions[http_method]:
        self.register_method(http_method, func_name, getattr(internals, func_name))
  
  def register_method(self, http_method, func_name, callback):
    self.callback_dict[http_method][func_name] = callback
