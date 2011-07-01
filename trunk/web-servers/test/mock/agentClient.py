'''
Created on Mar 11, 2011

@author: ielhelw
'''

class AgentException(Exception): pass

def getWebServerState(host, port):
  return True

def createWebServer(host, port, doc_root, web_port, php):
  return True

def updateWebServer(host, port, doc_root, web_port, php):
  return True

def stopWebServer(host, port):
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

def updateCode(host, port, codeVersionId, filename, filepath):
  return True
