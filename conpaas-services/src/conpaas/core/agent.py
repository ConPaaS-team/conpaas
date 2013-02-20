"""
Copyright (c) 2010-2013, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the Contrail consortium nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

from conpaas.core.expose import expose
from conpaas.core.log import create_logger

from conpaas.core import ipop

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
