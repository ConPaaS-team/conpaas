import inject

from conpaasdb.adapters.mysql.connection import MySQLConnectionData
from conpaasdb.adapters.execute import Execute, ExecuteException
from conpaasdb.utils.injection import fresh_scope
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class MySQLException(Exception):
    pass

@fresh_scope
class SqlFile(object):
    connection_data = inject.attr(MySQLConnectionData)
    execute = inject.attr(Execute)
    
    @mlog
    def __init__(self):
        args = (
            ('user', self.connection_data.user),
            ('password', self.connection_data.password),
            ('host', self.connection_data.hostname),
            ('port', self.connection_data.port)
        )
        
        escape = lambda x: str(x or '').replace('"', '\"')
        arg_to_str = lambda (k, v): '--%s="%s"' % (k, escape(v))
        
        self.args = ' '.join(map(arg_to_str, args))
    
    @mlog
    def run(self, file):
        cmd = 'mysql %s < "%s"' % (self.args, file)
        
        try:
            self.execute.execute(cmd)
        except ExecuteException, e:
            raise MySQLException(e)
        
        return True
