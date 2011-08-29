'''
Created on Aug 26, 2011

@author: ales
'''
import unittest
from conpaas.mysql.server.agent.server import AgentServer
from conpaas.mysql.client.agent_client import getMySQLServerState

class TestServerAgent(unittest.TestCase):

    host = '0.0.0.0'    
    port = 60000
    a = None
    
    def testName(self):
        pass
    
    def setUp(self):
        pass        
        #self.a = AgentServer((self.host, self.port))
        #self.a.serve_forever()

    def tearDown(self):
        pass
        #self.a.shutdown()
    
    def test_SQLServerState(self):
        ret=getMySQLServerState(self.host, self.port)
        print ret

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()   
    suite = unittest.TestLoader().loadTestsFromTestCase(TestServerAgent)
    unittest.TextTestRunner(verbosity=2).run(suite)    