'''
Copyright (c) 2010-2012, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the <ORGANIZATION> nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.


Created on Mar 9, 2011

@author: ielhelw
'''

BACKEND_PORT = 9000
WEB_PORT = 8080
PROXY_PORT = 80

memcache = None
iaas = None

import time
from conpaas.core.node import ServiceNode

class WebServiceNode(ServiceNode):
  def __init__(self, node, runProxy=False, runWeb=False, runBackend=False):
    ServiceNode.__init__(self, node.vmid, node.ip, node.cloud_name)
    self.isRunningProxy = runProxy
    self.isRunningWeb = runWeb
    self.isRunningBackend = runBackend
  
  def __repr__(self):
    return 'ServiceNode(vmid=%s, ip=%s, proxy=%s, web=%s, backend=%s)' % (str(self.vmid), self.ip, str(self.isRunningProxy), str(self.isRunningWeb), str(self.isRunningBackend))
  
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

class PHPINIConfiguration(object):
  defaults = {'max_execution_time': '30',
              'memory_limit': '128M',
              'log_errors': 'Off',
              'display_errors': 'Off',
              'upload_max_filesize': '2M',
              }
  ## Do not use $ to match end of string because it matches the end of the
  ## string or just before the newline at the end of the string.
  ## Use \Z matches the end of string
  format = {'max_execution_time': '^\d+\Z',
              'memory_limit': '^\d+[KkMmGg]?\Z',
              'log_errors': '^On|Off\Z',
              'display_errors': '^On|Off\Z',
              'upload_max_filesize': '^\d+[KkMmGg]?\Z',
              }
  def __init__(self):
    self.conf = {}
  
  def setAttribute(self, attr_name, value):
    self.conf[attr_name] = value

class PHP_FPM_Configuration(object):
  def __init__(self, port=BACKEND_PORT, scalaris='', php_conf=PHPINIConfiguration()):
    self.port = port
    self.php_conf = php_conf
    self.scalaris = scalaris

class WebServerConfiguration(object):
  def __init__(self, port=WEB_PORT, php=[]):
    self.port = port
    self.backends = php

class ProxyConfiguration(object):
  def __init__(self, port=PROXY_PORT, web=[]):
    self.port = port
    self.web_backends = web

class TomcatConfiguration(object):
  def __init__(self, port=BACKEND_PORT):
    self.port = BACKEND_PORT

class ServiceConfiguration(object):
  '''Representation of the deployment configuration'''
  def __init__(self):
    self.proxy_count = 0
    self.web_count = 1
    self.backend_count = 0
    
    self.serviceNodes = {}
    
    self.web_config = WebServerConfiguration()
    self.proxy_config = ProxyConfiguration()
    
    self.codeVersions = {}
    self.currentCodeVersion = None
  
  def update_mappings(self):
    self.web_config.backends = self.getBackendTuples()
    self.proxy_config.web_backends = self.getWebTuples()
  
  def getProxyServiceNodes(self):
    return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningProxy ]
  
  def getWebServiceNodes(self):
    return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningWeb ]
  
  def getBackendServiceNodes(self):
    return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningBackend ]
  
  def getBackendTuples(self):
    return [ {'ip': serviceNode.ip, 'port': BACKEND_PORT} for serviceNode in self.serviceNodes.values() if serviceNode.isRunningBackend ]
  
  def getWebTuples(self):
    return [ {'ip': serviceNode.ip, 'port': WEB_PORT} for serviceNode in self.serviceNodes.values() if serviceNode.isRunningWeb ]
  
  def getBackendIPs(self):
    return [ serviceNode.ip for serviceNode in self.serviceNodes.values() if serviceNode.isRunningBackend ]
  
  def getWebIPs(self):
    return [ serviceNode.ip for serviceNode in self.serviceNodes.values() if serviceNode.isRunningWeb ]
  
  def getProxyIPs(self):
    return [ serviceNode.ip for serviceNode in self.serviceNodes.values() if serviceNode.isRunningProxy ]

class PHPServiceConfiguration(ServiceConfiguration):
  def __init__(self):
    ServiceConfiguration.__init__(self)
    self.backend_config = PHP_FPM_Configuration()
    self.prevCodeVersion = None

class JavaServiceConfiguration(ServiceConfiguration):
  def __init__(self):
    ServiceConfiguration.__init__(self)
    self.backend_config = TomcatConfiguration()
    self.prevCodeVersion = None
