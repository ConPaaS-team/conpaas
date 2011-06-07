'''
Created on Mar 9, 2011

@author: ielhelw
'''

PHP_PORT = 9000
WEB_PORT = 8080
PROXY_PORT = 80

memcache = None
iaas = None

import time

class ServiceNode(object):
  def __init__(self, vmid, runProxy=False, runWeb=False, runPHP=False):
    self.vmid = vmid
    self.ip = iaas.getVMInfo(vmid)['ip']
    self.isRunningProxy = runProxy
    self.isRunningWeb = runWeb
    self.isRunningPHP = runPHP
  
  def __repr__(self):
    return 'ServiceNode(vmid=%s, ip=%s, proxy=%s, web=%s, php=%s)' % (str(self.vmid), self.ip, str(self.isRunningProxy), str(self.isRunningWeb), str(self.isRunningPHP))
  
  def __cmp__(self, other):
    if self.vmid == other.vmid: return 0
    elif self.vmid < other.vmid: return -1
    else: return 1

class CodeVersion(object):
  def __init__(self, id, filename, atype, description=''):
    self.id = id
    self.filename = filename
    self.type = atype
    self.description = description
    self.timestamp = time.time()
  
  def __repr__(self):
    return 'CodeVersion(id=%s, filename=%s)' % (self.id, self.filename)
  
  def __cmp__(self, other):
    if self.id == other.id: return 0
    elif self.id < other.id: return -1
    else: return 1

class PHPConfiguration(object):
  defaults = {'max_execution_time': '30',
              'memory_limit': '128M',
              'error_reporting': 'E_ALL & ~E_DEPRECATED',
              'log_errors': 'Off',
              'display_errors': 'Off',
              'upload_max_filesize': '2M',
              }
  def __init__(self):
    self.conf = {}
  
  def setAttribute(self, attr_name, value):
    self.conf[attr_name] = value

class PHP_FPM_Configuration(object):
  def __init__(self, port=PHP_PORT, scalaris='', php_conf=PHPConfiguration()):
    self.port = port
    self.php_conf = php_conf
    self.scalaris = scalaris

class WebServerConfiguration(object):
  def __init__(self, port=WEB_PORT, doc_root='/var/www', php=[]):
    self.port = port
    self.doc_root = doc_root
    self.php_backends = php

class ProxyConfiguration(object):
  def __init__(self, port=PROXY_PORT, web=[]):
    self.port = port
    self.web_backends = web

class Configuration(object):
  '''Representation of the deployment configuration'''
  def __init__(self):
    self.proxy_count = 0
    self.web_count = 1
    self.php_count = 0
    
    self.serviceNodes = {}
    
    self.web_config = WebServerConfiguration()
    self.php_config = PHP_FPM_Configuration()
    self.proxy_config = ProxyConfiguration()
    
    self.codeVersions = {}
    self.currentCodeVersion = None
  
  def update_mappings(self):
    self.web_config.php_backends = self.getPHPTuples()
    self.proxy_config.web_backends = self.getWebTuples()
  
  def getProxyServiceNodes(self):
    return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningProxy ]
  
  def getWebServiceNodes(self):
    return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningWeb ]
  
  def getPHPServiceNodes(self):
    return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningPHP ]
  
  def getPHPTuples(self):
    return [ [serviceNode.ip, PHP_PORT] for serviceNode in self.serviceNodes.values() if serviceNode.isRunningPHP ]
  
  def getWebTuples(self):
    return [ [serviceNode.ip, WEB_PORT] for serviceNode in self.serviceNodes.values() if serviceNode.isRunningWeb ]
  
  def getPHPIPs(self):
    return [ serviceNode.ip for serviceNode in self.serviceNodes.values() if serviceNode.isRunningPHP ]
  
  def getWebIPs(self):
    return [ serviceNode.ip for serviceNode in self.serviceNodes.values() if serviceNode.isRunningWeb ]
  
  def getProxyIPs(self):
    return [ serviceNode.ip for serviceNode in self.serviceNodes.values() if serviceNode.isRunningProxy ]

