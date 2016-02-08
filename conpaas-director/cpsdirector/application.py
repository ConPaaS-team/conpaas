# -*- coding: utf-8 -*-

"""
    cpsdirector.application
    =======================

    ConPaaS director: application support.

    :copyright: (C) 2013 by Contrail Consortium.
"""

from flask import Blueprint
from flask import jsonify, request, g

import simplejson, sys, traceback

import ConfigParser
from netaddr import IPNetwork

from threading import Thread
from cpsdirector import db
#from cpsdirector import cloud as manager_controller
from cpsdirector.iaas.controller import Controller

from cpsdirector.common import log
from cpsdirector.common import build_response
from cpsdirector.common import config_parser
from cpsdirector.cloud import _create_nodes as create_nodes, Resource

from conpaas.core.manager import BaseManager
from conpaas.core.node import ServiceNode


application_page = Blueprint('application_page', __name__)


class Application(db.Model):
    A_INIT = 'INIT'         # application initialized but not yet started
    A_PROLOGUE = 'PROLOGUE' # application is starting up
    A_RUNNING = 'RUNNING'   # application is running
    A_ADAPTING = 'ADAPTING' # application is in a transient state 
                            
    A_EPILOGUE = 'EPILOGUE' # application is shutting down
    A_STOPPED = 'STOPPED'   # application stopped
    A_ERROR = 'ERROR'       # application is in error state


    aid = db.Column(db.Integer, primary_key=True,
                    autoincrement=True)
    name = db.Column(db.String(256))
    # manager = db.Column(db.String(512))
    # vmid = db.Column(db.String(256))
    status = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    user = db.relationship('User', backref=db.backref('applications',
                           lazy="dynamic"))
    manager = db.relationship('Resource', uselist=False,
                            primaryjoin="and_(Application.aid==Resource.app_id, Resource.role=='manager')", 
                            backref='applciation')

    # manager = Resource.query.filter_by(app_id=aid).filter_by(role='manager').first()


    def __init__(self, **kwargs):
        # Default values
        self.name = "New Application"

        for key, val in kwargs.items():
            setattr(self, key, val)
        
        if not self.status:
            self.status = Application.A_INIT

    def to_dict(self):
        app_to_dict = { 'aid': self.aid, 'name': self.name,
                        'uid' : self.user_id, 'status' : self.status,
                        'manager' : None, 'vmid' : None, 'cloud' : None }
        if self.manager:
            app_to_dict['manager'] = self.manager.ip
            app_to_dict['vmid'] = self.manager.vmid
            app_to_dict['cloud'] = self.manager.cloud
        return app_to_dict
       

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
    # def stop(self):
    #     #TODO (genc): Probably the subnet and cloud name should be stored on the application table
    #     controller = Controller()

    #     controller.setup_default()
    #     controller.delete_nodes([ServiceNode(self.manager.vmid, self.manager.ip,'',self.manager.cloud,'') ])
    #     self.manager.remove()
    #     db.session.commit()
    #     log('Application %s stopped properly' % self.aid)
    #     return True

def get_app_by_id(user_id, app_id):
    app = Application.query.filter_by(aid=app_id).first()
    if not app:
        log('Application %s does not exist' % app_id)
        return

    if int(app.user_id) != int(user_id):
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

def _createapp(app_name, cloud_name):
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

    
    # store_app_controller(g.user.uid, a.aid, cloud_name)

    log('Application %s created properly' % (a.aid))
    return jsonify(a.to_dict())

def _startapp(user_id, app_id, cloud_name, new_thread=True):
    app = get_app_by_id(user_id, app_id)
    if not app:
        return { 'error': True, 'msg': 'Application not found' }    
    if app.status not in (Application.A_INIT, Application.A_STOPPED) :
        return { 'error': True, 'msg': 'Application already started' }
    if g.user.credit <= 0:
        return { 'error': True, 'msg': 'Insufficient credits' }
    try:
        app.status = Application.A_EPILOGUE

        vpn = app.get_available_vpn_subnet()

        man_args = { 'role' : 'manager', 'user_id' : user_id, 'app_id' : app_id,
                    'vpn' : vpn, 'nodes_info' : [{ 'cloud' : cloud_name }] }
        if new_thread:
            Thread(target=create_nodes, args=[man_args]).start()
        else:
            res = create_nodes(man_args)

        log('Application %s is starting' % (app_id))
        return True
    except Exception, err:
        app.status = Application.A_STOPPED
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        log(''.join('!! ' + line for line in lines))
        error_msg = 'Error upon application starting: %s %s' % (type(err), err)
        log(error_msg)
        return { 'error': True, 'msg': error_msg }
    finally:
        db.session.commit()

def delete_nodes(nodes):
    controller = Controller()
    controller.setup_default()
    controller.delete_nodes(nodes)

def _deleteapp(user_id, app_id, del_app_entry):
    app = get_app_by_id(user_id, app_id)
    if not app:
        return False

    # stop all services
    # we could ask the manager to kill the agents or kill them right here
    # if app.manager:
    #     res = callmanager(app_id, 0, "stopall", True, {})

    res_to_delete = []
    for resource in Resource.query.filter_by(app_id=app_id):
        res_to_delete.append(ServiceNode(resource.vmid, resource.ip,'',resource.cloud,''))
        resource.remove()

    Thread(target=delete_nodes, args=[res_to_delete]).start()

    # delete them from database (no need to remove them from application manager)
    for service in Service.query.filter_by(application_id=app_id):
        service.remove()


    # stop the application manager
    # if app.manager:
    #     app.stop()

    app.status = Application.A_STOPPED
    # delete the applciation from the database
    if del_app_entry:
        db.session.delete(app)
    db.session.commit()

    return True

from cpsdirector.user import cert_required
@application_page.route("/createapp", methods=['POST'])
@application_page.route("/createapp/<cloudname>", methods=['POST'])
@cert_required(role='user')
def createapp(cloudname="default"):
    app_name = request.values.get('name')
    if not app_name:
        log('"name" is a required argument')
        return build_response(simplejson.dumps(False))

    return build_response(_createapp(app_name, cloudname))

@application_page.route("/startapp/<int:appid>", methods=['POST'])
@application_page.route("/startapp/<int:appid>/<cloudname>", methods=['POST'])
@cert_required(role='user')
def startapp(appid, cloudname="default"):
    return build_response(simplejson.dumps(_startapp(g.user.uid, appid, cloudname)))

from cpsdirector.service import Service
from cpsdirector.service import _remove as remove_service
from cpsdirector.service import callmanager


@application_page.route("/stopapp/<int:appid>", methods=['POST'])
@cert_required(role='user')
def stopapp(appid, cloudname="default"):
    return build_response(simplejson.dumps(_deleteapp(g.user.uid, appid, False)))

    
    # app = get_app_by_id(g.user.uid, appid)
    # if not app:
    #     return build_response(simplejson.dumps(False))

    # # this will delete all the services and the application manager 

    # res = callmanager(appid, 0, "infoapp", False, {})
    # if 'states' in res:
    #     if len(res['states']) == 1:
    #         app.stop()
    #     else:
    #         return build_response(simplejson.dumps({ 'error': True,'msg': 'Cannot stop application while its services are running' }))
    # else:
    #     return build_response(simplejson.dumps({ 'error': True,'msg': res['msg'] }))
    # return build_response(simplejson.dumps(True))



@application_page.route("/deleteapp/<int:appid>", methods=['POST'])
@cert_required(role='user')
def delete(appid):
    """eg: POST /deleteapp/3

    POSTed values must contain username and password.

    Returns a boolean value. True in case of successful authentication and
    proper service termination. False otherwise.
    """
    log('User %s attempting to delete application %s' % (g.user.uid, appid))
    return build_response(simplejson.dumps(_deleteapp(g.user.uid, appid, True)))

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

