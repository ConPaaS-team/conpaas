import unittest

from conpaasdb.adapters.mysql.admin import MySQLAdmin

class Test(unittest.TestCase):
    def test_mysql_admin(self):
        ms = MySQLAdmin()
        
        engine = ms.engine
        
        engine.expect("CREATE USER %(username)s@%(hostname)s IDENTIFIED BY %(password)s", username='user', password='pass', hostname='localhost')
        engine.expect("GRANT ALL PRIVILEGES ON *.* TO %(username)s@%(hostname)s WITH GRANT OPTION", username='user', hostname='localhost')
        engine.expect("CREATE USER %(username)s@%(hostname)s IDENTIFIED BY %(password)s", username='user', password='pass', hostname='%')
        engine.expect("GRANT ALL PRIVILEGES ON *.* TO %(username)s@%(hostname)s WITH GRANT OPTION", username='user', hostname='%')
        engine.expect("DROP USER %(username)s@%(hostname)s", username='user', hostname='localhost')
        engine.expect("DROP USER %(username)s@%(hostname)s", username='user', hostname='%')
        engine.expect_result("SELECT user, host FROM mysql.user", [
            ('user', 'localhost'),
            ('user', '%'),
        ])
        engine.expect_result("SHOW DATABASES", [
            ('db1',),
            ('db2',),
        ])
        
        ms.create_user('user', 'pass')
        ms.drop_user('user')
        
        self.assertEqual(ms.users_list(), [
            {'user': 'user', 'host': 'localhost'},
            {'user': 'user', 'host': '%'}
        ])
        
        self.assertEqual(ms.db_list(), [
            'db1',
            'db2'
        ])
