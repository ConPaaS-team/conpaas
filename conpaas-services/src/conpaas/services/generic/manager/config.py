# -*- coding: utf-8 -*-

"""
    conpaas.services.xec.manager.config
    ==========================================

    ConPaaS eXec Service manager config.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import time

class CodeVersion(object):

    def __init__(self, id, filename, atype, description=''):
        self.id = id
        self.filename = filename
        self.type = atype
        self.description = description
        self.timestamp = time.time()

    def __repr__(self):
        return 'CodeVersion(id=%s, filename=%s)' % (self.id, self.filename)

    def __cmp__(self, other):
        if self.id == other.id:
            return 0
        elif self.id < other.id:
            return -1
        else:
            return 1

class ServiceConfiguration(object):

    '''Representation of the deployment configuration'''

    def __init__(self):
        self.codeVersions = {}
        self.currentCodeVersion = None
#        self.serviceNodes = {}
        self.volumes = {}

class AgentInfo(object):

    def __init__(self, id, ip, role):
        self.id = id
        self.ip = ip
        self.role = role

class VolumeInfo(object):

    def __init__(self, volumeName, volumeId, volumeSize, agentId, devName):
        self.volumeName = volumeName
        self.volumeId = volumeId
        self.volumeSize = volumeSize
        self.agentId = agentId
        self.devName = devName
