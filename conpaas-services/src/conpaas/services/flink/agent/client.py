import json
import httplib

from conpaas.core import https
from conpaas.core.misc import file_get_contents

class AgentException(Exception):
    pass


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

def init_agent(host, port, master_ip):
    """POST (master_ip) init_agent"""
    method = 'init_agent'
    params = { 'master_ip' : master_ip }
    return _check(https.client.jsonrpc_post(host, port, '/', method, params=params))

def start_master(host, port):
    """POST () start_master"""
    method = 'start_master'
    return _check(https.client.jsonrpc_post(host, port, '/', method))

def start_worker(host, port):
    """POST () start_worker"""
    method = 'start_worker'
    return _check(https.client.jsonrpc_post(host, port, '/', method))

def stop_worker(host, port):
    """POST () stop_worker"""
    method = 'stop_worker'
    return _check(https.client.jsonrpc_post(host, port, '/', method))

def wait_unregister(host, port):
    """POST () wait_unregister"""
    method = 'wait_unregister'
    return _check(https.client.jsonrpc_post(host, port, '/', method))
