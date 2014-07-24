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

from conpaas.core.https import client
from conpaas.core.misc import rlinput, string_to_hex, hex_to_string

class BaseClient(object):
    # Set this to the service type. eg: php, java, mysql...
    service_type = None

    def __init__(self):
        self.confdir = os.path.join(os.environ['HOME'], ".conpaas")

        if not os.path.isdir(self.confdir):
            os.mkdir(self.confdir, 0700)

        try:
            client.conpaas_init_ssl_ctx(self.confdir, 'user')
        except IOError:
            # We do not have the certificates yet. But we will get them soon: 
            # see getcerts()
            pass

    def write_conf_to_file(self, key, value):
        oldmask = os.umask(077)
        targetfile = open(os.path.join(self.confdir, key), 'w')
        targetfile.write(value)
        targetfile.close()
        os.umask(oldmask)

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

    # def callmanager(self, service_id, method, post, data, files=[]):
    #     """Call the manager API.

    #     'service_id': an integer holding the service id of the manager.
    #     'method': a string representing the API method name.
    #     'post': boolean value. True for POST method, false for GET.
    #     'data': a dictionary representing the data to be sent to the director.
    #     'files': sequence of (name, filename, value) tuples for data to be uploaded as files.

    #     callmanager loads the manager JSON response and returns it as a Python
    #     object.
    #     """
    #     service = self.service_dict(service_id)

    #     # File upload
    #     if files:
    #         res = client.https_post(service['manager'], 443, '/', data, files)
    #     # POST
    #     elif post:
    #         res = client.jsonrpc_post(service['manager'], 443, '/', method, data)
    #     # GET
    #     else:
    #         res = client.jsonrpc_get(service['manager'], 443, '/', method, data)

    #     if res[0] == 200:
    #         try:
    #             data = simplejson.loads(res[1])
    #         except simplejson.decoder.JSONDecodeError:
    #             # Not JSON, simply return what we got
    #             return res[1]

    #         return data.get('result', data)

    #     raise Exception, "Call to method %s on %s failed: %s.\nParams = %s" % (
    #         method, service['manager'], res[1], data)

    def callmanager(self, app_id, manager_id, method, post, data, files=[]):
        """Call the manager API.

        'service_id': an integer holding the service id of the manager.
        'method': a string representing the API method name.
        'post': boolean value. True for POST method, false for GET.
        'data': a dictionary representing the data to be sent to the director.
        'files': sequence of (name, filename, value) tuples for data to be uploaded as files.

        callmanager loads the manager JSON response and returns it as a Python
        object.
        """
        application = self.application_dict(app_id)
        

        # File upload
        if files:
            res = client.https_post(application['manager'], 443, '/', data, files)
        # POST
        elif post:
            res = client.jsonrpc_post(application['manager'], 443, '/', method, manager_id, data)
        # GET
        else:
            res = client.jsonrpc_get(application['manager'], 443, '/', method, manager_id, data)

        if res[0] == 200:
            try:
                data = simplejson.loads(res[1])
            except simplejson.decoder.JSONDecodeError:
                # Not JSON, simply return what we got
                return res[1]

            return data.get('result', data)

        raise Exception, "Call to method %s on %s failed: %s.\nParams = %s" % (
            method, application['manager'], res[1], data)

    def wait_for_state(self, sid, state):
        """Poll the state of service 'sid' till it matches 'state'."""
        res = { 'state': None }

        while res['state'] != state:
            try:
                res = self.callmanager(sid, "get_service_info", False, {})
            except (socket.error, urllib2.URLError):
                time.sleep(2)

    def createapp(self, app_name):
        print "Creating new application... "

        if self.callapi("createapp", True, { 'name': app_name }):
            print "done."
        else:
            print "failed."

        sys.stdout.flush()

    def create(self, service_type, cloud = None, application_id=None, initial_state='INIT'):
        data = {}
        if application_id is not None:
           data['appid'] = application_id
        if cloud is None:
            res = self.callapi("create/" + service_type, True, data)
        else:
            res = self.callapi("create/" + service_type + '/' + cloud, True, data)
        
        # data = {'service_type': service_type}
        # res  = self.callmanager(application_id, 0, "create_service", True, data)
        print res   
        
        #sid = res['sid']

        #print "Creating new manager on " + res['manager'] + "... ",
        #sys.stdout.flush()

        #self.wait_for_state(sid, initial_state)

        #print "done."
        #sys.stdout.flush()

    def start(self, service_id, app_id, cloud = "default"):
        #data = {'service_id': service_id, 'cloud': cloud}
        data = {'cloud': cloud}
        res = self.callmanager(app_id, service_id, "startup", True, data)
        if 'error' in res:
            print res['error']
        else:
            #print "Your service is starting up."
            print res

    def stop(self, service_id, app_id):
        print "Stopping service... "
        sys.stdout.flush()

        res = self.callmanager(service_id, "get_service_info", False, {})
        if res['state'] == "RUNNING":
            print "Service is in '%(state)s' state. Shutting it down." % res
            res = self.callmanager(service_id, "shutdown", True, {})
        else:
            print "Service is in '%(state)s' state. We can not stop it." % res

    def terminate(self, service_id, app_id):
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

    def rename(self, service_id, app_id, newname):
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

    def application_dict(self, app_id):
        """Return application's data as a dictionary"""
        applications = self.callapi("listapp", True, {})

        for application in applications:
            if str(application['aid']) == str(app_id):
                return application

        return []    

    def info(self, service_id, app_id):
        """Print service info. Clients should extend this method and print any
        additional information needed. Returns service_dict"""
        service = self.service_dict(service_id)
        for key, value in service.items():
            print "%s: %s" % (key, value)

        res = self.callmanager(service['sid'], "get_service_info", False, {})
        print "state:", res['state']

        for key, value in res.items():
            service[key] = value

        return service

    def logs(self, service_id, app_id):
        res = self.callmanager(service_id, "getLog", False, {})
        print res['log']

    def getcerts(self):
        res = self.callapi("getcerts", True, {}, use_certs=False)

        oldmask = os.umask(077)
        zipdata = zipfile.ZipFile(StringIO.StringIO(res))
        zipdata.extractall(path=self.confdir)
        client.conpaas_init_ssl_ctx(self.confdir, 'user')
        os.umask(oldmask)

        #for name in zipdata.namelist():
        #    print os.path.join(self.confdir, name)

    def credentials(self, trget, user, pwd):
        wrong_url = "E: Invalid target URL. Try with something like https://conpaas.example.com:5555\n"

        # Loop till  we get a valid URL
        while True:
            try:
                target = trget if trget else self.read_conf_value("target")
            except IOError:
                target = ''

            if not trget:
                target = rlinput('Enter the director URL: ', target)
            try:
                url = urlparse.urlparse(target)
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
                    endpoint=target, 
                    use_certs=False)

                # If this yields True we can be reasonably sure that the
                # provided URL is correct
                assert type(available_services) is list 
            except Exception, e:
                print "E: No ConPaaS Director at the provided URL: %s\n" % e
                continue

            # Valid URL
            self.write_conf_to_file('target', target)
            break

        while True:
            try:
                username = user if user else self.read_conf_value("username")
            except IOError:
                username = ''

            # Get the username
            if not user:
                username = rlinput('Enter your username: ', username)
            self.write_conf_to_file('username', username)

            # Get the password
            password = pwd if pwd else getpass.getpass('Enter your password: ')
            self.write_conf_to_file('password', password)

            if self.callapi('login', True, {}, use_certs=False):
                print "Authentication succeeded\n"
                self.getcerts()
                return

            print "Authentication failure\n"

    def available_services(self):
        return self.callapi('available_services', False, {})

    def available_clouds(self):
        return self.callapi('available_clouds', False, {})

    def available(self, types='services'):
        if types == 'clouds':
            for cloud in self.available_clouds():
                print cloud
        else:
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

    #TODO:genc this has been added an appid, update every call of it
    def check_service_id(self, sid, aid):
        # get requested service data
        for service in self.callapi("list", True, {}):
            if service['sid'] == sid and service['application_id'] == aid:
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

    
    def startapp(self, app_id):
        print "Starting application... "
        sys.stdout.flush()

        res = self.callapi("startapp/%s" % app_id, True, {})
        if res:
            print "done."
        else:
            print "failed."

    def deleteapp(self, app_id):
        print "Deleting application... "
        sys.stdout.flush()

        res = self.callapi("delete/%s" % app_id, True, {})
        if res:
            print "done."
        else:
            print "failed."

    def renameapp(self, appid, name):
        print "Renaming application... "
        sys.stdout.flush()

        res = self.callapi("renameapp/%s" % appid, True, { 'name' : name })
        if res:
            print "done."
        else:
            print "failed."

    def manifest(self, manifestfile, slofile, appfile):
        print "Uploading the manifest and slo... "
        sys.stdout.flush()

        f = open(manifestfile, 'r')
        manifest = f.read()
        f.close()

        f = open(slofile, 'r')
        slo = f.read()
        f.close()

        f = open(appfile, 'r')
        app_tar = f.read()
        f.close()
        
        app_tar = string_to_hex(app_tar) 
      
        res = self.callapi("upload_manifest", True, {'thread':True, 'manifest': manifest, 'slo':slo, 'app_tar':app_tar })
        #res = self.callapi("upload_manifest", True, {'manifest': manifest, 'slo':slo, 'app_tar':app_tar })
        if res:
            print "done."
        else:
            print "failed."

        print res    

    def download_manifest(self, appid):
        services = self.callapi("list/%s" % appid, True, {})
        for service in services:
            if service['type'] == 'xtreemfs':
                warning = """WARNING: this application contains an XtreemFS service
After downloading the manifest, the application will be deleted
Do you want to continue? (y/N): """

                sys.stderr.write(warning)
                sys.stderr.flush()

                confirm = ''
                confirm = rlinput('', confirm)
                if confirm != 'y':
                    sys.exit(1)

        res = self.callapi("download_manifest/%s" % appid, True, {})
        if res:
            print simplejson.dumps(res)
        else:
            print "E: Failed downloading manifest file"

    def listapp(self, doPrint=True):
        """Call the 'listapp' method on the director and print the results
        nicely"""
        apps = self.callapi("listapp", True, {})
        if apps:
            if doPrint:
                print self.prettytable(( 'aid', 'name', 'manager' ), apps)
            return [app['aid'] for app in apps]
        else:
            if doPrint:
                print "No existing applications"

    def list(self, appid):
        """Call the 'list' method on the director and print the results
        nicely"""
        if appid == 0:
            services = self.callapi("list", True, {})
        else:
            services = self.callapi("list/%s" % appid, True, {})

        if services:
            print self.prettytable(( 'type', 'sid', 'application_id', 'vmid', 
                                     'name', 'manager' ), services)
        else:
            print "No running services"

    def version(self):
        version = self.callapi("version", False, {})
        print "ConPaaS director version %s" % version

    def usage(self, service_id):
        """Print client usage. Extend it with your client commands"""
        print "Usage: %s COMMAND [params]" % sys.argv[0]
        print "COMMAND is one of the following"
        print
        print "    credentials                                     # set your ConPaaS credentials"
        print "    version                                         # show director's version"
        print "    listapp                                         # list all applications"
        print "    available                                       # list supported services"
        print "    clouds                                          # list available clouds"
        print "    list              [appid]                       # list running services under an application"
        print "    deleteapp         appid                         # delete an application"
        print "    createapp         appname                       # create a new application"
        print "    startapp          [appid]                       # start an application"
        print "    renameapp         appid       newname           # rename an application"
        print "    manifest          manifest    slo     app_tar   # upload a new manifest"
        print "    download_manifest appid                         # download an existing manifest"
        print "    create            servicetype [appid]           # create a new service [inside a specific application]"
        print "    start             serviceid   appid   [cloud]   # startup the given service [on a specific cloud]"
        print "    info              serviceid   appid             # get service details"
        print "    logs              serviceid   appid             # get service logs"
        print "    stop              serviceid   appid             # stop the specified service"
        print "    terminate         serviceid   appid             # delete the specified service"
        print "    rename            serviceid   appid   newname   # rename the specified service"
        print "    startup_script    serviceid   appid   filename  # upload a startup script"
        print "    usage             servicetype                   # show service-specific options"

    def main(self, argv):
        """What to do when invoked from the command line. Clients should extend
        this and add any client-specific argument. argv is sys.argv"""

        # We need at least one argument
        try:
            command = argv[1]
        except IndexError:
            self.usage(argv[0])
            sys.exit(0)

        if command == "version":
            return getattr(self, command)()

        # Service and application generic commands
        if command in ( "listapp", "createapp", "startapp","manifest",
                        "download_manifest", "list", "credentials", 
                        "available", "clouds", "create", "st_usage",
                        "deleteapp", "renameapp", "getcerts" ):

            if command == "st_usage":
                try:
                    # St_usage wants a service type. Check if we got one, and if
                    # it is acceptable.
                    service_type = argv[2]
                    if service_type not in self.available_services():
                        raise IndexError
                    # normal service usage
                    module = getattr(__import__('cps.' + service_type), service_type)
                    client = module.Client()
                    return getattr(client, 'usage')(service_type)
                except IndexError:
                    self.usage(argv[0])
                    sys.exit(0)

            if command == "create":
                try:
                    # Create wants a service type. Check if we got one, and if
                    # it is acceptable.
                    service_type = argv[2]
                    if service_type not in self.available_services():
                        raise IndexError

                    try:
                        appid = int(argv[3])
                        if appid not in self.listapp(False):
                            print "E: Unknown application id: %s" % appid
                            sys.exit(1)
                    except IndexError:
                        appid = None

                    cloud = None
                    if appid:
                        try:
                            cloud = argv[4]
                            if cloud not in self.available_clouds():
                                print "E: Unknown cloud: %s" % cloud
                                sys.exit(1)
                        except IndexError:
                            pass

                    # taskfarm-specific service creation
                    if service_type == 'taskfarm':
                        from cps.taskfarm import Client
                        return Client().create(service_type, cloud, appid)

                    # normal service creation
                    return getattr(self, command)(service_type, cloud, appid)
                except IndexError:
                    self.usage(argv[0])
                    sys.exit(0)

            if command == "createapp":
                appname = argv[2]
                return getattr(self, command)(appname)

            if command == "deleteapp":
                appid = argv[2]
                return getattr(self, command)(appid)

            if command == "startapp":
                appid = argv[2]
                return getattr(self, command)(appid)

            if command == "renameapp":
                appid = argv[2]
                name  = argv[3]
                return getattr(self, command)(appid, name)

            if command == "manifest":
                try:
                    # 'manifest' wants a filename type. Check if we got one,
                    # and if it is acceptable.
                    open(argv[2])
                    open(argv[3])
                    open(argv[4])
                    return getattr(self, command)(argv[2], argv[3], argv[4])
                except (IndexError, IOError):
                    self.usage(argv[0])
                    sys.exit(0)

            if command == "download_manifest":
                appid = argv[2]
                return getattr(self, command)(appid)

            if command == "credentials":
                target = user = pwd = ''
                if len(argv) == 5:
                    target = argv[2]
                    user = argv[3]
                    pwd = argv[4]
                return getattr(self, command)(target, user, pwd)

            if command == "list":
                if len(sys.argv) == 2:
                    appid = 0
                else:
                    appid = argv[2]
                return getattr(self, command)(appid)

            if command == "available":
                return getattr(self, command)('services')

            if command == "clouds":
                return getattr(self, 'available')('clouds')

            # We need no params, just call the method and leave
            return getattr(self, command)()

        # Service-specific commands
        # Commands requiring a service id. We want it to be an integer.
        try:
            sid = int(argv[2])
            aid = int(argv[2])
        except (ValueError):
            if command == "usage":
                self.main([ argv[0], 'st_usage', argv[2] ])
            else:
                self.usage(argv[0])
            sys.exit(0)
        except (IndexError):
            self.usage(argv[0])
            sys.exit(0)

        service_type = self.check_service_id(sid, aid)

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
            try:
                aid = int(argv[3])
            except (ValueError):
                if command == "usage":
                    self.main([ argv[0], 'st_usage', argv[2] ])
                else:
                    self.usage(argv[0])
                    sys.exit(0)
            except (IndexError):
                self.usage(argv[0])
                sys.exit(0)

            # Call the method 
            if command == "start":
                if len(sys.argv) == 4:
                    cloud = 'default'
                else:
                    cloud = argv[4]
                #return getattr(self, command)(sid, cloud)
                return getattr(client, command)(sid, aid, cloud)

            return getattr(client, command)(sid, aid)

        if command == "st_usage":
            return getattr(client, command)()

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
