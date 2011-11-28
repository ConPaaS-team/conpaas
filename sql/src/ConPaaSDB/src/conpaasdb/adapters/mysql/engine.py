import inject

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from conpaasdb.adapters.mysql.connection import MySQLConnectionData
from conpaasdb.utils.injection import fresh_scope
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

@fresh_scope
class MySQLEngine(object):
    connection_data = inject.attr(MySQLConnectionData)
    
    @mlog
    def __init__(self):
        c = self.connection_data
        
        url = URL('mysql+mysqldb', c.user, c.password, c.hostname, c.port)
        
        self.engine = create_engine(str(url))
