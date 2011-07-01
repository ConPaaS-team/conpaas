'''
Created on Jan 25, 2011

@author: ielhelw
'''
from tempfile import mkdtemp
from shutil import rmtree
from socket import gethostbyname
import unittest, time
from ConfigParser import ConfigParser

config_parser = ConfigParser()
config_parser.add_section('manager')
config_parser.set('manager', 'LOG_FILE', '/tmp/conpaas-unittest.log')

from conpaas import log
log.init(config_parser)
from conpaas.web.agent.role import Nginx, NginxProxy, S_RUNNING, S_STOPPED


class TestNginxValidation(unittest.TestCase):
  """Input validation tests for Nginx"""
  
  def test_CreationMissingRequiresParamenter(self):
    """Nginx Verify handling of missing parameters"""
    self.assertRaises(TypeError, Nginx)
    self.assertRaises(TypeError, Nginx, doc_root='/')
    self.assertRaises(TypeError, Nginx, port=2222)
  
  def test_CreationTypeChecks(self):
    """Nginx Check parameter types"""
    self.assertRaises(TypeError, Nginx, doc_root=11, port=2222)
    self.assertRaises(TypeError, Nginx, doc_root='/', port=2222, php='')
    self.assertRaises(TypeError, Nginx, doc_root='/', port=2222, php=[[]])
    self.assertRaises(TypeError, Nginx, doc_root='/', port=2222, php=[''])
    self.assertRaises(TypeError, Nginx, doc_root='/', port=2222, php=[['1.1.1.1', '1111']])
    self.assertRaises(ValueError, Nginx, doc_root='/', port=2222, php=[['1.1.1.f', 1111]])


class TestNginxProxyValidation(unittest.TestCase):
  """Input validation tests for NginxProxy"""
  
  def test_CreationMissingRequiredParameter(self):
    """NginxProxy Verify handling of missing parameters"""
    self.assertRaises(TypeError, NginxProxy)
    self.assertRaises(TypeError, NginxProxy, backends=[])
    self.assertRaises(TypeError, NginxProxy, port=2222)
  
  def test_CreationTypeChecks(self):
    """NginxProxy Check parameter types"""
    self.assertRaises(TypeError, NginxProxy, port=9999, backends='BLAH')
  
  def test_CreationValueChecks(self):
    """NginxProxy Check parameter values"""
    self.assertRaises(ValueError, NginxProxy, backends=[], port=-1)
    self.assertRaises(ValueError, NginxProxy, backends=[], port=65536)
    self.assertRaises(TypeError, NginxProxy, port=9999, backends=[''])
    self.assertRaises(TypeError, NginxProxy, port=9999, backends=[[]])
    self.assertRaises(ValueError, NginxProxy, port=9999, backends=[['1.2.3.f', 3333]])
    self.assertRaises(TypeError, NginxProxy, port=9999, backends=[['1.1.1.1', '3333']])


class TestNginx(unittest.TestCase):
  """Simple tests for Nginx"""
  
  def setUp(self):
    '''Create a temporary directory to act as doc_root and place an intial
    index.html in it
    '''
    self.port = 7777
    self.doc_root = mkdtemp(prefix='nginx-root', dir='/tmp')
    fd = open(self.doc_root + '/index.html', 'w')
    fd.write('This is a test file')
    fd.close()
  
  def tearDown(self):
    '''Remove the temporary doc_root
    '''
    rmtree(self.doc_root, ignore_errors=True)
  
  def __performRequest(self, method, uri, host=None, port=None, body=None):
    import httplib
    if not port: port = self.port
    if not host: host = 'localhost'
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
    w = Nginx(doc_root=self.doc_root, port=self.port)
    self.assertEqual(w.state, S_RUNNING)
    self.assertEqual(w.port, self.port)
    self.assertEqual(w.doc_root, self.doc_root)
    self.assertEquals(w.status(), {'state': S_RUNNING, 'doc_root': self.doc_root, 'port': self.port, 'php': None})
    self.assertTrue(self.__performRequest('GET', '/'), 'Failed to request / from web server')
    return w
  
  def __stopNginx(self, w):
    w.stop()
    self.assertEqual(w.state, S_STOPPED)
    time.sleep(2)
    self.assertFalse(self.__performRequest('GET', '/'), 'Web server still running after call to stop()')
  
  def test_runNoFCGI(self):
    """Nginx Start/Stop"""
    w = self.__startNginx()
    self.__stopNginx(w)
  
  def test_reconfigureNoFCGI(self):
    """Nginx reconfiguration (change port number)"""
    w = self.__startNginx()
    time.sleep(2)
    w.configure(self.doc_root, port=self.port + 1)
    w.restart()
    time.sleep(3)
    self.assertFalse(self.__performRequest('GET', '/'), 'Web server still accepting requests on old port after reconfiguration')
    
    self.port += 1
    self.assertTrue(self.__performRequest('GET', '/'), 'Web server not accepting requests on new port after reconfiguration')
    self.__stopNginx(w)
  

class TestNginxProxy(unittest.TestCase):
  """Simple tets for NginxProxy"""
  
  def setUp(self):
    self.service_port = 60000
    self.port = 8888
  
  def __isAlive(self, port):
    import socket
    try:
      soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      soc.connect(('127.0.0.1', port))
      soc.close()
      return True
    except:
      return False
  
  def __startProxy(self, backends=[]):
    p = NginxProxy(port=self.port, backends=backends, codeversion='AAAA')
    self.assertEqual(p.state, S_RUNNING)
    self.assertEqual(p.port, self.port)
    self.assertEquals(p.status(), {'state': S_RUNNING, 'port': self.port, 'backends': backends})
    time.sleep(1)
    self.assertTrue(self.__isAlive(self.port), 'http port is not bound')
    return p
  
  def __stopProxy(self, p, backends):
    p.stop()
    time.sleep(1)
    self.assertEqual(p.state, S_STOPPED)
    self.assertEquals(p.status(), {'state': S_STOPPED, 'port': self.port, 'backends': backends})
    self.assertFalse(self.__isAlive(self.port), 'http port is bound after stop()')
  
  def test_run(self):
    """NginxProxy Start/Stop"""
    backends = [[gethostbyname('www.example.com'), 80]]
    p = self.__startProxy(backends)
    time.sleep(1)
    self.__stopProxy(p, backends)
  
  def test_reconfigure(self):
    """NginxProxy Start/Reconfigure/Stop"""
    backends1 = [[gethostbyname('www.example.com'), 80], [gethostbyname('www.cs.vu.nl'), 80], [gethostbyname('www.vu.nl'), 80]]
    backends2 = [[gethostbyname('www.example.com'), 80], [gethostbyname('www.cs.vu.nl'), 80]]
    backends3 = [[gethostbyname('www.vu.nl'), 80]]
    p = self.__startProxy(backends1)
    
    p.configure(self.port, backends2, codeversion='AAAA')
    
    # also change port
    self.port = self.port + 2
    
    p.configure(self.port, backends3, codeversion='AAAA')
    
    self.__stopProxy(p, backends3)

if __name__ == '__main__':
  unittest.main()
