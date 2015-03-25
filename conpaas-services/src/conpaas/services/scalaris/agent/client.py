# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import httplib, json

from conpaas.core import https

def _check(response):
  code, body = response
  if code != httplib.OK: raise Exception('Received http response code %d' % (code))
  data = json.loads(body)
  if data['error']: raise Exception(data['error'])
  else: return data['result']

def check_agent_process(host, port):
  method = 'check_agent_process'
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def get_service_info(host, port):
  method = 'get_service_info'
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def startup(host, port, ip, cloud_group, number_of_cloudgroups, first_in_group):
  method = 'startup'
  return _check(https.client.jsonrpc_post(host, port, '/', method,
                                          params={'ip': ip, 'cloud_group': cloud_group,
                                           'first_in_group': first_in_group,
                                           'number_of_cloudgroups': number_of_cloudgroups}))

def graceful_leave(host, port):
  method = 'graceful_leave'
  return _check(https.client.jsonrpc_post(host, port, '/', method, params={}))
