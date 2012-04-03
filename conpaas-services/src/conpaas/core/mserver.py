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


Created on Mar 9, 2011

@author: ielhelw
'''
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

import memcache, httplib, inspect
from conpaas.core.http import AbstractRequestHandler
from conpaas.core import log
from conpaas.core.expose import exposed_functions
from conpaas.core.mservices import services


class ManagerRequestHandler(AbstractRequestHandler):

    def _do_dispatch(self, callback_type, callback_name, params):
      return self.server.callback_dict[callback_type][callback_name](self.server.manager, params)

    def _render_arguments(self, method, params):
      ret = '<p>Arguments:<table>'
      ret += '<tr><th>Method</th><td>' + method + '</td></tr>'
      for param in params:
        if isinstance(params[param], dict):
          ret += '<tr><th>' + param + '</th><td>Contents of: '
          ret += params[param].filename + '</td></tr>'
        else:
          ret += '<tr><th>' + param + '</th><td>' 
          ret += params[param] + '</td></tr>'
      ret += '</table></p>'
      return ret
  
    def send_action_missing(self, method, params):
      self.send_custom_response(httplib.BAD_REQUEST, '''<html>
    <head>
    <title>BAD REQUEST</title>
    </head>
    <body>
    <h1>ConPaaS PHP</h1>
    <p>No "action" specified.</p>
    <p>This URL is used to access the service manager directly.
    You may want to copy-paste the URL as a parameter 
    to the 'managerc.py' command-line utility.</p>
    ''' + self._render_arguments(method, params) + '</body></html>')
  
    def send_action_not_found(self, method, params):
      self.send_custom_response(httplib.NOT_FOUND, '''<html>
    <head>
    <title>ACTION NOT FOUND</title>
    </head>
    <body>
    <h1>ConPaaS PHP</h1>
    <p>The specified "action" was not found.</p>
    <p>You may want to review the list of supported actions 
    provided by the 'managerc.py' command-line utility.</p>
    ''' + self._render_arguments(method, params) + '</body></html>')


class ManagerServer(ThreadingMixIn, HTTPServer):

    """ 
    This class creates the requested manager. Each Service Manager class
    must fill in a dictionary named exposed_functions that contains the functions 
    visible from outside, i.e. callable by the frontend. This is done by using 
    the expose package. 
    """

    def __init__(self,
                 server_address,
                 config_parser,
                 **kwargs): 

      HTTPServer.__init__(self, server_address, ManagerRequestHandler)
      log.init(config_parser.get('manager', 'LOG_FILE'))

      self.whitelist_addresses = []

      # Instantiate the requested manager service class
      service_name = config_parser.get('manager', 'TYPE')
      try:
        module = __import__(services[service_name]['module'], \
                            globals(), locals(), ['*'])
      except ImportError:
        raise Exception('Could not import the module containing the manager class')   

      try:
        manager_class = getattr(module, services[service_name]['class'])
      except AttributeError:
        raise Exception('Could not get the manager class')

      self.manager = manager_class(config_parser, **kwargs)

      # Register the callable functions
      self.callback_dict = {'GET': {}, 'POST': {}, 'UPLOAD': {}}
      for http_method in exposed_functions:
        for func_name in exposed_functions[http_method]:
          self._register_method(http_method, func_name,
                      exposed_functions[http_method][func_name])

    def _register_method(self, http_method, func_name, callback):
      self.callback_dict[http_method][func_name] = callback
