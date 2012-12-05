from flask import Flask, jsonify, helpers, request, make_response
from flask.ext.sqlalchemy import SQLAlchemy

import os
import sys
import hashlib
import zipfile
import simplejson
from datetime import datetime
from StringIO import StringIO
from OpenSSL import crypto

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
    print "Debug mode on"
    app.debug = True

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
    except Exception:
        db.session.rollback()

def auth_user(username, password):
    """Return a User object if the specified (username, password) combination
    is valid. False otherwise."""
    res = User.query.filter_by(username=username, 
        password=hashlib.md5(password).hexdigest()).first()

    if res:
        return res

    return False

def build_response(data):
    response = make_response(data)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route("/new_user", methods=['POST'])
def new_user():
    values = {}
    required_fields = ( 'username', 'fname', 'lname', 'email', 
                        'affiliation', 'password', 'credit' )

    # check for presence of mandatory fields
    for field in required_fields:
        values[field] = request.values.get(field)

        if not values[field]:
            return build_response(jsonify({ 
                'error': True, 'msg': '%s is a required field' % field }))

    # check if the provided username already exists
    if User.query.filter_by(username=values['username']).first():
        return build_response(jsonify({ 
            'error': True, 
            'msg': 'Username "%s" already taken' % values['username'] }))

    try:
        user = create_user(**values)
        # successful creation
        return build_response(simplejson.dumps(user.to_dict()))
    except Exception:
        # something went wrong
        return build_response(jsonify({ 
            'error': True, 'msg': 'Unknown error upon user creation' }))

@app.route("/login", methods=['POST'])
def login():
    user = auth_user(request.values.get('username', ''), 
        request.values.get('password', ''))

    if not user:
        # Authentication failed
        return build_response(simplejson.dumps(False))

    # Authentication succeeded, return user data
    return build_response(simplejson.dumps(user.to_dict()))

@app.route("/getcerts", methods=['POST','GET'])
def get_user_certs():
    user = auth_user(request.values.get('username', ''), 
        request.values.get('password', ''))

    if not user:
        # Authentication failed
        return simplejson.dumps(False)

    # Creates new certificates for this user
    certs = x509cert.generate_certificate(
        cert_dir=common.config.get('conpaas', 'CERT_DIR'),
        uid=str(user.uid),
        sid='0',
        role='user',
        email=user.email,
        cn=user.username,
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

    # Send zip archive to the client
    return helpers.send_file(zipdata, mimetype="application/zip",
        as_attachment=True, attachment_filename='certs.zip')

@app.route("/available_services", methods=['GET'])
def available_services():
    """GET /available_services"""
    return simplejson.dumps(valid_services)

@app.route("/start/<servicetype>", methods=['POST'])
def start(servicetype):
    """eg: POST /start/php

    POSTed values must contain username and password.

    Returns a dictionary with service data (manager's vmid and IP address,
    service name and ID) in case of successful authentication and correct
    service creation. False is returned otherwise.
    """
    user = auth_user(request.values.get('username', ''), 
        request.values.get('password', ''))

    if not user:
        # Authentication failed
        return build_response(simplejson.dumps(False))

    # Check if we got a valid service type
    if servicetype not in valid_services:
        return build_response(jsonify({ 'error': True, 
                                        'msg': 'Unknown service type' }))

    # New service with default name, proper servicetype and user relationship
    s = Service(name="New %s service" % servicetype, type=servicetype, 
        user=user)
                
    db.session.add(s)
    # flush() is needed to get auto-incremented sid
    db.session.flush()

    try:
        s.manager, s.vmid, s.cloud = cloud.start(servicetype, s.sid, user.uid)
    except Exception, err:
        db.session.rollback()
        return build_response(jsonify({ 'error': True, 
                                        'msg': str(err) }))

    db.session.commit()
    return build_response(jsonify(s.to_dict()))

@app.route("/stop/<int:serviceid>", methods=['POST'])
def stop(serviceid):
    """eg: POST /stop/3

    POSTed values must contain username and password.

    Returns a boolean value. True in case of successful authentication and
    proper service termination. False otherwise.
    """
    user = auth_user(request.values.get('username', ''), 
        request.values.get('password', ''))

    if user:
        # Authentication succeeded
        s = Service.query.filter_by(sid=serviceid).first()
        if s and s in user.services:
            # If a service with id 'serviceid' exists and user is the owner
            cloud.stop(s.vmid)
            db.session.delete(s)
            db.session.commit()
            return build_response(simplejson.dumps(True))

    return build_response(simplejson.dumps(False))

@app.route("/list", methods=['POST', 'GET'])
def list_services():
    """POST /list

    List running ConPaaS services if the user is authenticated. Return False
    otherwise.
    """
    user = auth_user(request.values.get('username', ''), 
        request.values.get('password', ''))

    if not user:
        # Authentication failed
        return build_response(simplejson.dumps(False))

    return build_response(
            simplejson.dumps([ ser.to_dict() for ser in user.services.all() ]))

@app.route("/manager", methods=['GET','POST'])
def manager():
    method = request.values.get('method', '')
    sid = request.values.get('sid', '')
    params = {}

    service = Service.query.filter_by(sid=sid).one()

    if request.method == "POST":
        _, res = https.client.jsonrpc_post(str(service.manager), 80, "/", method, 
        request.values)
    else:
        _, res = https.client.jsonrpc_get(str(service.manager), 80, "/", method)

    return build_response(res)

@app.route("/download/ConPaaS.tar.gz", methods=['GET'])
def download():
    """GET /download/ConPaaS.tar.gz

    Returns ConPaaS tarball.
    """
    return helpers.send_from_directory(common.config.get('conpaas', 'CONF_DIR'), 
        "ConPaaS.tar.gz")

@app.route("/ca/get_cert.php", methods=['POST'])
def get_manager_cert():
    file = request.files['csr']
    csr = crypto.load_certificate_request(crypto.FILETYPE_PEM, file.read())
    return x509cert.create_x509_cert(
        common.config.get('conpaas', 'CERT_DIR'), csr)

@app.route("/callback/decrementUserCredit.php", methods=['POST'])
def credit():
    """POST /callback/decrementUserCredit.php

    POSTed values must contain sid and decrement.

    Returns a dictionary with the 'error' attribute set to False if the user
    had enough credit, True otherwise.
    """
    service_id = int(request.values.get('sid', -1))
    decrement  = int(request.values.get('decrement', 0))

    s = Service.query.filter_by(sid=service_id).first()
    if not s:
        # The given service does not exist
        print "The service does not exist"
        return jsonify({ 'error': True })
    
    if request.remote_addr and request.remote_addr != s.manager:
        # FIXME: When both the director and service masters run on EC2 the IP
        # address in request.remote_addr is not the public one.
        #return jsonify({ 'error': True })
        print "remote_addr != manager_ip (%s != %s)" % (request.remote_addr, 
            s.manager)

    # Decrement user's credit
    s.user.credit -= decrement

    if s.user.credit > -1:
        # User has enough credit
        db.session.commit()
        return jsonify({ 'error': False })

    # User does not have enough credit
    db.session.rollback()
    return jsonify({ 'error': True })

@app.route("/callback/terminateService.php")
def terminate():
    """To be implemented."""
    pass

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
