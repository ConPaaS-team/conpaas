# -*- coding: utf-8 -*-

"""
    cpsdirector.manifest
    =======================

    ConPaaS director: manifest support.

    :copyright: (C) 2013 by Contrail Consortium.
"""

from flask import Blueprint
from flask import jsonify, request, g

import simplejson
import time
import socket
import urllib2

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

    if msg is not 'ok':
        return build_response(jsonify({
            'error' : True,
            'msg' : msg }))

    log('Manifest created')
    return simplejson.dumps(True)

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
        tmp = {}
        tmp['Type'] = service.type
        tmp['ServiceName'] = service.name
        tmp['Cloud'] = service.cloud
        manifest['Services'].append(tmp)

    return simplejson.dumps(manifest)

from cpsdirector.service import callmanager

class MGeneral():
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

from cpsdirector.service import _start as service_start
from cpsdirector.service import _rename as service_rename
class MPhp(MGeneral):
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

        if json.get('Archive'):
            res = self.upload_code(sid, json.get('Archive'))
            if 'error' in res:
                return res['error']

            res = self.enable_code(sid, res['codeVersionId']);
            if 'error' in res:
                return res['error']

        env = self.update_environment(appid)
        url = ''

        if json.get('StartupScript'):
            url = json.get('StartupScript')

        res = self.upload_startup_script(sid, url, env)
        if 'error' in res:
            return res['error']

        if not json.get('Start') or json.get('Start') == 0:
            return 'ok'

        # Start == 1
        res = self.startup(sid)
        if 'error' in res:
            return res['error']

        self.wait_for_state(sid, 'RUNNING')

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

class MJava(MGeneral):
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

        if json.get('Archive'):
            res = self.upload_code(sid, json.get('Archive'))
            if 'error' in res:
                return res['error']

            res = self.enable_code(sid, res['codeVersionId']);
            if 'error' in res:
                return res['error']

        if json.get('StartupScript'):
            res = self.upload_startup_script(sid, json.get('StartupScript'))
            if 'error' in res:
                return res['error']

        if not json.get('Start') or json.get('Start') == 0:
            return 'ok'

        # Start == 1
        res = self.startup(sid)
        if 'error' in res:
            return res['error']

        self.wait_for_state(sid, 'RUNNING')

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

class MMySql(MGeneral):
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

        if json.get('StartupScript'):
            res = self.upload_startup_script(sid, json.get('StartupScript'))
            if 'error' in res:
                return res['error']

        if not json.get('Start') or json.get('Start') == 0:
            return 'ok'

        # Start == 1
        res = self.startup(sid)
        if 'error' in res:
            return res['error']

        self.wait_for_state(sid, 'RUNNING')

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
                    'slaves': 1
            }

            if json.get('StartupInstances').get('slaves'):
                params['slaves'] = int(json.get('StartupInstances').get('slaves'))

            res = self.add_nodes(sid, params)
            if 'error' in res:
                return res['error']

        return 'ok'

class MScalaris(MGeneral):
    def start(self, json, appid):
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

        if json.get('StartupScript'):
            res = self.upload_startup_script(sid, json.get('StartupScript'))
            if 'error' in res:
                return res['error']

        if not json.get('Start') or json.get('Start') == 0:
            return 'ok'

        # Start == 1
        res = self.startup(sid)
        if 'error' in res:
            return res['error']

        self.wait_for_state(sid, 'RUNNING')

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

        if json.get('StartupScript'):
            res = self.upload_startup_script(sid, json.get('StartupScript'))
            if 'error' in res:
                return res['error']

        if not json.get('Start') or json.get('Start') == 0:
            return 'ok'

        # Start == 1
        res = self.startup(sid)
        if 'error' in res:
            return res['error']

        self.wait_for_state(sid, 'RUNNING')

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

        if json.get('StartupScript'):
            res = self.upload_startup_script(sid, json.get('StartupScript'))
            if 'error' in res:
                return res['error']

        if not json.get('Start') or json.get('Start') == 0:
            return 'ok'

        # Start == 1
        res = self.startup(sid)
        if 'error' in res:
            return res['error']

        self.wait_for_state(sid, 'RUNNING')

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
    def createvolume(self, service_id, name, owner):
        params = {
                'volumeName': name,
                'owner' : owner
        }

        res = callmanager(service_id, 'createVolume', True, params)

        return res

    def start(self, json, appid):
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

        if json.get('StartupScript'):
            res = self.upload_startup_script(sid, json.get('StartupScript'))
            if 'error' in res:
                return res['error']

        if not json.get('Start') or json.get('Start') == 0:
            return 'ok'

        # Start == 1
        res = self.startup(sid)
        if 'error' in res:
            return res['error']

        self.wait_for_state(sid, 'RUNNING')

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

        if json.get('StartupScript'):
            res = self.upload_startup_script(sid, json.get('StartupScript'))
            if 'error' in res:
                return res['error']

        if not json.get('Start') or json.get('Start') == 0:
            return 'ok'

        # Start == 1
        res = self.startup(sid)
        if 'error' in res:
            return res['error']

        self.wait_for_state(sid, 'RUNNING')

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

from cpsdirector.application import check_app_exists
from cpsdirector.application import get_default_app
from cpsdirector.application import get_app_by_name
from cpsdirector.application import _createapp as createapp
def new_manifest(json):
    try:
        parse = simplejson.loads(json)
    except:
        return 'Error parsing json'

    app_name = parse.get('Application')
    appid = get_default_app(g.user.uid).aid
    if app_name:
        if not check_app_exists(app_name):
            res = createapp(app_name)
            appid = simplejson.loads(res.data).get('aid')
        else:
            appid = get_app_by_name(g.user.uid, app_name).aid

    if not parse.get('Services'):
        return 'ok'

    for service in parse.get('Services'):
        if service.get('Type') == 'php':
            msg = MPhp().start(service, appid)
        elif service.get('Type') == 'java':
            msg = MJava().start(service, appid)
        elif service.get('Type') == 'mysql':
            msg = MMySql().start(service, appid)
        elif service.get('Type') == 'scalaris':
            msg = MScalaris().start(service, appid)
        elif service.get('Type') == 'hadoop':
            msg = MHadoop().start(service, appid)
        elif service.get('Type') == 'selenium':
            msg = MSelenium().start(service, appid)
        elif service.get('Type') == 'xtreemfs':
            msg = MXTreemFS().start(service, appid)
        elif service.get('Type') == 'taskfarm':
            msg = MTaskFarm().start(service, appid)
        else:
            return 'Service %s does not exists' % service.get('Type')

        if msg is not 'ok':
            return msg

    return 'ok'
