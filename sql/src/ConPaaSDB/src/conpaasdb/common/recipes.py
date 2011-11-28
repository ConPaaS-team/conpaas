import os
import posixpath

from fabric.api import run, settings, prefix, put, cd
from fabric.contrib.files import append

from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

def host_tmp(file):
    return posixpath.join('/', 'tmp', os.path.basename(file))

@flog
def essentials_recipe():
    run('apt-get update')
    run('apt-get install -y python-setuptools build-essential python-dev git')
    run('easy_install pip')

@flog
def supervisor_recipe():
    run('apt-get update')
    run('apt-get install -y supervisor')
    append('/etc/supervisor/supervisord.conf', '''
[inet_http_server]
port = 0.0.0.0:9001
username = contrail
password = contrail
''', use_sudo=True)
    run('supervisorctl reload')

@flog
def mysql_server_recipe(mysql_root_password):
    with settings(warn_only=True):
        mysqld_installed = run('which mysqld').succeeded
    
    if not mysqld_installed:
        run('apt-get update')
    
    with settings(warn_only=True):
        supervisor_mysqld_installed = run('ls /etc/supervisor/conf.d/mysqld.conf').succeeded
    
    if supervisor_mysqld_installed:
        run('supervisorctl stop mysqld')
        run('rm -f /etc/supervisor/conf.d/mysqld.conf')
        run('supervisorctl reload')
    
    if not mysqld_installed:
        run('DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server')
        
        with prefix('MYSQL_PASSWORD="%s"' % mysql_root_password):
            run('mysqladmin password $MYSQL_PASSWORD')
    
    append('/etc/supervisor/conf.d/mysqld.conf', '''\
[program:mysqld]
command=/usr/sbin/mysqld --basedir=/usr --datadir=/var/lib/mysql --user=mysql --pid-file=/var/run/mysqld/mysqld.pid --skip-external-locking --socket=/var/run/mysqld/mysqld.sock
autorestart=true
redirect_stderr=true
''', use_sudo=True)
    
    run('/etc/init.d/mysql stop')
    run('supervisorctl reload')

@flog
def conpaasdb_dependencies_recipe():
    requirements = [
        'argparse',
        'Fabric',
        'fabric_threadsafe',
        'PyMySQL',
        'SQLAlchemy',
        'apache-libcloud',
        'colander',
        'jsonrpclib',
        'nose',
        'oca',
        'paramiko',
        '-e git+https://github.com/ivan-korobkov/python-inject.git#egg=python-inject',
        'requests'
    ]
    
    run('pip install %s' % ' '.join(requirements))

@flog
def conpaasdb_install_recipe(package):
    run('mkdir -p /srv/conpaasdb')
    
    put(package, '/srv/conpaasdb/conpaasdb.zip')
    
    with settings(warn_only=True):
        run('pip uninstall -y conpaasdb')
    
    run('pip install /srv/conpaasdb/conpaasdb.zip')

@flog
def agent_install_recipe(agent_config):
    agent_config_dest = host_tmp(agent_config)
    
    put(agent_config, agent_config_dest)
    
    run('rm -f /etc/supervisor/conf.d/conpaasdb_agent.conf')
    
    append('/etc/supervisor/conf.d/conpaasdb_agent.conf', '''\
[program:conpaasdb_agent]
command=python -m conpaasdb.agent.server -c %s
redirect_stderr=true
environment=PYTHONUNBUFFERED=t
''' % agent_config_dest)
    
    run('supervisorctl reload')

@flog
def manager_install_recipe(manager_config, agent_config):
    manager_config_dest = host_tmp(manager_config)
    agent_config_dest = host_tmp(agent_config)
    
    put(manager_config, manager_config_dest)
    put(agent_config, agent_config_dest)
    
    run('rm -f /etc/supervisor/conf.d/conpaasdb_manager.conf')
    
    append('/etc/supervisor/conf.d/conpaasdb_manager.conf', '''\
[program:conpaasdb_manager]
command=python -m conpaasdb.manager.server -c %s -a %s
redirect_stderr=true
environment=PYTHONUNBUFFERED=t
''' % (manager_config_dest, agent_config_dest))
    
    run('supervisorctl reload')

@flog
def test_dependencies_recipe():
    run('pip install nose')
    run('pip install requests')

@flog
def test_recipe():
    test_path = run('''python -c "import os; import conpaasdb; print os.path.dirname(conpaasdb.__file__)"''')
    
    with cd(test_path):
        run('nosetests -s -v')

@flog
def deploy_agent(config, package, mysql_root_password):
    essentials_recipe()
    supervisor_recipe()
    mysql_server_recipe(mysql_root_password)
    conpaasdb_dependencies_recipe()
    conpaasdb_install_recipe(package)
    agent_install_recipe(config)

@flog
def deploy_manager(manager_config, agent_config, package):
    essentials_recipe()
    supervisor_recipe()
    conpaasdb_dependencies_recipe()
    conpaasdb_install_recipe(package)
    manager_install_recipe(manager_config, agent_config)
