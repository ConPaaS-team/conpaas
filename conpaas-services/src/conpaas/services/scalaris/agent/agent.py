# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from conpaas.core.expose import expose
from conpaas.core.https.server import HttpJsonResponse, HttpError
from conpaas.core.agent import BaseAgent
from Cheetah.Template import Template

import subprocess
from os.path import join
from conpaas.services.scalaris.agent import scalaris

ETC = '/etc/scalaris/'

class ScalarisAgent(BaseAgent):
    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser
                                # (hopefully the new service won't need anything extra)
      BaseAgent.__init__(self, config_parser)
      self.config_template = join(ETC, 'scalaris.local.cfg.tmpl')
      self.config_file = join(ETC, 'scalaris.local.cfg')
      self.first_node = config_parser.get('agent', 'FIRST_NODE')
      self.known_hosts = config_parser.get('agent', 'KNOWN_HOSTS')
      self.mgmt_server = config_parser.get('agent', 'MGMT_SERVER')

    @expose('GET')
    def get_service_info(self, kwargs):
      self.logger.info('called get_service_info')
      try:
          params = []
          json = scalaris.JSONConnection()
          res = json.call('get_service_info', params)
          return HttpJsonResponse(res)
      except HttpError as e:
          self.logger.info('exception in get_service_info: %s', e)
          return HttpJsonResponse()
      except Exception as e:
          self.logger.info('exception in get_service_info: %s', e)
          return HttpJsonResponse()
      except:
          self.logger.info('unknown exception in get_service_info')
          return HttpJsonResponse()

    @expose('POST')
    def startup(self, kwargs):
      self.logger.info('called startup with "%s" %s', self.first_node, kwargs)
      self.ip = kwargs.pop('ip')
      known_hosts = ""
      mgmt_server = ""
      my_erlang_addr = self.ip.replace('.', ',')
      if self.first_node == 'true':
          flags = '-f -m -s'
          known_hosts = '[{{' + my_erlang_addr + '}, 14195, service_per_vm}]'
          mgmt_server = '{{' + my_erlang_addr + '}, 14195, mgmt_server}'
      else:
          flags = '-s'
          known_hosts = self.known_hosts
          mgmt_server = self.mgmt_server
      self.logger.info('writing config')
      self._write_config(known_hosts, mgmt_server)
      dist_erlang_port = ' -e "-kernel inet_dist_listen_min 14194 inet_dist_listen_max 14194"'
      cmd_wo_d = '/usr/bin/scalarisctl -n node@' + self.ip + ' -p 14195 -y 8000 ' + flags + dist_erlang_port + ' start'
      (stdout, stderr) = subprocess.Popen(["screen", "-d", "-m", "/bin/bash", "-c", cmd_wo_d], \
                                              stdout=subprocess.PIPE).communicate()
      self.logger.info('Started scalaris: %s; %s', stdout, stderr)
      self.state = 'RUNNING'
      self.logger.info('Agent is running')
      return HttpJsonResponse()

    @expose('POST')
    def graceful_leave(self, kwargs):
      self.logger.info('called graceful_leave')
      vm = scalaris.ScalarisVM()
      res = vm.shutdownVM()
      self.logger.info('called shutdownVM %s', res)
      return HttpJsonResponse(res)

    def _write_config(self, known_hosts, mgmt_server):
        tmpl = open(self.config_template).read()
        conf_fd = open(self.config_file, 'w')
        template = Template(tmpl, {
                'known_hosts'      : known_hosts,
                'mgmt_server'      : mgmt_server,
                })
        conf_fd.write(str(template))
        conf_fd.close()
        self.logger.info('Scalaris configuration written to %s', self.config_file)
