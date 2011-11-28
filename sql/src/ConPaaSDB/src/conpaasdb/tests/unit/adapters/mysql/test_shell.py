import unittest

from conpaasdb.adapters.mysql.shell import SqlFile

class Test(unittest.TestCase):
    def test_sql_file(self):
        sf = SqlFile()
        
        c = sf.connection_data
        
        sf.execute.expect('mysql --user="%s" --password="%s" '
                            '--host="%s" --port="%s" < "testfile.sql"'
                                % (c.user, c.password, c.hostname, c.port))
        
        sf.run('testfile.sql')
