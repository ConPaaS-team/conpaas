'''
Created on Jul 20, 2011

@author: ielhelw
'''

from conpaas.web.manager.server import DeploymentManager
from conpaas.web.manager.internal import InternalsBase, ManagerException
from conpaas.web.http import HttpJsonResponse, HttpErrorResponse



class FakeManagerInternals(InternalsBase):
  
  def __init__(self, memcache_in, iaas_in, code_repo, logfile):
    InternalsBase.__init__(self, memcache_in, iaas_in, code_repo, logfile)
    self.exposed_functions['GET']['get_service_info'] = self.get_service_info
    
  def _update_code(self, config, nodes): pass
  def _start_backend(self, config, nodes): pass
  def _stop_backend(self, config, nodes): pass
  def _start_proxy(self, config, nodes): pass
  def _update_proxy(self, config, nodes): pass
  def _stop_proxy(self, config, nodes): pass
  
  def get_service_info(self, kwargs):
    if len(kwargs) != 0:
      return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
    return HttpJsonResponse({'state': self._state_get(), 'type': 'FAKE'})


class FakeDeploymentManager(DeploymentManager):
  def __init__(self, *args, **kwargs):
    DeploymentManager.__init__(self, *args, **kwargs)
  def _create_fake_service(self):
    self.conpaas_implementation = FakeManagerInternals(
                            self.memcache,
                            self.iaas,
                            self.config_parser.get('manager', 'CODE_REPO'),
                            self.config_parser.get('manager', 'LOG_FILE'))

