#!/usr/bin/python

import os
import sys
import time
import socket
import zipfile
import httplib
import urllib
import urllib2
import urlparse
import StringIO
import simplejson

CONFDIR = os.path.join(os.environ['HOME'], ".conpaas")

if not os.path.isdir(CONFDIR):
    os.mkdir(CONFDIR)

USERNAME = "username"
PASSWORD = "password"
CONPAAS_DIR = os.path.join(os.environ['HOME'],  "conpaas-director", "conpaas-services")

sys.path.append(os.path.join(CONPAAS_DIR, "src"))
sys.path.append(os.path.join(CONPAAS_DIR, "contrib"))

from conpaas.core import https
https.client.conpaas_init_ssl_ctx(CONFDIR, 'user')

def usage():
    print "Usage: %s COMMAND [params]" % sys.argv[0]
    print "COMMAND is one of the following"
    print
    print "    target URL"
    print "    getcerts"
    print "    list"
    print "    start servicename"
    print "    stop serviceid"
    print "    info serviceid"
    print "    logs serviceid"
    print "    available_services"
    print
    sys.exit(0)
    
def callapi(method, post, data):
    try:
        endpoint = open(os.path.join(CONFDIR, "target")).read()
    except IOError:
        print "E: Please set your director URL using the 'target' subcommand"
        sys.exit(1)

    url = "%s/%s" % (endpoint, method)
    data['username'] = USERNAME
    data['password'] = PASSWORD
    data = urllib.urlencode(data)

    if post:
        res = urllib2.urlopen(url, data)
    else:
        url += "?" + data
        res = urllib2.urlopen(url)

    rawdata = res.read()

    try:
        return simplejson.loads(rawdata)
    except simplejson.decoder.JSONDecodeError:
        return rawdata

def http_jsonrpc_post(hostname, port, uri, method, params):
    url = "http://%s:%s%s" % (hostname, port, uri)

    data = simplejson.dumps({ 'method': method, 'params': params, 
        'jsonrpc': '2.0', 'id': 1 })

    req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    res = urllib2.urlopen(req).read()
    return res

def http_file_upload_post(host, port, uri, params={}, files=[]):
    content_type, body = https.client._encode_multipart_formdata(params, files)
    h = httplib.HTTP(host, port)
    h.putrequest('POST', uri)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def callmanager(service_id, method, post, data):
    service = service_dict(service_id)

    # temporary: task farm has a few peculiarities
    # port 8475 and http (no ssl)
    if service['type'] == "taskfarm":
        port = 8475
        jsonrpc_post = http_jsonrpc_post
        jsonrpc_get = http_jsonrpc_post

        if method == 'shutdown':
            method = 'terminate_workers'
    else:
        port = 443
        jsonrpc_post = https.client.jsonrpc_post
        jsonrpc_get = https.client.jsonrpc_get
             
    if post:
        res = jsonrpc_post(service['manager'], port, '/', method, params=data)

    else:
        res = jsonrpc_get(service['manager'], port, '/', method, params=data)

    try:
        data = simplejson.loads(res[1])
    except ValueError:
        data = simplejson.loads(res)

    return data.get('result', data)

def __longestvalues(rows):
    maxlens = {}

    fields = rows[0].keys()

    for field in fields:
        maxlens[field] = len(field)
        for row in rows:
            curlen = len(str(row[field]))
            if curlen > maxlens[field]:
                maxlens[field] = curlen 

    return maxlens

def __prettytable(print_order, rows):
    maxlens = __longestvalues(rows)

    # Header
    headerstr = [ "{%d:%d}" % (idx, maxlens[key]) 
        for idx, key in enumerate(print_order) ]

    output = " ".join(headerstr).format(*print_order)
    output += "\n" + "-" * (sum([ maxlens[el] for el in print_order ]) 
        + len(print_order) - 1)

    # Rows
    rowstr = [ "{%s:%d}" % (key, maxlens[key]) 
        for idx, key in enumerate(print_order) ]

    for row in rows:
        output += "\n" + " ".join(rowstr).format(**row)

    return output

def list():
    services = callapi("list", False, {})
    if services:
        print __prettytable(( 'type', 'sid', 'vmid', 'name', 'manager' ), 
            services)
    else:
        print "No running services"

def __wait_for_state(sid, state):
    res = { 'state': None }

    while res['state'] != state:
        try:
            res = callmanager(sid, "get_service_info", False, {})
        except (socket.error, urllib2.URLError):
            time.sleep(2)

def start():
    param = sys.argv[2]

    res = callapi("start/" + param, True, {})
    sid = res['sid']

    print "Creating new manager on " + res['manager'] + "... ",
    sys.stdout.flush()

    if res["type"] == "taskfarm":
        __wait_for_state(sid, 'RUNNING')
    else:
        __wait_for_state(sid, 'INIT')

    print "done."
    sys.stdout.flush()

    callmanager(sid, "startup", True, {})
    print "Your service is starting up.",
    sys.stdout.flush()

def stop():
    param = sys.argv[2]

    print "Shutting down service... ",
    sys.stdout.flush()

    try:
        res = callmanager(param, "get_service_info", False, {})
        if res['state'] == "RUNNING":
            res = callmanager(param, "shutdown", True, {})
    except socket.error:
        # manager unreachable
        pass

    res = callapi("stop/" + param, True, {})
    if res:
        print "done."
    else:
        print "failed."

def service_dict(sid):
    services = callapi("list", False, {})

    for service in services:
        if str(service['sid']) == str(sid):
            service.pop('state')
            return service

    return []

def info():
    param = sys.argv[2]

    service = service_dict(param)
    for key, value in service.items():
        print "%s: %s" % (key, value)

    res = callmanager(service['sid'], "get_service_info", False, {})
    print "state:", res['state']

    if service['type'] in ('php', 'java'):
        nodes = callmanager(service['sid'], "list_nodes", False, {})
        for proxy in nodes['proxy']:
            params = { 'serviceNodeId': proxy }
            details = callmanager(service['sid'], "get_node_info", False, params)
            print "url:", "http://%s" % details['serviceNode']['ip']

    if service['type'] == "selenium":
        nodes = callmanager(service['sid'], "list_nodes", False, {})
        # Only one HUB
        hub = nodes['hub'][0]
        params = { 'serviceNodeId': hub }
        details = callmanager(service['sid'], "get_node_info", False, params)
        print "url:", "http://%s:4444" % details['serviceNode']['ip']

    if service['type'] == "taskfarm":
        print "total tasks:", res['noTotalTasks']
        print "completed tasks:", res['noCompletedTasks']

def logs():
    param = sys.argv[2]

    res = callmanager(param, "getLog", False, {})
    print res['log']

def getcerts():
    res = callapi("getcerts", False, {})

    zipdata = zipfile.ZipFile(StringIO.StringIO(res))
    zipdata.extractall(path=CONFDIR)

    for name in zipdata.namelist():
        print os.path.join(CONFDIR, name)

def target():
    try:
        url = urlparse.urlparse(sys.argv[2])
    except IndexError:
        usage()

    if url.scheme != "https":
        print "E: Invalid target URL. Try with something like https://conpaas.example.com:1234"
        sys.exit(1)

    targetfile = open(os.path.join(CONFDIR, "target"), 'w')
    targetfile.write(sys.argv[2])
    targetfile.close()

def available_services():
    print callapi('available_services', False, {})

def upload_bag_of_tasks(host, port, filename, xtreemfs_location):
    """eg: upload_bag_of_tasks(host="192.168.122.17", 
                               port="8475",
                               filename="/var/lib/outsideTester/contrail3/test.bot", 
                               xtreemfs_location="192.168.122.1/uc3")
    """
    params = { 'uriLocation': xtreemfs_location, 'method': 'start_sampling' }
    filecontents = open(filename).read()
    return http_file_upload_post(host, port, '/', params, 
        files=[('botFile', filename, filecontents)])

if __name__ == "__main__":
    try:
        command = sys.argv[1]
    except IndexError:
        usage()

    if command not in ('list', 'start', 'stop', 'info', 'logs', 'getcerts', 'target', 'available_services'):
        usage()

    if command in ('stop', 'info', 'logs'):
        # params requiring a service id
        services = callapi("list", False, {})
        try:
            sid = int(sys.argv[2])
        except (IndexError, ValueError):
            usage()

        service_exists = [ service for service in services if service['sid'] == sid ]
        if not service_exists:
            print "E: cannot find service %s" % sid
            sys.exit(1)

    globals()[command]()
  
