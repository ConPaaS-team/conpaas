import fabric_threadsafe.patch

import inject
import argparse

from conpaasdb.utils.service import SimpleThreadedJSONRPCServer
from conpaasdb.agent.service import AgentService
from conpaasdb.utils.config import get_config
from conpaasdb.agent.config import ConfigSchema
from conpaasdb.utils.injection import FreshScope, fresh_scope
from conpaasdb.utils.log import get_logger_plus
from conpaasdb.common.injection import configure_mysql, configure_supervisor

logger, flog, mlog = get_logger_plus(__name__)

class Server(object):
    @mlog
    def __init__(self, bind, port, config_file):
        self.bind = bind
        self.port = port
        
        self.injector = inject.create()
        self.injector.bind_scope(FreshScope, fresh_scope)
        
        self.config = get_config(config_file, ConfigSchema)
        
        self.configure()
    
    @mlog
    def configure(self):
        configure_mysql(self.injector, self.config)
        configure_supervisor(self.injector, self.config)
    
    @mlog
    def run(self):
        print 'Starting MySQL agent server at %s:%d' % (self.bind, self.port)
        
        server = SimpleThreadedJSONRPCServer((self.bind, self.port))
        
        service = AgentService()
        service.register(server)
        
        server.serve_forever()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bind', default='0.0.0.0', help='Bind address')
    parser.add_argument('-p', '--port', default=60000, help='Bind port')
    parser.add_argument('-c', '--config', default='conpaasdb.conf')
    
    args = parser.parse_args()
    
    server = Server(args.bind, args.port, args.config)
    
    server.run()

if __name__ == '__main__':
    main()
