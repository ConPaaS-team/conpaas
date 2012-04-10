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

Created February, 2012

@author mrlarkin

'''


from threading import Thread, Lock, Timer, Event
from conpaas.core.expose import expose
from conpaas.core.http import HttpJsonResponse, HttpErrorResponse,\
                         HttpFileDownloadResponse, HttpRequest,\
                         FileUploadField, HttpError, _http_post
from conpaas.core.log import create_logger
from Cheetah.Template import Template

import os
import subprocess
import commands
from os.path import join

ETC='/etc/hadoop/conf/'

class MapReduceAgent():
    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser
                                # (hopefully the new service won't need anything extra)

      self.logger = create_logger(__name__)
      self.state = 'INIT'
      self.first_node = config_parser.get('agent', 'FIRST_NODE')
      self.mgmt_server = config_parser.get('agent', 'MGMT_SERVER')
      self.logger.info("Init done: first_node=%s, mgmt_server=%s", self.first_node, self.mgmt_server)

    @expose('GET')
    def check_agent_process(self, kwargs):
      """Check if agent process started - just return an empty response"""
      self.logger.info('called check_agent_process')
      if len(kwargs) != 0:
        return HttpErrorResponse('ERROR: Arguments unexpected')
      return HttpJsonResponse()

    @expose('POST')
    def startup(self, kwargs):
      self.logger.info('called startup with "%s" %s', self.first_node, kwargs)
      self.ip = kwargs.pop('ip')
      mgmt_server = ''
      
      if self.first_node == 'true':
        mgmt_server = self.ip
      else:
        mgmt_server = self.mgmt_server

      self._write_config(mgmt_server)

      try:
        Thread(target=self._do_startup, args=[]).start()
      except Exception as e:
        self.logger.debug('Exception in startup: %s', e)
      
      return HttpJsonResponse()

    def _do_startup(self):
      if self.first_node == 'true':
        (stdout, stderr) = subprocess.Popen(["sudo", "-u", "hdfs", "hadoop", "namenode", "-format"], \
                                              stdout=subprocess.PIPE).communicate()
        self.logger.info('Formatted namenode: %s; %s', stdout, stderr)
        
        (stdout, stderr) = subprocess.Popen(["/etc/init.d/hadoop-0.20-namenode", "start"], \
                                              stdout=subprocess.PIPE).communicate()
        self.logger.info('Started namenode: %s; %s', stdout, stderr)

        (stdout, stderr) = subprocess.Popen(["/etc/init.d/hadoop-0.20-secondarynamenode", "start"], \
                                              stdout=subprocess.PIPE).communicate()
        self.logger.info('Started secondarynamenode: %s; %s', stdout, stderr)
 
        (stdout, stderr) = subprocess.Popen(["sudo", "-u", "hdfs", "hadoop", "fs", "-chmod", "777", "/"], \
                                              stdout=subprocess.PIPE).communicate()
        self.logger.info('set hdfs writable: %s; %s', stdout, stderr)

        (stdout, stderr) = subprocess.Popen(["/etc/init.d/hadoop-0.20-jobtracker", "start"], \
                                              stdout=subprocess.PIPE).communicate()
        self.logger.info('Started jobtracker: %s; %s', stdout, stderr)

        (stdout, stderr) = subprocess.Popen(["/etc/init.d/hue", "start"], \
                                              stdout=subprocess.PIPE).communicate()
        self.logger.info('Started hue: %s; %s', stdout, stderr)


      (stdout, stderr) = subprocess.Popen(["/etc/init.d/hadoop-0.20-datanode", "start"], \
                                            stdout=subprocess.PIPE).communicate()
      self.logger.info('Started datanode: %s; %s', stdout, stderr)

      (stdout, stderr) = subprocess.Popen(["/etc/init.d/hadoop-0.20-tasktracker", "start"], \
                                            stdout=subprocess.PIPE).communicate()
      self.logger.info('Started tasktracker: %s; %s', stdout, stderr)
      self.state = 'RUNNING'
      self.logger.info('Agent is running')


    def _write_config(self, mgmt_server):
      self.logger.debug('called _write_config')
      try:
        tmpl = open(join(ETC, 'core-site.xml.tmpl')).read()
        cnfg = open(join(ETC, 'core-site.xml'), 'w')
        template = Template(tmpl, { 'HDFS_MASTER' : mgmt_server })
        cnfg.write(str(template))
        cnfg.close()

        tmpl = open(join(ETC, 'hadoop-metrics.properties.tmpl')).read()
        cnfg = open(join(ETC, 'hadoop-metrics.properties'), 'w')
        template = Template(tmpl, { 'GANGLIA_MASTER' : mgmt_server })
        cnfg.write(str(template))
        cnfg.close()

        tmpl = open(join(ETC, 'mapred-site.xml.tmpl')).read()
        cnfg = open(join(ETC, 'mapred-site.xml'), 'w')
        template = Template(tmpl, { 'MAPRED_MASTER' : mgmt_server, 'NR_MAPTASKS' : '2', 'NR_REDTASKS' : '2' })
        cnfg.write(str(template))
        cnfg.close()

        tmpl = open('/etc/hue/hue.ini.tmpl').read()
        cnfg = open('/etc/hue/hue.ini', 'w')
        template = Template(tmpl, { 'MAPRED_MASTER' : mgmt_server, 'HDFS_MASTER' : mgmt_server })
        cnfg.write(str(template))
        cnfg.close()

      except Exception as e:
        self.logger.debug('Exception in _write_config: %s', e)
      finally:
        self.logger.info('Hadoop configuration written.')
