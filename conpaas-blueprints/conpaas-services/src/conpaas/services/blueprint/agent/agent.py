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

        # Path to the BluePrint JAR file
        self.blueprint_dir = config_parser.get('agent', 'CONPAAS_HOME')
  
        # The following two variables have the same value on the Hub
        self.my_ip_address = None
        self.hub_ip_address = None

    @expose('POST')
    def create_hub(self, kwargs):
        """Create a BluePrint Hub by starting blueprint server with -role hub"""
        self.logger.info('Hub starting up')

        self.state = 'PROLOGUE'

        self.my_ip_address = self.hub_ip_address = kwargs['my_ip']

        # Starting blueprint hub
        start_args = [ "java", "-jar", "blueprint-server", "-role", "hub" ]

        self.logger.debug("Running command: '%s'. cwd='%s'" % (
            " ".join(start_args), self.blueprint_dir))

        proc = Popen(start_args, cwd=self.blueprint_dir, close_fds=True)

        self.state = 'RUNNING'
        self.logger.info('Hub started up. BluePrint pid=%d' % proc.pid)
        return HttpJsonResponse()

    @expose('POST')
    def create_node(self, kwargs):
        """Create a BluePrint Node. As this host will actually fire up browser
        sessions, and we want to run the tests in a non-interactive fashion, X 
        output will be sent to a fake display."""
        self.logger.info('Node starting up')

        self.state = 'ADAPTING'

        self.my_ip_address = kwargs['my_ip']
        self.hub_ip_address = kwargs['hub_ip']

        # Running the BluePrint Node via xvfb-run and DISPLAY set to :1.  We
        # have to specify the PATH because Popen overrides all the environment
        # variables if env is specified. Using port 3306 (MySQL) to avoid
        # requesting yet another port to be open.
	# TODO: as this file was created from a BLUEPRINT file,
	# 	you may want to change ports, paths and/or other start_args
	#	to meet your specific service/server needs
        start_args = [ 
            "xvfb-run", "--auto-servernum",
            "java", "-jar", "blueprint-server",
            "-role", "node", "-port", "3306",
            "-hub", "http://%s:4444/grid/register" % self.hub_ip_address,
            "-host", self.my_ip_address,
            "-maxSession", "6",
            "-browser", "browserName=firefox,maxInstances=3",
            "-browser", "browserName=chrome,maxInstances=3",
        ]

        env = { 
            'DISPLAY': ':1', 
            'PATH': '/bin:/usr/bin:/usr/local/bin' 
        }

        self.logger.debug("Running command: '%s'. cwd='%s', env='%s'" % (
            " ".join(start_args), self.blueprint_dir, env))

        proc = Popen(start_args, cwd=self.blueprint_dir, env=env, close_fds=True)

        self.state = 'RUNNING'
        self.logger.info('Node started up. BluePrint pid=%d' % proc.pid)
        return HttpJsonResponse()
