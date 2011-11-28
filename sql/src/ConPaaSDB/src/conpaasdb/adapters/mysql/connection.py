import inject

from conpaasdb.adapters.mysql import MySQLSettings
from conpaasdb.adapters.mysql.config import MySQLConfig
from conpaasdb.utils.injection import fresh_scope
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

@fresh_scope
class MySQLConnectionData(object):
    mysql_settings = inject.attr(MySQLSettings)
    config = inject.attr(MySQLConfig)
    
    @mlog
    def __init__(self):
        self.user = 'root'
        self.password = self.mysql_settings.password
        self.hostname = '127.0.0.1'
        self.port = self.config.get('mysqld', 'port', int)
