from conpaasdb.utils.client import ClientBase
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class AgentClient(ClientBase):
    @mlog
    def server_start(self):
        return self.service.server_start()
    
    @mlog
    def server_stop(self):
        return self.service.server_stop()
    
    @mlog
    def server_restart(self):
        return self.service.server_restart()
    
    @mlog
    def server_state(self):
        return self.service.server_state()
    
    @mlog
    def server_set_port(self, port):
        return self.service.server_set_port(port)
    
    @mlog
    def server_set_datadir(self, datadir):
        return self.service.server_set_datadir(datadir)
    
    @mlog
    def server_set_bind_address(self, bind_address):
        return self.service.server_set_bind_address(bind_address)
    
    @mlog
    def server_get_info(self):
        return self.service.server_get_info()
    
    @mlog
    def auth_user_create(self, username, password):
        return self.service.auth_user_create(username, password)
    
    @mlog
    def auth_user_drop(self, username):
        return self.service.auth_user_drop(username)
    
    @mlog
    def auth_user_list(self):
        return self.service.auth_user_list()
    
    @mlog
    def db_list(self):
        return self.service.db_list()
    
    @mlog
    def execute_sql(self, filename):
        hash = self.upload_file(filename)
        return self.service.execute_sql(hash)
