import inject

from conpaasdb.utils.service import ServiceBase, expose

from conpaasdb.adapters.mysql.state import MySQLState
from conpaasdb.adapters.mysql.config import MySQLConfig
from conpaasdb.adapters.mysql.admin import MySQLAdmin
from conpaasdb.adapters.mysql.shell import SqlFile
from conpaasdb.utils.file import FileUploads
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class Errors:
    UNKNOWN = 0
    MYSQL = 10
    
    ERRORS = {
        UNKNOWN: 'Unknown error',
        MYSQL: 'MySQL server error'
    }

class AgentService(ServiceBase):
    @expose
    @mlog
    @inject.param('file_uploads', FileUploads)
    def upload(self, file_uploads):
        return file_uploads.get_hash()
    
    @expose
    @mlog
    @inject.param('state', MySQLState)
    def server_start(self, state):
        return state.start()
    
    @expose
    @mlog
    @inject.param('state', MySQLState)
    def server_stop(self, state):
        return state.stop()
    
    @expose
    @mlog
    @inject.param('state', MySQLState)
    def server_restart(self, state):
        return state.restart()
    
    @expose
    @mlog
    @inject.param('state', MySQLState)
    def server_state(self, state):
        return state.state()
    
    @expose
    @mlog
    @inject.param('config', MySQLConfig)
    def server_set_port(self, port, config):
        config.set('mysqld', 'port', int(port))
        config.save()
        return True
    
    @expose
    @mlog
    @inject.param('config', MySQLConfig)
    def server_set_datadir(self, datadir, config):
        config.set('mysqld', 'datadir', datadir)
        config.save()
        return True
    
    @expose
    @mlog
    @inject.param('config', MySQLConfig)
    def server_set_bind_address(self, bind_address, config):
        config.set('mysqld', 'bind-address', bind_address)
        config.save()
        return True
    
    @expose
    @mlog
    @inject.param('config', MySQLConfig)
    def server_get_info(self, config):
        info = dict(
            mysqld_port = config.get('mysqld', 'port', int),
            mysqld_datadir = config.get('mysqld', 'datadir'),
            mysqld_bind_address = config.get('mysqld', 'bind-address')
        )
        
        return info
    
    @expose
    @mlog
    @inject.param('admin', MySQLAdmin)
    def auth_user_create(self, username, password, admin):
        return admin.create_user(username, password)
    
    @expose
    @mlog
    @inject.param('admin', MySQLAdmin)
    def auth_user_drop(self, username, admin):
        return admin.drop_user(username)
    
    @expose
    @mlog
    @inject.param('admin', MySQLAdmin)
    def auth_user_list(self, admin):
        return admin.users_list()
    
    @expose
    @mlog
    @inject.param('admin', MySQLAdmin)
    def db_list(self, admin):
        return admin.db_list()
    
    @expose
    @mlog
    @inject.param('file_uploads', FileUploads)
    @inject.param('sql_file', SqlFile)
    def execute_sql(self, hash, file_uploads, sql_file):
        if file_uploads.valid(hash):
            path = file_uploads.get_path(hash)
            sql_file.run(path)
            file_uploads.delete(hash)
            
            return True
