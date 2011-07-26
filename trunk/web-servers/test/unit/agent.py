'''
Created on Jan 26, 2011

@author: ielhelw
'''

import unittest, threading, time, urllib2, stat
from os.path import exists, join
from os import remove, mkdir, chmod
from shutil import rmtree
from tempfile import mkdtemp

from conpaas.web.agent.server import AgentServer
from conpaas.web.agent.internals import webserver_file, httpproxy_file, php_file
from conpaas.web.agent.client import createWebServer, updateWebServer, stopWebServer, getWebServerState,\
  createPHP, createHttpProxy, stopPHP, stopHttpProxy, updateHttpProxy, updatePHP

class AgentServerTest(unittest.TestCase):
  def setUp(self):
    self.agent_port = 5500
    self.web_port = 5600
    self.proxy_port = 5700
    self.php_port = 5800
    self.dir = mkdtemp(prefix='conpaas-web-agent', dir='/tmp')
    chmod(self.dir, stat.S_IRWXU | stat.S_IROTH | stat.S_IXOTH)
    self.www_dir = join(self.dir, 'www')
    self.code_version1 = 'MYVERSION1'
    self.code_version2 = 'MYVERSION2'
    
    mkdir(self.www_dir)
    
    mkdir(join(self.www_dir, self.code_version1))
    fd = open(join(self.www_dir, self.code_version1, 'index.html'), 'w')
    fd.write('MY FIRST INDEX')
    fd.close()
    
    mkdir(join(self.www_dir, self.code_version2))
    fd = open(join(self.www_dir, self.code_version2, 'index.html'), 'w')
    fd.write('MY SECOND INDEX')
    fd.close()
    
    try:
      if self.server != None:
        self.tearDown()
    except AttributeError: pass
    self.server = AgentServer(('0.0.0.0', self.agent_port))
    self.t = threading.Thread(target=self.server.serve_forever)
    self.t.start()
  
  def tearDown(self):
    host = 'localhost'
    port = self.agent_port
    try: stopPHP(host, port)
    except: pass
    try: stopWebServer(host, port)
    except: pass
    try: stopHttpProxy(host, port)
    except: pass
    
    self.server.shutdown()
    self.server = None
    self.t.join()
    self.t = None
    if exists(webserver_file):
      remove(webserver_file)
    if exists(httpproxy_file):
      remove(httpproxy_file)
    if exists(php_file):
      remove(php_file)
    rmtree(self.dir, ignore_errors=True)
  
  def test_proxyUpdateCodeVersion(self):
    host = 'localhost'
    port = self.agent_port
    self.assertTrue(createPHP(host, port, self.php_port, '', {}))
    self.assertTrue(createWebServer(host, port, self.www_dir, self.web_port, self.code_version1, [['127.0.0.1', self.php_port]], self.code_version2))
    self.assertTrue(createHttpProxy(host, port, self.proxy_port, [['127.0.0.1', self.web_port]], self.code_version1))
    
    time.sleep(5)
    
    r = urllib2.urlopen('http://127.0.0.1:' + str(self.proxy_port))
    self.assertEqual(r.read(), 'MY FIRST INDEX')
    r.close()
    
    self.assertTrue(updateHttpProxy(host, port, self.proxy_port, [['127.0.0.1', self.web_port]], self.code_version2))
    time.sleep(5)
    
    r = urllib2.urlopen('http://127.0.0.1:' + str(self.proxy_port))
    self.assertEqual(r.read(), 'MY SECOND INDEX')
    r.close()
  
  def test_webUsesCodeVersion(self):
    host = 'localhost'
    port = self.agent_port
    self.assertTrue(createPHP(host, port, self.php_port, '', {}))
    self.assertTrue(createWebServer(host, port, self.www_dir, self.web_port, self.code_version1, [['127.0.0.1', self.php_port]], self.code_version2))
    
    request1 = urllib2.Request('http://localhost:' + str(self.web_port),
                               headers={'host': self.code_version1,
                                        'conpaasversion': self.code_version1,
                                        'conpaashost': 'localhost'})
    request2 = urllib2.Request('http://localhost:' + str(self.web_port),
                               headers={'host': self.code_version2,
                                        'conpaasversion': self.code_version2,
                                        'conpaashost': 'localhost'})
    
    r = urllib2.urlopen(request1)
    self.assertEqual(r.read(), 'MY FIRST INDEX')
    r.close()
    
    r = urllib2.urlopen(request2)
    self.assertEqual(r.read(), 'MY SECOND INDEX')
    r.close()
    
    try:
      urllib2.urlopen('http://localhost:' + str(self.web_port))
    except urllib2.HTTPError as e:
      self.assertEqual(e.getcode(), 404)
  
  def test_phpConfiguration(self):
    host = 'localhost'
    port = self.agent_port
    self.assertTrue(createPHP(host, port, self.php_port, '', {'max_file_uploads': '10', 'file_uploads': '1'}))
    self.assertTrue(createWebServer(host, port, self.www_dir, self.web_port, self.code_version1, [['127.0.0.1', self.php_port]]))
    self.assertTrue(createHttpProxy(host, port, self.proxy_port, [['127.0.0.1', self.web_port]], self.code_version1))
    
    time.sleep(5)
    
    fd = open(join(self.www_dir, self.code_version1, 'index.php'), 'w')
    fd.write("<? echo 'XX ', ini_get('file_uploads'), ' ', ini_get('max_file_uploads'), ' YY'; ?>")
    fd.close()
    
    r = urllib2.urlopen('http://127.0.0.1:' + str(self.proxy_port) + '/index.php')
    self.assertEqual(r.read(), 'XX 1 10 YY')
    r.close()
    
    self.assertTrue(updatePHP(host, port, self.php_port, '', {'max_file_uploads': '7', 'file_uploads': '0'}))
    time.sleep(5)
    
    r = urllib2.urlopen('http://127.0.0.1:' + str(self.proxy_port) + '/index.php')
    self.assertEqual(r.read(), 'XX 0 7 YY')
    r.close()

if __name__ == '__main__':
  unittest.main()
