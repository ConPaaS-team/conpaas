'''
Created on Aug 31, 2011

@author: ales
'''
import unittest
from conpaas.mysql.server.manager.server import ManagerServer
import threading
from ConfigParser import ConfigParser
from conpaas.iaas import IaaSClient
from conpaas.mysql.server.manager import internals
from conpaas.mysql.server.manager.internals import MySQLServerManager


class Test(unittest.TestCase):

    def setUp(self):
        # This is prepared for integration unit testing.
        #=======================================================================
        # from optparse import OptionParser
        # from ConfigParser import ConfigParser    
        # parser = OptionParser()
        # parser.add_option('-p', '--port', type='int', default=50000, dest='port')
        # parser.add_option('-b', '--bind', type='string', default='0.0.0.0', dest='address')
        # parser.add_option('-c', '--config', type='string', default='./sql_manager_configuration.cnf', dest='config')          
        # options, args = parser.parse_args()
        # config_parser = ConfigParser()
        # config_parser.read(options.config)
        # print options.address, options.port
        # self.managerServer = ManagerServer((options.address, options.port), config_parser)
        # self.t = threading.Thread(target=self.managerServer.serve_forever)        
        # self.managerServer.serve_forever()       
        # self.t.start()
        #=======================================================================
        config = './sql_manager_configuration.cnf'
        config_parser = ConfigParser()
        config_parser.read(config)
        '''Set up configuration for the parser.
        '''
       
        # This is for integration testing
        #self.a = AgentServer((self.host, self.port), config_parser)
        #self.t = threading.Thread(target=self.a.serve_forever)        
        #self.t.start()
        self.a=IaaSClient(config_parser)
        internals.iaas = self.a
        internals.managerServer=MySQLServerManager(config_parser, True)
        self.managerServer = internals.managerServer
        
    def tearDown(self):
        #self.managerServer.shutdown()
        #self.managerServer = None
        #self.t.join()
        #self.t = None
        self.managerServer = None  
        self.a = None

    def testAddNodes(self):
        nodes = internals.listServiceNodes({})
        len1 = len(nodes['sql'])
        self.assertTrue( len(nodes['sql']) == 3 )
        internals.createServiceNode({})
        nodes = internals.listServiceNodes({})
        self.assertTrue(len(nodes['sql'])== 4)

    def testRemoveNodes(self):
        nodes = internals.listServiceNodes({})
        len1 = len(nodes['sql'])        
        internals.deleteServiceNode({'id':1})
        nodes = internals.listServiceNodes({})
        self.assertTrue(len(nodes['sql'])== len1-1)

    def testGetNodes(self):
        nodes = internals.listServiceNodes({})
        self.assertTrue(nodes)
        self.assertTrue(nodes['sql'])
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()