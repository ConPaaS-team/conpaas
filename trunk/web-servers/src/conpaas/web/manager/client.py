'''
Created on Mar 29, 2011

@author: ielhelw
'''

import httplib, json

from conpaas.web.http import _http_get, _http_post

def getState(host, port):
  params = {'action': 'getState'}
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def getStateChanges(host, port):
  params = {'action': 'getStateChanges'}
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def getLog(host, port):
  params = {'action': 'getLog'}
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def startup(host, port):
  params = {'action': 'startup'}
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def shutdown(host, port):
  params = {'action': 'shutdown'}
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def addServiceNodes(host, port, proxy=None, web=None, php=None):
  params = {'action': 'addServiceNodes'}
  if proxy: params['proxy'] = proxy
  if web: params['web'] = web
  if php: params['php'] = php
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def removeServiceNodes(host, port, proxy=None, web=None, php=None):
  params = {'action': 'removeServiceNodes'}
  if proxy: params['proxy'] = proxy
  if web: params['web'] = web
  if php: params['php'] = php
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def listServiceNodes(host, port):
  params = {'action': 'listServiceNodes'}
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def getServiceNodeById(host, port, serviceNodeId):
  params = {
            'action': 'getServiceNodeById',
            'serviceNodeId': serviceNodeId,
            }
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def listCodeVersions(host, port):
  params = {'action': 'listCodeVersions'}
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def downloadCodeVersion(host, port, codeVersionId):
  params = {
            'action': 'downloadCodeVersion',
            'codeVersionId': codeVersionId,
            }
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return body

def uploadCodeVersion(host, port, filename):
  params = {'action': 'uploadCodeVersion'}
  files = {'code': filename}
  code, body = _http_post(host, port, '/', params=params, files=files)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def getConfiguration(host, port):
  params = {'action': 'getConfiguration'}
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def updateConfiguration(host, port, codeVersionId=None, phpconf={}):
  params = {'action': 'updateConfiguration'}
  if codeVersionId != None:
    params['codeVersionId'] = codeVersionId
  i = 0
  for key in phpconf:
    params['phpconf.%s' % key] = phpconf[key]
    i += 1
  code, body = _http_post(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)

def getHighLevelMonitoring(host, port):
  params = {'action': 'getHighLevelMonitoring'}
  code, body = _http_get(host, port, '/', params=params)
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  return json.loads(body)
