'''
Created on Jul 4, 2013

@author: Vlad
'''
from conpaas.core.node import ServiceNode

class Worker(ServiceNode):
    
    def __init__(self, vmid, ip, private_ip, cloud_name, ht_type):
        super(Worker,self).__init__(vmid, ip, private_ip, cloud_name)
        self.type = ht_type
        
    def set_running_task(self, task):
        self.task = task
        
    def get_running_task(self):
        return self.task
    
    def __str__(self):
        return 'Worker: ip=' + self.ip + ' , type=' + self.type + ' , cloud=' + self.cloud_name

    def __repr__(self):
        return 'Worker: ip=' + self.ip + ' , type=' + self.type + ' , cloud=' + self.cloud_name
