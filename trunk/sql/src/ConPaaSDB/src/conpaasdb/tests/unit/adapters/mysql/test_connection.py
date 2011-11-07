import unittest

from conpaasdb.adapters.mysql.connection import MySQLConnectionData

class Test(unittest.TestCase):
    def test_mysql_connection_data(self):
        connection_data = MySQLConnectionData()
        
        self.assertEqual(connection_data.user, 'root')
        self.assertEqual(connection_data.password, 'testpassword')
        self.assertEqual(connection_data.hostname, '127.0.0.1')
        self.assertEqual(connection_data.port, 3306)
