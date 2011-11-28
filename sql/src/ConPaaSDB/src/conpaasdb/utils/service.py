from functools import wraps

from SocketServer import ThreadingMixIn
from jsonrpclib import Fault
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer,\
    SimpleJSONRPCRequestHandler
from conpaasdb.utils.file import FileUploads

def expose(func):
    func.exposed = True
    
    @wraps(func)
    def decorator(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception, e:
            import traceback
            traceback.print_exc()
            return Fault(0, 'Unknown error: "%s"' % e)
    
    return decorator

class ServiceBase(object):
    def __init__(self):
        self._methods = [x for x in dir(self)
                                    if hasattr(getattr(self, x), 'exposed')]
    
    @expose
    def _list_methods(self):
        return self._methods[:]
    
    def register(self, server):
        for m in self._methods:
            server.register_function(getattr(self, m), m)



class UploadsRequestHandler(SimpleJSONRPCRequestHandler):
    def do_POST(self):
        if self.path.startswith('/upload/'):
            hash = self.path.split('/upload/')[1]
            
            fu = FileUploads()
            
            if fu.exists(hash):
                with fu.open(hash, 'w') as dest:
                    max_chunk_size = 10*1024*1024
                    remaining = int(self.headers["content-length"])
                    
                    while remaining:
                        chunk_size = min(remaining, max_chunk_size)
                        chunk = self.rfile.read(chunk_size)
                        remaining -= len(chunk)
                        dest.write(chunk)
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write('OK')
                self.wfile.flush()
                self.connection.shutdown(1)
                
                return
        
        SimpleJSONRPCRequestHandler.do_POST(self)

class SimpleThreadedJSONRPCServer(ThreadingMixIn, SimpleJSONRPCServer):
    daemon_threads = True
    
    def __init__(self, *args, **kwargs):
        SimpleJSONRPCServer.__init__(self,
            requestHandler=UploadsRequestHandler, *args, **kwargs)
