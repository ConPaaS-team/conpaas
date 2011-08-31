'''
Created on Jul 20, 2011

@author: ielhelw
'''

import copy
import unittest
from os.path import join
from tarfile import TarFile

from unit.manager import Setup
from conpaas.web.manager import client
from conpaas.web.manager.internal import InternalsBase
from conpaas.web.manager.config import PHPServiceConfiguration

class PHPConfigTest(Setup, unittest.TestCase):
  CONFIGURATION_CLASS = PHPServiceConfiguration
  TYPE = 'PHP'
  phpconf_default = { 'memory_limit': '128M',
                      'max_execution_time': '30',
                      'display_errors': 'Off',
                      'log_errors': 'Off',
                      'upload_max_filesize': '2M'}
  
  
  def test_configCodeVersion(self):
    self._upload_codeVersions()
    self.assertEqual(client.get_configuration('127.0.0.1', self.server_port),
                     {'codeVersionId': 'code-default',
                      'phpconf': self.phpconf_default})
    self.assertEqual(client.update_php_configuration('127.0.0.1', self.server_port, codeVersionId=self.id1),
                     {})
    self.assertEqual(client.get_configuration('127.0.0.1', self.server_port),
                     {'codeVersionId': self.id1,
                      'phpconf': self.phpconf_default})
  
  def test_configPHP(self):
    phpconf_update = copy.deepcopy(self.phpconf_default)
    phpconf_update['upload_max_filesize'] = '10M'
    self.assertEqual(client.get_configuration('127.0.0.1', self.server_port),
                     {'codeVersionId': 'code-default', 'phpconf': self.phpconf_default})
    self.assertEqual(client.update_php_configuration('127.0.0.1', self.server_port, phpconf={'upload_max_filesize': '10M'}),
                     {})
    self.assertEqual(client.get_configuration('127.0.0.1', self.server_port),
                     {'codeVersionId': 'code-default', 'phpconf': phpconf_update})
  
  def test_configCodeVersionAndPHP(self):
    self._upload_codeVersions()
    phpconf_update = copy.deepcopy(self.phpconf_default)
    phpconf_update['upload_max_filesize'] = '10M'
    self.assertEqual(client.get_configuration('127.0.0.1', self.server_port),
                     {'codeVersionId': 'code-default', 'phpconf': self.phpconf_default})
    self.assertEqual(client.update_php_configuration('127.0.0.1', self.server_port, codeVersionId=self.id2, phpconf={'upload_max_filesize': '10M'}),
                     {})
    self.assertEqual(client.get_configuration('127.0.0.1', self.server_port),
                     {'codeVersionId': self.id2, 'phpconf': phpconf_update})

  def test_startupShutdown(self):
    self.test_configCodeVersionAndPHP()
    self.assertEqual(client.startup('127.0.0.1', self.server_port),
                     {'state': InternalsBase.S_PROLOGUE})
    
    self._waitTillState(InternalsBase.S_PROLOGUE, InternalsBase.S_RUNNING)
    
    ret = client.list_nodes('127.0.0.1', self.server_port)
    self.assertTrue('proxy' in ret)
    self.assertTrue('web' in ret)
    self.assertTrue('backend' in ret)
    self.assertTrue(ret['proxy'] == ret['web'] == ret['backend'])
    
    self.assertEqual(client.shutdown('127.0.0.1', self.server_port),
                     {'state': InternalsBase.S_EPILOGUE})
    
    self._waitTillState(InternalsBase.S_EPILOGUE, InternalsBase.S_STOPPED)
  
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
