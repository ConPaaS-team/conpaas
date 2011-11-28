import unittest

from conpaasdb.adapters.mysql.state import MySQLState

class Test(unittest.TestCase):
    def test_mysql_state(self):
        ms = MySQLState()
        
        self.failUnless(ms.start())
        self.failUnless(ms.stop())
        self.failUnless(ms.restart())
        self.assertEqual(ms.state()['name'], 'mysqld')
