"""
    cpsdirector.idp
    =======================

    ConPaaS director: interface with (OpenID) identification/authentication/authorization providers

    :copyright: (C) 2014 by Contrail Consortium.
"""

import ConfigParser
import pprint 

from flask import Blueprint
import flask_openid
#from flask import Flask, render_template, request, g, session, flash, \
from flask import render_template, request, g, session, flash, \
     redirect, url_for, abort
# from flask.ext.openid import OpenID
from openid.extensions import pape
from cpsdirector import oid, db
db_session = db.session()

import pkg_resources  # part of setuptools
from cpsdirector.common import build_response, config_parser
from cpsdirector.common import log
from get_external_idps import get_external_idps
from cpsdirector.user import User
from cpsdirector.user import create_user
from cpsdirector import debug
di = debug.Debug()
from werkzeug.routing import BuildError
import sys

def __LINE__():
        try:
                raise Exception
        except:
                return sys.exc_info()[2].tb_frame.f_back.f_lineno
#def __FILE__():
#        return inspect.currentframe().f_code.co_filename


idp_page = Blueprint('idp_page', __name__)
#log( '%s:%d:idp.py started' % (__file__,__LINE__() ) )

ei_dict = get_external_idps("/etc/cpsdirector/director.cfg")
#oid = None

# setup flask-openid
#def init_oid(app):
#    global oid

#oid = OpenID(app, safe_roots=[], extension_responses=[pape.Response])

@idp_page.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()

@idp_page.route("/Xversion", methods=['GET'])
def Xversion():
    version = pkg_resources.require("cpsdirector")[0].version
    return build_response(version)

@idp_page.route("/Xsupport_external_idp", methods=['GET'])
def Xsupport_external_idp():
    try:
        result = config_parser.getboolean('conpaas', 'SUPPORT_EXTERNAL_IDP')
    except ConfigParser.NoOptionError:
        result = False;       # default value
    return build_response(result.__str__())


@idp_page.route('/')
def index():
    return render_template('cpsindex.html')

@idp_page.route("/Xidplogin", methods=['POST', 'GET'])
def Xidplogin():
    log("%s:%d:Gotcha: /idplogin" % (__file__,__LINE__() ))
    #log( pprint.pformat ( request.environ['wsgi.errors'] ) )
    res = "<html><head><title>Success</title></head><body>IDP-test geslaagd</body></html>"
    #global oid
    try:
#        from cpsdirector import app
#        oid = OpenID(app, safe_roots=[], extension_responses=[pape.Response])
        log("%s:%d:next = %s" % (__file__,__LINE__(), oid.get_next_url() ) )
        log("%s:%d:ei_dict = %s" % (__file__,__LINE__(),  pprint.pformat(ei_dict) ) )
        #res = render_template('cpslogin.html', items=ei_dict, next='blah', error='foutje')
        res = render_template('cpslogin.html', next=oid.get_next_url(), error=oid.fetch_error(), items=ei_dict)
    except BuildError as error:
        log ("%s:%d:error = %s" % (__file__,__LINE__(), error) )
        res = "<html><head><title>Failure</title></head><body>IDP-test mislukt:<br> BuildError: %s </body></html>" % error
    return build_response( res )
    #return build_response("<html><head><title>Success</title></head><body>IDP-test geslaagd</body></html>")

@idp_page.route('/idplogin', methods=['GET', 'POST'])
@oid.loginhandler
def idplogin():
    """Does the login via OpenID.  Has to call into `oid.try_login`
    to start the OpenID machinery.
    """
    # log('%s:%d:login g.user = %s' % (__file__,__LINE__(),g.user) )
    di.d3('login g.user = %s' % (g.user) )
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        source = request.form.get('source')
        # log('%s:%d:login with open ID "%s", source = "%s"' % (__file__,__LINE__(),openid, source))
        di.d3('login with open ID "%s", source = "%s"' % (openid, source))
        if openid:
            pape_req = pape.Request([])
            return oid.try_login(openid, ask_for=['email', 'nickname'],
                                         ask_for_optional=['fullname','dob'],
                                         extensions=[pape_req])
        if source:
            #openid = sources[source]
            openid = ei_dict[source]['discovery-url']
            #print >> sys.stderr, 'source = %s, openid = %s' % ( source, openid )
            # log('%s:%d:login with open ID "%s", source = "%s"' % (__file__,__LINE__(),openid, source))
            di.d3('login with open ID "%s", source = "%s"' % (openid, source))
            pape_req = pape.Request([])
            return oid.try_login(openid, ask_for=['email', 'nickname'],
                                         ask_for_optional=['fullname','dob'],
                                         extensions=[pape_req])
    return render_template('cpslogin.html', next=oid.get_next_url(),
                           error=oid.fetch_error(), items=ei_dict)
    """The following strings can be used in the ask_for and 
    ask_for_optional parameters: aim, blog, country, dob (date of birth), 
    email, fullname, gender, icq, image, jabber, language, msn, nickname, 
    phone, postcode, skype, timezone, website, yahoo
    """

@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session['openid'] = resp.identity_url
    if 'pape' in resp.extensions:
        pape_resp = resp.extensions['pape']
        session['auth_time'] = pape_resp.auth_time
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())
    for key in flask_openid.COMMON_PROVIDERS:
        val = flask_openid.COMMON_PROVIDERS[key]
        di.d3("COMMON_PROVIDER %s => %s" % (key, val))
    di.d3("oid.get_next_url() = %s " % (oid.get_next_url()))
    #for key in resp:
    #    val = resp.key
    #    di.d3("resp.%s = %s" % (key, val))
    return redirect(url_for('idp_page.create_profile', next=oid.get_next_url(),
                            name='F '+resp.fullname or 'N '+resp.nickname,
                            dob=resp.date_of_birth or 'dob?',
                            date_of_birth=resp.date_of_birth or 'date_of_birth?',
                            email=resp.email))
    return redirect(url_for('idp_page.create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))


@idp_page.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    """If this is the user's first login, the create_or_login function
    will redirect here so that the user can set up his profile.
    """
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('idp_page.index'))
    if request.method == 'POST':
        for k in request.form:
            di.d3("form[%s] = %s" % (k,request.form[k]))
        username = request.form['name']
        fname = None
        lname = None
        email = request.form['email']
        affiliation = None
        password = 'testpass'
        credit = 50
        uuid = None
        openid = session['openid']
        di.d3("username = %s" % username)
        di.d3("not username = %s" % (not username))
        if not username:
            flash(u'Error: you have to provide a name')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address')
        else:
            di.d2('Profile successfully created')
            flash(u'Profile successfully created')
            create_user(username, fname, lname, email, affiliation, password, credit, uuid, openid)
            #db_session.add(new_user)
            #db_session.commit()
            return redirect(oid.get_next_url())
    return render_template('cpscreate_profile.html', next_url=oid.get_next_url())


@idp_page.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    """Updates a profile"""
    if g.user is None:
        abort(401)
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db_session.delete(g.user)
            db_session.commit()
            session['openid'] = None
            flash(u'Profile deleted')
            return redirect(url_for('idp_page.index'))
        form['name'] = request.form['name']
        form['email'] = request.form['email']
        if not form['name']:
            flash(u'Error: you have to provide a name')
        elif '@' not in form['email']:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            g.user.name = form['name']
            g.user.email = form['email']
            db_session.commit()
            return redirect(url_for('edit_profile'))
    return render_template('cpsedit_profile.html', form=form)


@idp_page.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect(oid.get_next_url())


#if __name__ == '__main__':
    #app.run()
    #app.run(host='0.0.0.0')
    #app.add_url_rule('/google-idp.png', redirect_to=url_for('images', filename='google-idp.png'))
    #app.add_url_rule('/yahoo-idp.png', redirect_to=url_for('images', filename='yahoo-idp.png'))
