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


Created on Mar 11, 2011

@author: ielhelw
'''

class AgentException(Exception): pass

def getWebServerState(host, port):
  return True

def createWebServer(host, port, web_port, code_versions):
  return True

def updateWebServer(host, port, web_port, code_versions):
  return True

def stopWebServer(host, port):
  return True

def getHttpProxyState(host, port):
  return True

def createHttpProxy(host, port, proxy_port, code_version, web_list=[], fpm_list=[], tomcat_list=[], tomcat_servlets=[]):
  return True

def updateHttpProxy(host, port, proxy_port, code_version, web_list=[], fpm_list=[], tomcat_list=[], tomcat_servlets=[]):
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
