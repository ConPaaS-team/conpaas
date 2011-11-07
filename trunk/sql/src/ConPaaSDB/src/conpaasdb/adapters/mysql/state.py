import inject

from conpaasdb.adapters.supervisor import Supervisor
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class MySQLState(object):
    supervisor = inject.attr(Supervisor)
    
    @mlog
    def __init__(self, name='mysqld'):
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
