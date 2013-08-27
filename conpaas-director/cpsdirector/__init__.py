# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from cpsdirector import common

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = common.config_parser.get(
    'director', 'DATABASE_URI')
db = SQLAlchemy(app)

if common.config_parser.has_option('director', 'DEBUG'):
    app.debug = True

from cpsdirector import application
app.register_blueprint(application.application_page)

from cpsdirector import service
app.register_blueprint(service.service_page)

from cpsdirector import user
app.register_blueprint(user.user_page)

from cpsdirector import cloud
app.register_blueprint(cloud.cloud_page)

from cpsdirector import manifest
app.register_blueprint(manifest.manifest_page)

from cpsdirector import director
app.register_blueprint(director.director_page)

if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", debug=True)
