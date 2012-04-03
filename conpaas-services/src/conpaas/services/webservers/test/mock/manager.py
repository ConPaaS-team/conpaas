'''
Copyright (C) 2010-2011 Contrail consortium.

This file is part of ConPaaS, an integrated runtime environment 
for elastic cloud applications.

ConPaaS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ConPaaS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.


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

