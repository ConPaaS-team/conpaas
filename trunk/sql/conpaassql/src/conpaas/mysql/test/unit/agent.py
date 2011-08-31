'''
Created on Aug 26, 2011

@author: ales
'''
import unittest
from conpaas.mysql.server.agent.server import AgentServer
from conpaas.mysql.client.agent_client import getMySQLServerState
import threading

class TestServerAgent(unittest.TestCase):

    host = '0.0.0.0'    
    port = 60000
    a = None
    
    def setUp(self):        
        self.a = AgentServer((self.host, self.port))
        self.t = threading.Thread(target=self.a.serve_forever)        
        self.t.start()
        
    def tearDown(self):        
        self.a.shutdown()
        self.a = None
        self.t.join()
        self.t = None       
    
    def test_SQLServerState(self):
        self.assertTrue(getMySQLServerState(self.host, self.port))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()   
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestServerAgent)
    #unittest.TextTestRunner(verbosity=2).run(suite)