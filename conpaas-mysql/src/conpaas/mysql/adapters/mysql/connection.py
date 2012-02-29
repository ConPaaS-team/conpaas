from conpaas.mysql.utils.log import get_logger_plus
from conpaas.mysql.adapters.mysql.config import MySQLConfig
from conpaas.mysql.adapters.mysql import MySQLSettings

logger, flog, mlog = get_logger_plus(__name__)

class MySQLConnectionData(object):
    mysql_settings = MySQLSettings
    config = MySQLConfig
    
    @mlog
    def __init__(self):
        self.user = 'root'
        self.password = self.mysql_settings.password
        self.hostname = '127.0.0.1'
        self.port = self.config.get('mysqld', 'port', int)
