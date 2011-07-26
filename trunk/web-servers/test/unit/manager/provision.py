'''
Created on Mar 28, 2011

@author: ielhelw
'''
import unittest
from os.path import join
from tarfile import TarFile

from conpaas.web.manager.client import ClientError
from conpaas.web.manager import client
from conpaas.web.manager.internal import InternalsBase
from conpaas.web.manager.config import CodeVersion, PHPServiceConfiguration

from unit.manager import Setup, intersection

class ManagerScaleOutFromMinimalTest(Setup, unittest.TestCase):
  CONFIGURATION_CLASS = PHPServiceConfiguration
  TYPE = 'FAKE'
  def setUp(self):
    Setup.setUp(self)
    version1 = join(self.code_repo, 'version1.tar')
    t = TarFile(name=version1, mode='w')
    t.add('/etc/passwd', arcname='index.html')
    t.close()
    
    config = PHPServiceConfiguration()
    config.web_count = 1
    config.proxy_count = 0
    config.backend_count = 0
    config.codeVersions['version1'] = CodeVersion('version1', 'version1.tar', 'tar')
    config.currentCodeVersion = 'version1'
    self.mc.set(InternalsBase.CONFIG, config)
  
  def test_request1Web(self, shutdown=True):
    client.startup('localhost', self.server_port)
    
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertRaises(ClientError, client.add_nodes, 'localhost', self.server_port, web=1)
    if shutdown:
      client.shutdown('localhost', self.server_port)
      self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1Backend(self, shutdown=True):
    client.startup('localhost', self.server_port)
    
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('localhost', self.server_port, backend=1),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('backend' in ret and len(ret['backend']) == 1 and proxyNode not in ret['backend'])
    self.assertTrue('web' in ret and len(ret['web']) == 1 and ret['web'] == [proxyNode])
    
    if shutdown:
      client.shutdown('localhost', self.server_port)
      self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1BackendRequest1Web(self):
    self.test_request1Backend(shutdown=False)
    ret = client.list_nodes('localhost', self.server_port)
    backendNode = ret['backend'][0]
    proxyNode = ret['proxy'][0] # web should be here as well
    self.assertTrue(backendNode != proxyNode)
    self.assertTrue(ret['web'] == [proxyNode])
    self.assertRaises(ClientError, client.add_nodes, 'localhost', self.server_port, web=1)
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1BackendRequest1Proxy(self):
    self.test_request1Backend(shutdown=False)
    ret = client.list_nodes('localhost', self.server_port)
    backendNode = ret['backend'][0]
    proxyNode = ret['proxy'][0] # web should be here as well
    self.assertTrue(backendNode != proxyNode)
    self.assertTrue(ret['web'] == [proxyNode])
    ret = client.add_nodes('localhost', self.server_port, proxy=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('backend' in ret and ret['backend'] == [backendNode])
    self.assertTrue('web' in ret and len(ret['web']) == 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1Proxy(self, shutdown=True):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('localhost', self.server_port, proxy=1),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('backend' in ret and len(ret['backend']) == 1 and proxyNode not in ret['backend'])
    backendNode = ret['backend'][0]
    self.assertTrue('web' in ret and len(ret['web']) == 1 and ret['web'] == [backendNode])
    
    if shutdown:
      client.shutdown('localhost', self.server_port)
      self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1ProxyRequest1Web(self):
    self.test_request1Proxy(shutdown=False)
    ret = client.list_nodes('localhost', self.server_port)
    oldWebNode = ret['backend'][0] # web should be here as well
    self.assertTrue(ret['web'] == [oldWebNode])
    proxyNode = ret['proxy'][0]
    self.assertTrue(oldWebNode != proxyNode)
    self.assertRaises(ClientError, client.add_nodes, 'localhost', self.server_port, web=1)
    client.shutdown('localhost', self.server_port)
    ret = client.get_service_info('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1ProxyRequest1Backend(self):
    self.test_request1Proxy(shutdown=False)
    ret = client.list_nodes('localhost', self.server_port)
    oldWebNode = ret['backend'][0] # web should be here as well
    self.assertTrue(ret['web'] == [oldWebNode])
    proxyNode = ret['proxy'][0]
    self.assertTrue(oldWebNode != proxyNode)
    ret = client.add_nodes('localhost', self.server_port, backend=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    
    self.assertTrue('web' in ret and len(ret['web']) == 1)
    self.assertTrue(ret['web'] == [oldWebNode])
    
    self.assertTrue('backend' in ret and len(ret['backend']) == 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1Proxy4Web5Backend(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('localhost', self.server_port, proxy=1, web=4, backend=5),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertEqual(len(ret['web']), 5)
    self.assertEqual(len(ret['backend']), 5)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.shutdown('localhost', self.server_port)
    ret = client.get_service_info('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request3Web2Proxy1Backend(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('localhost', self.server_port, web=3, proxy=2, backend=1),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertEqual(len(ret['proxy']), 2)
    self.assertEqual(len(ret['web']), 4)
    self.assertEqual(len(ret['backend']), 1)
    
    self.assertTrue(proxyNode in ret['proxy'])
    
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request3Backend2Proxy(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('localhost', self.server_port, backend=3, proxy=2),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertEqual(len(ret['proxy']), 2)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 3)
    
    self.assertTrue(proxyNode in ret['proxy'])
    
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request4Web5Backend2Proxy(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('localhost', self.server_port, web=4, backend=5, proxy=2),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertEqual(len(ret['proxy']), 2)
    self.assertEqual(len(ret['web']), 5)
    self.assertEqual(len(ret['backend']), 5)
    
    self.assertTrue(proxyNode in ret['proxy'])
    
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.shutdown('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)


class ManagerScaleInFrom1Proxy1Web1BackendTest(Setup, unittest.TestCase):
  CONFIGURATION_CLASS = PHPServiceConfiguration
  TYPE = 'FAKE'
  def setUp(self):
    Setup.setUp(self)
    version1 = join(self.code_repo, 'version1.tar')
    t = TarFile(name=version1, mode='w')
    t.add('/etc/passwd', arcname='index.html')
    t.close()
    
    config = PHPServiceConfiguration()
    config.web_count = 1
    config.proxy_count = 1
    config.backend_count = 1
    config.codeVersions['version1'] = CodeVersion('version1', 'version1.tar', 'tar')
    config.currentCodeVersion = 'version1'
    self.mc.set(InternalsBase.CONFIG, config)
  
  def test_goToMinimal(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    proxyNode = ret['proxy'][0]
    
    client.remove_nodes('localhost', self.server_port, proxy=1, backend=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertEqual(ret['proxy'], ret['web'])
    self.assertEqual(ret['web'], ret['backend'])
  
  def test_remove1Proxy(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    proxyNode = ret['proxy'][0]
    
    client.remove_nodes('localhost', self.server_port, proxy=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertEqual(ret['proxy'], ret['web'])
    self.assertNotEqual(ret['proxy'], ret['backend'])
  
  def test_remove1Backend(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    proxyNode = ret['proxy'][0]
    
    client.remove_nodes('localhost', self.server_port, backend=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertNotEqual(ret['proxy'], ret['web'])
    self.assertEqual(ret['web'], ret['backend'])
  
  def test_removeMore(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    self.assertRaises(ClientError, client.remove_nodes, 'localhost', self.server_port, backend=2)
    self.assertRaises(ClientError, client.remove_nodes, 'localhost', self.server_port, proxy=2)
    self.assertRaises(ClientError, client.remove_nodes, 'localhost', self.server_port, web=1)


class ManagerScaleInFrom1Proxy2Web1BackendTest(Setup, unittest.TestCase):
  CONFIGURATION_CLASS = PHPServiceConfiguration
  TYPE = 'FAKE'
  def setUp(self):
    Setup.setUp(self)
    version1 = join(self.code_repo, 'version1.tar')
    t = TarFile(name=version1, mode='w')
    t.add('/etc/passwd', arcname='index.html')
    t.close()
    
    config = PHPServiceConfiguration()
    config.web_count = 2
    config.proxy_count = 1
    config.backend_count = 1
    config.codeVersions['version1'] = CodeVersion('version1', 'version1.tar', 'tar')
    config.currentCodeVersion = 'version1'
    self.mc.set(InternalsBase.CONFIG, config)
  
  def test_goToMinimal(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 2)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    proxyNode = ret['proxy'][0]
    
    client.remove_nodes('localhost', self.server_port, proxy=1, backend=1, web=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertEqual(ret['proxy'], ret['web'])
    self.assertEqual(ret['web'], ret['backend'])
  
  def test_removeMore(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 2)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    self.assertRaises(ClientError, client.remove_nodes, 'localhost', self.server_port, proxy=1)
    self.assertRaises(ClientError, client.remove_nodes, 'localhost', self.server_port, backend=1)
    self.assertRaises(ClientError, client.remove_nodes, 'localhost', self.server_port, web=2)
  
  def test_remove1Web(self):
    client.startup('localhost', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 2)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.remove_nodes('localhost', self.server_port, web=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('localhost', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])


if __name__ == "__main__":
  unittest.main()
