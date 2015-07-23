# -*- coding: utf-8 -*-

"""
    conpaas.services.xec.manager.config
    ==========================================

    ConPaaS eXec Service manager config.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

memcache = None

import time


class AgentInfo(object):

    def __init__(self, id, ip, role):
        self.id = id
        self.ip = ip
        self.role = role
