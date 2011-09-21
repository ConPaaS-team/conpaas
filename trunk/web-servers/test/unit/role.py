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


Created on Jan 25, 2011

@author: ielhelw
'''
from os.path import join, exists
from shutil import rmtree
import unittest, time, urllib

from conpaas.web.agent.role import NginxStatic, NginxProxy,\
                                   Tomcat6, PHPProcessManager,\
                                   S_RUNNING, S_STOPPED
from conpaas.web.agent import role
from os import makedirs
from random import randint

class NginxStaticTest(unittest.TestCase):
  
  def setUp(self):
    '''Create a temporary directory to act as doc_root and place an intial
    index.html in it
    '''
    self.port = randint(4000, 5000)
    self.doc_root = join(config_parser.get('agent', 'VAR_CACHE'), 'www', 'code-default')
    if not exists(self.doc_root):
      makedirs(self.doc_root)
    fd = open(self.doc_root + '/index.html', 'w')
    fd.write('This is a test file')
    fd.close()
    self.server = None
  
  def tearDown(self):
    '''Remove the temporary doc_root
    '''
    if self.server:
      try: self.server.stop()
      except: pass
    rmtree(self.doc_root, ignore_errors=True)
  
  def __performRequest(self, method, uri, host=None, port=None, body=None):
    import httplib
    if not port: port = self.port
    if not host: host = '127.0.0.1'
    try:
      conn = httplib.HTTPConnection(host, port)
      conn.request(method, uri, body=body)
      response = conn.getresponse()
      response.read()
      conn.close()
    except:
      return False
    else:
      return True
  
  def __startNginx(self):
    w = NginxStatic(port=self.port, code_versions=self.code_versions)
    self.assertEqual(w.state, S_RUNNING)
    self.assertEqual(w.port, self.port)
    self.assertEquals(w.status(), {'state': S_RUNNING, 'port': self.port, 'code_versions': self.code_versions})
    self.assertTrue(self.__performRequest('GET', '/'), 'Failed to request / from web server')
    self.server = w
    return w
  
  def __stopNginx(self, w):
    w.stop()
    self.assertEqual(w.state, S_STOPPED)
    time.sleep(2)
    self.assertFalse(self.__performRequest('GET', '/'), 'Web server still running after call to stop()')
  
  validation_params = [
              [TypeError, {}],
              [TypeError, {'port': 1234}],# missing code_versions
              [TypeError, {'code_versions': []}],# missing port
              [TypeError, {'port': '1234', 'code_versions': ['aaa']}], # invalid port},
              [ValueError, {'port': 123411123, 'code_versions': []}], # invalid port
              [TypeError, {'port': 1234, 'code_versions': ''}], # invalid code_versions
              [TypeError, {'port': 1234, 'code_versions': [1, '']}], # invalid code_versions
              ]
  
  def test_initValidation(self):
    for p in self.validation_params:
      self.assertRaises(p[0], NginxStatic, **p[1])
  
  def test_configureValidation(self):
    self.code_versions = ['code-default']
    w = self.__startNginx()
    for p in self.validation_params:
      self.assertRaises(p[0], w.configure, **p[1])
    self.__stopNginx(w)
  
  def test_startStop(self):
    self.code_versions = ['code-default']
    w = self.__startNginx()
    self.__stopNginx(w)
  
  def test_startReconfigureStop(self):
    self.code_versions = ['code-default']
    w = self.__startNginx()
    time.sleep(2)
    w.configure(port=self.port + 1, code_versions=self.code_versions)
    w.restart()
    time.sleep(3)
    self.assertFalse(self.__performRequest('GET', '/'), 'Web server still accepting requests on old port after reconfiguration')
    
    self.port += 1
    self.assertTrue(self.__performRequest('GET', '/'), 'Web server not accepting requests on new port after reconfiguration')
    self.__stopNginx(w)
  

class NginxProxyTest(unittest.TestCase):
  
  def setUp(self):
    self.service_port = randint(4000, 5000)
    self.port = randint(4000, 5000)
    self.code_version = 'AAAA'
    self.web_list = []
    self.fpm_list = []
    self.tomcat_list = []
    self.tomcat_servlets = []
    self.doc_root = join(role.VAR_CACHE, 'www')
    if exists(self.doc_root):
      rmtree(self.doc_root, ignore_errors=True)
    version_dir = join(self.doc_root, self.code_version)
    makedirs(version_dir)
    fd = open(join(version_dir, 'index.html'), 'w')
    fd.write('TEST FILE')
    fd.close()
    
  def tearDown(self):
    if exists(self.doc_root):
      rmtree(self.doc_root, ignore_errors=True)
  
  def __isAlive(self, port):
    import socket
    try:
      soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      soc.connect(('127.0.0.1', port))
      soc.close()
      return True
    except:
      return False
  
  def __startProxy(self):
    kwargs = {'port': self.port,
              'code_version': self.code_version,
              'web_list': self.web_list,
              'fpm_list': self.fpm_list,
              'tomcat_list': self.tomcat_list,
              'tomcat_servlets': self.tomcat_servlets}
    p = NginxProxy(**kwargs)
    self.assertEqual(p.state, S_RUNNING)
    self.assertEqual(p.port, self.port)
    self.assertEquals(p.status(), {'state': S_RUNNING, 'port': self.port,
                                   'code_version': self.code_version,
                                   'web_list': self.web_list,
                                   'fpm_list': self.fpm_list,
                                   'tomcat_list': self.tomcat_list,
                                   'tomcat_servlets': self.tomcat_servlets})
    time.sleep(1)
    self.assertTrue(self.__isAlive(self.port), 'http port is not bound')
    return p
  
  def __configure(self, p):
    kwargs = {'port': self.port,
              'code_version': self.code_version,
              'web_list': self.web_list,
              'fpm_list': self.fpm_list,
              'tomcat_list': self.tomcat_list,
              'tomcat_servlets': self.tomcat_servlets}
    p.configure(**kwargs)
  
  def __stopProxy(self, p):
    p.stop()
    time.sleep(1)
    self.assertEqual(p.state, S_STOPPED)
    self.assertEquals(p.status(), {'state': S_STOPPED, 'port': self.port,
                                   'code_version': self.code_version,
                                   'web_list': self.web_list,
                                   'fpm_list': self.fpm_list,
                                   'tomcat_list': self.tomcat_list,
                                   'tomcat_servlets': self.tomcat_servlets})
    self.assertFalse(self.__isAlive(self.port), 'http port is bound after stop()')
  
  def test_startStop(self):
    p = self.__startProxy()
    time.sleep(1)
    self.__stopProxy(p)
  
  def test_startReconfigureStop(self):
    self.web_list = [{'ip': 'www.vu.nl', 'port': 80}]
    p = self.__startProxy()
    self.assertTrue(self.__isAlive(self.port))
    self.port = self.port + 2
    self.__configure(p)
    p.restart()
    time.sleep(2)
    self.assertTrue(self.__isAlive(self.port))
    self.__stopProxy(p)


class FPMTest(unittest.TestCase):
  def setUp(self):
    self.fpm_port = randint(4000, 5000)
    self.nginx_port = randint(4000, 5000)
    self.fpm_list = [{'ip': '127.0.0.1', 'port': self.fpm_port}]
    self.doc_root = join(role.VAR_CACHE, 'www')
    self.code_version = 'code-default'
    if exists(self.doc_root):
      rmtree(self.doc_root, ignore_errors=True)
    version_dir = join(self.doc_root, self.code_version)
    makedirs(version_dir)
    fd = open(join(version_dir, 'index.php'), 'w')
    fd.write('<? echo "This is a php test"; ?>')
    fd.close()
    fd = open(join(version_dir, 'max_execution_time.php'), 'w')
    fd.write('<? echo ini_get("max_execution_time"); ?>')
    fd.close()
    nginx_kwargs = {'port': self.nginx_port,
              'code_version': self.code_version,
              'fpm_list': self.fpm_list
              }
    self.fpm = None
    self.nginx = None
    try:
      self.fpm = PHPProcessManager(self.fpm_port, '', {})
      self.nginx = NginxProxy(**nginx_kwargs)
    except:
      if self.fpm:
        try: self.fpm.stop()
        except: pass
      if self.nginx:
        try: self.nginx.stop()
        except: pass
      raise
    time.sleep(2)
  
  def tearDown(self):
    if exists(self.doc_root):
      rmtree(self.doc_root, ignore_errors=True)
    if self.fpm: self.fpm.stop()
    if self.nginx: self.nginx.stop()
  
  def test_startStop(self):
    response = urllib.urlopen('http://127.0.0.1:%d/' % (self.nginx_port))
    self.assertEqual('This is a php test', response.read())
    response.close()
    
  def test_startReconfigureStop(self):
    response = urllib.urlopen('http://127.0.0.1:%d/max_execution_time.php' % (self.nginx_port))
    max_execution_time = int(response.read())
    response.close()
    
    self.fpm.configure(self.fpm_port, '', {'max_execution_time': max_execution_time + 13})
    self.fpm.restart()
    time.sleep(2)
    
    response = urllib.urlopen('http://127.0.0.1:%d/max_execution_time.php' % (self.nginx_port))
    new_max_execution_time = int(response.read())
    response.close()
    
    self.assertEqual(max_execution_time + 13, new_max_execution_time)


class TomcatTest(unittest.TestCase):
  def setUp(self):
    self.tomcat_port = randint(4000, 5000)
    self.code_version = 'code-default'
    self.instance_dir = join(config_parser.get('agent', 'VAR_CACHE'), 'tomcat_instance')
    version_dir = join(self.instance_dir, 'webapps', self.code_version)
    
    if exists(self.instance_dir):
      rmtree(self.instance_dir, ignore_errors=True)
    
    self.tomcat = None
    try:
      self.tomcat = Tomcat6(tomcat_port=self.tomcat_port)
    except:
      if self.tomcat:
        try: self.tomcat.stop()
        except: pass
      raise
    
    makedirs(version_dir)
    fd = open(join(version_dir, 'index.jsp'), 'w')
    fd.write('<%= new String( "This is a jsp test") %>')
    fd.close()
    time.sleep(2)
  
  def tearDown(self):
    if self.tomcat: self.tomcat.stop()
    if exists(self.instance_dir):
      rmtree(self.instance_dir, ignore_errors=True)
  
  def test_startStop(self):
    response = urllib.urlopen('http://localhost:%d/%s/' % (self.tomcat_port, self.code_version))
    self.assertEqual('This is a jsp test', response.read())


def init(cparser):
  role.init(cparser)
  global config_parser
  config_parser = cparser

if __name__ == '__main__':
  from ConfigParser import ConfigParser
  from optparse import OptionParser
  import sys
  
  parser = OptionParser()
  parser.add_option('-c', '--config', type='string', default=None, dest='config')
  options, args = parser.parse_args()
  if not options.config:
    print >>sys.stderr, 'Failed to find configuration file'
    sys.exit(1)
  config_parser = ConfigParser()
  config_parser.read(options.config)
  init(config_parser)
  unittest.main(argv=[sys.argv[0]]+args)
