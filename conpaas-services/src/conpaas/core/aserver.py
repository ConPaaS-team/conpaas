'''
Copyright (c) 2010-2012, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the <ORGANIZATION> nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.


Created on Jan 24, 2011

@author: ielhelw
'''

from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

from conpaas.core.http import AbstractRequestHandler
from conpaas.core import log
from conpaas.core.misc import verify_ip_or_domain
from conpaas.core.expose import exposed_functions
from conpaas.core.aservices import services

class AgentRequestHandler(AbstractRequestHandler):

    def _do_dispatch(self, callback_type, callback_name, params):
      return self.server.callback_dict[callback_type][callback_name](self.server.agent, params)


class AgentServer(ThreadingMixIn, HTTPServer):

    def __init__(self,
                 server_address,
                 config_parser,
                 **kwargs): 

      HTTPServer.__init__(self, server_address, AgentRequestHandler)
      log.init(config_parser.get('agent', 'LOG_FILE'))
      self.callback_dict = {'GET': {}, 'POST': {}, 'UPLOAD': {}}
 
      self.whitelist_addresses = []
      '''if config_parser.has_option('agent', 'IP_WHITE_LIST'):
        ip_list = config_parser.get('agent', 'IP_WHITE_LIST').split(',')
        try:
          for ip in ip_list:
            verify_ip_or_domain(ip)
            self.whitelist_addresses.append(ip)
        except Exception:
          raise Exception('Invalid IP_WHITE_LIST in configuration file')
      '''
      # Instantiate the requested agent service class
      service_type = config_parser.get('agent', 'TYPE')
      try:
        module = __import__(services[service_type]['module'], \
                            globals(), locals(), ['*'])
      except ImportError:
        raise Exception('Could no import the module containing the agent class')   

      try:
        agent_class = getattr(module, services[service_type]['class'])
      except AttributeError:
        raise Exception('Could not get the agent class')

      self.agent = agent_class(config_parser, **kwargs)

      # Register the callable functions
      self.callback_dict = {'GET': {}, 'POST': {}, 'UPLOAD': {}}
      for http_method in exposed_functions:
        for func_name in exposed_functions[http_method]:
          self._register_method(http_method, func_name,
                      exposed_functions[http_method][func_name])

    def _register_method(self, http_method, func_name, callback):
      self.callback_dict[http_method][func_name] = callback
