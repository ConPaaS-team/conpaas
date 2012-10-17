import urllib
import unittest
import simplejson

import app

class Common(unittest.TestCase):

    def setUp(self):
        app.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///director-test.db"
        app.db.drop_all()
        app.db.create_all()

    def create_user(self):
        return app.create_user("ema", "Emanuele", "Rocca", "ema@linux.it", 
            "VU University Amsterdam", "properpass", 120)

class DbTest(Common):

    def test_create_user(self):
        self.create_user()

        self.assertFalse(app.auth_user("ema", "wrongpass"))
        self.assert_(app.auth_user("ema", "properpass") is not None)
        self.assertFalse(app.auth_user("wronguname", "properpass"))

    def test_create_service(self):
        self.create_user()

        user = app.auth_user("ema", "properpass")
        service = app.Service(name="New selenium service", type="selenium", 
            user=user)
        app.db.session.add(service)
        app.db.session.commit()

        # Testing service->user backref
        self.assertEquals(120, service.user.credit)

    def test_decrement_user_credit(self):
        user = self.create_user()
        user.credit -= 10

        if user.credit > -1:
            app.db.session.commit()
        else:
            app.db.session.rollback()

        user = app.auth_user("ema", "properpass")
        self.assertEquals(110, user.credit)

        user.credit -= 5000

        if user.credit > -1:
            app.db.session.commit()
        else:
            app.db.session.rollback()

        user = app.auth_user("ema", "properpass")
        self.assertEquals(110, user.credit)

class DirectorTest(Common):
    
    def setUp(self):
        Common.setUp(self)
        self.app = app.app.test_client()          

    def test_404_on_root(self):
        response = self.app.get("/")
        self.assertEquals(404, response.status_code)

    def test_200_on_start(self):
        response = self.app.post('/start/php')
        self.assertEquals(200, response.status_code)

    def test_200_on_stop(self):
        response = self.app.post('/stop/1')
        self.assertEquals(200, response.status_code)

    def test_200_on_list(self):
        response = self.app.get('/list')
        self.assertEquals(200, response.status_code)

    def test_200_on_download_conpaas(self):
        response = self.app.get('/download/ConPaaS.tar.gz')
        self.assertEquals(200, response.status_code)

    def test_200_on_credit(self):
        response = self.app.post('/callback/decrementUserCredit.php')
        self.assertEquals(200, response.status_code)

    def test_false_start(self):
        data = { 'username': "wronguser", 'password': "properpass" }

        response = self.app.post('/start/php', data=data)
        self.assertEquals(False, simplejson.loads(response.data))

    def test_proper_start(self):
        self.create_user()

        data = { 'username': "ema", 'password': "properpass" }
        
        response = self.app.post('/start/php', data=data)
        servicedict = simplejson.loads(response.data)
    
        self.assertEquals("New php service", servicedict['name'])
        self.assertEquals(1, servicedict['sid'])
        self.assertEquals('INIT', servicedict['state'])
        self.assertEquals('php', servicedict['type'])
        self.assertEquals(1, servicedict['user_id'])

        # Values returned by libcloud's dummy driver
        self.assertEquals('3', servicedict['vmid'])
        self.assertEquals('127.0.0.3', servicedict['manager'])

    def test_false_stop(self):
        data = { 'username': "wronguser", 'password': "properpass" }

        response = self.app.post('/stop/1', data=data)
        self.assertEquals(False, simplejson.loads(response.data))

    def test_proper_stop(self):
        self.create_user()
        data = { 'username': "ema", 'password': "properpass" }

        # No service with id 1
        response = self.app.post('/stop/1', data=data)
        self.assertEquals(False, simplejson.loads(response.data))
    
        # Let's create one
        response = self.app.post('/start/php', data=data)
        servicedict = simplejson.loads(response.data)
        self.assertEquals(1, servicedict['sid'])

        # Now /stop/1 should return True
        response = self.app.post('/stop/1', data=data)
        self.assertEquals(True, simplejson.loads(response.data))

    def test_list(self):
        self.create_user()

        data = { 'username': "ema", 'password': "properpass" }
        list_url = '/list?' + urllib.urlencode(data)

        # No available service
        response = self.app.get(list_url)
        self.assertEquals([], simplejson.loads(response.data))

        # Let's create a service
        response = self.app.post('/start/php', data=data)
        servicedict = simplejson.loads(response.data)
        self.assertEquals(1, servicedict['sid'])

        # Check if it's returned by /list
        response = self.app.get(list_url)
        result = simplejson.loads(response.data)
        self.assertEquals(1, len(result))
        self.assertEquals('New php service', result[0]['name'])

    def test_credit(self):
        self.create_user()
        data = { 'username': "ema", 'password': "properpass" }

        # Let's create a service
        response = self.app.post('/start/php', data=data)
        servicedict = simplejson.loads(response.data)
        self.assertEquals(1, servicedict['sid'])

        # No sid and decrement
        data = {}
        response = self.app.post('/callback/decrementUserCredit.php', data=data)
        self.assertEquals({ 'error': True }, simplejson.loads(response.data))
            
        # Right sid but not enough credit
        data = { 'sid': 1, 'decrement': 10000 }
        response = self.app.post('/callback/decrementUserCredit.php', data=data)
        self.assertEquals({ 'error': True }, simplejson.loads(response.data))

        user = app.auth_user("ema", "properpass")
        self.assertEquals(120, user.credit)

        # Right sid and enough credit
        data = { 'sid': 1, 'decrement': 1 }
        response = self.app.post('/callback/decrementUserCredit.php', data=data)
        self.assertEquals({ 'error': False }, simplejson.loads(response.data))

        user = app.auth_user("ema", "properpass")
        self.assertEquals(119, user.credit)

if __name__ == "__main__":
    unittest.main()
