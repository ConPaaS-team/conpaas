# -*- coding: utf-8 -*-

"""
    conpaas.core.agent
    ====================

    ConPaaS core: service-independent agent code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from conpaas.core.expose import expose
from conpaas.core.log import create_logger

from conpaas.core import ipop

from conpaas.core.ganglia import AgentGanglia

from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse
                          
class BaseAgent(object):
    """Agent class with the following exposed methods:

    check_agent_process() -- GET
    """

    def __init__(self, config_parser):
        self.logger = create_logger(__name__)    
        self.state = 'INIT'

        service_type = config_parser.get('agent', 'TYPE')
        user_id      = config_parser.get('agent', 'USER_ID')
        service_id   = config_parser.get('agent', 'SERVICE_ID')

        self.logger.info("'%s' agent started (uid=%s, sid=%s)" % (
            service_type, user_id, service_id))

        # IPOP setup
        ipop.configure_conpaas_node(config_parser)
    
        # Ganglia setup
        self.ganglia = AgentGanglia(config_parser)

        try:
            self.ganglia.configure()
        except Exception, err:
            self.logger.exception('Error configuring Ganglia: %s' % err)
            # Something went wrong while configuring Ganglia. We do not want
            # our agent to think it can be used
            self.ganglia = None
            return

        err = self.ganglia.start()
        if err:
            self.logger.exception(err)
            # Same as above, our agent can not use Ganglia
            self.ganglia = None
        else:
            self.logger.info('Ganglia started successfully')

    @expose('GET')
    def check_agent_process(self, kwargs):
        """Check if agent process started - just return an empty response"""
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        return HttpJsonResponse()

class AgentException(Exception):

    E_CONFIG_NOT_EXIST = 0
    E_CONFIG_EXISTS = 1
    E_CONFIG_READ_FAILED = 2
    E_CONFIG_CORRUPT = 3
    E_CONFIG_COMMIT_FAILED = 4
    E_ARGS_INVALID = 5
    E_ARGS_UNEXPECTED = 6
    E_ARGS_MISSING = 7
    E_UNKNOWN = 8

    E_STRINGS = [
      'No configuration exists',
      'Configuration already exists',
      'Failed to read configuration state of %s from %s', # 2 params
      'Configuration is corrupted',
      'Failed to commit configuration',
      'Invalid arguments',
      'Unexpected arguments %s', # 1 param (a list)
      'Missing argument "%s"', # 1 param
      'Unknown error',
    ]

    def __init__(self, code, *args, **kwargs):
        self.code = code
        self.args = args
        if 'detail' in kwargs:
            self.message = '%s DETAIL:%s' % ((self.E_STRINGS[code] % args), 
                                             str(kwargs['detail']))
        else:
            self.message = self.E_STRINGS[code] % args
