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
