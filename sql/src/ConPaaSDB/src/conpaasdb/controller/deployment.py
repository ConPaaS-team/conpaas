import inject

from libcloud.compute.types import NodeState

from conpaasdb.manager import ManagerSettings
from conpaasdb.manager.client import ManagerClient
from conpaasdb.common.deployment import Deployment
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class ManagerDeployment(Deployment):
    @mlog
    @inject.param('manager_settings', ManagerSettings)
    def is_node(self, node, manager_settings):
        if (node.name == manager_settings.name
                and node.state == NodeState.RUNNING):
            
            try:
                c = ManagerClient(node.public_ip[0], manager_settings.port)
                
                if c.state():
                    return True
            except:
                pass
