import unittest

from conpaasdb.adapters.mysql.engine import MySQLEngine

class Test(unittest.TestCase):
    def test_mysql_engine(self):
        engine = MySQLEngine()
        
        self.failUnless(engine)
