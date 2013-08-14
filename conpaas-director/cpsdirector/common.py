from flask import request, make_response

import os

from pwd import getpwnam
from grp import getgrnam

from ConfigParser import ConfigParser

config_parser = ConfigParser()

CONFFILE = os.getenv('DIRECTOR_CFG')

if not CONFFILE:
    CONFFILE = "/etc/cpsdirector/director.cfg"

# Config values for unit testing
if os.getenv('DIRECTOR_TESTING'):
    CONFFILE = 'director.cfg.example'

config_parser.read(CONFFILE)

if os.getenv('DIRECTOR_TESTING'):
    # dummy cloud
    config_parser.set("iaas", "DRIVER", "dummy")
    config_parser.set("iaas", "USER", "dummy")

    # separate database
    config_parser.set("director", "DATABASE_URI", "sqlite:///director-test.db")
    config_parser.set("director", "DIRECTOR_URL", "")

def get_director_url():
    return config_parser.get("director", "DIRECTOR_URL")

def get_userdata_dir():
    return config_parser.get("director", "USERDATA_DIR")

def chown(path, username, groupname):
    os.chown(path, getpwnam(username).pw_uid, getgrnam(groupname).gr_gid)

def log(msg):
    try:
        print >> request.environ['wsgi.errors'], msg
    except RuntimeError:
        print msg

def build_response(data):
    response = make_response(data)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
