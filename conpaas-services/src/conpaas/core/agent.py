# -*- coding: utf-8 -*-

"""
    conpaas.core.agent
    ====================

    ConPaaS core: service-independent agent code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""
import os.path

from conpaas.core.expose import expose
from conpaas.core.log import create_logger

from conpaas.core import ipop

from conpaas.core.ganglia import AgentGanglia

from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse
from conpaas.core.https.server import ConpaasRequestHandlerComponent

from conpaas.core.misc import file_get_contents
from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file

class BaseAgent(ConpaasRequestHandlerComponent):

    def __init__(self, config_parser):
        ConpaasRequestHandlerComponent.__init__(self)
        self.logger = create_logger(__name__)

        service_type = config_parser.get('agent', 'TYPE')
        user_id      = config_parser.get('agent', 'USER_ID')
        service_id   = config_parser.get('agent', 'SERVICE_ID')

        self.LOG_FILE = config_parser.get('agent', 'LOG_FILE')
        self.ROOT_DIR = '/root'

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
    def check_process(self, kwargs):
        """Check if agent process started - just return an empty response"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse()

    @expose('GET')
    def get_log(self, kwargs):
        """Return the contents of a logfile"""
        exp_params = [('filename', is_string, self.LOG_FILE)]
        try:
            filename = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        try:
            return HttpJsonResponse({'log': file_get_contents(filename)})
        except:
            return HttpErrorResponse("Failed to read log file: '%s'" % filename)

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
