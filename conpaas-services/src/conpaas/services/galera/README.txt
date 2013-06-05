ConPaaSGalera - pydev project for Contrail Galera MySQL Server. Project can easily be imported into eclipse environment.

Author: miha.stopar@xlab.si

Simplified testing
==================

1. Generate VM with galera-* script inside create_vm folder.
2. Start VM inside VirtualBox (with Bridged Adapter).
3. Modify /etc/network/interfaces to use dhcp instead of static. Restart networking.
4. Download ConPaaS sources - src folder inside conpaas-services. Include this folder in PYTHONPATH. If you want to test it 
without SSL certificates - temporarily modify code inside https/server.py and https/client.py to work without certificates:

--- client.py	(revision 4712)
+++ client.py	(working copy)
@@ -122,16 +122,17 @@
     """
 
     def __init__(self, host, port=None, strict=None, **ssl):
-        try:
-            self.ssl_ctx = ssl['ssl_context']
-            assert isinstance(self.ssl_ctx, SSL.Context), self.ssl_ctx
-        except KeyError:
-            self.ssl_ctx = SSL.Context(SSL.SSLv23_METHOD)
+        #try:
+        #    self.ssl_ctx = ssl['ssl_context']
+        #    assert isinstance(self.ssl_ctx, SSL.Context), self.ssl_ctx
+        #except KeyError:
+        #    self.ssl_ctx = SSL.Context(SSL.SSLv23_METHOD)
         HTTPConnection.__init__(self, host, port, strict)
 
     def connect(self):
         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
-        self.sock = SSLConnectionWrapper(self.ssl_ctx, sock)
+        #self.sock = SSLConnectionWrapper(self.ssl_ctx, sock)
+        self.sock = sock
         self.sock.connect((self.host, self.port))


--- server.py	(revision 4712)
+++ server.py	(working copy)
@@ -110,14 +110,15 @@
 
 
 class HTTPSServer(HTTPServer):
-    def __init__(self, server_address, handler, ctx):
+    #def __init__(self, server_address, handler, ctx):
+    def __init__(self, server_address, handler):
         BaseServer.__init__(self, server_address, handler)
-        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
-                                                        self.socket_type))
+        #self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
+        #                                                self.socket_type))
+        self.socket = socket.socket(self.address_family, self.socket_type)
         self.server_bind()
         self.server_activate()
 
-
 class ConpaasSecureServer(HTTPSServer):
     '''
     HTTPS server for ConPaaS.
@@ -128,7 +129,7 @@
     '''
 
     def __init__(self, server_address, config_parser, role, **kwargs):
-        log.init(config_parser.get(role, 'LOG_FILE'))
+        #log.init(config_parser.get(role, 'LOG_FILE'))
         self.config_parser = config_parser
         self.callback_dict = {'GET': {}, 'POST': {}, 'UPLOAD': {}}
 
@@ -138,7 +139,8 @@
             from conpaas.core.services import agent_services as services
 
         # Instantiate the requested service class
-        service_type = config_parser.get(role, 'TYPE')
+        #service_type = config_parser.get(role, 'TYPE')
+        service_type = "galera"
         try:
             module = __import__(services[service_type]['module'], 
                                 globals(), locals(), ['*'])
@@ -165,9 +167,10 @@
                             exposed_functions[http_method][func_name])
 
         # Start the HTTPS server
-        ctx = self._conpaas_init_ssl_ctx(role,
-                                    config_parser.get(role, 'CERT_DIR'), SSL.SSLv23_METHOD)
-        HTTPSServer.__init__(self, server_address, ConpaasRequestHandler, ctx)
+        #ctx = self._conpaas_init_ssl_ctx(role,
+        #                            config_parser.get(role, 'CERT_DIR'), SSL.SSLv23_METHOD)
+        #HTTPSServer.__init__(self, server_address, ConpaasRequestHandler, ctx)
+        HTTPSServer.__init__(self, server_address, ConpaasRequestHandler)
 
     def _register_method(self, http_method, func_name, callback):
         self.callback_dict[http_method][func_name] = callback
@@ -463,3 +466,24 @@
         ret += '</table></p>'
         return ret

5. Put agent.cfg in src folder with the following content:

[agent]

#Filled in by the manager
TYPE = agent
USER_ID = 1
SERVICE_ID = 1
APP_ID = 1

MY_IP= 192.168.1.20


LOG_FILE = /home/miha/Desktop/agent.log
ETC = 
CERT_DIR =
VAR_TMP = 
VAR_CACHE = 
VAR_RUN = 
CONPAAS_HOME = /home/miha/projects/conpaas

# Will be filled in by the manager
IP_WHITE_LIST = 

IPOP_BASE_NAMESPACE = $IPOP_BASE_NAMESPACE

# The following will be added only if IPOP has to be used
# IPOP_BASE_IP = 
# IPOP_NETMASK = 
# IPOP_IP_ADDRESS = 

MYSQLDUMP_PATH=/tmp/contrail_dbdump.db

[MySQL_root_connection]
location=localhost
# Filled in by the manager
username=musername
password=mpassword  

[MySQL_configuration]
my_cnf_file=/etc/mysql/my.cnf
path_mysql_ssr=/etc/init.d/mysql

[Galera_configuration]
wsrep_file=/etc/mysql/conf.d/wsrep.cnf
wsrep_sst_username=sst
wsrep_sst_password=sstpasswd
wsrep_provider=/usr/lib/galera/libgalera_smm.so
wsrep_sst_method=rsync

NOTE: Change MY_IP to be the IP of this VM.

6. Repeat steps 2 - 5 for a second VM.
7. Add the following snippet into https/server.py on both machines:

+if __name__ == "__main__":
+    from conpaas.core import https
+    config_file = "/root/con/agent.cfg"
+    #config_file = "/home/miha/Desktop/agent.cfg"
+    import ConfigParser
+    config = ConfigParser.ConfigParser()
+    config.readfp(open(config_file))
+    d = https.server.ConpaasSecureServer(("0.0.0.0", 4443), config, "agent")
+    #d = https.server.ConpaasSecureServer(("0.0.0.0", 4443), config, "manager")
+    d.serve_forever()
+
+
+    # example call: https.client.jsonrpc_post("192.168.1.16", 4443, "/", 'create_master', params={'master_server_id':0})
+    # example call: https.client.jsonrpc_post("192.168.1.16", 4443, "/", 'create_slave', params={'slaves':{0:{'ip':'192.168.1.5', 'port':4443}}})

8. Run https/server.py on both machines.
9. Execute the following command in Python console (replace with IP of the first VM):

https.client.jsonrpc_post("192.168.1.16", 4443, "/", 'create_master', params={'master_server_id':0})

10. Execute (use first VM's IP as the first parameter, second VM's IP for the parameter in 'slaves'):

https.client.jsonrpc_post("192.168.1.16", 4443, "/", 'create_slave', params={'slaves':{0:{'ip':'192.168.1.5', 'port':4443}}})







