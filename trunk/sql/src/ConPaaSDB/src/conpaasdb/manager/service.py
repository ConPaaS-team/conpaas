import inject

from jsonrpclib.jsonrpc import Fault

from conpaasdb.utils.service import ServiceBase, expose
from conpaasdb.common import PackageSettings
from conpaasdb.agent import AgentSettings
from conpaasdb.agent.client import AgentClient
from conpaasdb.common.recipes import deploy_agent
from conpaasdb.utils.log import get_logger_plus
from conpaasdb.adapters.mysql import MySQLSettings
from conpaasdb.manager import ConfigSettings
from conpaasdb.manager.deployment import AgentDeployment

logger, flog, mlog = get_logger_plus(__name__)

class Errors:
    UNKNOWN = 0
    AGENT_NOT_FOUND = 10
    IMAGE_NOT_FOUND = 20
    NETWORK_NOT_FOUND = 30
    MYSQL = 40
    
    ERRORS = {
        UNKNOWN: 'Unknown error',
        AGENT_NOT_FOUND: 'Agent not found',
        IMAGE_NOT_FOUND: 'Image not found',
        NETWORK_NOT_FOUND: 'Network not found',
        MYSQL: 'MySQL server error',
    }
    
    def get_error(self, error):
        return Fault(error, self.ERRORS[error])

class ManagerService(ServiceBase):
    deployment = inject.attr(AgentDeployment)
    
    @expose
    @mlog
    def agent_list(self):
        return [x.uuid for x in self.deployment.node_list()]
    
    @expose
    @mlog
    @inject.param('agent_settings', AgentSettings)
    @inject.param('package_settings', PackageSettings)
    @inject.param('mysql_settings', MySQLSettings)
    @inject.param('config_settings', ConfigSettings)
    def agent_create(self, agent_settings,
                package_settings, mysql_settings, config_settings):
        
        kwargs = dict(
            name = agent_settings.name,
            image_id = agent_settings.image_id,
            network_id = agent_settings.network_id,
        )
        
        node, host_settings = self.deployment.deploy(**kwargs)
        
        deploy_args = dict(
            config = config_settings.agent_config,
            package = package_settings.package,
            mysql_root_password = mysql_settings.password
        )
        
        with host_settings():
            deploy_agent(**deploy_args)
        
        return node.uuid
    
    @expose
    @mlog
    def agent_destroy(self, uuid):
        agent = self.deployment.get_node(uuid)
        
        return agent.destroy()
    
    @expose
    @mlog
    @inject.param('agent_settings', AgentSettings)
    def agent_state(self, uuid, agent_settings):
        agent = self.deployment.get_node(uuid)
        
        c = AgentClient(agent.public_ip[0], agent_settings.port)
        
        return c.server_state()
    
    @expose
    @mlog
    @inject.param('agent_settings', AgentSettings)
    def agent_info(self, uuid, agent_settings):
        agent = self.deployment.get_node(uuid)
        
        info = {
            'ip': agent.public_ip[0],
            'port': agent_settings.port
        }
        
        return info
    
    @expose
    @mlog
    def state(self):
        return True
