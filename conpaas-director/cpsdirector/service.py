# -*- coding: utf-8 -*-

"""
    cpsdirector.service
    ===================

    ConPaaS director: services implementation

    :copyright: (C) 2013 by Contrail Consortium.
"""

from flask import Blueprint
from flask import jsonify, helpers, request, make_response, g

from sqlalchemy.exc import InvalidRequestError

import sys
import traceback

import simplejson
from datetime import datetime

from cpsdirector import db

from cpsdirector.common import log
from cpsdirector.common import build_response

from cpsdirector import cloud as manager_controller

from cpsdirector import common
from cpsdirector.application import Application

from conpaas.core.services import manager_services
from conpaas.core.https import client

service_page = Blueprint('service_page', __name__)

valid_services = manager_services.keys()

class Service(db.Model):
    sid = db.Column(db.Integer, primary_key=True,
        autoincrement=True)
    name = db.Column(db.String(256))
    type = db.Column(db.String(32))
    state = db.Column(db.String(32))
    created = db.Column(db.DateTime)
    # manager = db.Column(db.String(512))
    # vmid = db.Column(db.String(256))
    cloud = db.Column(db.String(128))
    subnet = db.Column(db.String(18))

    # user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    # user = db.relationship('User', backref=db.backref('services',
    #     lazy="dynamic"))

    application_id = db.Column(db.Integer, db.ForeignKey('application.aid'))
    application = db.relationship('Application', backref=db.backref('services',
                                  lazy="dynamic"))

    def __init__(self, **kwargs):
        # Default values
        self.state = "INIT"
        self.created = datetime.now()

        for key, val in kwargs.items():
            setattr(self, key, val)

    def to_dict(self):
        serv = {}
        app = {}
        for c in self.__table__.columns:
            serv[c.name] = getattr(self, c.name)
            if type(serv[c.name]) is datetime:
                serv[c.name] = serv[c.name].isoformat()

        # for c in self.application.__table__.columns:
        #     app[c.name] = getattr(self.application, c.name)

        app = self.application.to_dict()
        
        return {'service':serv, 'application':app}

    def remove(self):
        db.session.delete(self)
        db.session.commit()
        log('Service %s removed properly' % self.sid)
        return True

def get_service(user_id, application_id, service_id):
    service = Service.query.filter_by(sid=service_id, application_id=application_id).first()
    if not service:
        log('Service %s does not exist' % service_id)
        return

    if service.application.user_id != user_id:
        log('Service %s is not owned by user %s' % (service_id, user_id))
        return

    return service


def callmanager(app_id, service_id, method, post, data, files=[]):
    """Call the manager API.

    'service_id': an integer holding the service id of the manager.
    'method': a string representing the API method name.
    'post': boolean value. True for POST method, false for GET.
    'data': a dictionary representing the data to be sent to the director.
    'files': sequence of (name, filename, value) tuples for data to be uploaded as files.

    callmanager loads the manager JSON response and returns it as a Python
    object.
    """
    client.conpaas_init_ssl_ctx('/etc/cpsdirector/certs', 'director')
    
    application = get_app_by_id(g.user.uid, app_id)
    
    if application is None:
       msg = "Application %s not found." % app_id
       log(msg)
       return { 'error': True,'msg': msg }
    elif application.to_dict()['manager'] is None:
        msg = "Application %s not started." % app_id
        log(msg)
        return { 'error': True,'msg': msg}

    application = application.to_dict()
    # File upload
    if files:
        data['service_id'] = service_id
        res = client.https_post(application['manager'], 443, '/', data, files)
    # POST
    elif post:
        res = client.jsonrpc_post(application['manager'], 443, '/', method, service_id, data)
    # GET
    else:
        res = client.jsonrpc_get(application['manager'], 443, '/', method, service_id, data)

    if res[0] == 200:
        try:
            data = simplejson.loads(res[1])
        except simplejson.decoder.JSONDecodeError:
            # Not JSON, simply return what we got
            return res[1]

        return data.get('result', data)

    raise Exception, "Call to method %s on %s failed: %s.\nParams = %s" % (method, application['manager'], res[1], data)


@service_page.route("/available_services", methods=['GET'])
def available_services():
    """GET /available_services"""
    return simplejson.dumps(valid_services)

from cpsdirector.application import get_default_app, get_app_by_id

from cpsdirector.user import cert_required

def _add(service_type, cloud_name, app_id):
    log('User %s creating a new %s service for application %s' % (g.user.username, service_type, app_id))

    # Use default application id if no appid was specified
    if not app_id:
        app = get_default_app(g.user.uid)
        if not app:
            return build_response(jsonify({ 'error': True,'msg': "No existing applications" }))
        else:
            app_id = app.aid
    else:
        app = get_app_by_id(g.user.uid, app_id)

    # Check if we got a valid service type
    if service_type not in valid_services:
        error_msg = 'Unknown service type: %s' % service_type
        log(error_msg)
        return build_response(jsonify({ 'error': True,'msg': error_msg }))

    data = {'service_type': service_type, 'cloud_name': cloud_name}
    res  = callmanager(app_id, 0, "add_service", True, data)
    
    if 'service_id' in res:  
        sid = res['service_id'] 
        s = Service(sid=sid, name="New %s service" % service_type, type=service_type,
            user=g.user, application=app, manager=app.to_dict()['manager'])
        db.session.add(s)
        db.session.commit()
        log('%s (id=%s) created properly' % (s.name, s.sid))
        return build_response(jsonify(s.to_dict()))

    
    return build_response(jsonify({ 'error': True,'msg': res['error'] }))


@service_page.route("/add/<servicetype>", methods=['POST'])
@service_page.route("/add/<servicetype>/<cloudname>", methods=['POST'])
@cert_required(role='user')
def add(servicetype, cloudname="default"):
    """eg: POST /start/php

    POSTed values might contain 'appid' to specify that the service to be
    created has to belong to a specific application. If 'appid' is omitted, the
    service will belong to the default application.

    Returns a dictionary with service data (manager's vmid and IP address,
    service name and ID) in case of successful authentication and correct
    service creation. False is returned otherwise.
    """
    appid = request.values.get('appid')

    return _add(servicetype, cloudname, appid)

def _rename(app_id, serviceid, newname):
    log('User %s attempting to rename service %s' % (g.user.uid, serviceid))

    service = get_service(g.user.uid, app_id, serviceid)
    if not service:
        return make_response(simplejson.dumps(False))

    if not newname:
        log('"name" is a required argument')
        return build_response(simplejson.dumps(False))

    service.name = newname
    db.session.commit()
    return simplejson.dumps(True)

def _remove(app_id, service_id):
    log('User %s attempting to remove service %s from application %s' % (g.user.uid, service_id, app_id))
    data = {'service_id': service_id}
    res  = callmanager(app_id, 0, "remove_service", True, data)

    if 'error' in res:
        msg = res['msg'] if 'msg' in res else 'An error occurred during service removal'
        return build_response(jsonify({ 'error': True,'msg': msg }))

    service = get_service(g.user.uid, app_id, service_id)
    service.remove()
    

@service_page.route("/rename", methods=['POST'])
@cert_required(role='user')
def rename():
    app_id = request.values.get('app_id')
    service_id = request.values.get('service_id')
    newname = request.values.get('name')
    try:
        app_id = int(app_id)
        service_id = int(service_id)
    except:
        return build_response(simplejson.dumps({ 'error': True,'msg': 'Bad specification of application or service IDs' }))

    if not newname:
        log('"name" is a required argument')
        return build_response(simplejson.dumps(False))

    return _rename(app_id, service_id, newname)

# @service_page.route("/callback/terminateService.php", methods=['POST'])
@service_page.route("/remove", methods=['POST'])
@cert_required(role='user')
# @cert_required(role='manager')
def remove():
    """Terminate the service whose id matches the one provided in the manager
    certificate."""
    # log('User %s attempting to terminate service %s' % (g.user.uid, g.service.sid))
    # if g.service.stop():
    #     return jsonify({ 'error': False })

    # return jsonify({ 'error': True })
    app_id = request.values.get('app_id')
    service_id = request.values.get('service_id')
    try:
        app_id = int(app_id)
        service_id = int(service_id)
    except:
        return build_response(simplejson.dumps({ 'error': True,'msg': 'Bad specification of application or service IDs' }))
    _remove(app_id, service_id)
    return build_response(simplejson.dumps(True))


@service_page.route("/list", methods=['POST', 'GET'])
@cert_required(role='user')
def list_all_services():
    """POST /list

    List running ConPaaS services under a specific application if the user is
    authenticated. Return False otherwise.
    """
    return build_response(simplejson.dumps([
        ser.to_dict() for ser in Service.query.join(Application).filter_by(user_id=g.user.uid)
    ]))

@service_page.route("/list/<int:appid>", methods=['POST', 'GET'])
@cert_required(role='user')
def list_services(appid):
    """POST /list/2

    List running ConPaaS services under a specific application if the user is
    authenticated. Return False otherwise.
    """
    return build_response(simplejson.dumps([
        ser.to_dict() for ser in Service.query.filter_by(application_id=appid)
    ]))

@service_page.route("/download/ConPaaS.tar.gz", methods=['GET'])
def download():
    """GET /download/ConPaaS.tar.gz

    Returns ConPaaS tarball.
    """
    return helpers.send_from_directory(common.config_parser.get('conpaas', 'CONF_DIR'),
        "ConPaaS.tar.gz")
