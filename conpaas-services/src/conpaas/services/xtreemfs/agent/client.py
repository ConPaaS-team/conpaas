# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from conpaas.core import https
import httplib, json

class AgentException(Exception):
  pass

def _check(response):
  code, body = response
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  data = json.loads(body)
  if data['error']: raise Exception(data['error'])
  else: return data['result']

def check_agent_process(host, port):
  method = 'check_agent_process'
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def startup(host, port):
  method = 'startup'
  return _check(https.client.jsonrpc_post(host, port, '/', method))

def createMRC(host, port, dir_serviceHost, uuid):
  method = 'createMRC'
  params = {
    'dir_serviceHost' : dir_serviceHost,
    'uuid' : uuid
  }
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def createDIR(host, port, uuid):
  method = 'createDIR'
  params = {
    'uuid' : uuid
  }
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def createOSD(host, port, dir_serviceHost, uuid, mkfs=True):
  method = 'createOSD'
  params = {
      'dir_serviceHost' : dir_serviceHost,
      'uuid' : uuid,
      'mkfs': mkfs
  }
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def stopDIR(host, port):
  method = 'stopDIR'
  return _check(https.client.jsonrpc_post(host, port, '/', method))

def stopMRC(host, port):
  method = 'stopMRC'
  return _check(https.client.jsonrpc_post(host, port, '/', method))

def stopOSD(host, port, drain = True):
  method = 'stopOSD'
  params = {
      'drain': drain
  }
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))
  
def get_snapshot(host, port):
  method = 'get_snapshot'
  return https.client.jsonrpc_post(host, port, '/', method)

