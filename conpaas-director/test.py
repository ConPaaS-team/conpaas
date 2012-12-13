# -*- coding: utf-8 -*-

import os
import urllib
import hashlib
import unittest
import simplejson

os.environ['DIRECTOR_TESTING'] = "true"

import cpsdirector 

TEST_USER_DATA = { 
    'username': 'testuser', 
    'fname': 'TestName', 
    'lname': 'TestSurname', 
    'email': 'test@example.org',
    'affiliation': 'Test Institution', 
    'password': 'properpass', 
    'credit': 120 
}

class Common(unittest.TestCase):

    def setUp(self):
        cpsdirector.db.drop_all()
        cpsdirector.db.create_all()

    def create_user(self, data=TEST_USER_DATA):
        return cpsdirector.create_user(data['username'], 
                                       data['fname'],
                                       data['lname'],
                                       data['email'],
                                       data['affiliation'],
                                       data['password'],
                                       data['credit'])

class DbTest(Common):

    def test_create_user(self):
        self.create_user()

        self.assertFalse(cpsdirector.get_user(TEST_USER_DATA['username'], 
            "wrongpass"))

        self.assert_(cpsdirector.get_user(TEST_USER_DATA['username'], 
            TEST_USER_DATA['password']) is not None)

        self.assertFalse(cpsdirector.get_user("wronguname", TEST_USER_DATA['password']))

    def test_create_service(self):
        self.create_user()

        user = cpsdirector.get_user(TEST_USER_DATA['username'], TEST_USER_DATA['password'])
        service = cpsdirector.Service(name="New selenium service", type="selenium", 
            user=user)
        cpsdirector.db.session.add(service)
        cpsdirector.db.session.commit()

        # Testing service->user backref
        self.assertEquals(120, service.user.credit)

    def test_decrement_user_credit(self):
        user = self.create_user()
        user.credit -= 10

        if user.credit > -1:
            cpsdirector.db.session.commit()
        else:
            cpsdirector.db.session.rollback()

        user = cpsdirector.get_user(TEST_USER_DATA['username'], TEST_USER_DATA['password'])
        self.assertEquals(110, user.credit)

        user.credit -= 5000

        if user.credit > -1:
            cpsdirector.db.session.commit()
        else:
            cpsdirector.db.session.rollback()

        user = cpsdirector.get_user(TEST_USER_DATA['username'], TEST_USER_DATA['password'])
        self.assertEquals(110, user.credit)

class DirectorTest(Common):
    
    def setUp(self):
        Common.setUp(self)
        self.app = cpsdirector.app.test_client()          

    def test_404_on_root(self):
        response = self.app.get("/")
        self.assertEquals(404, response.status_code)

    def test_200_on_start(self):
        response = self.app.post('/start/php', data={ 'uid': 1 })
        self.assertEquals(200, response.status_code)

    def test_200_on_stop(self):
        response = self.app.post('/stop/1', data={ 'uid': 1 })
        self.assertEquals(200, response.status_code)

    def test_200_on_list(self):
        response = self.app.get('/list?uid=1')
        self.assertEquals(200, response.status_code)

    def test_200_on_download_conpaas(self):
        response = self.app.get('/download/ConPaaS.tar.gz')
        self.assertEquals(200, response.status_code)

    def test_200_on_credit(self):
        response = self.app.post('/callback/decrementUserCredit.php', data={ 'uid': 1 })
        self.assertEquals(200, response.status_code)

    def test_false_start_wrong_credentials(self):
        # Here the credentials are wrong because no user in the DB has uid 1
        response = self.app.post('/start/php', data={ 'uid': 1 })
        self.assertEquals(False, simplejson.loads(response.data))

    def test_false_start_wrong_servicetype(self):
        self.create_user()
        response = self.app.post('/start/wrong', data={ 'uid': 1 })
        ret = simplejson.loads(response.data)
        self.assertEquals('Unknown service type: wrong', ret['msg'])

    def test_proper_start(self):
        self.create_user()

        response = self.app.post('/start/php', data={ 'uid': 1 })
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
        self.create_user()
        response = self.app.post('/stop/1', data={ 'uid': 1 })
        self.assertEquals(False, simplejson.loads(response.data))

    def test_proper_stop(self):
        self.create_user()
        data = { 'uid': 1 }

        # No service with id 1
        response = self.app.post('/stop/1', data=data)
        self.assertEquals(False, simplejson.loads(response.data))
    
        # Let's create one
        response = self.app.post('/start/php', data=data)
        servicedict = simplejson.loads(response.data)
        self.assertEquals(1, servicedict['sid'])

        # Now /stop/1 should return True
        response = self.app.post('/stop/1', data=data)
        self.failUnless(simplejson.loads(response.data))

    def test_stop_wrong_user(self):
        # create default user
        self.create_user()

        # create a service
        data = { 'uid': 1, } 
        response = self.app.post('/start/php', data=data)
        servicedict = simplejson.loads(response.data)
        self.assertEquals(1, servicedict['sid'])

        # create another user
        other_user = {
            'username': 'testuser_other',
            'fname': 'TestName',
            'lname': 'TestSurname',
            'email': 'test_other@example.org',
            'affiliation': 'Test Institution',
            'password': 'properpass',
            'credit': 120
        }
        self.create_user(other_user)

        # we expect false now that the newly created user tries to stop the
        # service she does not own
        response = self.app.post('/stop/1', data={ 'uid': 2 })
        self.failIf(simplejson.loads(response.data))

        # whereas the owner should be able to stop the service
        response = self.app.post('/stop/1', data={ 'uid': 1 })
        self.failUnless(simplejson.loads(response.data))

    def test_list(self):
        self.create_user()

        data = { 'uid': 1 }
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
        data = { 'uid': 1 }

        # Let's create a service
        response = self.app.post('/start/php', data=data)
        servicedict = simplejson.loads(response.data)
        self.assertEquals(1, servicedict['sid'])

        # No sid and decrement
        data = { 'uid': 1, 'sid': -1 }
        response = self.app.post('/callback/decrementUserCredit.php', data=data)
        expected = False
        self.assertEquals(expected, simplejson.loads(response.data))
            
        # Right sid but not enough credit
        data = { 'sid': 1, 'decrement': 10000, 'uid': 1 }
        response = self.app.post('/callback/decrementUserCredit.php', data=data)
        self.assertEquals({ 'error': True }, simplejson.loads(response.data))

        user = cpsdirector.get_user(TEST_USER_DATA['username'], TEST_USER_DATA['password'])
        self.assertEquals(120, user.credit)

        # Right sid and enough credit
        data = { 'sid': 1, 'decrement': 1, 'uid': 1 }
        response = self.app.post('/callback/decrementUserCredit.php', data=data)
        self.assertEquals({ 'error': False }, simplejson.loads(response.data))

        user = cpsdirector.get_user(TEST_USER_DATA['username'], TEST_USER_DATA['password'])
        self.assertEquals(119, user.credit)

    def test_proper_login(self):
        self.create_user()

        data = { 'username': TEST_USER_DATA['username'], 'password': TEST_USER_DATA['password'] }
        response = self.app.post('/login', data=data)
        self.assertEquals(200, response.status_code)

        user = simplejson.loads(response.data)
        self.assertEquals(TEST_USER_DATA['affiliation'], user['affiliation'])

    def test_login_unicode_encode_error(self):
        self.create_user()

        data = { 'username': TEST_USER_DATA['username'], 'password': 'pré' }
        response = self.app.post('/login', data=data)
        self.assertEquals(200, response.status_code)

        # the user does not exist, we expect /login to return false
        retval = simplejson.loads(response.data)
        self.failIf(retval)

    def test_getcerts(self):
        self.create_user()

        data = { 'username': TEST_USER_DATA['username'], 
                 'password': TEST_USER_DATA['password'] }

        response = self.app.post('/getcerts', data=data)
        self.assertEquals(200, response.status_code)
        self.assertEquals("application/zip", response.mimetype)

    def __test_new_user(self, data):
        response = self.app.post('/new_user', data=data)
        self.assertEquals(200, response.status_code)

        user = simplejson.loads(response.data)
        self.assertEquals(None, user.get('msg'))

        # /new_user returns the hashed password
        data['password'] = hashlib.md5(data['password']).hexdigest()

        for key, value in data.items():
            self.assertEquals(user[key], data[key])

    def test_new_user(self):
        data = TEST_USER_DATA
        self.__test_new_user(data)

    def test_new_user_unicode_encode_error(self):
        data = { 
            'username': 'namà', 'fname': 'Namé', 'lname': 'Surnàme',
                'email': 'test@example.org', 'affiliation': 'Our Affiliàtion', 
                    'password': 'properpàss', 'credit': 120 
        }
        self.__test_new_user(data)

    def test_new_user_duplicate_username(self):
        self.__test_new_user(TEST_USER_DATA)

        data = { 
            'username': TEST_USER_DATA['username'], 
            'fname': 'Firstname',
            'lname': 'Lastname',
            'email': 'test@example.org', 
            'affiliation': 'whatever',
            'password': TEST_USER_DATA['password'], 
            'credit': 50 
        }

        response = self.app.post('/new_user', data=data)
        self.assertEquals(200, response.status_code)

        user = simplejson.loads(response.data)
        self.assertEquals('Username "%s" already taken' % data['username'], user.get('msg'))

    def test_new_user_duplicate_email(self):
        self.__test_new_user(TEST_USER_DATA)

        data = { 
            'username': 'new_username', 
            'fname': 'Firstname',
            'lname': 'Lastname',
            'email': TEST_USER_DATA['email'], 
            'affiliation': 'whatever',
            'password': TEST_USER_DATA['password'], 
            'credit': 50 
        }

        response = self.app.post('/new_user', data=data)
        self.assertEquals(200, response.status_code)

        user = simplejson.loads(response.data)
        self.assertEquals('E-mail "%s" already registered' % data['email'], user.get('msg'))

    def test_new_user_missing_field(self):
        data = {
            'fname': 'Firstname',
            'lname': 'Lastname',
            'email': TEST_USER_DATA['email'], 
            'affiliation': 'whatever',
            'password': TEST_USER_DATA['password'], 
            'credit': 50 
        }

        response = self.app.post('/new_user', data=data)
        self.assertEquals(200, response.status_code)

        user = simplejson.loads(response.data)
        self.assertEquals('username is a required field', user.get('msg')) 

if __name__ == "__main__":
    unittest.main()
