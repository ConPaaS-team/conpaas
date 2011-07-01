'''
Created on Mar 9, 2011

@author: ielhelw
'''
from BaseHTTPServer import HTTPServer
from os.path import exists

import memcache, httplib
from conpaas.iaas import IaaSClient
from conpaas.web.http import AbstractRequestHandler
from conpaas import log


class ManagerRequestHandler(AbstractRequestHandler):
  def _render_arguments(self, method, params):
    ret = '<p>Arguments:<table>'
    ret += '<tr><th>Method</th><td>' + method + '</td></tr>'
    for param in params:
      if isinstance(params[param], dict):
        ret += '<tr><th>' + param + '</th><td>Contents of: ' + params[param].filename + '</td></tr>'
      else:
        ret += '<tr><th>' + param + '</th><td>' + params[param] + '</td></tr>'
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
You may want to copy-paste the URL as a parameter to the 'managerc.py' command-line utility.</p>
''' + self._render_arguments(method, params) + '</body></html>')
  
  def send_action_not_found(self, method, params):
    self.send_custom_response(httplib.NOT_FOUND, '''<html>
<head>
<title>ACTION NOT FOUND</title>
</head>
<body>
<h1>ConPaaS PHP</h1>
<p>The specified "action" was not found.</p>
<p>You may want to review the list of supported actions provided by the 'managerc.py' command-line utility.</p>
''' + self._render_arguments(method, params) + '</body></html>')


class DelpoymentManager(HTTPServer):
  def __init__(self, server_address, memcache_addr, config_parser, code_repository, scalaris_addr, RequestHandlerClass=ManagerRequestHandler):
    HTTPServer.__init__(self, server_address, RequestHandlerClass)
    log.init(config_parser)
    self.memcache = memcache.Client([memcache_addr])
    self.iaas = IaaSClient(config_parser)
    from conpaas.web.manager import internals
    internals.init(self.memcache, self.iaas, code_repository, config_parser.get('manager', 'LOG_FILE'))
    from conpaas.web.manager import config
    config.memcache = self.memcache
    config.iaas = self.iaas
    self.callback_dict = {'GET': {}, 'POST': {}}
    
    for http_method in internals.exposed_functions:
      for func_name in internals.exposed_functions[http_method]:
        self.register_method(http_method, func_name, getattr(internals, func_name))
    internals.createInitialCodeVersion()
    internals.registerScalaris(scalaris_addr)
  
  def register_method(self, http_method, func_name, callback):
    self.callback_dict[http_method][func_name] = callback

if __name__ == '__main__':
  from optparse import OptionParser
  from ConfigParser import ConfigParser
  import sys
  
  parser = OptionParser()
  parser.add_option('-p', '--port', type='int', default=6666, dest='port')
  parser.add_option('-b', '--bind', type='string', default='0.0.0.0', dest='address')
  parser.add_option('-c', '--config', type='string', default='./config.cfg', dest='config')
  parser.add_option('-s', '--scalaris', type='string', default=None, dest='scalaris')
  options, args = parser.parse_args()
  
  if options.scalaris == None:
    print >>sys.stderr, 'Scalaris IP is required'
    sys.exit(1)
  
  if not exists(options.config):
    print >>sys.stderr, 'Failed to find configuration file'
    sys.exit(1)
  
  config_parser = ConfigParser()
  config_parser.read(options.config)
  if not config_parser.has_section('manager')\
  or not config_parser.has_option('manager', 'MEMCACHE_ADDR')\
  or not config_parser.has_option('manager', 'CODE_REPO')\
  or not config_parser.has_option('manager', 'LOG_FILE')\
  or not config_parser.has_option('manager', 'BOOTSTRAP'):
    print >>sys.stderr, 'Missing configuration variables for section "manager"'
    sys.exit(1)
  
  print options.address, options.port
  d = DelpoymentManager((options.address, options.port), config_parser.get('manager', 'MEMCACHE_ADDR'), config_parser, config_parser.get('manager', 'CODE_REPO'), options.scalaris)
  d.serve_forever()

