'''
Created on Jan 26, 2011

@author: ielhelw
'''

import unittest, threading, time, urllib2
from os.path import exists, join
from os import remove, makedirs
from shutil import rmtree
from random import randint

from conpaas.web.agent.server import AgentServer
from conpaas.web.agent import internals
from conpaas.web.agent.client import createWebServer, stopWebServer,\
  createPHP, createHttpProxy, stopPHP, stopHttpProxy, updateHttpProxy, updatePHP

def init(cparser):
  global config_parser
  config_parser = cparser
  internals.init(config_parser)

class AgentServerTest(unittest.TestCase):
  def setUp(self):
    global config_parser
    self.agent_port = randint(4000, 5000)
    self.web_port = randint(4000, 5000)
    self.proxy_port = randint(4000, 5000)
    self.php_port = randint(4000, 5000)
    self.www_dir = join(config_parser.get('agent', 'VAR_CACHE'), 'www')
    if exists(self.www_dir):
      rmtree(self.www_dir, ignore_errors=True)
    self.code_version1 = 'MYVERSION1'
    self.code_version2 = 'MYVERSION2'
    
    makedirs(join(self.www_dir, self.code_version1))
    fd = open(join(self.www_dir, self.code_version1, 'index.html'), 'w')
    fd.write('MY FIRST INDEX')
    fd.close()
    
    makedirs(join(self.www_dir, self.code_version2))
    fd = open(join(self.www_dir, self.code_version2, 'index.html'), 'w')
    fd.write('MY SECOND INDEX')
    fd.close()
    
    try:
      if self.server != None:
        self.tearDown()
    except AttributeError: pass
    self.server = AgentServer(('0.0.0.0', self.agent_port), config_parser)
    self.t = threading.Thread(target=self.server.serve_forever)
    self.t.start()
  
  def tearDown(self):
    host = '127.0.0.1'
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
    if exists(internals.webserver_file):
      remove(internals.webserver_file)
    if exists(internals.httpproxy_file):
      remove(internals.httpproxy_file)
    if exists(internals.php_file):
      remove(internals.php_file)
    if exists(self.www_dir):
      rmtree(self.www_dir, ignore_errors=True)
  
  def test_proxyUpdateCodeVersion(self):
    host = '127.0.0.1'
    port = self.agent_port
    self.assertTrue(createPHP(host, port, self.php_port, '', {}))
    self.assertTrue(createWebServer(host, port, self.web_port, [self.code_version1]))
    self.assertTrue(createHttpProxy(host, port,
                                    self.proxy_port,
                                    self.code_version1,
                                    web_list=[{'ip': '127.0.0.1',
                                               'port': self.web_port}
                                              ],
                                    fpm_list=[{'ip': '127.0.0.1',
                                               'port': self.php_port}]))
    
    time.sleep(5)
    
    r = urllib2.urlopen('http://127.0.0.1:' + str(self.proxy_port))
    self.assertEqual(r.read(), 'MY FIRST INDEX')
    r.close()
    
    self.assertTrue(updateHttpProxy(host, port, self.proxy_port, self.code_version2, web_list=[{'ip': '127.0.0.1', 'port': self.web_port}]))
    time.sleep(5)
    
    r = urllib2.urlopen('http://127.0.0.1:' + str(self.proxy_port))
    self.assertEqual(r.read(), 'MY SECOND INDEX')
    r.close()
  
  def test_webUsesCodeVersion(self):
    host = '127.0.0.1'
    port = self.agent_port
    self.assertTrue(createPHP(host, port, self.php_port, '', {}))
    self.assertTrue(createWebServer(host, port, self.web_port, [self.code_version1, self.code_version2]))
    
    request1 = urllib2.Request('http://127.0.0.1:' + str(self.web_port),
                               headers={'host': self.code_version1})
    request2 = urllib2.Request('http://127.0.0.1:' + str(self.web_port),
                               headers={'host': self.code_version2})
    
    r = urllib2.urlopen(request1)
    self.assertEqual(r.read(), 'MY FIRST INDEX')
    r.close()
    
    r = urllib2.urlopen(request2)
    self.assertEqual(r.read(), 'MY SECOND INDEX')
    r.close()
    
    try:
      urllib2.urlopen('http://127.0.0.1:' + str(self.web_port))
    except urllib2.HTTPError as e:
      self.assertEqual(e.getcode(), 404)
  
  def test_phpConfiguration(self):
    host = '127.0.0.1'
    port = self.agent_port
    self.assertTrue(createPHP(host, port, self.php_port, '',
                              {'max_file_uploads': '10', 'file_uploads': '1'}))
    self.assertTrue(createWebServer(host, port, self.web_port, [self.code_version1]))
    self.assertTrue(createHttpProxy(host, port,
                                    self.proxy_port,
                                    self.code_version1,
                                    web_list=[{'ip': '127.0.0.1',
                                               'port': self.web_port}
                                              ],
                                    fpm_list=[{'ip': '127.0.0.1',
                                               'port': self.php_port}]))
    
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
