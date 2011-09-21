'''
Copyright (C) 2010-2011 Contrail consortium.

This file is part of ConPaaS, an integrated runtime environment 
for elastic cloud applications.

ConPaaS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ConPaaS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.


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
    config.web_count = 0
    config.proxy_count = 1
    config.backend_count = 0
    config.codeVersions['version1'] = CodeVersion('version1', 'version1.tar', 'tar')
    config.currentCodeVersion = 'version1'
    self.mc.set(InternalsBase.CONFIG, config)
  
  def test_request1Web(self, shutdown=True):
    client.startup('127.0.0.1', self.server_port)
    
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('127.0.0.1', self.server_port, web=1), {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('backend' in ret and ret['backend'] == [proxyNode])
    self.assertTrue('web' in ret and len(ret['web']) == 1 and ret['web'] != [proxyNode])
    if shutdown:
      client.shutdown('127.0.0.1', self.server_port)
      self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1Backend(self, shutdown=True):
    client.startup('127.0.0.1', self.server_port)
    
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('127.0.0.1', self.server_port, backend=1),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret and ret['proxy'] == [proxyNode])
    self.assertTrue('backend' in ret and len(ret['backend']) == 1 and proxyNode not in ret['backend'])
    self.assertTrue('web' in ret and len(ret['web']) == 1 and ret['web'] == [proxyNode])
    
    if shutdown:
      client.shutdown('127.0.0.1', self.server_port)
      self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1Proxy(self, shutdown=True):
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    self.assertRaises(ClientError, client.add_nodes, '127.0.0.1', self.server_port, proxy=1)
    
    if shutdown:
      client.shutdown('127.0.0.1', self.server_port)
      self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1BackendRequest1Web(self):
    self.test_request1Backend(shutdown=False)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    backendNode = ret['backend'][0]
    proxyNode = ret['proxy'][0] # web should be here as well
    self.assertTrue(backendNode != proxyNode)
    self.assertTrue(ret['web'] == [proxyNode])
    
    self.assertEqual(client.add_nodes('127.0.0.1', self.server_port, web=1), {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    
    self.assertTrue(ret['proxy'] == [proxyNode])
    self.assertTrue(ret['backend'] == [backendNode])
    self.assertTrue(len(ret['web']) == 1 and ret['web'] != [proxyNode] and ret['web'] != [backendNode])
    
    client.shutdown('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1BackendRequest1Proxy(self):
    self.test_request1Backend(shutdown=False)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    backendNode = ret['backend'][0]
    proxyNode = ret['proxy'][0] # web should be here as well
    self.assertTrue(backendNode != proxyNode)
    self.assertTrue(ret['web'] == [proxyNode])
    self.assertRaises(ClientError, client.add_nodes, '127.0.0.1', self.server_port, proxy=1)
    
    client.shutdown('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1WebRequest1Backend(self):
    self.test_request1Web(shutdown=False)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('127.0.0.1', self.server_port, backend=1),
                     {})
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue(ret['proxy'] == [proxyNode])
    self.assertTrue(len(ret['web']) == 1 and ret['web'] != [proxyNode])
    self.assertTrue(len(ret['backend']) == 1
                    and ret['backend'] != ret['web']
                    and ret['backend'] != ret['web'])
    
    client.shutdown('127.0.0.1', self.server_port)
    ret = client.get_service_info('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1WebRequest1Proxy(self):
    self.test_request1Web(shutdown=False)
    self.assertRaises(ClientError, client.add_nodes, '127.0.0.1', self.server_port, proxy=1)
    client.shutdown('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request1Proxy4Web5Backend(self):
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('127.0.0.1', self.server_port, proxy=1, web=4, backend=5),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue(proxyNode in ret['proxy'] and len(ret['proxy']) == 2)
    self.assertEqual(len(ret['web']), 4)
    self.assertEqual(len(ret['backend']), 5)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.shutdown('127.0.0.1', self.server_port)
    ret = client.get_service_info('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request3Web2Proxy1Backend(self):
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('127.0.0.1', self.server_port, web=3, proxy=2, backend=1),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue(proxyNode in ret['proxy'])
    self.assertEqual(len(ret['proxy']), 3)
    self.assertEqual(len(ret['web']), 3)
    self.assertEqual(len(ret['backend']), 1)
    
    self.assertTrue(proxyNode in ret['proxy'])
    
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.shutdown('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request3Backend2Web(self):
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('127.0.0.1', self.server_port, backend=3, web=2),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 2)
    self.assertEqual(len(ret['backend']), 3)
    
    self.assertTrue(proxyNode in ret['proxy'])
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.shutdown('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def test_request4Web5Backend2Proxy(self):
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(isinstance(ret['web'], list) and len(ret['web']) == 1)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    proxyNode = ret['proxy'][0]
    self.assertEqual(client.add_nodes('127.0.0.1', self.server_port, web=4, backend=5, proxy=2),
                     {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertEqual(len(ret['proxy']), 3)
    self.assertEqual(len(ret['web']), 4)
    self.assertEqual(len(ret['backend']), 5)
    
    self.assertTrue(proxyNode in ret['proxy'])
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.shutdown('127.0.0.1', self.server_port)
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
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
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
    
    client.remove_nodes('127.0.0.1', self.server_port, web=1, backend=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertEqual(ret['proxy'], ret['web'])
    self.assertEqual(ret['web'], ret['backend'])
  
  def test_remove1Web(self):
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
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
    
    client.remove_nodes('127.0.0.1', self.server_port, web=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
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
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
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
    
    client.remove_nodes('127.0.0.1', self.server_port, backend=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertNotEqual(ret['proxy'], ret['web'])
    self.assertEqual(ret['proxy'], ret['backend'])
  
  def test_removeMore(self):
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    self.assertRaises(ClientError, client.remove_nodes, '127.0.0.1', self.server_port, backend=2)
    self.assertRaises(ClientError, client.remove_nodes, '127.0.0.1', self.server_port, proxy=1)
    self.assertRaises(ClientError, client.remove_nodes, '127.0.0.1', self.server_port, proxy=2)
    self.assertRaises(ClientError, client.remove_nodes, '127.0.0.1', self.server_port, web=2)


class ManagerScaleInFrom2Proxy1Web1BackendTest(Setup, unittest.TestCase):
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
    config.proxy_count = 2
    config.backend_count = 1
    config.codeVersions['version1'] = CodeVersion('version1', 'version1.tar', 'tar')
    config.currentCodeVersion = 'version1'
    self.mc.set(InternalsBase.CONFIG, config)
  
  def test_goToMinimal(self):
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 2)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    proxyNode = ret['proxy'][0]
    
    client.remove_nodes('127.0.0.1', self.server_port, proxy=1, backend=1, web=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 1)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    
    self.assertEqual(ret['proxy'], [proxyNode])
    self.assertEqual(ret['proxy'], ret['web'])
    self.assertEqual(ret['proxy'], ret['backend'])
  
  def test_removeMore(self):
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 2)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    self.assertRaises(ClientError, client.remove_nodes, '127.0.0.1', self.server_port, proxy=2)
    self.assertRaises(ClientError, client.remove_nodes, '127.0.0.1', self.server_port, backend=2)
    self.assertRaises(ClientError, client.remove_nodes, '127.0.0.1', self.server_port, web=2)
  
  def test_remove1Proxy(self):
    client.startup('127.0.0.1', self.server_port)
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertEqual(len(ret['proxy']), 2)
    self.assertEqual(len(ret['web']), 1)
    self.assertEqual(len(ret['backend']), 1)
    self.assertEqual(intersection(ret['proxy'], ret['web']), [])
    self.assertEqual(intersection(ret['proxy'], ret['backend']), [])
    self.assertEqual(intersection(ret['web'], ret['backend']), [])
    
    client.remove_nodes('127.0.0.1', self.server_port, proxy=1)
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    ret = client.list_nodes('127.0.0.1', self.server_port)
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
