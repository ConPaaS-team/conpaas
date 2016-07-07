import getpass
import os
import simplejson
import socket
import sys
import time
import urllib2
import urlparse
import traceback

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

    def wait_for_app_state(self, aid, states):
        """Poll the state of application 'aid' till it matches one of expected 'states'."""
        state = None
        while state not in states:
            try:
                state = self.application_dict(aid)['status']
            except (socket.error, urllib2.URLError):
                time.sleep(2)
        return state

    def wait_for_service_state(self, aid, sid, states):
        """Poll the state of service 'sid' till it matches one of expected 'states'."""
        res = { 'state' : None }
        while res['state'] not in states:
            try:
                res = self.call_manager_get(aid, sid, "get_service_info")
            except (socket.error, urllib2.URLError):
                time.sleep(2)
        return res['state']

    def call_director_post(self, method, data=None, use_certs=True):
        return self.call_director(method, True, data, use_certs)

    def call_director_get(self, method, data=None, use_certs=True):
        return self.call_director(method, False, data, use_certs)

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

        if use_certs:
            # If certificates are used, the ssl context should already have
            # been initialized with the user's certificates in __init__
            if not client.is_ssl_ctx_initialized():
                raise Exception("Cannot call the ConPaaS director:"
                                " user certificates are not present.\n"
                                "Try to run 'cps-user get_certificate'"
                                " first.")

            if self.debug:
                self.logger.debug("User certificates are present and will be used.")
        else:
            # If not, we need to send the user's password and initialize the
            # ssl context with one that does not use certificates
            data['password'] = self._get_password()
            client.conpaas_init_ssl_ctx_no_certs()

            if self.debug:
                self.logger.debug("User certificates will NOT be used.")

        url = "%s/%s" % (self.director_url, method)

        if self.debug:
            if 'password' in data:
                data_log = dict(data)
                # hiding password from log
                if data_log['password'] == '':
                    data_log['password'] = '<empty>'
                else:
                    data_log['password'] = '<hidden>'
            else:
                data_log = data
            self.logger.info("Requesting '%s' with data %s." % (url, data_log))

        parsed_url = urlparse.urlparse(self.director_url)
        try:
            if post:
                status, body = client.https_post(parsed_url.hostname,
                                                 parsed_url.port or 443,
                                                 url,
                                                 data)
            else:
                status, body = client.https_get(parsed_url.hostname,
                                                parsed_url.port or 443,
                                                url,
                                                data)
        except:
            if self.debug:
                traceback.print_exc()
            ex = sys.exc_info()[1]
            raise Exception("Cannot contact the director at URL '%s': %s"
                            % (url, ex))

        if status != 200:
            raise Exception("Call to method '%s' on '%s' failed: HTTP status %s.\n"
                            "Params = %s" % (method, url, status, data))

        try:
            res = simplejson.loads(body)
        except simplejson.decoder.JSONDecodeError:
            # Not JSON, simply return what we got
            if self.debug:
                self.logger.info("Call succeeded, result is not json.")
            return body

        if type(res) is dict and 'error' in res:
            if self.debug:
                self.logger.info("Call succeeded, result contains an error")
            raise Exception(res['error'])

        self.logger.info("Call succeeded, result is: %s" % res)
        return res

    def get_services(self, app_id=None, serv_type=None):
        if self.services is None:
            self.services = self.call_director_get('list')
        services = self.services

        # filter out services from different apps if an app is specified
        if app_id is not None:
            services = [service for service in services
                        if service['service']['application_id'] == app_id]

        # filter out services of unexpected type if a type is specified
        if serv_type is not None:
            services = [service for service in services
                        if service['service']['type'] == serv_type]

        return services

    def service_dict(self, app_id, service_id):
        """Return service's data as a dictionary"""
        services = self.get_services(app_id)
        for service in services:
            if str(service['service']['sid']) == str(service_id):
                #service.pop('state')
                return service
        return []

    def application_dict(self, app_id):
        """Return application's data as a dictionary"""
        applications = self.call_director_get("listapp")

        for application in applications:
            if str(application['aid']) == str(app_id):
                return application
        return None

    def call_manager(self, app_id, service_id, method, post, data=None, files=None):
        """Call the manager API.
        Loads the manager JSON response and returns it as a Python object.

        'service_id': an integer holding the service id of the manager.
        'method': a string representing the API method name.
        'post': boolean value. True for POST method, false for GET.
        'data': a dictionary representing the data to be sent to the director.
        'files': sequence of (name, filename, value) tuples for data to be
                 uploaded as files.
        """

        application = self.application_dict(app_id)

        if application['manager'] is None:
            raise Exception('Application %s has not started. Try to start it first.'
                            % app_id)

        if data is None:
            data = {}
        if files is None:
            files = []

        # Certificates are always used, the ssl context should already have
        # been initialized with the user's certificates in __init__
        if not client.is_ssl_ctx_initialized():
            raise Exception("Cannot call the manager:"
                            " user certificates are not present.\n"
                            "Try to run 'cps-user get_certificate'"
                            " first.")
        if self.debug:
            self.logger.debug("User certificates are present and will be used.")
            url = "https://%s/" % application['manager']
            self.logger.info("Requesting '%s' with aid %s, sid %s, method '%s', "
                              "data %s and %s files." %
                              (url, app_id, service_id, method, data, len(files)))

        try:
            # File upload
            if files:
                status, body = client.https_post(application['manager'], 443,
                                        '/', data, files)
            # POST
            elif post:
                status, body = client.jsonrpc_post(application['manager'], 443,
                                        '/', method, service_id, data)
            # GET
            else:
                status, body = client.jsonrpc_get(application['manager'], 443,
                                        '/', method, service_id, data)
        except:
            if self.debug:
                traceback.print_exc()
            ex = sys.exc_info()[1]
            raise Exception("Cannot contact the manager at URL '%s': %s"
                            % (url, ex))

        if status != 200:
            raise Exception("Call to method '%s' on '%s' failed: HTTP status %s.\n"
                            "Params = %s" % (method, application['manager'],
                            status, data))

        try:
            data = simplejson.loads(body)
        except simplejson.decoder.JSONDecodeError:
            # Not JSON, simply return what we got
            if self.debug:
                self.logger.info("Call succeeded, result is not json.")
            return body

        res = data.get('result', data)
        if type(res) is dict and 'error' in res:
            if self.debug:
                self.logger.info("Call succeeded, result contains an error")
            raise Exception(res['error'])

        self.logger.info("Call succeeded, result is: %s" % res)
        return res

    def call_manager_post(self, app_id, service_id, method, data=None, files=None):
        if files is None:
            files = []
        return self.call_manager(app_id, service_id, method, True, data, files)

    def call_manager_get(self, app_id, service_id, method, data=None, files=None):
        if files is None:
            files = []
        return self.call_manager(app_id, service_id, method, False, data, files)

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
