"""
    cpsdirector.director
    =======================

    ConPaaS director: interface to the director itself.

    :copyright: (C) 2013 by Contrail Consortium.
"""

import ConfigParser

from flask import Blueprint
import pkg_resources  # part of setuptools
from cpsdirector.common import build_response, config_parser


director_page = Blueprint('director_page', __name__)


@director_page.route("/version", methods=['GET'])
def version():
    version = pkg_resources.require("cpsdirector")[0].version
    return build_response(version)

@director_page.route("/support_external_idp", methods=['GET'])
def support_external_idp():
    try:
        result = config_parser.getboolean('conpaas', 'SUPPORT_EXTERNAL_IDP')
    except ConfigParser.NoOptionError:
        result = False;       # default value, i.e. if not found in the config file
    return build_response(result.__str__())

@director_page.route("/support_openid", methods=['GET'])
def support_openid():
    try:
        result = config_parser.getboolean('conpaas', 'SUPPORT_OPENID')
    except ConfigParser.NoOptionError:
        result = False;       # default value, i.e. if not found in the config file
    return build_response(result.__str__())

# set up to support debugging messages and alerts for python, php, ajax an js (javascript)
# until now only js is actually used
# see also configuration files  director.cgf*example
@director_page.route("/debug_level/<debug_type>", methods=['GET'])
def debug_level(debug_type):
    try:
        result = config_parser.getint('conpaas', debug_type + '_debug_level')
    except ConfigParser.NoOptionError:
        result = 0;       # default value, i.e. if not found in the config file
    return build_response(result.__str__())
