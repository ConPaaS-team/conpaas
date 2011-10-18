import os
import sys
from wtforms.fields import FileField
import shutil
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, '..')))

import logging
from flask import (Flask, Response, jsonify, redirect, url_for,
                   json, abort, request, render_template, g, flash)
from wtforms import Form, TextField, PasswordField, validators

from ManagerGUI.api import Manager

class Settings:
    DEBUG = False
    SECRET_KEY = 'Z%B6eHJJVvXTnU |Oji%>+$X1U{Smp+=+)y=U+#rFyAM-QUNRbo'
    LOGGING_LEVEL = 'ERROR'
    LOGGING_FORMAT = '%(asctime)s %(message)s'
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 5000
    MANAGER_HOST = '127.0.0.1'
    MANAGER_PORT = 50000
    AGENT_PORT = 60000

app = Flask(__name__)
app.config.from_object(Settings)
app.config.from_pyfile('manager-gui.conf', silent=True)
app.config.from_pyfile('/etc/conpaassql/manager-gui.conf', silent=True)
app.config.from_envvar('MANAGERGUI_SETTINGS', silent=True)

logger = logging.getLogger(__name__)

manager = None

@app.route('/')
def index():
    agents = manager.agent_list()
    return render_template('index.html', **locals())

@app.route('/agent/create')
def agent_create():
    agent = manager.agent_create()
    
    flash('Agent has been successfully created.')
    
    return redirect(url_for('agent_detail', id=agent['id']))

@app.route('/agent/<int:id>')
def agent_detail(id):
    agent = manager.agent_detail(id)
    users = manager.agent_user_list(agent['ip'])
    
    return render_template('agent_detail.html', **locals())

@app.route('/agent/<int:id>/remove')
def agent_remove(id):
    manager.agent_remove(id)
    
    flash('Agent has been successfully removed.')
    
    return redirect(url_for('index'))

class UploadSQLForm(Form):
    file = FileField('sql file')

@app.route('/agent/<int:id>/upload', methods=['GET', 'POST'])
def agent_upload_sql(id):
    agent = manager.agent_detail(id)
    
    form = UploadSQLForm(request.form)
    
    if request.method == 'POST' and form.validate():
        file = request.files[form.file.name]
        
        sql_file = tempfile.mktemp()
        
        with open(sql_file, 'w') as f:
            shutil.copyfileobj(file, f)
        
        manager.agent_upload_sql(agent['ip'], sql_file)
        
        flash('SQL file has been successfully uploaded.')
        
        return redirect(url_for('agent_detail', id=agent['id']))
    
    return render_template('agent_upload_sql.html', **locals())

class UserForm(Form):
    username = TextField('username')
    password = PasswordField('password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('password (repeat)')

@app.route('/agent/<int:id>/user/create', methods=['GET', 'POST'])
def agent_user_create(id):
    agent = manager.agent_detail(id)
    
    form = UserForm(request.form)
    
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        
        manager.agent_user_create(agent['ip'], username, password)
        
        flash('User has been successfully created.')
        
        return redirect(url_for('agent_detail', id=agent['id']))
    
    return render_template('agent_user_create.html', **locals())

@app.route('/agent/<int:id>/user/<username>/remove')
def agent_user_remove(id, username):
    agent = manager.agent_detail(id)
    manager.agent_user_remove(agent['ip'], username)
    
    flash('User has been successfully removed.')
    
    return redirect(url_for('agent_detail', id=id))

def configure():
    global manager
    
    manager = Manager(app.config['MANAGER_HOST'],
                        app.config['MANAGER_PORT'],
                        app.config['AGENT_PORT'])
    
    logging_level = logging.getLevelName(app.config['LOGGING_LEVEL'])
    logging_format = app.config['LOGGING_FORMAT']
    
    logging.basicConfig(format=logging_format, level=logging_level)

configure()

def main():
    app.run(app.config['SERVER_HOST'], app.config['SERVER_PORT'])

if __name__ == '__main__':
    main()
