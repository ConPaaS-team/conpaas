import inject

from conpaasdb.adapters.mysql.engine import MySQLEngine
from conpaasdb.utils.injection import fresh_scope
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class MySQLCommands:
    create_user = "CREATE USER %(username)s@%(hostname)s IDENTIFIED BY %(password)s"
    grant_user = "GRANT ALL PRIVILEGES ON *.* TO %(username)s@%(hostname)s WITH GRANT OPTION"
    drop_user = "DROP USER %(username)s@%(hostname)s"
    users_list = "SELECT user, host FROM mysql.user"
    db_list = "SHOW DATABASES"

@fresh_scope
class MySQLAdmin(object):
    engine = inject.attr(MySQLEngine)
    commands = inject.attr(MySQLCommands)
    
    @mlog
    def __init__(self):
        self.user_hosts = ('localhost', '%')
    
    @mlog
    def execute(self, command, **kwargs):
        return self.engine.engine.execute(command, **kwargs)
    
    @mlog
    def create_user(self, username, password):
        for host in self.user_hosts:
            self.execute(self.commands.create_user,
                          username=username, password=password, hostname=host)
            self.execute(self.commands.grant_user,
                          username=username, hostname=host)
        
        return True
    
    @mlog
    def drop_user(self, username):
        for host in self.user_hosts:
            self.execute(self.commands.drop_user,
                          username=username, hostname=host)
        
        return True
    
    @mlog
    def users_list(self):
        res = self.execute(self.commands.users_list)
        
        return [dict(user=user, host=host) for (user, host) in res]
    
    @mlog
    def db_list(self):
        res = self.execute(self.commands.db_list)
        
        return [db for (db,) in res]
