# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import httplib
import json
import logging 
from conpaas.core import https


class AgentException(Exception):
    pass


def _check(response):
    code, body = response
    if code != httplib.OK:
        raise AgentException('Received HTTP response code %d' % (code))
    try:
        data = json.loads(body)
    except Exception as e:
        raise AgentException(*e.args)
    if data['error']:
        raise AgentException(data['error'])
    elif data['result']:
	return  data['result']
    else:
        return True


def start_mysqld(host, port, nodes=None, device_name=None):
    method = 'start_mysqld'
    nodes = nodes or []
    params = {'nodes': nodes,
              'device_name': device_name}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params))


def configure_user(host, port, username, password):
    method = 'configure_user'
    params = {'username': username,
              'password': password}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))


def get_all_users(host, port):
    method = 'get_all_users'
    result = https.client.jsonrpc_get(host, port, '/', method)
    if _check(result):
        return result
    else:
        return False


def set_password(host, port, username, password):
    method = 'set_password'
    params = {'username': username,
              'password': password}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))


def remove_user(host, port, name):
    method = 'remove_user'
    params = {'username': name}
    return _check(https.client.jsonrpc_get(host, port, '/', method, params=params))


def check_agent_process(host, port):
    method = 'check_agent_process'
    return _check(https.client.jsonrpc_get(host, port, '/', method))


def load_dump(host, port, mysqldump_path):
    params = {'method': 'load_dump'}
    f = open(mysqldump_path, 'r')
    filecontent = f.read()
    f.close()
    files = [('mysqldump_file', mysqldump_path, filecontent)]
    return _check(https.client.https_post(host, port, '/', params, files=files))


def stop(host, port):
    method = 'stop'
    return _check(https.client.jsonrpc_post(host, port, '/', method))


def getLoad(host, port):
    method = 'getLoad'
    return _check(https.client.jsonrpc_get(host, port, '/', method))


def start_glbd(host, port, nodes):
    method = 'start_glbd'
    params = {'nodes': nodes}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))


def add_glbd_nodes(host, port, nodesIp):
    method = 'add_glbd_nodes'
    params = {'nodesIp': nodesIp}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))


def remove_glbd_nodes(host, port, nodes):
    method = 'remove_glbd_nodes'
    params = {'nodes': nodes}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))
