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

class SQLServerRequestHandler(AbstractRequestHandler):
	
	def _dispatch(self, method, params):
		if 'action' not in params:
			self.send_custom_response(httplib.BAD_REQUEST, 'Did not specify "action"')
		elif params['action'] not in self.server.callback_dict[method]:
			self.send_custom_response(httplib.NOT_FOUND, 'action not found')
		else:
			callback_name = params['action']
			del params['action']
			self.send_custom_response(httplib.OK, json.dumps(self.server.callback_dict[method][callback_name](params)))

class ManagerServer(HTTPServer):
	
	def register_method(self, http_method, func_name, callback):
		self.callback_dict[http_method][func_name] = callback
	
	def __init__(self, server_address, iaas_config, RequestHandlerClass=SQLServerRequestHandler):
		HTTPServer.__init__(self, server_address, RequestHandlerClass)
		self.callback_dict = {'GET': {}, 'POST': {}}		
		from conpaas.mysql.server.manager import internals
		internals.iaas = IaaSClient(iaas_config)
		#internals.config = iaas_config
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
	print options.address, options.port
	d = ManagerServer((options.address, options.port), config_parser)
	d.serve_forever()