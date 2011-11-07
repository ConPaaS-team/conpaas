import inject

from libcloud.compute.types import NodeState

from conpaasdb.agent import AgentSettings
from conpaasdb.agent.client import AgentClient
from conpaasdb.common.deployment import Deployment
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class AgentDeployment(Deployment):
    @mlog
    @inject.param('agent_settings', AgentSettings)
    def is_node(self, node, agent_settings):
        if (node.name == agent_settings.name
                and node.state == NodeState.RUNNING):
            
            try:
                c = AgentClient(node.public_ip[0], agent_settings.port)
                
                if c.server_state():
                    return True
            except:
                pass
