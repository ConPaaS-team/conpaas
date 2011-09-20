'''
Created on Jan 24, 2011

@author: ielhelw
'''

from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

from conpaas.web.http import AbstractRequestHandler
from conpaas.web import log
from conpaas.web.misc import verify_ip_or_domain

class AgentServer(ThreadingMixIn, HTTPServer):
  def __init__(self, server_address, config_parser, RequestHandlerClass=AbstractRequestHandler):
    HTTPServer.__init__(self, server_address, RequestHandlerClass)
    log.init(config_parser.get('agent', 'LOG_FILE'))
    self.callback_dict = {'GET': {}, 'POST': {}, 'UPLOAD': {}}
    
    self.whitelist_addresses = []
    if config_parser.has_option('agent', 'IP_WHITE_LIST'):
      ip_list = config_parser.get('agent', 'IP_WHITE_LIST').split(',')
      try:
        for ip in ip_list:
          verify_ip_or_domain(ip)
          self.whitelist_addresses.append(ip)
      except Exception:
        raise Exception('Invalid IP_WHITE_LIST in configuration file')
    
    from conpaas.web.agent import role
    role.init(config_parser)
    
    from conpaas.web.agent import internals
    internals.init(config_parser)
    for http_method in internals.exposed_functions:
      for func_name in internals.exposed_functions[http_method]:
        self.register_method(http_method, func_name, getattr(internals, func_name))
  
  def register_method(self, http_method, func_name, callback):
    self.callback_dict[http_method][func_name] = callback
