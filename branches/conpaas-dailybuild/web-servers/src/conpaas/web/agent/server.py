'''
Copyright (C) 2010-2011 Contrail consortium.

This file is part of ConPaaS, an integrated runtime environment 
for elastic cloud applications.

ConPaaS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ConPaaS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.


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
