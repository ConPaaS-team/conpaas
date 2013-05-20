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

from conpaas.core.services import manager_services

service_page = Blueprint('service_page', __name__)

# Manually add task farming to the list of valid services
valid_services = manager_services.keys() + ['taskfarm', ]

class Service(db.Model):
    sid = db.Column(db.Integer, primary_key=True,
        autoincrement=True)
    name = db.Column(db.String(256))
    type = db.Column(db.String(32))
    state = db.Column(db.String(32))
    created = db.Column(db.DateTime)
    manager = db.Column(db.String(512))
    vmid = db.Column(db.String(256))
    cloud = db.Column(db.String(128))
    subnet = db.Column(db.String(18))

    user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    user = db.relationship('User', backref=db.backref('services',
        lazy="dynamic"))

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
        ret = {}
        for c in self.__table__.columns:
            ret[c.name] = getattr(self, c.name)
            if type(ret[c.name]) is datetime:
                ret[c.name] = ret[c.name].isoformat()

        return ret

    def stop(self):
        controller = manager_controller.ManagerController(self.type,
                self.sid, self.user_id, self.cloud, self.application_id,
                self.subnet)

        controller.stop(self.vmid)
        db.session.delete(self)
        db.session.commit()
        log('Service %s stopped properly' % self.sid)
        return True

def get_service(user_id, service_id):
    service = Service.query.filter_by(sid=service_id).first()
    if not service:
        log('Service %s does not exist' % service_id)
        return

    if service.user_id != user_id:
        log('Service %s is not owned by user %s' % (service_id, user_id))
        return

    return service

from conpaas.core import https
def callmanager(service_id, method, post, data, files=[]):
    """Call the manager API.

    'service_id': an integer holding the service id of the manager.
    'method': a string representing the API method name.
    'post': boolean value. True for POST method, false for GET.
    'data': a dictionary representing the data to be sent to the director.
    'files': sequence of (name, filename, value) tuples for data to be uploaded as files.

    callmanager loads the manager JSON response and returns it as a Python
    object.
    """
    service = get_service(g.user.uid, service_id)

    https.client.conpaas_init_ssl_ctx('/etc/cpsdirector/certs', 'director')

    # File upload
    if files:
        res = https.client.https_post(service.manager, 443, '/', data, files)
    # POST
    elif post:
        res = https.client.jsonrpc_post(service.manager, 443, '/', method, data)
    # GET
    else:
        res = https.client.jsonrpc_get(service.manager, 443, '/', method, data)

    if res[0] == 200:
        try:
            data = simplejson.loads(res[1])
        except simplejson.decoder.JSONDecodeError:
            # Not JSON, simply return what we got
            return res[1]

        return data.get('result', data)

    raise Exception, "Call to method %s on %s failed: %s.\nParams = %s" % (
        method, service.manager, res[1], data)

@service_page.route("/available_services", methods=['GET'])
def available_services():
    """GET /available_services"""
    return simplejson.dumps(valid_services)

from cpsdirector.application import get_default_app, get_app_by_id

from cpsdirector.user import cert_required

def _start(servicetype, cloudname, appid):
    log('User %s creating a new %s service inside application %s' % (
	    g.user.username, servicetype, appid))

    # Check if we got a valid service type
    if servicetype not in valid_services:
        error_msg = 'Unknown service type: %s' % servicetype
        log(error_msg)
        return build_response(jsonify({ 'error': True,
                                        'msg': error_msg }))

    app = get_app_by_id(g.user.uid, appid)
    if not app:
        return build_response(jsonify({ 'error': True,
		                        'msg': "Application not found" }))

    # Do we have to assign a VPN subnet to this service?
    vpn = app.get_available_vpn_subnet()

    # New service with default name, proper servicetype and user relationship
    s = Service(name="New %s service" % servicetype, type=servicetype,
        user=g.user, application=app, subnet=vpn)

    db.session.add(s)
    # flush() is needed to get auto-incremented sid
    db.session.flush()

    try:
        s.manager, s.vmid, s.cloud = manager_controller.start(
            servicetype, s.sid, g.user.uid, cloudname, appid, vpn)
    except Exception, err:
        try:
            db.session.delete(s)
            db.session.commit()
        except InvalidRequestError:
            db.session.rollback()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        log(''.join('!! ' + line for line in lines))
        error_msg = 'Error upon service creation: %s %s' % (type(err), err)
        log(error_msg)
        return build_response(jsonify({ 'error': True, 'msg': error_msg }))

    db.session.commit()

    log('%s (id=%s) created properly' % (s.name, s.sid))
    return build_response(jsonify(s.to_dict()))

@service_page.route("/start/<servicetype>", methods=['POST'])
@service_page.route("/start/<servicetype>/<cloudname>", methods=['POST'])
@cert_required(role='user')
def start(servicetype, cloudname="default"):
    """eg: POST /start/php

    POSTed values might contain 'appid' to specify that the service to be
    created has to belong to a specific application. If 'appid' is omitted, the
    service will belong to the default application.

    Returns a dictionary with service data (manager's vmid and IP address,
    service name and ID) in case of successful authentication and correct
    service creation. False is returned otherwise.
    """
    appid = request.values.get('appid')

    # Use default application id if no appid was specified
    if not appid:
        appid = get_default_app(g.user.uid).aid

    return _start(servicetype, cloudname, appid)

def _rename(serviceid, newname):
    log('User %s attempting to rename service %s' % (g.user.uid, serviceid))

    service = get_service(g.user.uid, serviceid)
    if not service:
        return make_response(simplejson.dumps(False))

    if not newname:
        log('"name" is a required argument')
        return build_response(simplejson.dumps(False))

    service.name = newname
    db.session.commit()
    return simplejson.dumps(True)

@service_page.route("/rename/<int:serviceid>", methods=['POST'])
@cert_required(role='user')
def rename(serviceid):
    newname = request.values.get('name')
    if not newname:
        log('"name" is a required argument')
        return build_response(simplejson.dumps(False))

    return _rename(serviceid, newname)

@service_page.route("/callback/terminateService.php", methods=['POST'])
@cert_required(role='manager')
def terminate():
    """Terminate the service whose id matches the one provided in the manager
    certificate."""
    log('User %s attempting to terminate service %s' % (g.user.uid,
                                                        g.service.sid))

    if g.service.stop():
        return jsonify({ 'error': False })

    return jsonify({ 'error': True })

@service_page.route("/stop/<int:serviceid>", methods=['POST'])
@cert_required(role='user')
def stop(serviceid):
    """eg: POST /stop/3

    POSTed values must contain username and password.

    Returns a boolean value. True in case of successful authentication and
    proper service termination. False otherwise.
    """
    log('User %s attempting to stop service %s' % (g.user.uid, serviceid))

    service = get_service(g.user.uid, serviceid)
    if not service:
        return build_response(simplejson.dumps(False))

    # If a service with id 'serviceid' exists and user is the owner
    service.stop()
    return build_response(simplejson.dumps(True))

@service_page.route("/list", methods=['POST', 'GET'])
@cert_required(role='user')
def list_all_services():
    """POST /list

    List running ConPaaS services under a specific application if the user is
    authenticated. Return False otherwise.
    """
    return build_response(simplejson.dumps([
        ser.to_dict() for ser in g.user.services.all()
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
