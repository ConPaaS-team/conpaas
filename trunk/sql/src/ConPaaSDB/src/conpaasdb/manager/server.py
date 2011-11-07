import fabric_threadsafe.patch

import inject
import argparse

from conpaasdb.utils.service import SimpleThreadedJSONRPCServer
from conpaasdb.utils.config import get_config
from conpaasdb.utils.injection import FreshScope, fresh_scope
from conpaasdb.manager.config import ConfigSchema
from conpaasdb.manager.service import ManagerService
from conpaasdb.utils.log import get_logger_plus
from conpaasdb.common.injection import configure_package, configure_provider,\
    configure_agent
from conpaasdb.adapters.mysql import MySQLSettings
from conpaasdb.manager import ConfigSettings

logger, flog, mlog = get_logger_plus(__name__)

class Server(object):
    @mlog
    def __init__(self, bind, port, config, agent_config):
        self.bind = bind
        self.port = port
        self.agent_config = agent_config
        
        self.injector = inject.create()
        self.injector.bind_scope(FreshScope, fresh_scope)
        
        self.config = get_config(config, ConfigSchema)
        
        self.configure()
    
    @mlog
    def configure(self):
        configure_package(self.injector, self.config)
        configure_provider(self.injector, self.config)
        configure_agent(self.injector, self.config)
        
        mysql_settings = MySQLSettings()
        mysql_settings.password = self.config.mysql.password
        self.injector.bind(MySQLSettings, mysql_settings)
        
        config_settings = ConfigSettings()
        config_settings.agent_config = self.agent_config
        self.injector.bind(ConfigSettings, config_settings)
    
    @mlog
    def run(self):
        print 'Starting MySQL manager server at %s:%d' % (self.bind, self.port)
        
        server = SimpleThreadedJSONRPCServer((self.bind, self.port))
        
        service = ManagerService()
        service.register(server)
        
        server.serve_forever()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bind', default='0.0.0.0', help='Bind address')
    parser.add_argument('-p', '--port', default=60000, help='Bind port')
    parser.add_argument('-c', '--config', default='manager.conf')
    parser.add_argument('-a', '--agent-config', default='agent.conf')
    
    args = vars(parser.parse_args())
    
    server = Server(**args)
    
    server.run()

if __name__ == '__main__':
    main()
