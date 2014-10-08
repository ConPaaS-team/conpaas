# -*- coding: utf-8 -*-

"""
    cpsdirector.application
    =======================

    ConPaaS director: application support.

    :copyright: (C) 2013 by Contrail Consortium.
"""

from flask import Blueprint
from flask import jsonify, request, g

import sys
import traceback

import simplejson

import ConfigParser
from netaddr import IPNetwork

from cpsdirector import db
from cpsdirector import cloud as manager_controller


from cpsdirector.common import log
from cpsdirector.common import build_response
from cpsdirector.common import config_parser


application_page = Blueprint('application_page', __name__)
# aug = {}
app_controllers = {}

class Application(db.Model):
    aid = db.Column(db.Integer, primary_key=True,
                    autoincrement=True)
    name = db.Column(db.String(256))
    manager = db.Column(db.String(512))
    vmid = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    user = db.relationship('User', backref=db.backref('applications',
                           lazy="dynamic"))

    def __init__(self, **kwargs):
        # Default values
        self.name = "New Application"
        
        for key, val in kwargs.items():
            setattr(self, key, val)


    def to_dict(self):
        return  {
            'aid': self.aid, 'name': self.name, 'manager':self.manager,
        }

    def get_available_vpn_subnet(self):
        """Find an available VPN subnet for the next service to be created in
        this application."""
        try:
            network = config_parser.get('conpaas', 'VPN_BASE_NETWORK')
            netmask = config_parser.get('conpaas', 'VPN_NETMASK')
            srvbits = config_parser.get('conpaas', 'VPN_SERVICE_BITS')
        except ConfigParser.NoOptionError:
            return
            
        # Split the given network into subnets. 
        base_net = IPNetwork(network + '/' + netmask)
        vpn_subnets = base_net.subnet(32 - base_net.prefixlen - int(srvbits))

        assigned_networks = [ service.subnet for service in self.services ]

        for candidate_network in vpn_subnets:
            candidate_network = str(candidate_network)

            if candidate_network not in assigned_networks:
                return candidate_network

def get_app_by_id(user_id, app_id):
    app = Application.query.filter_by(aid=app_id).first()
    if not app:
        log('Application %s does not exist' % app_id)
        return

    if app.user_id != user_id:
        log('Application %s is not owned by user %s' % (app_id, user_id))
        return

    return app

def get_app_by_name(user_id, app_name):
    app = Application.query.filter_by(name=app_name).first()
    if not app:
        log('Application %s does not exist' % app_name)
        return

    if app.user_id != user_id:
        log('Application %s is not owned by user %s' % (app_name, user_id))
        return

    return app

def get_default_app(user_id):
    return Application.query.filter_by(user_id=user_id).order_by(
        Application.aid).first()

def check_app_exists(app_name):
    if Application.query.filter_by(name=app_name, user_id=g.user.uid).first():
        return True

    return False

def _createapp(app_name):
    log('User %s creating a new application %s' % (g.user.username, app_name))

    # check if the application already exists
    if check_app_exists(app_name):
        log('Application name %s already exists' % app_name)

        return jsonify({
            'error': True,
            'msg': 'Application name "%s" already taken' % app_name })

    a = Application(name=app_name, user=g.user)

    db.session.add(a)
    # flush() is needed to get auto-incremented sid
    db.session.flush()
    
    db.session.commit()

    _store_app_controller(g.user.uid, a.aid, 'iaas')
    # global aug
    # aug['1'] = 'create'
    log('create app_controllers %s' % app_controllers)

    log('Application %s created properly' % (a.aid))
    return jsonify(a.to_dict())

def deleteapp(user_id, app_id):
    app = get_app_by_id(user_id, app_id)
    if not app:
        return False

    # global aug
    # aug['3'] = 'delete'
    # log('aug at delete %s' % aug)
    
    # If an application with id 'app_id' exists and user is the owner
    #TODO: (genc) fix the following loop
    for service in Service.query.filter_by(application_id=app_id):
        # callmanager(app.to_dict(), service.sid, "shutdown", True, {})
        stop(service.sid)

    controller = app_controllers[app_id]    
    controller.release_reservation(app.vmid)
    del app_controllers[app_id]
   
    db.session.delete(app)
    db.session.commit()

    return True

def _store_app_controller(user_id, app_id, cloudname):
    app = get_app_by_id(user_id, app_id)
    if not app:
        return None
    vpn = app.get_available_vpn_subnet()
    controller = manager_controller.ManagerController(user_id, cloudname, app_id, vpn)
    global app_controllers
    app_controllers[app_id] = controller

#def _startapp(user_id, app_id, cloudname, manifest=None, slo=None):
def _startapp(user_id, app_id, cloudname):
    app = get_app_by_id(user_id, app_id)
    if not app:
        return False    
    try:
        #s.manager, s.vmid, s.cloud = manager_controller.start(
        #    servicetype, s.sid, g.user.uid, cloudname, appid, vpn)
        log('start app_controllers %s' % app_controllers)
        #app.manager, app.vmid, _ = manager_controller.startapp(user_id, cloudname, app_id, vpn, manifest, slo)
        controller = app_controllers[app_id] if app_id in app_controllers else None
        vpn = app.get_available_vpn_subnet() if controller is None else None

        app.manager, app.vmid, _, _= manager_controller.startapp(user_id, cloudname, app_id, vpn, controller)
        
        # global aug
        # aug['2'] = 'start'
        # log('aug at startapp %s' % aug)

        db.session.commit()
        return True
    except Exception, err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        log(''.join('!! ' + line for line in lines))
        error_msg = 'Error upon service creation: %s %s' % (type(err), err)
        log(error_msg)
        return { 'error': True, 'msg': error_msg }
    


from cpsdirector.user import cert_required
@application_page.route("/createapp", methods=['POST'])
@cert_required(role='user')
def createapp():
    app_name = request.values.get('name')
    if not app_name:
        log('"name" is a required argument')
        return build_response(simplejson.dumps(False))

    return build_response(_createapp(app_name))


@application_page.route("/startapp/<int:appid>", methods=['POST'])
@application_page.route("/startapp/<int:appid>/<cloudname>", methods=['POST'])
@cert_required(role='user')
def startapp(appid, cloudname="default"):
    return build_response(simplejson.dumps(_startapp(g.user.uid, appid, cloudname)))


from cpsdirector.service import Service
from cpsdirector.service import stop
from cpsdirector.service import callmanager

@application_page.route("/delete/<int:appid>", methods=['POST'])
@cert_required(role='user')
def delete(appid):
    """eg: POST /delete/3

    POSTed values must contain username and password.

    Returns a boolean value. True in case of successful authentication and
    proper service termination. False otherwise.
    """
    log('User %s attempting to delete application %s' % (g.user.uid, appid))
    return build_response(simplejson.dumps(deleteapp(g.user.uid, appid)))

def _renameapp(appid, newname):
    log('User %s attempting to rename application %s' % (g.user.uid, appid))

    app = get_app_by_id(g.user.uid, appid)
    if not app:
        return build_response(simplejson.dumps(False))

    app.name = newname
    db.session.commit()
    return simplejson.dumps(True)

@application_page.route("/renameapp/<int:appid>", methods=['POST'])
@cert_required(role='user')
def renameapp(appid):
    newname = request.values.get('name')
    if not newname:
        log('"name" is a required argument')
        return build_response(simplejson.dumps(False))

    return _renameapp(appid, newname)

@application_page.route("/listapp", methods=['POST', 'GET'])
@cert_required(role='user')
def list_applications():
    """POST /listapp

    List all the ConPaaS applications if the user is authenticated. Return False
    otherwise.
    """
    return build_response(simplejson.dumps([
        app.to_dict() for app in g.user.applications.all()
    ]))



