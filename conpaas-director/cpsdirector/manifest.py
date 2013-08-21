# -*- coding: utf-8 -*-

"""
    cpsdirector.manifest
    =======================

    ConPaaS director: manifest support.

    :copyright: (C) 2013 by Contrail Consortium.
"""

from flask import Blueprint
from flask import jsonify, request, g

import os
import time
import base64
import socket
import urllib2
import simplejson

from cpsdirector.common import log
from cpsdirector.common import build_response

manifest_page = Blueprint('manifest_page', __name__)

def check_manifest(json):
    try:
        parse = simplejson.loads(json)
    except:
        log('The uploaded manifest is not valid json')
        return False

    for service in parse.get('Services'):
        if not service.get('Type'):
            log('The "Type" field is mandatory')
            return False

    return True

from cpsdirector.user import cert_required
from multiprocessing import Process
@manifest_page.route("/upload_manifest", methods=['POST'])
@cert_required(role='user')
def upload_manifest():
    json = request.values.get('manifest')
    if not json:
        log('"manifest" is a required argument')
        return build_response(simplejson.dumps(False))

    log('User %s has uploaded the following manifest %s' % (g.user.username, json))

    if not check_manifest(json):
        return simplejson.dumps(False)

    if request.values.get('thread'):
        log('Starting a new process for the manifest')
        p = Process(target=new_manifest, args=(json,))
        p.start()
        log('Process started, now return')
        return simplejson.dumps(True)

    msg = new_manifest(json)

    if msg != 'ok':
        return build_response(jsonify({
            'error' : True,
            'msg' : msg }))

    log('Manifest created')
    return simplejson.dumps(True)

from cpsdirector.service import callmanager
def get_list_nodes(sid):
    nodes = callmanager(sid, "list_nodes", False, {})
    if 'error' in nodes:
        return ''

    tmp = {}
    for node in nodes:
        tmp[node] = len(nodes[node])

    return tmp

from tempfile import mkstemp
from cpsdirector.common import get_director_url
from cpsdirector.common import get_userdata_dir
from os.path import basename
def get_startup_script(sid):
    script = callmanager(sid, "get_startup_script", False, {})
    if 'error' in script:
        return ''

    _, temp_path = mkstemp(prefix='startup', dir=get_userdata_dir())
    open(temp_path, 'w').write(script)

    return '%s/download_data/%s' % (get_director_url(), basename(temp_path))

def get_service_state(sid):
    res = callmanager(sid, "get_service_info", False, {})
    return res['state']

from cpsdirector.service import Service
from cpsdirector.application import get_app_by_id
@manifest_page.route("/download_manifest/<appid>", methods=['POST'])
@cert_required(role='user')
def download_manifest(appid):
    manifest = {}

    app = get_app_by_id(g.user.uid, appid)

    if not app:
        log('The appid %s does not exist' % appid)
        return simplejson.dumps(False)

    manifest['Services'] = []
    manifest['Application'] = app.name

    for service in Service.query.filter_by(application_id=appid):
        svc_manifest = get_manifest_class(
                service.type)().get_service_manifest(service)

        manifest['Services'].append(svc_manifest)

    return simplejson.dumps(manifest)

from os.path import exists
from flask import helpers
@manifest_page.route("/download_data/<fileid>", methods=['GET'])
def download_data(fileid):
    if not exists('%s/%s' % (get_userdata_dir(), fileid)):
        return ''

    return helpers.send_from_directory(get_userdata_dir(), fileid)

class MGeneral(object):

    def get_service_manifest(self, service):
        tmp = {}
        tmp['Type'] = service.type
        tmp['ServiceName'] = service.name
        tmp['Cloud'] = service.cloud

        ret = get_service_state(service.sid)
        if ret == "RUNNING":
            tmp['Start'] = 1

        ret = get_list_nodes(service.sid)
        if ret != '':
            tmp['StartupInstances'] = ret

        ret = get_startup_script(service.sid)
        if ret != '':
            tmp['StartupScript'] = ret

        return tmp

    def check_error(self, ret):
        try:
            return simplejson.loads(ret.data).get('msg')
        except:
            return False

    def startup(self, service_id, cloud = 'default'):
        data = {'cloud': cloud}

        res = callmanager(service_id, "startup", True, data)

        return res

    def shutdown(self, service_id):
        res = callmanager(service_id, "get_service_info", False, {})

        if res['state'] == "RUNNING":
            res = callmanager(service_id, "shutdown", True, {})
        else:
            log("Service is in '%(state)s' state. We can not stop it." % res)

        return res

    def wait_for_state(self, sid, state):
        """Poll the state of service 'sid' till it matches 'state'."""
        res = { 'state': None }

        while res['state'] != state:
            try:
                res = callmanager(sid, "get_service_info", False, {})
            except (socket.error, urllib2.URLError):
                time.sleep(2)

    def update_environment(self, appid):
        env = ''

        # Find mysql ip address
        try:
            sid = Service.query.filter_by(application_id=appid, type='mysql').first().sid
            nodes = callmanager(sid, "list_nodes", False, {})

            params = { 'serviceNodeId': nodes['masters'][0] }
            details = callmanager(sid, "get_node_info", False, params)
            env = env + 'echo "env[MYSQL_IP]=\'%s\'" >> /root/ConPaaS/src/conpaas/services/webservers/etc/fpm.tmpl\n' % details['serviceNode']['ip']
            env = env + 'export MYSQL_IP=\'%s\'\n' % details['serviceNode']['ip']
        except:
            env = env + ''

        # Find xtreemfs ip address
        try:
            sid = Service.query.filter_by(application_id=appid, type='xtreemfs').first().sid
            nodes = callmanager(sid, "list_nodes", False, {})

            params = { 'serviceNodeId': nodes['dir'][0] }
            details = callmanager(sid, "get_node_info", False, params)
            env = env + 'echo "env[XTREEMFS_IP]=\'%s\'" >> /root/ConPaaS/src/conpaas/services/webservers/etc/fpm.tmpl\n' % details['serviceNode']['ip']
            env = env + 'export XTREEMFS_IP=\'%s\'\n' % details['serviceNode']['ip']
        except:
            env = env + ''

        return env

    def upload_startup_script(self, service_id, url, environment=''):
        contents = environment
        filename = 'env.sh'

        if url != '':
            contents = environment + urllib2.urlopen(url).read()
            filename = url.split('/')[-1]

        files = [ ( 'script', filename, contents ) ]

        res = callmanager(service_id, "/", True,
            { 'method': 'upload_startup_script', }, files)

        return res

    def add_nodes(self, service_id, params):
        params['cloud'] = 'default'

        res = callmanager(service_id, 'add_nodes', True, params)

        return res

    def start(self, json, appid, need_env=False):
        """Start the given service. Return service id upon successful
        termination."""
        servicetype = json.get('Type')
        cloud = 'default'

        if json.get('Cloud'):
            cloud = json.get('Cloud')

        res = service_start(servicetype, cloud, appid)
        error = self.check_error(res)
        if error:
            return error

        sid = simplejson.loads(res.data).get('sid')

        self.wait_for_state(sid, 'INIT')

        if json.get('ServiceName'):
            res = service_rename(sid, json.get('ServiceName'))
            error = self.check_error(res)
            if error:
                return error

        env = ''
        if need_env:
            env = self.update_environment(appid)

        url = ''

        if json.get('StartupScript'):
            url = json.get('StartupScript')

        if url or env:
            # Only upload startup script if necessary
            res = self.upload_startup_script(sid, url, env)
            if 'error' in res:
                return res['error']

        if not json.get('Start') or json.get('Start') == 0:
            return sid

        # Start == 1
        res = self.startup(sid)
        if 'error' in res:
            return res['error']

        self.wait_for_state(sid, 'RUNNING')
        return sid

from cpsdirector.service import _start as service_start
from cpsdirector.service import _rename as service_rename
class MPhp(MGeneral):
    
    def get_service_manifest(self, service):
        tmp = MGeneral.get_service_manifest(self, service)

        ret = self.get_archive(service.sid)
        if ret != '':
            tmp['Archive'] = ret

        return tmp

    def get_archive(self, service_id):
        res = callmanager(service_id, 'list_code_versions', False, {})
        if 'error' in res:
            return ''

        version = ''
        filename = ''
        for row in res['codeVersions']:
            if 'current' in row:
                version = row['codeVersionId']
                filename = row['filename']
                break

        if version == '' or filename == '':
            return ''

        params = { 'codeVersionId': version }

        res = callmanager(service_id, "download_code_version", False, params)
        if 'error' in res:
            return ''

        _, temp_path = mkstemp(suffix=filename, dir=get_userdata_dir())
        open(temp_path, 'w').write(res)

        return '%s/download_data/%s' % (get_director_url(), basename(temp_path))

    def upload_code(self, service_id, url):
        contents = urllib2.urlopen(url).read()
        filename = url.split('/')[-1]

        files = [ ( 'code', filename, contents ) ]

        res = callmanager(service_id, "/", True, { 'method': "upload_code_version",  }, files)

        return res

    def enable_code(self, service_id, code_version):
        params = { 'codeVersionId': code_version }

        res = callmanager(service_id, "update_php_configuration", True, params)

        return res

    def start(self, json, appid):
        sid = MGeneral.start(self, json, appid, need_env=True)

        if type(sid) != int:
            # Error!
            return sid

        if json.get('Archive'):
            res = self.upload_code(sid, json.get('Archive'))
            if 'error' in res:
                return res['error']

            res = self.enable_code(sid, res['codeVersionId']);
            if 'error' in res:
                return res['error']

        if json.get('StartupInstances'):
            params = {
                    'proxy': 1,
                    'web': 1,
                    'backend': 1
            }

            if json.get('StartupInstances').get('proxy'):
                params['proxy'] = int(json.get('StartupInstances').get('proxy'))
            if json.get('StartupInstances').get('web'):
                params['web'] = int(json.get('StartupInstances').get('web'))
            if json.get('StartupInstances').get('backend'):
                params['backend'] = int(json.get('StartupInstances').get('backend'))

            res = self.add_nodes(sid, params)
            if 'error' in res:
                return res['error']

        return 'ok'

class MJava(MPhp):

    def enable_code(self, service_id, code_version):
        params = { 'codeVersionId': code_version }

        res = callmanager(service_id, "update_java_configuration", True, params)

        return res

class MMySql(MGeneral):

    def get_service_manifest(self, service):
        tmp = MGeneral.get_service_manifest(self, service)

        ret = self.save_dump(service.sid)
        if ret != '':
            tmp['Dump'] = ret

        password = callmanager(service.sid, "get_password", False, {})
        if password:
            tmp['Password'] = password

        return tmp

    def save_dump(self, service_id):
        res = callmanager(service_id, 'sqldump', False, {})
        if type(res) is dict and 'error' in res:
            log(res['error'])
            return ''

        _, temp_path = mkstemp(dir=get_userdata_dir())
        open(temp_path, 'w').write(res)

        return '%s/download_data/%s' % (get_director_url(), basename(temp_path))

    def load_dump(self, sid, url):
        contents = urllib2.urlopen(url).read()
        filename = url.split('/')[-1]

        files = [ ( 'mysqldump_file', filename, contents ) ]

        res = callmanager(sid, "/", True, { 'method' : 'load_dump' }, files)

        return res

    def set_password(self, sid, password):
        data = { 'user': 'mysqldb', 'password': password }
        res = callmanager(sid, "set_password", True, data)

        return res

    def start(self, json, appid):
        sid = MGeneral.start(self, json, appid)

        if type(sid) != int:
            # Error!
            return sid

        if json.get('Password'):
            res = self.set_password(sid, json.get('Password'))
            if 'error' in res:
                return res['error']

        if json.get('Dump'):
            res = self.load_dump(sid, json.get('Dump'))
            if 'error' in res:
                return res['error']

        if json.get('StartupInstances'):
            params = {
                    'slaves': 0
            }

            if json.get('StartupInstances').get('slaves'):
                params['slaves'] = int(json.get('StartupInstances').get('slaves'))

            res = self.add_nodes(sid, params)
            if 'error' in res:
                return res['error']

        return 'ok'

class MScalaris(MGeneral):
    def start(self, json, appid):
        sid = MGeneral.start(self, json, appid)

        if type(sid) != int:
            # Error!
            return sid

        if json.get('StartupInstances'):
            params = {
                    'scalaris': 1
            }

            if json.get('StartupInstances').get('scalaris'):
                params['scalaris'] = int(json.get('StartupInstances').get('scalaris'))

            res = self.add_nodes(sid, params)
            if 'error' in res:
                return res['error']

        return 'ok'

class MHadoop(MGeneral):
    def start(self, json, appid):
        sid = MGeneral.start(self, json, appid)

        if type(sid) != int:
            # Error!
            return sid

        if json.get('StartupInstances'):
            params = {
                    'workers': 1
            }

            if json.get('StartupInstances').get('workers'):
                params['workers'] = int(json.get('StartupInstances').get('workers'))

            res = self.add_nodes(sid, params)
            if 'error' in res:
                return res['error']

        return 'ok'

class MSelenium(MGeneral):
    def start(self, json, appid):
        sid = MGeneral.start(self, json, appid)

        if type(sid) != int:
            # Error!
            return sid

        if json.get('StartupInstances'):
            params = {
                    'node': 1
            }

            if json.get('StartupInstances').get('node'):
                params['node'] = int(json.get('StartupInstances').get('node'))

            res = self.add_nodes(sid, params)
            if 'error' in res:
                return res['error']

        return 'ok'

class MXTreemFS(MGeneral):

    def set_persistent(self, service_id):
        res = callmanager(service_id, 'get_service_info', False, {})

        if res['persistent']:
            log('Service %s is already persistent' % service_id)
        else:
            res = callmanager(service_id, 'toggle_persistent', True, {})
            log('Service %s is now persistent' % service_id)

        return res['persistent']

    def __get_node_archive_filename(self, node):
        node_id = "%s_%s_%s" % (node['osd_uuid'], node['dir_uuid'],
                node['mrc_uuid'])
        return os.path.join(get_userdata_dir(), node_id + '.tar.gz')

    def get_service_manifest(self, service):
        tmp = MGeneral.get_service_manifest(self, service)

        self.set_persistent(service.sid)
        
        log('Calling get_service_snapshot')
        snapshot = callmanager(service.sid, 'get_service_snapshot', True, {})

        if 'StartupInstances' not in tmp:
            tmp['StartupInstances'] = {}

        tmp['StartupInstances']['resume'] = []

        for node in snapshot:
            node_filename = self.__get_node_archive_filename(node)
            data = base64.b64decode(node.pop('data'))
            open(node_filename, 'wb').write(data)
            log('%s created' % node_filename)

            tmp['StartupInstances']['resume'].append(node)

        return tmp

    def createvolume(self, service_id, name, owner):
        params = {
                'volumeName': name,
                'owner' : owner
        }

        res = callmanager(service_id, 'createVolume', True, params)

        return res

    def start(self, json, appid):
        sid = MGeneral.start(self, json, appid)

        if type(sid) != int:
            # Error!
            return sid

        if json.get('VolumeStartup'):
            name = json.get('VolumeStartup').get('volumeName')
            owner = json.get('VolumeStartup').get('owner')

            # Wait few seconds so that the new node is up.
            time.sleep(20)

            if name != "" and owner != "":
                res = self.createvolume(sid, name, owner)
                if 'error' in res:
                    return res['error']

        if json.get('StartupInstances'):
            params = {
                    'osd': 1
            }

            if json.get('StartupInstances').get('osd'):
                params['osd'] = int(json.get('StartupInstances').get('osd'))

            res = self.add_nodes(sid, params)
            if 'error' in res:
                return res['error']

        return 'ok'

class MTaskFarm(MGeneral):
    def start(self, json, appid):
        sid = MGeneral.start(self, json, appid)

        if type(sid) != int:
            # Error!
            return sid

        if json.get('StartupInstances'):
            params = {
                    'node': 1
            }

            if json.get('StartupInstances').get('node'):
                params['node'] = int(json.get('StartupInstances').get('node'))

            res = self.add_nodes(sid, params)
            if 'error' in res:
                return res['error']

        return 'ok'

def get_manifest_class(service_type):
    if service_type == 'php':
        return MPhp
    elif service_type == 'java':
        return MJava
    elif service_type == 'mysql':
        return MMySql
    elif service_type == 'scalaris':
        return MScalaris
    elif service_type == 'hadoop':
        return MHadoop
    elif service_type == 'selenium':
        return MSelenium
    elif service_type == 'xtreemfs':
        return MXTreemFS
    elif service_type == 'taskfarm':
        return MTaskFarm
    else:
        raise Exception('Service type %s does not exists' % service_type)

from cpsdirector.application import check_app_exists
from cpsdirector.application import _createapp as createapp
def new_manifest(json):
    try:
        parse = simplejson.loads(json)
    except:
        return 'Error parsing json'

    # 'Application' has to be defined
    app_name = parse.get('Application')
    if not app_name:
        return 'Application is not defined'

    if not check_app_exists(app_name):
        # Create application if it does not exist yet
        res = createapp(app_name)
        appid = simplejson.loads(res.data).get('aid')
    else:
        # Try different application names
        for i in range(2, 99):
            new_name = "%s (%d)" % (app_name, i)
            if not check_app_exists(new_name):
                res = createapp(new_name)
                appid = simplejson.loads(res.data).get('aid')
                break

        # If all the applications exists, then exit
        if i is 99:
            return 'Application can not be created'

    if not parse.get('Services'):
        return 'ok'

    for service in parse.get('Services'):
        try:
            cls = get_manifest_class(service.get('Type'))
        except Exception:
            return 'Service %s does not exists' % service.get('Type')

        msg = cls().start(service, appid)

        if msg is not 'ok':
            return msg

    return 'ok'
