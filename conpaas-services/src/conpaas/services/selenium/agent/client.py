# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from conpaas.core.https import client

def check_agent_process(host, port):
    """GET () check_agent_process"""
    method = 'check_agent_process'
    return client.check_response(client.jsonrpc_get(host, port, '/', method))

def create_hub(host, port):
    """POST (my_ip) create_hub"""
    method = 'create_hub'
    params = { 'my_ip': host }
    return client.check_response(client.jsonrpc_post(
        host, port, '/', method, params))

def create_node(host, port, hub_ip):
    """POST (my_ip, hub_ip) create_node"""
    method = 'create_node'
    params = { 'my_ip': host, 'hub_ip': hub_ip }
    return client.check_response(client.jsonrpc_post(
        host, port, '/', method, params))
