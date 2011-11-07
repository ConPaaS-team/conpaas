from conpaasdb.utils.client import ClientBase
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class ManagerClient(ClientBase):
    @mlog
    def agent_list(self):
        return self.service.agent_list()
    
    @mlog
    def agent_create(self):
        return self.service.agent_create()
    
    @mlog
    def agent_destroy(self, uuid):
        return self.service.agent_destroy(uuid)
    
    @mlog
    def agent_state(self, uuid):
        return self.service.agent_state(uuid)
    
    @mlog
    def agent_info(self, uuid):
        return self.service.agent_info(uuid)
    
    @mlog
    def state(self):
        return self.service.state()
