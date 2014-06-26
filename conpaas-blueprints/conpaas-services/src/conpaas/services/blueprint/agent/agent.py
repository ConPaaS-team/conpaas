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

from subprocess import Popen

from conpaas.core.expose import expose
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse
from conpaas.core.agent import BaseAgent

class BluePrintAgent(BaseAgent):
    """Agent class with the following exposed methods:

    check_agent_process() -- GET
    create_hub(my_ip) -- POST
    create_node(my_ip, hub_ip) -- POST
    """
    def __init__(self, config_parser, **kwargs): 
        """Initialize BluePrint Agent.
  
        'config_parser' represents the agent config file.
        **kwargs holds anything that can't be sent in config_parser.
        """
        BaseAgent.__init__(self, config_parser)


    @expose('POST')
    def create_node(self, kwargs):
        self.logger.info('Node starting up')

        self.state = 'ADAPTING'

        self.my_ip_address = kwargs['my_ip']
        #Do something on agent startup

        self.state = 'RUNNING'
        self.logger.info('Node started up')
        return HttpJsonResponse()

    @expose('GET')
    def test(self, kwargs):
        self.logger.info('Test method started')

        self.state = 'ADAPTING'

        msg = "hello kitty"
        
        self.state = 'RUNNING'
        self.logger.info('Test method ended')
        return HttpJsonResponse({'msg': msg})    
