from conpaas.mysql.adapters.supervisor import Supervisor
from conpaas.mysql.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class MySQLState(object):
    
    supervisor = None
    
    @mlog
    def __init__(self, supervisor, name='mysqld'):
        self.supervisor = supervisor
        self.name = name
    
    @mlog
    def start(self):
        return self.supervisor.start(self.name)
    
    @mlog
    def stop(self):
        return self.supervisor.stop(self.name)
    
    @mlog
    def restart(self):
        self.stop()
        self.start()
        return True
    
    @mlog
    def state(self):
        return self.supervisor.info(self.name)
