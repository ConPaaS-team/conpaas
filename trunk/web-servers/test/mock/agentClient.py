'''
Created on Mar 11, 2011

@author: ielhelw
'''

class AgentException(Exception): pass

def getWebServerState(host, port):
  return True

def createWebServer(host, port, doc_root, web_port, codeVersion, php, prevCodeVersion=None):
  return True

def updateWebServer(host, port, doc_root, web_port, codeVersion, php, prevCodeVersion=None):
  return True

def stopWebServer(host, port):
  return True

def getTomcatWebServerState(host, port):
  return True

def createTomcatWebServer(host, port, doc_root, web_port, php, codeCurrent,
               servletsCurrent, codeOld=None, servletsOld=[]):
  return True

def updateTomcatWebServer(host, port, doc_root, web_port, php, codeCurrent,
               servletsCurrent, codeOld=None, servletsOld=[]):
  return True

def stopTomcatWebServer(host, port):
  return True

def getHttpProxyState(host, port):
  return True

def createHttpProxy(host, port, proxy_port, backends, codeVersion):
  return True

def updateHttpProxy(host, port, proxy_port, backends, codeVersion):
  return True

def stopHttpProxy(host, port):
  return True

def getPHPState(host, port):
  return True

def createPHP(host, port, php_port, scalaris, conf):
  return True

def updatePHP(host, port, php_port, scalaris, conf):
  return True

def stopPHP(host, port):
  return True

def updatePHPCode(host, port, codeVersionId, filename, filepath):
  return True

def getTomcatState(host, port):
  return True

def createTomcat(host, port, tomcat_port):
  return True

def stopTomcat(host, port):
  return True

def updateTomcatCode(host, port, codeVersionId, filetype, filepath):
  return True
