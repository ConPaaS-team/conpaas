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


Created on Jul 20, 2011

@author: ielhelw
'''
import unittest
import tempfile
from tarfile import TarFile
from os import remove
from os.path import join


from unit.manager import Setup
from conpaas.web.manager import client
from conpaas.web.manager.internal import InternalsBase
from conpaas.web.manager.config import JavaServiceConfiguration

class JavaConfigTest(Setup, unittest.TestCase):
  CONFIGURATION_CLASS = JavaServiceConfiguration
  TYPE = 'JAVA'
  
  def test_startupShutdown(self):
    self._startup()
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    self._shutdown()
  
  def test_uploadCodeVersions(self):
    self._upload_codeVersions()
  
  def test_configCodeVersion(self):
    self._upload_codeVersions()
    self.assertEqual(client.update_java_configuration('127.0.0.1',
                                                      self.server_port,
                                                      codeVersionId=self.id1),
                                                      {})
    self.assertEqual(client.get_configuration('127.0.0.1', self.server_port),
                     {'codeVersionId': self.id1})
    self._startup()
    self.assertEqual(client.update_java_configuration('127.0.0.1',
                                                      self.server_port,
                                                      codeVersionId=self.id2),
                                                      {})
    self._waitTillState(InternalsBase.S_ADAPTING, InternalsBase.S_RUNNING)
    self.assertEqual(client.get_configuration('127.0.0.1', self.server_port),
                     {'codeVersionId': self.id2})
    self._shutdown()
    self.assertEqual(client.get_configuration('127.0.0.1', self.server_port),
                     {'codeVersionId': self.id2})
  
  def _startup(self):
    self.assertEqual(client.startup('127.0.0.1', self.server_port),
                     {'state': InternalsBase.S_PROLOGUE})
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
  
  def _shutdown(self):
    self.assertEqual(client.shutdown('127.0.0.1', self.server_port),
                     {'state': InternalsBase.S_EPILOGUE})
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
  def _upload_codeVersions(self):
    _, fname = tempfile.mkstemp()
    fd = open(fname, 'w')
    fd.write('<%%= new String("This is a test jsp page") %%>')
    fd.close()
    version1 = join(self.dir, 'version1.tar')
    t = TarFile(name=version1, mode='w')
    t.add(fname, arcname='index.jsp')
    t.close()
    fd = open(fname, 'w')
    fd.write('<%%= new String("This is another test jsp page") %%>')
    fd.close()
    version2 = join(self.dir, 'version2.tar')
    t = TarFile(name=version2, mode='w')
    t.add(fname, arcname='index.html')
    t.close()
    remove(fname)
    
    # upload first
    ret = client.upload_code_version('127.0.0.1', self.server_port, version1)
    self.assertTrue('codeVersionId' in ret)
    self.id1 = ret['codeVersionId']
    
    ret = client.list_code_versions('127.0.0.1', self.server_port)
    self.assertEqual(2, len(ret['codeVersions']))
    self.assertEqual(ret['codeVersions'][0]['codeVersionId'], self.id1)
    self.assertEqual(ret['codeVersions'][0]['filename'], 'version1.tar')
    self.assertEqual(ret['codeVersions'][0]['description'], '')
    # upload second
    ret = client.upload_code_version('127.0.0.1', self.server_port, version2)
    self.assertTrue('codeVersionId' in ret)
    self.id2 = ret['codeVersionId']
    ret = client.list_code_versions('127.0.0.1', self.server_port)
    self.assertEqual(3, len(ret['codeVersions']))
    self.assertEqual(ret['codeVersions'][1]['codeVersionId'], self.id1)
    self.assertEqual(ret['codeVersions'][1]['filename'], 'version1.tar')
    self.assertEqual(ret['codeVersions'][1]['description'], '')
    self.assertEqual(ret['codeVersions'][0]['codeVersionId'], self.id2)
    self.assertEqual(ret['codeVersions'][0]['filename'], 'version2.tar')
    self.assertEqual(ret['codeVersions'][0]['description'], '')

if __name__ == '__main__':
  unittest.main()
