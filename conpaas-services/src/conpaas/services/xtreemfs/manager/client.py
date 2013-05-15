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

Created May, 2012

@author Dragos Diaconescu

'''

import httplib, json
from conpaas.core import https

def _check(response):
  code, body = response
  if code != httplib.OK: raise HttpError('Received http response code %d' % (code))
  data = json.loads(body)
  if data['error']: raise Exception(data['error'])
  else: return data['result']

def get_service_info(host, port):
  method = 'get_service_info'
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def startup(host, port):
  method = 'startup'
  return _check(https.client.jsonrpc_post(host, port, '/', method))

def add_nodes(host, port, nr_dir=None, nr_mrc=None, osd=0):
  method = 'add_nodes'
  params = {}
  if nr_dir: params['dir'] = nr_dir
  if nr_mrc: params['mrc'] = nr_mrc
  params['osd'] = osd
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def remove_nodes(host, port,nr_dir=None,nr_mrc=None, osd=0):
  method = 'remove_nodes'
  params = {}
  if nr_dir: params['dir'] = nr_dir
  if nr_mrc: params['mrc'] = nr_mrc
  params['osd'] = osd
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def list_nodes(host, port):
  method = 'list_nodes'
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def createMRC(host, port):
  method = 'createMRC'
  params = {}
  return _check(https.client.jsonrpc_post(host, port, '/', method))

def createDIR(host, port):
  method = 'createDIR'
  params = {}
  return _check(https.client.jsonrpc_post(host, port, '/', method))

def createOSD(host, port):
  method = 'createOSD'
  params = {}
  return _check(https.client.jsonrpc_post(host, port, '/', method))

def createVolume(host, port, volumeName=None):
  method = 'createVolume'
  params = {}
  params['volumeName'] = volumeName
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def deleteVolume(host, port, volumeName=None):
  method = 'deleteVolume'
  params = {}
  params['volumeName'] = volumeName
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def listVolumes(host, port):
  method = 'listVolumes'
  params = {}
  return _check(https.client.jsonrpc_get(host, port, '/', method))
  
def list_striping_policies(host, port):
  method = 'list_striping_policies'
  params = {}
  return _check(https.client.jsonrpc_get(host, port, '/', method))
  
def list_replication_policies(host, port):
  method = 'list_replication_policies'
  params = {}
  return _check(https.client.jsonrpc_get(host, port, '/', method))
  
def list_osd_sel_policies(host, port):
  method = 'list_osd_sel_policies'
  params = {}
  return _check(https.client.jsonrpc_get(host, port, '/', method))
  
def list_replica_sel_policies(host, port):
  method = 'list_replica_sel_policies'
  params = {}
  return _check(https.client.jsonrpc_get(host, port, '/', method))

def set_osd_sel_policy(host, port, volumeName=None, policy=None):
  method = 'set_osd_sel_policy'
  params = {}
  params['volumeName'] = volumeName
  params['policy'] = policy
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def set_replica_sel_policy(host, port, volumeName=None, policy=None):
  method = 'set_replica_sel_policy'
  params = {}
  params['volumeName'] = volumeName
  params['policy'] = policy
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def set_replication_policy(host, port, volumeName=None, policy=None, factor=None):
  method = 'set_replication_policy'
  params = {}
  params['volumeName'] = volumeName
  params['policy'] = policy
  params['factor'] = factor
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def set_striping_policy(host, port, volumeName=None, policy=None, width=None, stripe_size=None):
  method = 'set_striping_policy'
  params = {}
  params['volumeName'] = volumeName
  params['policy'] = policy
  params['width'] = width
  params['stripe-size'] = stripe_size
  return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

