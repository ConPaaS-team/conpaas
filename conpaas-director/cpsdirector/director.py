"""
    cpsdirector.director
    =======================

    ConPaaS director: interface to the director itself.

    :copyright: (C) 2013 by Contrail Consortium.
"""

from flask import Blueprint
import pkg_resources  # part of setuptools
from cpsdirector.common import build_response


director_page = Blueprint('director_page', __name__)


@director_page.route("/version", methods=['GET'])
def version():
    version = pkg_resources.require("cpsdirector")[0].version
    return build_response(version)
