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

def createOSD(host, port, dir_serviceHost, uuid):
  method = 'createOSD'
  params = {
      'dir_serviceHost':dir_serviceHost,
      'uuid' : uuid
  }
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def stopOSD(host, port):
  method = 'stopOSD'
  return _check(https.client.jsonrpc_post(host, port, '/', method))
