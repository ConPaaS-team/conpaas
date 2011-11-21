from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from conpaas.mysql.utils.log import get_logger_plus
from conpaas.mysql.adapters.mysql.connection import MySQLConnectionData

logger, flog, mlog = get_logger_plus(__name__)

class MySQLEngine(object):
    
    connection_data = MySQLConnectionData
    
    @mlog
    def __init__(self):
        c = self.connection_data
        
        url = URL('mysql+mysqldb', c.user, c.password, c.hostname, c.port)
        
        self.engine = create_engine(str(url))