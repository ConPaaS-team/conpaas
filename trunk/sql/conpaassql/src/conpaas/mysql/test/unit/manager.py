'''
Created on Aug 31, 2011

@author: ales
'''
import unittest
from conpaas.mysql.server.manager.server import ManagerServer
import threading


class Test(unittest.TestCase):

    def setUp(self):
        from optparse import OptionParser
        from ConfigParser import ConfigParser    
        parser = OptionParser()
        parser.add_option('-p', '--port', type='int', default=50000, dest='port')
        parser.add_option('-b', '--bind', type='string', default='0.0.0.0', dest='address')
        parser.add_option('-c', '--config', type='string', default='./sql_manager_configuration.cfg', dest='config')          
        options, args = parser.parse_args()
        config_parser = ConfigParser()
        config_parser.read(options.config)
        print options.address, options.port
        self.managerServer = ManagerServer((options.address, options.port), config_parser)
        self.t = threading.Thread(target=self.managerServer.serve_forever)        
        self.managerServer.serve_forever()       
        self.t.start()

    def tearDown(self):
        self.managerServer.shutdown()
        self.managerServer = None
        self.t.join()
        self.t = None  

    def testGetNodes(self):
        self.assertTrue(self.managerServer.getListServiceNodes())     
         

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()