import memcache
import inspect
from subprocess import Popen
from tempfile import mkdtemp
from os import mkdir, getuid
from os.path import join
from shutil import rmtree
from threading import Thread
from time import sleep
from random import randint
from ConfigParser import ConfigParser

from conpaas.web.manager import client
from conpaas.web.manager.internal import InternalsBase

from mock.manager import FakeDeploymentManager


def init_test_env():
  from mock import agentClient
  from mock.iaas import IaaSClient
  from conpaas.web.manager import server, internal
  from conpaas.web.manager.internal import php, java
  # patch mock implementations
  server.IaaSClient = IaaSClient
  internal.client = agentClient
  php.client = agentClient
  java.client = agentClient

## Initialize the test environment
## This entails patching some components with mock implementations
init_test_env()

def intersection(l1, l2):
  l3 = []
  for i in l1:
    if i in l2:
      l3.append(i)
  return l3

class Setup:
  def setUp(self):
    if not hasattr(self, 'CONFIGURATION_CLASS') or not inspect.isclass(self.CONFIGURATION_CLASS):
      raise Exception('Expecting member %s.CONFIGURATION_CLASS to hold a configuration class' % (type(self).__name__))
    if not hasattr(self, 'TYPE') or not isinstance(self.TYPE, str):
      raise Exception('Expecting member %s.TYPE to hold a service type string' % (type(self).__name__))
    
    self.maxDiff = None
    self.mc_port = randint(6000, 6999)
    if getuid() != 0:
      self.mc_proc = Popen(['/usr/bin/memcached', '-p', str(self.mc_port)], close_fds=True)
    else:
      self.mc_proc = Popen(['/usr/bin/memcached', '-u', 'www-data', '-p', str(self.mc_port)], close_fds=True)
    sleep(2)
    self.mc = memcache.Client(['127.0.0.1:'+str(self.mc_port)])
    self.mc.set(InternalsBase.CONFIG, self.CONFIGURATION_CLASS())
    self.mc.set(InternalsBase.DEPLOYMENT_STATE, InternalsBase.S_INIT)
    
    self.server_port = randint(7000, 7999)
    self.dir = mkdtemp(prefix='conpaas-web-manager-', dir='/tmp')
    self.code_repo = join(self.dir, 'code-repo')
    mkdir(self.code_repo)
    
    config_parser = ConfigParser()
    config_parser.add_section('manager')
    config_parser.set('manager', 'LOG_FILE', '/dev/null')
    config_parser.set('manager', 'MEMCACHE_ADDR', '127.0.0.1:'+str(self.mc_port))
    config_parser.set('manager', 'CODE_REPO', self.code_repo)
    config_parser.set('manager', 'TYPE', self.TYPE)
    
    try:
      self.server = FakeDeploymentManager(('0.0.0.0', self.server_port),
                                             config_parser,
                                             '',
                                             reset_config=True)
    except Exception as e:
      self.mc_proc.terminate()
      self.mc_proc.wait()
      raise e
    self.t = Thread(target=self.server.serve_forever)
    self.t.start()
  
  def tearDown(self):
    self.mc_proc.terminate()
    self.mc_proc.wait()
    self.server.shutdown()
    self.server = None
    self.t.join()
    self.t = None
    rmtree(self.dir, ignore_errors=True)
    self.mc = None
  
  def _waitTillState(self, transient, state):
    ret = client.get_service_info('127.0.0.1', self.server_port)
    while ret['state'] == transient:
      sleep(1)
      ret = client.get_service_info('127.0.0.1', self.server_port)
    self.assertEqual(ret['state'], state)

