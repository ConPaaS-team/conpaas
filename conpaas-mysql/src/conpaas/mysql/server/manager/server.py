'''
Created on Jun 7, 2011

@author: ales
'''
from BaseHTTPServer import HTTPServer
from conpaas.web.http import AbstractRequestHandler
import httplib
import json
from conpaas.mysql.server.manager import internals
from conpaas.iaas import IaaSClient
from conpaas.mysql.server.manager.internals import MySQLServerManager
from SocketServer import ThreadingMixIn
from conpaas.log import log_dir_path
from conpaas.mysql.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class SQLServerRequestHandler(AbstractRequestHandler):
	
	
	#===========================================================================
	# def _dispatch(self, method, params):
	#	if 'action' not in params:
	#		self.send_custom_response(httplib.BAD_REQUEST, 'Did not specify "action"')
	#	elif params['action'] not in self.server.callback_dict[method]:
	#		self.send_custom_response(httplib.NOT_FOUND, 'action not found')
	#	else:
	#		callback_name = params['action']
	#		del params['action']
	#		self.send_custom_response(httplib.OK, json.dumps(self.server.callback_dict[method][callback_name](params)))
	#===========================================================================

	@mlog
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
	<h1>ConPaaS MySQL</h1>
	<p>No "action" specified.</p>
	<p>This URL is used to access the service manager directly.
	You may want to copy-paste the URL as a parameter to the 'managerc.py' command-line utility.</p>
	''' + self._render_arguments(method, params) + '</body></html>')
	
	@mlog
	def send_action_not_found(self, method, params):
	    self.send_custom_response(httplib.NOT_FOUND, '''<html>
	<head>
	<title>ACTION NOT FOUND</title>
	</head>
	<body>
	<h1>ConPaaS MySQL</h1>
	<p>The specified "action" was not found.</p>
	<p>You may want to review the list of supported actions provided by the 'managerc.py' command-line utility.</p>
	''' + self._render_arguments(method, params) + '</body></html>')

#class MultithreadedHTTPServer(ThreadingMixIn, HTTPServer):
#	pass

class ManagerServer(ThreadingMixIn, HTTPServer):
		
	def register_method(self, http_method, func_name, callback):
		self.callback_dict[http_method][func_name] = callback
	
	@mlog
	def __init__(self, server_address, iaas_config, RequestHandlerClass=SQLServerRequestHandler):
		HTTPServer.__init__(self, server_address, RequestHandlerClass)		
		self.callback_dict = {'GET': {}, 'POST': {}, 'UPLOAD':{}}		
		from conpaas.mysql.server.manager import internals
		internals.iaas = IaaSClient(iaas_config)				
		self.whitelist_addresses = []
		
		internals.managerServer=MySQLServerManager(iaas_config)
		for http_method in internals.exposed_functions:
			for func_name in internals.exposed_functions[http_method]:
				print 'Going to register ', http_method, func_name
				self.register_method(http_method, func_name, getattr(internals, func_name))
		
if __name__ == '__main__':
	from optparse import OptionParser
	from ConfigParser import ConfigParser	
	parser = OptionParser()
	parser.add_option('-p', '--port', type='int', default=50000, dest='port')
	parser.add_option('-b', '--bind', type='string', default='0.0.0.0', dest='address')
	parser.add_option('-c', '--config', type='string', default='./config.cfg', dest='config')  		
	options, args = parser.parse_args()
	config_parser = ConfigParser()
	config_parser.read(options.config)	
	logger.debug("Bind ip %s, port %s" % (options.address, str(options.port)))
	config_parser.add_section('_manager')
	config_parser.set('_manager', 'ip', options.address)
	config_parser.set('_manager', 'port', str(options.port))
	d = ManagerServer((options.address, options.port), config_parser)
	d.serve_forever()