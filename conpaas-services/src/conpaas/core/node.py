# -*- coding: utf-8 -*-

"""
    conpaas.core.node
    =================

    ConPaaS core: service node abstraction.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""
DEFAULT_WEIGHT = 100

class ServiceNode(object):
    '''
        This class represents the abstraction of a node. A basic node is
        represented by a vmid and an ip address. This class can be extented
        with more information about the node, specific to each service.

    '''

    def __init__(self, vmid, ip, private_ip, cloud_name, weightBackend=DEFAULT_WEIGHT):
        self.id = vmid
        self.ip = ip
        self.private_ip = private_ip
        self.cloud_name = cloud_name
        self.weightBackend = weightBackend

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
        n.id = self.id
        n.ip = self.ip
        return n
