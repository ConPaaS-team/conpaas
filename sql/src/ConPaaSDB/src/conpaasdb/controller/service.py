import inject

from jsonrpclib.jsonrpc import Fault

from conpaasdb.utils.service import ServiceBase, expose
from conpaasdb.common import PackageSettings
from conpaasdb.utils.log import get_logger_plus
from conpaasdb.controller.deployment import ManagerDeployment
from conpaasdb.utils.injection import FreshScope, fresh_scope
from conpaasdb.utils.config import get_config
from conpaasdb.controller.config import ConfigSchema
from conpaasdb.common.injection import configure_package, configure_provider,\
    configure_manager
from conpaasdb.manager import ManagerSettings
from conpaasdb.utils.validators import valid_file
from conpaasdb.common.recipes import deploy_manager
from conpaasdb.manager.client import ManagerClient

logger, flog, mlog = get_logger_plus(__name__)

class Errors:
    UNKNOWN = 0
    
    ERRORS = {
        UNKNOWN: 'Unknown error',
    }
    
    def get_error(self, error):
        return Fault(error, self.ERRORS[error])

class ControllerService(ServiceBase):
    deployment = inject.attr(ManagerDeployment)
    
    @expose
    @mlog
    def __init__(self, config_file):
        self.injector = inject.create()
        self.injector.bind_scope(FreshScope, fresh_scope)
        
        self.config = get_config(config_file, ConfigSchema)
        
        self.configure()
    
    @expose
    @mlog
    def configure(self):
        configure_package(self.injector, self.config)
        configure_provider(self.injector, self.config)
        configure_manager(self.injector, self.config)
    
    @expose
    @mlog
    def manager_list(self):
        return [x.uuid for x in self.deployment.node_list()]
    
    @expose
    @mlog
    @inject.param('manager_settings', ManagerSettings)
    @inject.param('package_settings', PackageSettings)
    def manager_create(self, manager_config, agent_config,
                        manager_settings, package_settings):
        
        manager_config = valid_file(manager_config)
        agent_config = valid_file(agent_config)
        
        kwargs = dict(
            name = manager_settings.name,
            image_id = manager_settings.image_id,
            network_id = manager_settings.network_id,
        )
        
        node, host_settings = self.deployment.deploy(**kwargs)
        
        deploy_args = dict(
            manager_config = manager_config,
            agent_config = agent_config,
            package = package_settings.package
        )
        
        with host_settings():
            deploy_manager(**deploy_args)
        
        return node.uuid
    
    @expose
    @mlog
    def manager_destroy(self, uuid):
        manager = self.deployment.get_node(uuid)
        
        return manager.destroy()
    
    @expose
    @mlog
    @inject.param('manager_settings', ManagerSettings)
    def manager_info(self, uuid, manager_settings):
        manager = self.deployment.get_node(uuid)
        
        info = {
            'ip': manager.public_ip[0],
            'port': manager_settings.port
        }
        
        return info
    
    @expose
    @mlog
    @inject.param('manager_settings', ManagerSettings)
    def manager_state(self, uuid, manager_settings):
        manager = self.deployment.get_node(uuid)
        
        c = ManagerClient(manager.public_ip[0], manager_settings.port)
        
        return c.state()
