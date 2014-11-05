# -*- coding: utf-8 -*-

"""
    cpsdirector.user
    ================

    ConPaaS director: users and authentication handling

    :copyright: (C) 2013 by Contrail Consortium.
"""

from flask import Blueprint
from flask import jsonify, helpers, request, make_response, g

import os
import hashlib
import zipfile
import simplejson
from datetime import datetime
from functools import wraps
from StringIO import StringIO
from OpenSSL import crypto

from cpsdirector import db, x509cert
from cpsdirector.common import log, config_parser, build_response

from conpaas.core import https

default_max_credit = 50

user_page = Blueprint('user_page', __name__)


class cert_required(object):

    def __init__(self, role):
        self.role = role

    def __call__(self, fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            g.cert = {}

            if os.environ.get('DIRECTOR_TESTING'):
                # No SSL certificate check if we are testing. Trust what the
                # client is sending.
                g.cert['UID'] = request.values.get('uid')
                g.cert['role'] = request.values.get('role')
                g.cert['serviceLocator'] = request.values.get('sid')
            else:
                cert = request.environ['SSL_CLIENT_CERT']
                for key in 'serviceLocator', 'UID', 'role':
                    g.cert[key] = https.x509.get_x509_dn_field(cert, key)

            try:
                uid = int(g.cert['UID'])
            except (AttributeError, ValueError, TypeError):
                error_msg = 'cert_required: client certificate does NOT provide UID'
                log(error_msg)
                return make_response(error_msg, 401)

            # Getting user data from DB
            g.user = User.query.get(uid)
            if not g.user:
                # authentication failed
                return build_response(simplejson.dumps(False))

            if self.role == 'manager':
                # manager cert required
                try:
                    service_locator = int(g.cert['serviceLocator'])
                except (AttributeError, ValueError):
                    error_msg = 'cert_required: client certificate does NOT provide serviceLocator'
                    log(error_msg)
                    # Return HTTP_UNAUTHORIZED
                    return make_response(error_msg, 401)

                # check if the service is actually owned by the user
                from cpsdirector.service import get_service
                g.service = get_service(uid, service_locator)
                if not g.service:
                    return build_response(simplejson.dumps(False))

                log('cert_required: valid certificate (user %s, service %s)' %
                    (uid, service_locator))

            return fn(*args, **kwargs)
        return decorated


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
    uuid = db.Column(db.String(80))
    openid = db.Column(db.String(200))

    def __init__(self, **kwargs):
        # Default values
        self.credit = 0
        self.created = datetime.now()

        for key, val in kwargs.items():
            setattr(self, key, val)

    def to_dict(self):
        return {
            'uid': self.uid, 'username': self.username,
            'fname': self.fname, 'lname': self.lname,
            'email': self.email, 'affiliation': self.affiliation,
            'password': self.password, 'credit': self.credit,
            'created': self.created.isoformat(),
            'uuid': self.uuid,
            'openid': self.openid,
        }


def get_user(username, password):
    """Return a User object if the specified (username, password) combination
    is valid."""
    log('user login attempt with username %s' % username)
    return User.query.filter_by(username=username,
                                password=hashlib.md5(password).hexdigest()).first()

def get_user_by_uuid(uuid):
    """Return a User object if the specified uuid is found."""
    log('uuid login attempt with uuid %s' % uuid)
    return User.query.filter_by(uuid=uuid).first()

def get_user_by_openid(openid):
    """Return a User object if the specified openid is found."""
    log('openid login attempt with openid %s' % openid)
    return User.query.filter_by(openid=openid).first()

from cpsdirector.application import Application


def list_users():
    """
    List all known users.
    """
    return User.query.all()

def create_user(username, fname, lname, email, affiliation, password, credit, uuid = None, openid = None):
    """Create a new user with the given attributes. Return a new User object
    in case of successful creation. None otherwise."""
    new_user = User(username=username,
                    fname=fname,
                    lname=lname,
                    email=email,
                    affiliation=affiliation,
                    password=hashlib.md5(password).hexdigest(),
                    credit=credit,
                    uuid=uuid,
                    openid=openid)

    app = Application(user=new_user)

    db.session.add(new_user)
    db.session.add(app)

    try:
        db.session.commit()
        return new_user
    except Exception, err:
        db.session.rollback()
        raise err


def login_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        username = request.values.get('username', '')
        password = request.values.get('password', '')
        uuid = request.values.get('uuid', '')
        if uuid == '<none>':
            uuid = ''
        openid = request.values.get('openid', '')
        if openid == '<none>':
            openid = ''

        # Getting user data from DB through username and password
        if len(username.strip()):
            log('username authentication attempt for <%s, %s> ' % (username, password) )
            g.user = get_user(username, password)

            if g.user:
                # user authenticated through username and passwword
                return fn(*args, **kwargs)

        # authentication failed, try uuid
        # Getting user data from DB through uuid
        if len(uuid.strip()):
            log('uuid authentication attempt for <%s> ' % (uuid) )
            g.user = get_user_by_uuid(uuid)

            if g.user:
                # user authenticated through uuid
                return fn(*args, **kwargs)

        # authentication failed, try openid
        # Getting user data from DB through openid
        if len(openid.strip()):
            log('openid authentication attempt for <%s> ' % (openid) )
            g.user = get_user_by_openid(openid)

            if g.user:
                # user authenticated through openid
                return fn(*args, **kwargs)

        # authentication failed
        return build_response(simplejson.dumps(False))

    return decorated_view


@user_page.route("/new_user", methods=['POST'])
def new_user():
    values = {}
    required_fields = ('username', 'fname', 'lname', 'email',
                       'affiliation', 'password', 'credit', 'uuid', 'openid')

    log('New user "%s <%s>" creation attempt' % (
        request.values.get('username'), request.values.get('email')))

    # check for presence of mandatory fields
    for field in required_fields:
        values[field] = request.values.get(field)

        if not values[field]:
            log('Missing required field: %s' % field)

            return build_response(jsonify({
                'error': True, 'msg': '%s is a required field' % field,
            }))
        if field == 'uuid' and values[field] == '<none>':
            values[field] = ''

    # check if the provided username already exists
    if User.query.filter_by(username=values['username']).first():
        log('User %s already exists' % values['username'])

        return build_response(jsonify({
            'error': True,
            'msg': 'Username "%s" already taken' % values['username'],
        }))

    # check if the provided email already exists
    if False and User.query.filter_by(email=values['email']).first(): # for debugging purposes allow duplicate email address
        log('Duplicate email: %s' % values['email'])

        return build_response(jsonify({
            'error': True,
            'msg': 'E-mail "%s" already registered' % values['email'],
        }))

    # check that the requested credit does not exceed the maximum
    if config_parser.has_option('conpaas', 'MAX_CREDIT'):
        max_credit = config_parser.get('conpaas', 'MAX_CREDIT')
        try:
            max_credit = int(max_credit)
        except ValueError:
            log('ERROR: Parameter MAX_CREDIT "%s" is not a valid integer.'
                ' Defaulting to maximum credit %s.' % (max_credit, default_max_credit))
            max_credit = default_max_credit
        if max_credit < 0:
            log('ERROR: Parameter MAX_CREDIT "%s" cannot be a negative number.'
                ' Defaulting to maximum credit %s.' % (max_credit, default_max_credit))
            max_credit = default_max_credit
    else:
        max_credit = default_max_credit
    try:
        req_credit = int(values['credit'])
    except ValueError:
        return build_response(jsonify({
            'error': True,
            'msg': 'Required credit "%s" is not a valid integer.' % values['credit']}))
    if req_credit < 0:
        return build_response(jsonify({
            'error': True,
            'msg': 'Required credit "%s" cannot be a negative integer.' % values['credit']}))
    if req_credit > max_credit:
        return build_response(jsonify({
            'error': True,
            'msg': 'Cannot allocate %s credit for a new user (max credit %s).' % (values['credit'], max_credit)}))

    try:
        user = create_user(**values)
        # successful creation
        log('User %s created successfully' % user.username)
        return build_response(simplejson.dumps(user.to_dict()))
    except Exception, err:
        # something went wrong
        error_msg = 'Error upon user creation: %s -> %s' % (type(err), err)
        log(error_msg)
        return build_response(jsonify({'error': True, 'msg': error_msg}))


@user_page.route("/login", methods=['POST'])
@login_required
def login():
    log('Successful login for user %s' % g.user.username)
    # return user data
    return build_response(simplejson.dumps(g.user.to_dict()))


@user_page.route("/getcerts", methods=['POST', 'GET'])
@login_required
def get_user_certs():
    # Creates new certificates for this user
    certs = x509cert.generate_certificate(
        cert_dir=config_parser.get('conpaas', 'CERT_DIR'),
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


@user_page.route("/ca/get_cert.php", methods=['POST'])
@cert_required(role='manager')
def get_manager_cert():
    log('Certificate request from manager %s (user %s)' % (
        g.cert['serviceLocator'], g.cert['UID']))

    csr = crypto.load_certificate_request(crypto.FILETYPE_PEM,
                                          request.files['csr'].read())
    return x509cert.create_x509_cert(
        config_parser.get('conpaas', 'CERT_DIR'), csr)


@user_page.route("/callback/decrementUserCredit.php", methods=['POST'])
@cert_required(role='manager')
def credit():
    """POST /callback/decrementUserCredit.php

    POSTed values must contain sid and decrement.

    Returns a dictionary with the 'error' attribute set to False if the user
    had enough credit, True otherwise.
    """
    service_id = int(request.values.get('sid', -1))
    decrement = int(request.values.get('decrement', 0))

    log('Decrement user credit: sid=%s, old_credit=%s, decrement=%s' % (
        service_id, g.service.user.credit, decrement))

    # Decrement user's credit
    g.service.user.credit -= decrement

    if g.service.user.credit > -1:
        # User has enough credit
        db.session.commit()
        log('New credit for user %s: %s' %
            (g.service.user.uid, g.service.user.credit))
        return jsonify({'error': False})

    # User does not have enough credit
    db.session.rollback()
    log('User %s does not have enough credit' % g.service.user.uid)
    return jsonify({'error': True})


@user_page.route("/user_config", methods=['GET'])
@cert_required(role="user")
def user_config():
    """
    Returns all information about a user identified by a certificate.
    """
    user = g.user.to_dict()
    user.pop('password', None)
    res = build_response(simplejson.dumps(user))
    return res


@user_page.route("/user_credit", methods=['GET'])
@cert_required(role="user")
def user_credit():
    """
    Returns the remaining credit of a user identified by a certificate.
    """
    return build_response(simplejson.dumps(g.user.credit))


def add_credit(username, credit):
    """Add credit to a user."""
    user = User.query.filter_by(username=username).first()
    if not user:
        raise Exception("Unknown user '%s'" % username)
    user.credit += credit
    if user.credit < 0:
        user.credit = 0
    db.session.commit()
