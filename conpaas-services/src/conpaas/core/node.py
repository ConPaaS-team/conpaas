# -*- coding: utf-8 -*-

"""
    conpaas.core.node
    =================

    ConPaaS core: service node abstraction.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""
DEFAULT_WEIGHT = 100


class ServiceNode(object):
    """
    This class represents the abstraction of a node.
    """

    def __init__(self, vmid, ip, private_ip, cloud_name, weight_backend=DEFAULT_WEIGHT, role='node'):
        """
        Parameters
        ----------
        vmid : string
            virtual machine (VM) identifier provided by the cloud provider
        ip : string
            public IP address of the VM
        private_ip : string
            private IP address of the VM in a VPN
        cloud_name : string
            name of the cloud provider
        weight_backend : int
            weight of the VM representing the efficiency of this VM
        """
        self.id = "%s%s" % (cloud_name, vmid)
        self.vmid = vmid
        self.ip = ip
        self.private_ip = private_ip
        self.cloud_name = cloud_name
        self.weight_backend = weight_backend
        self.role = role
        self.volumes = []

    def __repr__(self):
        return 'ServiceNode(id=%s, ip=%s)' % (str(self.id), self.ip)

    def __cmp__(self, other):
        if self.id == other.id and self.cloud_name == other.cloud_name:
            return 0
        elif self.id < other.id:
            return -1
        else:
            return 1

    def as_libcloud_node(self):
        class Node:
            pass
        n = Node()
        n.id = self.vmid
        n.ip = self.ip
        return n

    def to_dict(self):
        return {'id':self.id, 
                'vmid':self.vmid, 
                'ip':self.ip, 
                'private_ip':self.private_ip, 
                'cloud_name':self.cloud_name,
                'weight_backend':self.weight_backend,
                'volumes':[volume.to_dict() for volume in self.volumes]
                }

    @staticmethod
    def from_dict(node):
        s = ServiceNode(node['vmid'], node['ip'],node['private_ip'],node['cloud_name'],node['weight_backend'])
        if 'volumes' in node and node['volumes']:
            for volume in node['volumes']:
                s.volumes += [ServiceVolume.from_dict(volume)]
        return s

class ServiceVolume(object):


    def __init__(self, vol_name, vol_size):
        self.vol_name=vol_name
        self.vol_size=vol_size
        self.vol_id=None
        self.vm_id=None
        self.dev_name=None
        self.cloud=None

    def to_dict(self):
        return {'vol_name':self.vol_name, 
                'vol_size':self.vol_size, 
                'vol_id':self.vol_id, 
                'vm_id':self.vm_id, 
                'dev_name':self.dev_name,
                'cloud':self.cloud
                }

    @staticmethod
    def from_dict(volume):
        v = ServiceVolume(volume['vol_name'], volume['vol_size'])
        v.vol_id=volume['vol_id'] if 'vol_id' in volume else None
        v.vm_id=volume['vm_id'] if 'vm_id' in volume else None
        v.dev_name=volume['dev_name'] if 'dev_name' in volume else None
        v.cloud=volume['cloud'] if 'cloud' in volume else None
        return v