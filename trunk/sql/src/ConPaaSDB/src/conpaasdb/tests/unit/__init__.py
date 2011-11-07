import inject
import tempfile

from conpaasdb.adapters.mysql import MySQLSettings
from conpaasdb.adapters.supervisor import SupervisorSettings, Supervisor
from conpaasdb.adapters.mysql.engine import MySQLEngine
from conpaasdb.adapters.execute import Execute

from conpaasdb.tests.unit.adapters.mysql import FakeMySQLEngine
from conpaasdb.tests.unit.adapters.execute import FakeExecute
from conpaasdb.tests.unit.adapters.supervisor import FakeSupervisor
from conpaasdb.utils.injection import FreshScope, fresh_scope

injector = None

def setup():
    injector = inject.create()
    injector.bind_scope(FreshScope, fresh_scope)
    
    mysql_cnf = tempfile.mktemp()
    
    with open(mysql_cnf, 'w') as f:
        f.write('''\
#
# The MySQL database server configuration file.
#
[client]
port            = 3306
socket          = /var/run/mysqld/mysqld.sock

[mysqld]
user            = mysql
port            = 3306
datadir         = /var/lib/mysql

skip-external-locking

bind-address            = 0.0.0.0

!includedir /etc/mysql/conf.d/''')
    
    execute = FakeExecute()
    injector.bind(Execute, execute)
    
    mysql_settings = MySQLSettings()
    mysql_settings.password = 'testpassword'
    mysql_settings.config = mysql_cnf
    injector.bind(MySQLSettings, mysql_settings)
    
    mysql_engine = FakeMySQLEngine()
    injector.bind(MySQLEngine, mysql_engine)
    
    supervisor_settings = SupervisorSettings()
    supervisor_settings.rpc = 'http://testhost:1234'
    injector.bind(SupervisorSettings, supervisor_settings)
    
    supervisor = FakeSupervisor()
    injector.bind(Supervisor, supervisor)
