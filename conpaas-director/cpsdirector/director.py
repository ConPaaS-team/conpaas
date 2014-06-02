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
        result = config_parser.get('conpaas', 'SUPPORT_EXTERNAL_IDP')
    except ConfigParser.NoOptionError:
        result = 'false';       # default value
    return build_response(result)
