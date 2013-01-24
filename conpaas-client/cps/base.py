import os
import ssl
import sys
import time
import socket
import zipfile
import urllib
import urllib2
import httplib
import getpass
import urlparse
import StringIO
import simplejson

from conpaas.core import https

class BaseClient(object):
    # Set this to the service type. eg: php, java, mysql...
    service_type = None

    def __init__(self):
        self.confdir = os.path.join(os.environ['HOME'], ".conpaas")

        if not os.path.isdir(self.confdir):
            os.mkdir(self.confdir, 0700)

        try:
            https.client.conpaas_init_ssl_ctx(self.confdir, 'user')
        except IOError:
            # We do not have the certificates yet. But we will get them soon: 
            # see getcerts()
            pass

    def write_conf_to_file(self, key, value):
        targetfile = open(os.path.join(self.confdir, key), 'w')
        targetfile.write(value)
        targetfile.close()

    def read_conf_value(self, key):
        return open(os.path.join(self.confdir, key)).read()

    def __callapi_creds(self, method, post, data, endpoint, username='', password='', use_certs=True):
        url = "%s/%s" % (endpoint, method)
        data['username'] = username
        data['password'] = password
        data = urllib.urlencode(data)

        if use_certs:
            opener = urllib2.build_opener(HTTPSClientAuthHandler(
                os.path.join(self.confdir, 'key.pem'),
                os.path.join(self.confdir, 'cert.pem')))
        else:
            opener = urllib2.build_opener(urllib2.HTTPSHandler())

        if post:
            res = opener.open(url, data)
        else:
            url += "?" + data
            res = opener.open(url)

        rawdata = res.read()

        try:
            res = simplejson.loads(rawdata)
            if type(res) is dict and res.get('error') is True:
                raise Exception(res['msg'] + " while calling %s" % method)

            return res
        except simplejson.decoder.JSONDecodeError:
            return rawdata

    def callapi(self, method, post, data, use_certs=True):
        """Call the director API.

        'method': a string representing the API method name.
        'post': boolean value. True for POST method, false for GET.
        'data': a dictionary representing the data to be sent to the director.

        callapi loads the director JSON response and returns it as a Python
        object. If the returned data can not be decoded it is returned as it is.
        """
        try:
            endpoint = self.read_conf_value("target")
            username = self.read_conf_value("username")
            password = self.read_conf_value("password")
        except IOError:
            self.credentials()
            return self.callapi(method, post, data, use_certs)

        try:
            return self.__callapi_creds(method, post, data, endpoint, username, password, use_certs)
        except (ssl.SSLError, urllib2.URLError):
            print "E: Cannot perform the requested action.\nTry updating your client certificates with %s credentials" % sys.argv[0]
            sys.exit(1)

    def callmanager(self, service_id, method, post, data, files=[]):
        """Call the manager API.

        'service_id': an integer holding the service id of the manager.
        'method': a string representing the API method name.
        'post': boolean value. True for POST method, false for GET.
        'data': a dictionary representing the data to be sent to the director.
        'files': sequence of (name, filename, value) tuples for data to be uploaded as files.

        callmanager loads the manager JSON response and returns it as a Python
        object.
        """
        service = self.service_dict(service_id)

        # File upload
        if files:
            res = https.client.https_post(service['manager'], 443, '/', data, files)
        # POST
        elif post:
            res = https.client.jsonrpc_post(service['manager'], 443, '/', method, data)
        # GET
        else:
            res = https.client.jsonrpc_get(service['manager'], 443, '/', method, data)

        if res[0] == 200:
            data = simplejson.loads(res[1])
            return data.get('result', data)

        raise Exception, "Call to method %s on %s failed: %s.\nParams = %s" % (
            method, service['manager'], res[1], data)

    def wait_for_state(self, sid, state):
        """Poll the state of service 'sid' till it matches 'state'."""
        res = { 'state': None }

        while res['state'] != state:
            try:
                res = self.callmanager(sid, "get_service_info", False, {})
            except (socket.error, urllib2.URLError):
                time.sleep(2)

    def create(self, service_type, initial_state='INIT'):
        res = self.callapi("start/" + service_type, True, {})
        sid = res['sid']

        print "Creating new manager on " + res['manager'] + "... ",
        sys.stdout.flush()

        self.wait_for_state(sid, initial_state)

        print "done."
        sys.stdout.flush()

    def start(self, service_id):
        res = self.callmanager(service_id, "startup", True, {})
        if 'error' in res:
            print res['error']
        else:
            print "Your service is starting up.",

    def stop(self, service_id):
        print "Stopping service... "
        sys.stdout.flush()

        res = self.callmanager(service_id, "get_service_info", False, {})
        if res['state'] == "RUNNING":
            print "Service is in '%(state)s' state. Shutting it down." % res
            res = self.callmanager(service_id, "shutdown", True, {})
        else:
            print "Service is in '%(state)s' state. We can not stop it." % res

    def terminate(self, service_id):
        print "Terminating service... "
        sys.stdout.flush()

        res = self.callmanager(service_id, "get_service_info", False, {})
        if res['state'] not in ( "STOPPED", "INIT" ):
            print "Service is in '%s' state. We can not terminate it." % res['state']
            return

        res = self.callapi("stop/%s" % service_id, True, {})
        if res:
            print "done."
        else:
            print "failed."

    def rename(self, service_id, newname):
        print "Renaming service... "

        if self.callapi("rename/%s" % service_id, True, { 'name': newname }):
            print "done."
        else:
            print "failed."

    def service_dict(self, service_id):
        """Return service's data as a dictionary"""
        services = self.callapi("list", True, {})

        for service in services:
            if str(service['sid']) == str(service_id):
                service.pop('state')
                return service

        return []

    def info(self, service_id):
        """Print service info. Clients should extend this method and print any
        additional information needed. Returns service_dict"""
        service = self.service_dict(service_id)
        for key, value in service.items():
            print "%s: %s" % (key, value)

        res = self.callmanager(service['sid'], "get_service_info", False, {})
        print "state:", res['state']

        return service

    def logs(self, service_id):
        res = self.callmanager(service_id, "getLog", False, {})
        print res['log']

    def getcerts(self):
        res = self.callapi("getcerts", True, {}, use_certs=False)

        zipdata = zipfile.ZipFile(StringIO.StringIO(res))
        zipdata.extractall(path=self.confdir)
        https.client.conpaas_init_ssl_ctx(self.confdir, 'user')

        #for name in zipdata.namelist():
        #    print os.path.join(self.confdir, name)

    def credentials(self):
        wrong_url = "E: Invalid target URL. Try with something like https://conpaas.example.com:443\n"

        # Loop till  we get a valid URL
        while True:
            target_url = raw_input('Enter the director URL: ')
            try:
                url = urlparse.urlparse(target_url)
            except IndexError:
                print wrong_url
                continue

            if url.scheme != "https":
                print wrong_url
                continue

            # Check if a ConPaaS director is listening at the provided URL
            try:
                available_services = self.__callapi_creds(
                    method='available_services', 
                    post=False, 
                    data={}, 
                    endpoint=target_url, 
                    use_certs=False)

                # If this yields True we can be reasonably sure that the
                # provided URL is correct
                assert type(available_services) is list 
            except Exception, err:
                print "E: No ConPaaS Director at the provider URL\n"
                #raise err
                continue

            # Valid URL
            self.write_conf_to_file('target', target_url)
            break

        while True:
            # Get the username
            username = raw_input('Enter your username: ')
            self.write_conf_to_file('username', username)

            # Get the password
            password = getpass.getpass('Enter your password: ')
            self.write_conf_to_file('password', password)

            if self.callapi('login', True, {}, use_certs=False):
                print "Authentication succeeded\n"
                self.getcerts()
                return

            print "Authentication failure\n"

    def available_services(self):
        return self.callapi('available_services', True, {})

    def available(self):
        for service in self.available_services():
            print service

    def upload_startup_script(self, service_id, filename):
        contents = open(filename).read()

        files = [ ( 'script', filename, contents ) ]

        res = self.callmanager(service_id, "/", True, 
            { 'method': 'upload_startup_script', }, files)

        if 'error' in res:
            print res['error']
        else:
            print "Startup script uploaded correctly."

    def check_service_id(self, sid):
        # get requested service data
        for service in self.callapi("list", True, {}):
            if service['sid'] == sid:
                # return service type
                return service['type'].lower()

        print "E: cannot find service %s" % sid
        sys.exit(1)

    def prettytable(self, print_order, rows):
        maxlens = {}

        fields = rows[0].keys()

        for field in fields:
            maxlens[field] = len(field)
            for row in rows:
                curlen = len(str(row[field]))
                if curlen > maxlens[field]:
                    maxlens[field] = curlen 

        # Header
        headerstr = [ "{%d:%d}" % (idx, maxlens[key]) 
            for idx, key in enumerate(print_order) ]

        output = " ".join(headerstr).format(*print_order)
        output += "\n" + "-" * (sum([ maxlens[el] for el in print_order ]) 
            + len(print_order) - 1)

        # Rows
        rowstr = [ "{%s:%d}" % (key, maxlens[key]) 
            for idx, key in enumerate(print_order) ]

        for row in rows:
            output += "\n" + " ".join(rowstr).format(**row)

        return output

    def list(self):
        """Call the 'list' method on the director and print the results
        nicely"""
        services = self.callapi("list", True, {})
        if services:
            print self.prettytable(( 'type', 'sid', 'vmid', 
                                     'name', 'manager' ), services)
        else:
            print "No running services"

    def usage(self, service_id):
        """Print client usage. Extend it with your client commands"""
        print "Usage: %s COMMAND [params]" % sys.argv[0]
        print "COMMAND is one of the following"
        print
        print "    credentials                           # set your ConPaaS credentials"
        print "    list                                  # list running services" 
        print "    available                             # list supported services" 
        print "    create            servicetype         # create a new service"
        print "    start             serviceid           # startup the specified service"
        print "    info              serviceid           # get service details"
        print "    logs              serviceid           # get service logs"
        print "    stop              serviceid           # stop the specified service"
        print "    terminate         serviceid           # delete the specified service"
        print "    rename            serviceid newname   # rename the specified service"
        print "    startup_script    serviceid filename  # upload a startup script"
        print "    usage             serviceid           # show service-specific options"
    
    def main(self, argv):
        """What to do when invoked from the command line. Clients should extend
        this and add any client-specific argument. argv is sys.argv"""

        # We need at least one argument
        try:
            command = argv[1]
        except IndexError:
            self.usage(argv[0])
            sys.exit(0)

        # Service-generic commands
        if command in ( "list", "credentials", "available", "create" ):
            
            if command == "create":
                try:
                    # Create wants a service type. Check if we got one, and if
                    # it is acceptable.
                    service_type = argv[2]
                    if service_type not in self.available_services():
                        raise IndexError

                    module = getattr(__import__('cps.' + service_type), service_type)
                    client = module.Client()
                    # Create the service and leave (if the client does not have a specific create method, the generic create is taken automagically)
                    return client.create(service_type)
                except IndexError:
                    self.usage(argv[0])
                    sys.exit(0)

            # We need no params, just call the method and leave
            return getattr(self, command)()

        # Service-specific commands
        # Commands requiring a service id. We want it to be an integer.
        try:
            sid = int(argv[2])
        except (IndexError, ValueError):
            self.usage(argv[0])
            sys.exit(0)

        service_type = self.check_service_id(sid)

        if command == "startup_script":
            try:
                # startup_script wants a filename type. Check if we got
                # one, and if it is acceptable.
                open(argv[3])
                return self.upload_startup_script(sid, argv[3])
            except (IndexError, IOError):
                self.usage(argv[0])
                sys.exit(0)

        if command == "rename":
            try:
                return self.rename(sid, argv[3])
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

        module = getattr(__import__('cps.' + service_type), service_type)
        client = module.Client()

        if command == "help":
            # We have all been there
            command = "usage"

        if command in ( 'start', 'stop', 'terminate', 'info', 'logs', 'usage' ):
            # Call the method 
            return getattr(client, command)(sid)

        client.main(sys.argv)

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)
