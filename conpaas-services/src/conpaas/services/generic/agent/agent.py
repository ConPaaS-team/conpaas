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
from os.path import exists, devnull, join
from os import remove, makedirs, fdopen
from shutil import rmtree
import pickle 
import zipfile
import tarfile
import tempfile
import simplejson

from conpaas.core.expose import expose
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse, FileUploadField
from conpaas.core.agent import BaseAgent, AgentException
from conpaas.core import git

class GenericAgent(BaseAgent):
    """Agent class with the following exposed methods:

    check_agent_process() -- GET
    create_hub(my_ip) -- POST
    create_node(my_ip, hub_ip) -- POST
    """
    def __init__(self, config_parser, **kwargs): 
        """Initialize Generic Agent.
  
        'config_parser' represents the agent config file.
        **kwargs holds anything that can't be sent in config_parser.
        """
        BaseAgent.__init__(self, config_parser)

        # Path to the Generic JAR file
        self.generic_dir = config_parser.get('agent', 'CONPAAS_HOME')
        self.VAR_CACHE = config_parser.get('agent', 'VAR_CACHE')
        self.env = {}
        # The following two variables have the same value on the Hub
      #  self.my_ip_address = None
      #  self.hub_ip_address = None

    @expose('POST')
    def create_hub(self, kwargs):
        """Create a Generic Hub by starting generic server with -role hub"""
        self.logger.info('Hub starting up')

        self.state = 'PROLOGUE'

        self.my_ip_address = self.hub_ip_address = kwargs['my_ip']

        # Starting generic hub
        #start_args = [ "java", "-jar", "generic-server", "-role", "hub" ]
        start_args = [ "echo", "hub" ]

        self.logger.debug("Running command: '%s'. cwd='%s'" % (
            " ".join(start_args), self.generic_dir))

        proc = Popen(start_args, cwd=self.generic_dir, close_fds=True)

        self.state = 'RUNNING'
        self.logger.info('Hub started up. Generic pid=%d' % proc.pid)
        return HttpJsonResponse()

    @expose('POST')
    def create_node(self, kwargs):
        """Create a Generic Node. As this host will actually fire up browser
        sessions, and we want to run the tests in a non-interactive fashion, X 
        output will be sent to a fake display."""
        self.logger.info('Node starting up')

        self.state = 'ADAPTING'

        self.my_ip_address = kwargs['my_ip']
        self.hub_ip_address = kwargs['hub_ip']

        start_args = [ "echo", "node" ]

        env = { 
            'DISPLAY': ':1', 
            'PATH': '/bin:/usr/bin:/usr/local/bin' 
        }

        self.logger.debug("Running command: '%s'. cwd='%s', env='%s'" % (
            " ".join(start_args), self.generic_dir, env))

        proc = Popen(start_args, cwd=self.generic_dir, env=env, close_fds=True)

        self.state = 'RUNNING'
        self.logger.info('Node started up. Generic pid=%d' % proc.pid)
        return HttpJsonResponse()

    @expose('UPLOAD')                                                                                    
    def update_code(self, kwargs):                                                                     
                                                                                                         
        if 'filetype' not in kwargs:                                                                     
            return HttpErrorResponse(AgentException(                                                     
                AgentException.E_ARGS_MISSING, 'filetype').message)                                      
        filetype = kwargs.pop('filetype')                                                                
                                                                                                         
        if 'codeVersionId' not in kwargs:                                                                
            return HttpErrorResponse(AgentException(                                                     
                AgentException.E_ARGS_MISSING, 'codeVersionId').message)                                 
        codeVersionId = kwargs.pop('codeVersionId')                                                      
                                                                                                         
        if 'file' not in kwargs:                                                                         
            return HttpErrorResponse(AgentException(                                                     
                AgentException.E_ARGS_MISSING, 'file').message)                                          
        file = kwargs.pop('file')                                                                        
                                                                                                         
        if filetype != 'git' and not isinstance(file, FileUploadField):                                  
            return HttpErrorResponse(AgentException(                                                     
                AgentException.E_ARGS_INVALID, detail='"file" should be a file').message)                
                                                                                                         
        if len(kwargs) != 0:                                                                             
            return HttpErrorResponse(AgentException(                                                     
                AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)                                
                                                                                                         
        if filetype == 'zip':                                                                            
            source = zipfile.ZipFile(file.file, 'r')                                                     
        elif filetype == 'tar':                                                                          
            source = tarfile.open(fileobj=file.file)                                                     
        elif filetype == 'git':                                                                          
            source = git.DEFAULT_CODE_REPO                                                               
        else:                                                                                            
            return HttpErrorResponse('Unknown archive type ' + str(filetype))                            
                                                                                                         
        if not exists(join(self.VAR_CACHE, 'bin')):                                                      
            makedirs(join(self.VAR_CACHE, 'bin'))                                                        
                                                                                                         
        target_dir = join(self.VAR_CACHE, 'bin')                                          
        if exists(target_dir):                                                                           
            rmtree(target_dir)                                                                           
                                                                                                         
        if filetype == 'git':                                                                            
            target_dir = join(self.VAR_CACHE, 'bin')                                                     
            self.logger.debug("git_enable_revision('%s', '%s', '%s')" % (target_dir, source, codeVersionId))                                                                                                      
            git.git_enable_revision(target_dir, source, codeVersionId)                                   
        else:                                                                                            
            source.extractall(target_dir)                                                                
                                                                                                         
        # Fix session handlers                                                                           
        #self.fix_session_handlers(target_dir)                                                            
                                                                                                         
        return HttpJsonResponse()   

    @expose('UPLOAD') 
    def init_agent(self, kwargs):
        """Set the environment variables"""
        
        self.logger.info('Setting agent environment')

        #TODO: do some checks on the arguments
        agents_info = simplejson.loads(kwargs.pop('agents_info'))
        #agents_info = kwargs.pop('agents_info')
        file = kwargs.pop('file')
        agent_ip = kwargs.pop('ip')
        self.state = 'ADAPTING'
        
        #maybe some permission issues
        #if not exists(join(self.VAR_CACHE, 'init')):                                                      
        #    makedirs(join(self.VAR_CACHE, 'init'))                                                        
                                                                                                         
        #target_dir = join(self.VAR_CACHE, 'init')                                          
        #if exists(target_dir):                                                                           
        #    rmtree(target_dir)        
        
        target_dir = self.VAR_CACHE
        
        fd, name = tempfile.mkstemp(prefix='init-', dir=target_dir)
        fd = fdopen(fd, 'w')
        upload = file.file
        
        #self.logger.info('agents info = %s' % agents_info)
        #self.logger.info('agents info[0] = %s' % agents_info[0])

        bytes = upload.read(2048)
        while len(bytes) != 0:
            fd.write(bytes)
            bytes = upload.read(2048)
        fd.close()
        
        with open(join(target_dir, 'agents.json'), 'w') as outfile:
            simplejson.dump(agents_info, outfile)
       
        agent_role = [i['Role'] for i in agents_info if i['IP'] == agent_ip][0]
        master_ip = [i['IP'] for i in agents_info if i['Role'] == 'MASTER'][0]
        
        self.env.update({'MY_IP':agent_ip})
        self.env.update({'MY_ROLE':agent_role})
        self.env.update({'MASTER_IP':master_ip})
        
        initpath = join(target_dir, name)
        start_args = [ "bash",  initpath ]
        
        proc = Popen(start_args, cwd=self.generic_dir, env=self.env, close_fds=True)
        

        self.state = 'RUNNING'
        self.logger.info('Agent initialized')
        return HttpJsonResponse()

    @expose('POST')
    def run(self, kwargs):
        
        startpath = join(self.VAR_CACHE, 'bin', 'start.sh')
        start_args = [ "bash",  startpath ]
        
        proc = Popen(start_args, cwd=self.generic_dir, env=self.env, close_fds=True)
        proc.wait()
        self.state = 'RUNNING'
        self.logger.info('Starter is running')
        return HttpJsonResponse()
