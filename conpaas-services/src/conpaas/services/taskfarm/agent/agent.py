# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from subprocess import Popen

from conpaas.core.expose import expose
from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.agent import BaseAgent

class TaskFarmAgent(BaseAgent):
    """Agent class with the following exposed methods:

    check_agent_process() -- GET
    create_hub(my_ip) -- POST
    create_node(my_ip, hub_ip) -- POST
    """
    def __init__(self, config_parser, **kwargs): 
        """Initialize TaskFarm Agent.
  
        'config_parser' represents the agent config file.
        **kwargs holds anything that can't be sent in config_parser.
        """
        BaseAgent.__init__(self, config_parser)

        # Path to the TaskFarm JAR file
        self.taskfarm_dir = config_parser.get('agent', 'CONPAAS_HOME')
  
        # The following two variables have the same value on the Hub
        self.my_ip_address = None
        self.hub_ip_address = None

    @expose('POST')
    def create_hub(self, kwargs):
        """Create a TaskFarm Hub by starting taskfarm server with -role hub"""
        self.logger.info('Hub starting up')

        self.state = 'PROLOGUE'

        self.my_ip_address = self.hub_ip_address = kwargs['my_ip']

        # Starting taskfarm hub
        start_args = [ "java", "-jar", "taskfarm-server", "-role", "hub" ]

        self.logger.debug("Running command: '%s'. cwd='%s'" % (
            " ".join(start_args), self.taskfarm_dir))

        proc = Popen(start_args, cwd=self.taskfarm_dir, close_fds=True)

        self.state = 'RUNNING'
        self.logger.info('Hub started up. TaskFarm pid=%d' % proc.pid)
        return HttpJsonResponse()

    @expose('POST')
    def create_node(self, kwargs):
        """Create a TaskFarm Node. As this host will actually fire up browser
        sessions, and we want to run the tests in a non-interactive fashion, X 
        output will be sent to a fake display."""
        self.logger.info('Node starting up')

        self.state = 'ADAPTING'

        self.my_ip_address = kwargs['my_ip']
        self.hub_ip_address = kwargs['hub_ip']

        # Running the TaskFarm Node via xvfb-run and DISPLAY set to :1.  We
        # have to specify the PATH because Popen overrides all the environment
        # variables if env is specified. Using port 3306 (MySQL) to avoid
        # requesting yet another port to be open.
	# TODO: as this file was created from a BLUEPRINT file,
	# 	you may want to change ports, paths and/or other start_args
	#	to meet your specific service/server needs
        start_args = [ 
            "xvfb-run", "--auto-servernum",
            "java", "-jar", "taskfarm-server",
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
            " ".join(start_args), self.taskfarm_dir, env))

        proc = Popen(start_args, cwd=self.taskfarm_dir, env=env, close_fds=True)

        self.state = 'RUNNING'
        self.logger.info('Node started up. TaskFarm pid=%d' % proc.pid)
        return HttpJsonResponse()
