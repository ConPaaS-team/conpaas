'''
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
                 'user': 'oneadmin',
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
  
  def newInstance(self):
    n = self.nodes.pop()
    self.vms.append(n)
    return self.getVMInfo(n)
  
  def killInstance(self, vm_id):
    self.vms.remove(vm_id)
    self.nodes.append(vm_id)
    return True
