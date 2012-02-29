
from conpaas.mysql.client.agent_client import getMySQLServerState, createMySQLServer, stopMySQLServer, setMySQLServerConfiguration,\
    remove_user, get_all_users, configure_user
import unittest

class test_startup (unittest.TestCase):
    def test1_is_shutdown(self):
        dict = getMySQLServerState("127.0.0.1", 60000)
        self.assertEqual(dict['return']['state'], 'STOPPED')
        #we create Mysql server and check if it is really up and what's the server state
    def test2_starting_server(self):
        dict = createMySQLServer('127.0.0.1', 60000)
        self.assertEqual(dict['opState'], 'OK')
    def test3_is_running(self):
        dictionari = getMySQLServerState("127.0.0.1", 60000)
        self.assertEqual(dictionari['return']['port'], "3306")
        self.assertEqual(dictionari['return']['state'],"RUNNING")
    #def test4_adding_user(self):
    #    dict = get_all_users('127.0.0.1',60000)
    #    self.assertEqual(dict['opState'], 'OK')
    #    dict = configure_user('127.0.0.1', 60000, 'janez4','rekar')
    #    self.assertEqual(dict['opState'],'OK')
    #def test5_removing_user(self):
    #    dict = remove_user('127.0.0.1', 60000, 'janez4')
    #    self.assertEqual(dict['opState'],'OK')   
    def test6_changing_port_number(self):     
        dict = setMySQLServerConfiguration('127.0.0.1', 60000, "port", 50000)        
        self.assertEqual(dict['opState'], 'OK');
        dictionari = getMySQLServerState("127.0.0.1", 60000)
        self.assertNotEqual(dictionari['return']['port'], "3306", "port wasn't changed")
        self.assertEqual(dictionari['return']['port'], "50000", "wrong port")
        dict = setMySQLServerConfiguration('127.0.0.1', 60000, "port", 3306) 
    def test6_stoping_server(self):
        dict = stopMySQLServer("127.0.0.1", 60000)
        self.assertEqual(dict['opState'], "OK")
        dict = getMySQLServerState("127.0.0.1", 60000)
        self.assertEqual(dict['return']['state'], 'STOPPED')
        test_startup.test1_is_shutdown(self)
                
if __name__ == '__main__':
#server mora biti ugasnen predno se zacnejo testi 
    if (getMySQLServerState('127.0.0.1', 60000)['return'] != 'shutdown'):
        if (getMySQLServerState('127.0.0.1', 60000)['return']['state'] == 'RUNNING') :
            stopMySQLServer('127.0.0.1', 60000)
    unittest.main()
    