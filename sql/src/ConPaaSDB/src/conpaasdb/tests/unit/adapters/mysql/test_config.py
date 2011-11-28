import unittest

from conpaasdb.adapters.mysql.config import MySQLConfig

class Test(unittest.TestCase):
    def test_mysql_config(self):
        mc = MySQLConfig()
        
        self.assertEqual(mc.get('mysqld', 'port', int), 3306)
        
        mc.set('mysqld', 'port', 3305)
        mc.save()
        
        self.assertEqual(mc.get('mysqld', 'port', int), 3305)
        
        with open(mc.config_file) as f:
            new_config = f.read()
            
            self.assertEqual(new_config, '''\
#
# The MySQL database server configuration file.
#
[client]
port = 3305
socket          = /var/run/mysqld/mysqld.sock

[mysqld]
user            = mysql
port = 3305
datadir         = /var/lib/mysql

skip-external-locking

bind-address            = 0.0.0.0

!includedir /etc/mysql/conf.d/''')
        
        mc.set('mysqld', 'port', 3306)
        mc.save()
