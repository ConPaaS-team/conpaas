'''
Created on Aug 26, 2011

@author: ales
'''
import unittest
from conpaas.mysql.server.agent.server import AgentServer
from conpaas.mysql.client.agent_client import getMySQLServerState
from conpaas.mysql.client.agent_client import createMySQLServer
from conpaas.mysql.client.agent_client import restartMySQLServer
from conpaas.mysql.client.agent_client import stopMySQLServer
import threading
from ConfigParser import ConfigParser
from conpaas.mysql.server.agent.internals import MySQLServer
from conpaas.mysql.server.agent import internals

class TestServerAgent(unittest.TestCase):
  
    #host = '0.0.0.0'
    #port = 60000
    a = None
    
    def setUp(self):        
        config = './configuration.cnf'
        config_parser = ConfigParser()
        config_parser.read(config)
        '''Set up configuration for the parser.
        '''
        config_parser.set('MySQL_configuration', 'my_cnf_file', '/etc/mysql/my.cnf')
        config_parser.set('MySQL_configuration', 'path_mysql_ssr', '/etc/init.d/mysql')        
        config_parser.set('MySQL_root_connection', 'location', '')
        config_parser.set('MySQL_root_connection', 'username', '')
        config_parser.set('MySQL_root_connection', 'password', '')
       
        # This is for integration testing
        #self.a = AgentServer((self.host, self.port), config_parser)
        #self.t = threading.Thread(target=self.a.serve_forever)        
        #self.t.start()
        self.a=MySQLServer(config_parser, True)
        internals.agent = self.a
        self.a.start()
        
    def tearDown(self):        
        self.a.stop()
        self.a = None
        #self.t.join()
        #self.t = None       
    
    def testSQLServerState(self):
        #self.assertTrue(getMySQLServerState(self.host, self.port))
        ret=internals.getMySQLServerState(False)
        self.assertTrue(ret)
        self.__check_reply(ret)

    def testStartStopSQLServer(self):
        #ret = createMySQLServer(self.host,self.port)        
        #self.assertTrue(ret)
        #self.__check_reply(ret)
        #ret = stopMySQLServer(self.host,self.port)
        #self.assertTrue(ret)
        #self.__check_reply(ret)
        ret = internals.createMySQLServer(False)
        self.assertTrue(ret)    
        self.__check_reply(ret)
        ret = internals.stopMySQLServer(False)
        self.assertTrue(ret)
        self.__check_reply(ret)                   
        
    def testRestartSQLServer(self):        
        ret = internals.restartMySQLServer(False)
        self.assertTrue(ret)
        self.__check_reply(ret)        

    def __check_reply(self, ret):            
        self.assertTrue( ret['opState'] == 'OK')            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()   
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestServerAgent)
    #unittest.TextTestRunner(verbosity=2).run(suite)