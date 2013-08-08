# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import httplib
import json

from conpaas.core import https


class AgentException(Exception):
    pass


def _check(response):
    code, body = response
    if code != httplib.OK:
        raise AgentException('Received http response code %d' % (code))
    try:
        data = json.loads(body)
    except Exception as e:
        raise AgentException(*e.args)
    if data['error']:
        raise AgentException(data['error'])
    else:
        return True


def create_master(host, port, master_server_id):
    """TODO: with dump?"""
    method = 'create_master'
    params = {
        'master_server_id': master_server_id
    }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))


'''
    Methods called by the manager and executed on a master agent
'''


def create_slave(host, port, slaves):
    method = 'create_slave'
    params = {'slaves': slaves}
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))


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


def setup_slave(host, port, slave_server_id, master_host, master_log_file,
                master_log_pos, mysqldump_path):
    '''
    Method called by a master agent to configure a slave agent
    (is executed inside the slave)
    '''
    params = {
        'method': 'setup_slave',
        'master_host': master_host,
        'master_log_file': master_log_file,
        'master_log_pos': master_log_pos,
        'slave_server_id': slave_server_id
    }
    f = open(mysqldump_path, 'r')
    filecontent = f.read()
    f.close()
    files = [('mysqldump_file', mysqldump_path, filecontent)]
    return _check(https.client.https_post(host, port, '/', params, files=files))
