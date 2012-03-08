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


Created on Mar 11, 2011

@author: ielhelw
'''

class IaaSClient:
  def __init__(self, *args, **kwargs):
    self.nodes = [str(i) for i in range(1,100)]
    self.vms = []
  
  def listVMs(self):
    ret = {}
    for vm in self.vms:
      ret[vm] = {'id': str(vm),
                 'state': 'running',
                 'name': 'conpaasweb',
                 'ip': '192.168.0.%s' % str(vm)
      }
    return ret
  
  def getVMInfo(self, vm_id):
    vms = self.listVMs()
    if vm_id not in vms:
      print vms
      print type(vm_id), vm_id
      raise Exception('Failed to find vm id = "%s"' % str(vm_id))
    return vms[vm_id]
  
  def newInstances(self, count):
    instances = []
    ret = []
    for i in range(count):
      n = self.nodes.pop()
      instances.append(n)
      self.vms.append(n)
      ret.append(self.getVMInfo(n))
    return ret
  
  def killInstance(self, vm_id):
    self.vms.remove(vm_id)
    self.nodes.append(vm_id)
    return True
