# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread
from conpaas.core.expose import expose
from conpaas.core.https.server import HttpJsonResponse
from Cheetah.Template import Template
from conpaas.core.agent import BaseAgent
import subprocess
from os.path import join

ETC='/etc/hadoop/conf/'

class MapReduceAgent(BaseAgent):
    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser
                                # (hopefully the new service won't need anything extra)
      BaseAgent.__init__(self, config_parser)
      self.first_node = config_parser.get('agent', 'FIRST_NODE')
      self.mgmt_server = config_parser.get('agent', 'MGMT_SERVER')
      self.logger.info("Init done: first_node=%s, mgmt_server=%s", self.first_node, self.mgmt_server)

    @expose('POST')
    def startup(self, kwargs):
      self.logger.info('called startup with "%s" %s', self.first_node, kwargs)
      self.ip = kwargs.pop('ip')
      self.private_ip = kwargs.pop('private_ip')
      mgmt_server = ''
      
      if self.first_node == 'true':
        mgmt_server = self.private_ip
      else:
        mgmt_server = self.mgmt_server

      self._write_config(mgmt_server)

      try:
        Thread(target=self._do_startup, args=[]).start()
	#TODO: return only after everithing started
        #self._do_startup()
      except Exception as e:
        self.logger.debug('Exception in startup: %s', e)
      return HttpJsonResponse()

    def _do_startup(self):
      if self.first_node == 'true':
        (stdout, stderr) = subprocess.Popen(
            "su - hdfs -c '/usr/bin/hadoop namenode -format'",
            stdout=subprocess.PIPE, shell=True).communicate()

        self.logger.info('Formatted namenode: %s; %s', stdout, stderr)
        
        (stdout, stderr) = subprocess.Popen(["/etc/init.d/hadoop-0.20-namenode", "start"], \
                                              stdout=subprocess.PIPE).communicate()
        self.logger.info('Started namenode: %s; %s', stdout, stderr)

        (stdout, stderr) = subprocess.Popen(["/etc/init.d/hadoop-0.20-secondarynamenode", "start"], \
                                              stdout=subprocess.PIPE).communicate()
        self.logger.info('Started secondarynamenode: %s; %s', stdout, stderr)
 
        (stdout, stderr) = subprocess.Popen(
            "su - hdfs -c '/usr/bin/hadoop fs -chmod 777 /'",
            stdout=subprocess.PIPE, shell=True).communicate()

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
