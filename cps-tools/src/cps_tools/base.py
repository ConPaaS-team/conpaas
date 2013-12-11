import getpass
import httplib
import os
import simplejson
import socket
import sys
import time
import urllib
import urllib2

from conpaas.core.https import client


class HTTPMethod(object):
    GET, POST, DELETE = range(3)


class BaseClient(object):

    def __init__(self, logger):
        self.logger = logger
        self.confdir = os.path.join(os.environ['HOME'], ".conpaas")
        if not os.path.isdir(self.confdir):
            os.mkdir(self.confdir, 0700)
        try:
            client.conpaas_init_ssl_ctx(self.confdir, 'user')
        except IOError:
            # We do not have the certificates yet.
            pass

        self.username = None
        self.password = None
        self.director_url = None
        self.debug = False
        self.services = None

    def error(self, error_msg, error_code=1):
        """Log an error message and exit."""
        self.logger.error(error_msg)
        raise Exception(error_msg)

    def set_director_url(self, dir_url):
        if dir_url is None:
            self.director_url = None
            return

        list_scheme = dir_url.split('://')
        if len(list_scheme) == 1:
            # default scheme
            scheme = 'https'
        else:
            scheme = list_scheme[0]
        list_port = list_scheme[-1].split(':')
        if len(list_port) == 1:
            # default port
            port = '5555'
        else:
            port = list_port[-1]
        domain = list_port[0]
        rev_url = scheme + '://' + domain + ':' + port
        self.director_url = rev_url

    def set_config(self, director_url=None, username=None, password=None,
                   debug=False):
        self.set_director_url(director_url)
        self.username = username
        self.password = password
        self.debug = debug

    def _get_password(self):
        if self.password is None:
            return getpass.getpass('Enter your password: ')
        else:
            return self.password

    def wait_for_state(self, sid, states):
        """Poll the state of service 'sid' till it matches one of expected
        'states'."""
        res = {'state': None}

        while res['state'] not in states:
            try:
                res = self.call_manager_get(sid, "get_service_info")
            except (socket.error, urllib2.URLError):
                time.sleep(2)
        return res['state']

    def call_director_post(self, method, data=None, user_certs=True):
        return self.call_director(method, True, data, user_certs)

    def call_director_get(self, method, data=None, user_certs=True):
        return self.call_director(method, False, data, user_certs)

    def call_director(self, method, post, data=None, use_certs=True):
        """Call the director API.
        Loads the director JSON response and returns it as a Python object.
        If the returned data can not be decoded it is returned as it is.

        'method': a string representing the API method name.
        'post': boolean value. True for POST method, false for GET.
        'data': a dictionary representing the data to be sent to the director.

        TODO: use HTTPMethod.x instead of bool for post parameter...
        """
        if self.director_url is None:
            raise Exception("Cannot call the ConPaaS director:"
                            " the director URL address is not specified.")

        if self.username is None:
            raise Exception("Cannot call the ConPaaS director:"
                            " user name is not specified.")

        if data is None:
            data = {}

        data['username'] = self.username

        url = "%s/%s" % (self.director_url, method)

        if use_certs:
            opener = urllib2.build_opener(HTTPSClientAuthHandler(
                os.path.join(self.confdir, 'key.pem'),
                os.path.join(self.confdir, 'cert.pem')))
        else:
            opener = urllib2.build_opener(urllib2.HTTPSHandler())
            data['password'] = self._get_password()

        if self.debug:
            if 'password' in data:
                data_log = dict(data)
                # hiding password from log
                if data_log['password'] == '':
                    data_log['password'] = '<empty_password>'
                else:
                    data_log['password'] = '<hidden_password>'
            else:
                data_log = data
            self.logger.debug("Requesting %s with data %s." % (url, data_log))

        data = urllib.urlencode(data)

        try:
            if post:
                res = opener.open(url, data)
            else:
                url += "?" + data
                res = opener.open(url)
        except:
            ex = sys.exc_info()[1]
            self.error("Cannot contact the director at URL %s: %s"
                       % (self.director_url, ex))

        rawdata = res.read()

        try:
            res = simplejson.loads(rawdata)
            if type(res) is dict and 'error' in res:
                raise Exception(res['msg'] + " while calling %s" % method)

            return res
        except simplejson.decoder.JSONDecodeError:
            return rawdata

    def get_services(self, serv_type=None):
        if self.services is None:
            self.services = self.call_director_get('list')
        services = self.services
        # filter out services of unexpected type if a type is specified
        if serv_type is not None:
            services = [service for service in self.services
                        if service['type'] == serv_type]
        return services

    def service_dict(self, service_id):
        """Return service's data as a dictionary"""
        services = self.get_services()
        for service in services:
            if str(service['sid']) == str(service_id):
                #service.pop('state')
                return service
        return []

    def call_manager(self, service_id, method, post, data=None, files=None):
        """Call the manager API.
        Loads the manager JSON response and returns it as a Python object.

        'service_id': an integer holding the service id of the manager.
        'method': a string representing the API method name.
        'post': boolean value. True for POST method, false for GET.
        'data': a dictionary representing the data to be sent to the director.
        'files': sequence of (name, filename, value) tuples for data to be
                 uploaded as files.
        """
        service = self.service_dict(service_id)

        if data is None:
            data = {}
        if files is None:
            files = []

        # File upload
        if files:
            res = client.https_post(service['manager'], 443, '/', data, files)
        # POST
        elif post:
            res = client.jsonrpc_post(service['manager'], 443, '/', method, data)
        # GET
        else:
            res = client.jsonrpc_get(service['manager'], 443, '/', method, data)

        if res[0] == 200:
            try:
                data = simplejson.loads(res[1])
            except simplejson.decoder.JSONDecodeError:
                # Not JSON, simply return what we got
                return res[1]

            return data.get('result', data)

        raise Exception("Call to method %s on %s failed: %s.\nParams = %s" % (
            method, service['manager'], res[1], data))

    def call_manager_post(self, service_id, method, data=None, files=None):
        if files is None:
            files = []
        return self.call_manager(service_id, method, True, data, files)

    def call_manager_get(self, service_id, method, data=None, files=None):
        if files is None:
            files = []
        return self.call_manager(service_id, method, False, data, files)

    def prettytable(self, print_order, rows):
        if rows == []:
            return ""
        maxlens = {}

        fields = rows[0].keys()

        for field in fields:
            maxlens[field] = len(field)
            for row in rows:
                curlen = len(str(row[field]))
                if curlen > maxlens[field]:
                    maxlens[field] = curlen

        # Header
        headerstr = ["{%d:%d}" % (idx, maxlens[key])
                     for idx, key in enumerate(print_order)]

        output = " ".join(headerstr).format(*print_order)
        output += "\n" + "-" * (sum([maxlens[el] for el in print_order])
                                + len(print_order) - 1)

        # Rows
        rowstr = ["{%s:%d}" % (key, maxlens[key])
                  for idx, key in enumerate(print_order)]

        for row in rows:
            output += "\n" + " ".join(rowstr).format(**row)

        return output


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):

    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        return self.do_open(self.get_connection, req)

    def get_connection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)
