'''
Copyright (c) 2010-2013, Contrail consortium.
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
 3. Neither the name of the Contrail consortium nor the
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

Creaated February, 2012

@author tschuett

'''


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
