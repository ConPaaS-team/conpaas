# -*- coding: utf-8 -*-

from flask import Flask, jsonify, helpers, request, make_response, g
from flask.ext.sqlalchemy import SQLAlchemy

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import hashlib
import zipfile
import simplejson
from datetime import datetime
from StringIO import StringIO
from OpenSSL import crypto
from functools import wraps

from conpaas.core import https
from conpaas.core.services import manager_services

from cpsdirector import common
from cpsdirector import cloud
from cpsdirector import x509cert

# Manually add task farming to the list of valid services
valid_services = manager_services.keys() + [ 'taskfarm', ]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = common.config.get(
    'director', 'DATABASE_URI')
db = SQLAlchemy(app)

if common.config.has_option('director', 'DEBUG'):
    app.debug = True

def log(msg):
    print >> request.environ['wsgi.errors'], msg

def get_user(username, password):
    """Return a User object if the specified (username, password) combination
    is valid."""
    return User.query.filter_by(username=username, 
        password=hashlib.md5(password).hexdigest()).first()

def create_user(username, fname, lname, email, affiliation, password, credit):
    """Create a new user with the given attributes. Return a new User object
    in case of successful creation. None otherwise."""
    user = User(username=username, 
                fname=fname, 
                lname=lname, 
                email=email, 
                affiliation=affiliation, 
                password=hashlib.md5(password).hexdigest(), 
                credit=credit)

    db.session.add(user)

    try:
        db.session.commit()
        return user
    except Exception, err:
        db.session.rollback()
        raise err

def build_response(data):
    response = make_response(data)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

def login_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        username = request.values.get('username', '')
        password = request.values.get('password', '')

        g.user = get_user(username, password)
        if g.user:
            # user authenticated
            return fn(*args, **kwargs)       

        # authentication failed
        return build_response(simplejson.dumps(False))

    return decorated_view

def cert_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if os.environ.get('DIRECTOR_TESTING'):
            # No SSL certificate check if we are testing
            return fn(*args, **kwargs)

        msg = 'cert_required: '
        cert = request.environ['SSL_CLIENT_CERT']
        g.cert = {}
        for key in 'serviceLocator', 'UID', 'role':
            g.cert[key] = https.x509.get_x509_dn_field(cert, key)
            msg += '%s=%s ' % (key, g.cert[key])

        log(msg)
        return fn(*args, **kwargs)
    return decorated_view

@app.route("/new_user", methods=['POST'])
def new_user():
    values = {}
    required_fields = ( 'username', 'fname', 'lname', 'email', 
                        'affiliation', 'password', 'credit' )

    log('New user "%s <%s>" creation attempt' % (
        request.values.get('username'), request.values.get('email')))

    # check for presence of mandatory fields
    for field in required_fields:
        values[field] = request.values.get(field)

        if not values[field]:
            log('Missing required field: %s' % field)

            return build_response(jsonify({ 
                'error': True, 'msg': '%s is a required field' % field }))

    # check if the provided username already exists
    if User.query.filter_by(username=values['username']).first():
        log('User %s exists already' % values['username'])

        return build_response(jsonify({ 
            'error': True, 
            'msg': 'Username "%s" already taken' % values['username'] }))

    # check if the provided email already exists
    if User.query.filter_by(email=values['email']).first():
        log('Duplicate email: %s' % values['email'])

        return build_response(jsonify({ 
            'error': True, 
            'msg': 'E-mail "%s" already registered' % values['email'] }))

    try:
        user = create_user(**values)
        # successful creation
        log('User %s created successfully' % user.username)
        return build_response(simplejson.dumps(user.to_dict()))
    except Exception, err:
        # something went wrong
        error_msg = 'Error upon user creation: %s' % err
        log(error_msg)
        return build_response(jsonify({ 'error': True, 'msg': error_msg }))

@app.route("/login", methods=['POST'])
@login_required
def login():
    # return user data
    return build_response(simplejson.dumps(g.user.to_dict()))

@app.route("/getcerts", methods=['POST','GET'])
@login_required
def get_user_certs():
    # Creates new certificates for this user
    certs = x509cert.generate_certificate(
        cert_dir=common.config.get('conpaas', 'CERT_DIR'),
        uid=str(g.user.uid),
        sid='0',
        role='user',
        email=g.user.email,
        cn=g.user.username,
        org='Contrail'
    )

    # In-memory zip file
    zipdata = StringIO()
    archive = zipfile.ZipFile(zipdata, mode='w')

    # Add key.pem, cert.pem and ca_cert.pem to the zip file
    for name, data in certs.items():
        archive.writestr(name + '.pem', data)

    archive.close()
    zipdata.seek(0)

    log('New certificates for user %s created' % g.user.username)

    # Send zip archive to the client
    return helpers.send_file(zipdata, mimetype="application/zip",
        as_attachment=True, attachment_filename='certs.zip')

@app.route("/available_services", methods=['GET','POST'])
def available_services():
    """GET /available_services"""
    return simplejson.dumps(valid_services)

@app.route("/start/<servicetype>", methods=['POST'])
@login_required
def start(servicetype):
    """eg: POST /start/php

    POSTed values must contain username and password.

    Returns a dictionary with service data (manager's vmid and IP address,
    service name and ID) in case of successful authentication and correct
    service creation. False is returned otherwise.
    """
    log('User %s creating a new %s service' % (g.user.username, servicetype))

    # Check if we got a valid service type
    if servicetype not in valid_services:
        error_msg = 'Unknown service type: %s' % servicetype
        log(error_msg)
        return build_response(jsonify({ 'error': True, 
                                        'msg': error_msg }))

    # New service with default name, proper servicetype and user relationship
    s = Service(name="New %s service" % servicetype, type=servicetype, 
        user=g.user)
                
    db.session.add(s)
    # flush() is needed to get auto-incremented sid
    db.session.flush()

    try:
        s.manager, s.vmid, s.cloud = cloud.start(servicetype, s.sid, 
                                                 g.user.uid)
    except Exception, err:
        db.session.rollback()
        error_msg = 'Error upon service creation: %s' % err
        log(error_msg)
        return build_response(jsonify({ 'error': True, 'msg': error_msg }))

    db.session.commit()

    log('%s (id=%s) created properly' % (s.name, s.sid))
    return build_response(jsonify(s.to_dict()))

@app.route("/stop/<int:serviceid>", methods=['POST'])
@login_required
def stop(serviceid):
    """eg: POST /stop/3

    POSTed values must contain username and password.

    Returns a boolean value. True in case of successful authentication and
    proper service termination. False otherwise.
    """
    log('User %s attempting to stop service %s' % (g.user.uid, serviceid))

    s = Service.query.filter_by(sid=serviceid).first()
    if not s:
        log('Service %s does not exist' % serviceid)
        return build_response(simplejson.dumps(False))

    if s not in g.user.services:
        log('Service %s is not owned by user %s' % (serviceid, g.user.uid))
        return build_response(simplejson.dumps(False))

    # If a service with id 'serviceid' exists and user is the owner
    cloud.stop(s.vmid)
    db.session.delete(s)
    db.session.commit()
    log('Service %s stopped properly' % serviceid)
    return build_response(simplejson.dumps(True))

@app.route("/list", methods=['POST', 'GET'])
@login_required
def list_services():
    """POST /list

    List running ConPaaS services if the user is authenticated. Return False
    otherwise.
    """
    return build_response(simplejson.dumps([ 
        ser.to_dict() for ser in g.user.services.all() 
    ]))

@app.route("/download/ConPaaS.tar.gz", methods=['GET'])
def download():
    """GET /download/ConPaaS.tar.gz

    Returns ConPaaS tarball.
    """
    return helpers.send_from_directory(common.config.get('conpaas', 'CONF_DIR'), 
        "ConPaaS.tar.gz")

@app.route("/ca/get_cert.php", methods=['POST'])
@cert_required 
def get_manager_cert():
    #XXX if g.cert['role'] != 'manager':
    log('Certificate request from manager %s (user %s)' % (
        g.cert['serviceLocator'], g.cert['UID']))

    csr = crypto.load_certificate_request(crypto.FILETYPE_PEM, 
        request.files['csr'].read())
    return x509cert.create_x509_cert(
        common.config.get('conpaas', 'CERT_DIR'), csr)

@app.route("/callback/decrementUserCredit.php", methods=['POST'])
@cert_required
def credit():
    """POST /callback/decrementUserCredit.php

    POSTed values must contain sid and decrement.

    Returns a dictionary with the 'error' attribute set to False if the user
    had enough credit, True otherwise.
    """
    service_id = int(request.values.get('sid', -1))
    decrement  = int(request.values.get('decrement', 0))

    log('Decrement user credit: sid=%s, decrement=%s' % (service_id, decrement))

    if os.environ.get('DIRECTOR_TESTING'):
        # no certificate when testing. assume all is good.
        service_locator = service_id
    else:
        try:
            service_locator = int(g.cert['serviceLocator'])
            uid = int(g.cert['UID']) 
        except (AttributeError, ValueError):
            error_msg = 'Missing client certificate providing serviceLocator and UID'
            log(error_msg)
            # Return HTTP_UNAUTHORIZED
            return make_response(error_msg, 401)

    if service_id != service_locator:
        error_msg = 'service_id != serviceLocator (%s != %s)' % (
            service_id, service_locator)
        log(error_msg)
        return make_response(error_msg, 401)

    s = Service.query.filter_by(sid=service_id).first()
    if not s:
        # The given service does not exist
        error_msg = "Service %s does not exist" % service_id
        log(error_msg)
        return jsonify({ 'error': True, 'msg': error_msg })
    
    if os.environ.get('DIRECTOR_TESTING'):
        # no certificate when testing. assume all is good.
        uid = s.user.uid

    if s.user.uid != uid:
        error_msg = 'service.uid != UID (%s != %s)' % (s.user.uid, uid)
        log(error_msg)
        return make_response(error_msg, 401)

    # Decrement user's credit
    s.user.credit -= decrement

    if s.user.credit > -1:
        # User has enough credit
        db.session.commit()
        log('New credit for user %s: %s' % (s.user.uid, s.user.credit))
        return jsonify({ 'error': False })

    # User does not have enough credit
    db.session.rollback()
    log('User %s does not have enough credit' % s.user.uid)
    return jsonify({ 'error': True })

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True, 
        autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    fname = db.Column(db.String(256))
    lname = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True)
    affiliation = db.Column(db.String(256))
    password = db.Column(db.String(256))
    created = db.Column(db.DateTime)
    credit = db.Column(db.Integer)

    def __init__(self, **kwargs):
        # Default values
        self.credit = 0
        self.created = datetime.now()

        for key, val in kwargs.items():
            setattr(self, key, val)

    def to_dict(self):
        return  {
            'uid': self.uid, 'username': self.username, 
            'fname': self.fname, 'lname': self.lname,
            'email': self.email, 'affiliation': self.affiliation,
            'password': self.password, 'credit': self.credit, 
            'created': self.created.isoformat(),
        }

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

    user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    user = db.relationship('User', backref=db.backref('services', 
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

if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", debug=True)
