import unittest
import requests
import urlparse
import jsonrpclib
from StringIO import StringIO

from conpaasdb.adapters.supervisor import SupervisorProcessStates

class Test(unittest.TestCase):
    rpc = 'http://127.0.0.1:60000'
    
    def setUp(self):
        self.agent = jsonrpclib.Server(self.rpc)
    
    def test_connection(self):
        self.failUnless(self.agent._list_methods())
    
    def test_state(self):
        def state():
            return self.agent.server_state()['state']
        
        if state() == SupervisorProcessStates.RUNNING:
            self.agent.server_stop()
        
        self.failUnless(self.agent.server_start())
        self.assertEqual(state(), SupervisorProcessStates.RUNNING)
        
        self.failUnless(self.agent.server_stop())
        self.assertEqual(state(), SupervisorProcessStates.STOPPED)
        
        self.failUnless(self.agent.server_start())
        self.assertEqual(state(), SupervisorProcessStates.RUNNING)
        
        self.failUnless(self.agent.server_restart())
        self.assertEqual(state(), SupervisorProcessStates.RUNNING)
        
    def test_config(self):
        self.failUnless(self.agent.server_set_port(3305))
        self.failUnless(self.agent.server_set_datadir('/var/lib/mysql'))
        self.failUnless(self.agent.server_set_bind_address('127.0.0.1'))
        
        self.failUnless(self.agent.server_restart())
        
        self.failUnless(self.agent.server_set_port(3306))
        
        self.failUnless(self.agent.server_restart())
    
    def test_auth(self):
        self.failUnless(self.agent.auth_user_create('test', 'password'))
        
        self.failUnless(dict(user='test', host='%') in self.agent.auth_user_list())
        
        self.failUnless(self.agent.auth_user_drop('test'))
        
        self.failUnless(dict(user='test', host='%') not in self.agent.auth_user_list())
    
    def test_db_list(self):
        self.failUnless('mysql' in self.agent.db_list())
    
    def upload_file(self, fp):
        upload_hash = self.agent.upload()
        url = urlparse.urljoin(self.rpc, '/upload/%s' % upload_hash)
        requests.post(url, fp.read())
        return upload_hash
    
    def test_upload(self):
        fp = StringIO('create database testdb;')
        
        hash = self.upload_file(fp)
        
        self.failUnless(hash)
        
        self.failUnless(self.agent.execute_sql(hash))
        
        self.failUnless('testdb' in self.agent.db_list())
