# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import json
import httplib

from conpaas.core import https 

def _check(response):
    """Check the given HTTP response, returning the result if everything went
    fine"""
    code, body = response
    if code != httplib.OK: 
        raise Exception('Received http response code %d' % (code))

    data = json.loads(body)
    if data['error']: 
        raise Exception(data['error'])
    
    return data['result']

def check_agent_process(host, port):
    """GET () check_agent_process"""
    method = 'check_agent_process'
    return _check(https.client.jsonrpc_get(host, port, '/', method))

def create_hub(host, port):
    """POST (my_ip) create_hub"""
    method = 'create_hub'
    params = { 'my_ip': host }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params))

def create_node(host, port, hub_ip):
    """POST (my_ip, hub_ip) create_node"""
    method = 'create_node'
    params = { 'my_ip': host, 'hub_ip': hub_ip }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params))

def condor_off(host, port):
    """POST (my_ip) condor_off"""
    method = 'condor_off'
    # params = { 'my_ip': host, 'hub_ip': hub_ip }
    return _check(https.client.jsonrpc_post(host, port, '/', method))
