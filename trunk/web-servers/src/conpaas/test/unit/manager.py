'''
Created on Mar 28, 2011

@author: ielhelw
'''
import unittest
import memcache
from subprocess import Popen
from tempfile import mkdtemp
from os import mkdir, getuid
from os.path import join
from shutil import rmtree
from threading import Thread
from time import sleep
from tarfile import TarFile
from random import randint

from conpaas.web.manager import server, internals, client
from conpaas.web.manager.config import Configuration, CodeVersion

from conpaas.test.mock import agentClient
from conpaas.test.mock.iaas import IaaSClient

# PATCH the real implementations with mock
server.IaaSClient = IaaSClient
internals.client = agentClient

def intersection(l1, l2):
  l3 = []
  for i in l1:
    if i in l2:
      l3.append(i)
  return l3

class Setup:
  def setUp(self):
    self.maxDiff = None
    self.mc_port = randint(6000, 6999)
    if getuid() != 0:
      self.mc_proc = Popen(['/usr/bin/memcached', '-p', str(self.mc_port)], close_fds=True)
    else:
      self.mc_proc = Popen(['/usr/bin/memcached', '-u', 'www-data', '-p', str(self.mc_port)], close_fds=True)
    sleep(2)
    self.mc = memcache.Client(['localhost:'+str(self.mc_port)])
    self.mc.set(internals.NODES, [str(i) for i in range(1,100)])
    self.mc.set(internals.CONFIG, Configuration())
    self.mc.set(internals.DEPLOYMENT_STATE, internals.S_INIT)
    
    self.server_port = randint(7000, 7999)
    self.dir = mkdtemp(prefix='conpaas-web-manager-', dir='/tmp')
    self.code_repo = join(self.dir, 'code-repo')
    mkdir(self.code_repo)
    
    self.server = server.DelpoymentManager(('0.0.0.0', self.server_port), 'localhost:'+str(self.mc_port), '', self.code_repo)
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
    ret = client.getState('localhost', self.server_port)
    while ret == {'opState': 'OK', 'state': transient}:
      sleep(1)
      ret = client.getState('localhost', self.server_port)
    self.assertEqual(ret, {'opState': 'OK', 'state': state})

class ManagerConfigTest(Setup, unittest.TestCase):
  
  def test_configCodeVersion(self):
    self._upload_codeVersions()
    self.assertEqual(client.getConfiguration('localhost', self.server_port),
                     {'opState': 'OK', 'codeVersionId': None, 'phpconf': {}})
    self.assertEqual(client.updateConfiguration('localhost', self.server_port, codeVersionId=self.id1),
                     {'opState': 'OK'})
    self.assertEqual(client.getConfiguration('localhost', self.server_port),
                     {'opState': 'OK', 'codeVersionId': self.id1, 'phpconf': {}})
  
  def test_configPHP(self):
    self.assertEqual(client.getConfiguration('localhost', self.server_port),
                     {'opState': 'OK', 'codeVersionId': None, 'phpconf': {}})
    self.assertEqual(client.updateConfiguration('localhost', self.server_port, phpconf={'file_uploads': '0'}),
                     {'opState': 'OK'})
    self.assertEqual(client.getConfiguration('localhost', self.server_port),
                     {'opState': 'OK', 'codeVersionId': None, 'phpconf': {'file_uploads': '0'}})
  
  def test_configCodeVersionAndPHP(self):
    self._upload_codeVersions()
    self.assertEqual(client.getConfiguration('localhost', self.server_port),
                     {'opState': 'OK', 'codeVersionId': None, 'phpconf': {}})
    self.assertEqual(client.updateConfiguration('localhost', self.server_port, codeVersionId=self.id2, phpconf={'file_uploads': '0'}),
                     {'opState': 'OK'})
    self.assertEqual(client.getConfiguration('localhost', self.server_port),
                     {'opState': 'OK', 'codeVersionId': self.id2, 'phpconf': {'file_uploads': '0'}})

  def test_startupShutdown(self):
    self.test_configCodeVersionAndPHP()
    self.assertEqual(client.startup('localhost', self.server_port),
                     {'opState': 'OK', 'state': internals.S_PROLOGUE})
    
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['php'])
    
    self.assertEqual(client.shutdown('localhost', self.server_port),
                     {'opState': 'OK', 'state': internals.S_EPILOGUE})
    
    self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def _upload_codeVersions(self):
    # create 2 archives
    version1 = join(self.dir, 'version1.tar')
    t = TarFile(name=version1, mode='w')
    t.add('/etc/passwd', arcname='index.html')
    t.close()
    version2 = join(self.dir, 'version2.tar')
    t = TarFile(name=version2, mode='w')
    t.add('/etc/group', arcname='index.html')
    t.close()
    # upload first
    ret = client.uploadCodeVersion('localhost', self.server_port, version1)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('codeVersionId' in ret)
    self.id1 = ret['codeVersionId']
    
    ret = client.listCodeVersions('localhost', self.server_port)
    self.assertEqual('OK', ret['opState'])
    self.assertEqual(1, len(ret['codeVersions']))
    self.assertEqual(ret['codeVersions'][self.id1]['codeVersionId'], self.id1)
    self.assertEqual(ret['codeVersions'][self.id1]['filename'], 'version1.tar')
    self.assertEqual(ret['codeVersions'][self.id1]['description'], '')
    
    # upload second
    ret = client.uploadCodeVersion('localhost', self.server_port, version2)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('codeVersionId' in ret)
    self.id2 = ret['codeVersionId']
    ret = client.listCodeVersions('localhost', self.server_port)
    self.assertEqual('OK', ret['opState'])
    self.assertEqual(2, len(ret['codeVersions']))
    self.assertEqual(ret['codeVersions'][self.id1]['codeVersionId'], self.id1)
    self.assertEqual(ret['codeVersions'][self.id1]['filename'], 'version1.tar')
    self.assertEqual(ret['codeVersions'][self.id1]['description'], '')
    self.assertEqual(ret['codeVersions'][self.id2]['codeVersionId'], self.id2)
    self.assertEqual(ret['codeVersions'][self.id2]['filename'], 'version2.tar')
    self.assertEqual(ret['codeVersions'][self.id2]['description'], '')


class ManagerScaleOutFromMinimalTest(Setup, unittest.TestCase):
  
  def setUp(self):
    Setup.setUp(self)
    version1 = join(self.code_repo, 'version1.tar')
    t = TarFile(name=version1, mode='w')
    t.add('/etc/passwd', arcname='index.html')
    t.close()
    
    config = Configuration()
    config.web_count = 1
    config.proxy_count = 0
    config.php_count = 0
    config.codeVersions['version1'] = CodeVersion('version1', 'version1.tar', 'tar')
    config.currentCodeVersion = 'version1'
    self.mc.set(internals.CONFIG, config)
  
  def test_request1Web(self, shutdown=True):
    client.startup('localhost', self.server_port)
    
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['php'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.addServiceNodes('localhost', self.server_port, web=1),
                     {'opState': 'OK'})
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('php' in ret and len(ret['php']) == 1)
    self.assertTrue('web' in ret and len(ret['web']) == 2)
    self.assertTrue(ret['web'][0] != ret['web'][1])
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    if shutdown:
      client.shutdown('localhost', self.server_port)
      self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def test_request1PHP(self, shutdown=True):
    client.startup('localhost', self.server_port)
    
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['php'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.addServiceNodes('localhost', self.server_port, php=1),
                     {'opState': 'OK'})
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('php' in ret and len(ret['php']) == 1 and proxyNode not in ret['php'])
    self.assertTrue('web' in ret and len(ret['web']) == 1 and ret['web'] == [proxyNode])
    
    if shutdown:
      client.shutdown('localhost', self.server_port)
      self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def test_request1PHPRequest1Web(self):
    self.test_request1PHP(shutdown=False)
    ret = client.listServiceNodes('localhost', self.server_port)
    phpNode = ret['php'][0]
    proxyNode = ret['proxy'][0] # web should be here as well
    self.assertTrue(phpNode != proxyNode)
    self.assertTrue(ret['web'] == [proxyNode])
    ret = client.addServiceNodes('localhost', self.server_port, web=1)
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('php' in ret and ret['php'] == [phpNode])
    self.assertTrue('web' in ret and len(ret['web']) == 2)
    self.assertTrue(ret['web'][0] != ret['web'][1])
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def test_request1PHPRequest1Proxy(self):
    self.test_request1PHP(shutdown=False)
    ret = client.listServiceNodes('localhost', self.server_port)
    phpNode = ret['php'][0]
    proxyNode = ret['proxy'][0] # web should be here as well
    self.assertTrue(phpNode != proxyNode)
    self.assertTrue(ret['web'] == [proxyNode])
    ret = client.addServiceNodes('localhost', self.server_port, proxy=1)
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('php' in ret and ret['php'] == [phpNode])
    self.assertTrue('web' in ret and len(ret['web']) == 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def test_request1Proxy(self, shutdown=True):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['php'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.addServiceNodes('localhost', self.server_port, proxy=1),
                     {'opState': 'OK'})
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('php' in ret and len(ret['php']) == 1 and proxyNode not in ret['php'])
    phpNode = ret['php'][0]
    self.assertTrue('web' in ret and len(ret['web']) == 1 and ret['web'] == [phpNode])
    
    if shutdown:
      client.shutdown('localhost', self.server_port)
      self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def test_request1ProxyRequest1Web(self):
    self.test_request1Proxy(shutdown=False)
    ret = client.listServiceNodes('localhost', self.server_port)
    oldWebNode = ret['php'][0] # web should be here as well
    self.assertTrue(ret['web'] == [oldWebNode])
    proxyNode = ret['proxy'][0]
    self.assertTrue(oldWebNode != proxyNode)
    ret = client.addServiceNodes('localhost', self.server_port, web=1)
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('php' in ret and len(ret['php']) == 1)
    self.assertTrue('web' in ret and len(ret['web']) == 2)
    self.assertTrue(ret['web'][0] != ret['web'][1])
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    client.shutdown('localhost', self.server_port)
    ret = client.getState('localhost', self.server_port)
    self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def test_request1ProxyRequest1PHP(self):
    self.test_request1Proxy(shutdown=False)
    ret = client.listServiceNodes('localhost', self.server_port)
    oldWebNode = ret['php'][0] # web should be here as well
    self.assertTrue(ret['web'] == [oldWebNode])
    proxyNode = ret['proxy'][0]
    self.assertTrue(oldWebNode != proxyNode)
    ret = client.addServiceNodes('localhost', self.server_port, php=1)
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    
    self.assertTrue('web' in ret and len(ret['web']) == 1)
    self.assertTrue(ret['web'] == [oldWebNode])
    
    self.assertTrue('php' in ret and len(ret['php']) == 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def test_request4Web5PHP(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['php'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.addServiceNodes('localhost', self.server_port, web=4, php=5),
                     {'opState': 'OK'})
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertEqual(len(ret['web']), 5)
    self.assertEqual(len(ret['php']), 5)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    client.shutdown('localhost', self.server_port)
    ret = client.getState('localhost', self.server_port)
    self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def test_request3Web2Proxy(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['php'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.addServiceNodes('localhost', self.server_port, web=3, proxy=2),
                     {'opState': 'OK'})
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertEqual(len(ret['proxy']), 2)
    self.assertEqual(len(ret['web']), 4)
    self.assertEqual(len(ret['php']), 1)
    
    self.assertTrue(proxyNode in ret['proxy'])
    
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def test_request3PHP2Proxy(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['php'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.addServiceNodes('localhost', self.server_port, php=3, proxy=2),
                     {'opState': 'OK'})
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertEqual(len(ret['proxy']), 2)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['php']), 3)
    
    self.assertTrue(proxyNode in ret['proxy'])
    
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)
  
  def test_request4Web5PHP2Proxy(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['php'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.addServiceNodes('localhost', self.server_port, web=4, php=5, proxy=2),
                     {'opState': 'OK'})
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertEqual(len(ret['proxy']), 2)
    self.assertEqual(len(ret['web']), 5)
    self.assertEqual(len(ret['php']), 5)
    
    self.assertTrue(proxyNode in ret['proxy'])
    
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(internals.S_EPILOGUE, internals.S_STOPPED)


class ManagerScaleInFrom1L1W1PTest(Setup, unittest.TestCase):
  
  def setUp(self):
    Setup.setUp(self)
    version1 = join(self.code_repo, 'version1.tar')
    t = TarFile(name=version1, mode='w')
    t.add('/etc/passwd', arcname='index.html')
    t.close()
    
    config = Configuration()
    config.web_count = 1
    config.proxy_count = 1
    config.php_count = 1
    config.codeVersions['version1'] = CodeVersion('version1', 'version1.tar', 'tar')
    config.currentCodeVersion = 'version1'
    self.mc.set(internals.CONFIG, config)
  
  def test_goToMinimal(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['php']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    proxyNode = ret['proxy'][0]
    
    client.removeServiceNodes('localhost', self.server_port, proxy=1, php=1)
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['php']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertEqual(ret['proxy'], ret['web'])
    self.assertEqual(ret['web'], ret['php'])
  
  def test_remove1Proxy(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['php']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    proxyNode = ret['proxy'][0]
    
    client.removeServiceNodes('localhost', self.server_port, proxy=1)
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['php']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertEqual(ret['proxy'], ret['web'])
    self.assertNotEqual(ret['proxy'], ret['php'])
  
  def test_remove1PHP(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['php']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    proxyNode = ret['proxy'][0]
    
    client.removeServiceNodes('localhost', self.server_port, php=1)
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['php']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertNotEqual(ret['proxy'], ret['web'])
    self.assertEqual(ret['web'], ret['php'])
  
  def test_removeMore(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['php']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    ret = client.removeServiceNodes('localhost', self.server_port, php=2)
    self.assertEqual(ret['opState'], 'ERROR')
    ret = client.removeServiceNodes('localhost', self.server_port, proxy=2)
    self.assertEqual(ret['opState'], 'ERROR')
    ret = client.removeServiceNodes('localhost', self.server_port, web=1)
    self.assertEqual(ret['opState'], 'ERROR')


class ManagerScaleInFrom1L2W1PTest(Setup, unittest.TestCase):
  def setUp(self):
    Setup.setUp(self)
    version1 = join(self.code_repo, 'version1.tar')
    t = TarFile(name=version1, mode='w')
    t.add('/etc/passwd', arcname='index.html')
    t.close()
    
    config = Configuration()
    config.web_count = 2
    config.proxy_count = 1
    config.php_count = 1
    config.codeVersions['version1'] = CodeVersion('version1', 'version1.tar', 'tar')
    config.currentCodeVersion = 'version1'
    self.mc.set(internals.CONFIG, config)
  
  def test_goToMinimal(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 2)
    self.assertEqual(len(ret['php']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    proxyNode = ret['proxy'][0]
    
    client.removeServiceNodes('localhost', self.server_port, proxy=1, php=1, web=1)
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['php']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertEqual(ret['proxy'], ret['web'])
    self.assertEqual(ret['web'], ret['php'])
  
  def test_removeMore(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 2)
    self.assertEqual(len(ret['php']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    ret = client.removeServiceNodes('localhost', self.server_port, proxy=1)
    self.assertEqual(ret['opState'], 'ERROR')
    ret = client.removeServiceNodes('localhost', self.server_port, php=1)
    self.assertEqual(ret['opState'], 'ERROR')
    ret = client.removeServiceNodes('localhost', self.server_port, web=2)
    self.assertEqual(ret['opState'], 'ERROR')
  
  def test_remove1Web(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(internals.S_PROLOGUE, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 2)
    self.assertEqual(len(ret['php']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])
    
    client.removeServiceNodes('localhost', self.server_port, web=1)
    self._waitTillState(internals.S_ADAPTING, internals.S_RUNNING)
    ret = client.listServiceNodes('localhost', self.server_port)
    self.assertTrue('opState' in ret and ret['opState'] == 'OK')
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('php' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['php']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['php']), [])
    self.assertEqual(intersection(ret['web'], ret['php']), [])


if __name__ == "__main__":
  unittest.main()
