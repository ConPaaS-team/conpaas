'''
Copyright (c) 2010-2012, Contrail consortium.
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


   This file contains all the available service implementations.

'''

manager_services = {'php'    : {'class' : 'PHPManager', 
                                'module': 'conpaas.services.webservers.manager.internal.php'},
                    'java'   : {'class' : 'JavaManager',
                                'module': 'conpaas.services.webservers.manager.internal.java'},
                    'scalaris' : {'class' : 'ScalarisManager',
                                  'module': 'conpaas.services.scalaris.manager.manager'},
                    'hadoop' : {'class' : 'MapReduceManager',
                                'module': 'conpaas.services.mapreduce.manager.manager'},
                    'helloworld' : {'class' : 'HelloWorldManager',
                                    'module': 'conpaas.services.helloworld.manager.manager'},
                    'mysql' : {'class' : 'MySQLManager',
                               'module': 'conpaas.services.mysql.manager.manager'},
                    'xtreemfs' : {'class' : 'XtreemFSManager',
                                  'module': 'conpaas.services.xtreemfs.manager.manager'},
                    'selenium' : {'class' : 'SeleniumManager',
                                  'module': 'conpaas.services.selenium.manager.manager'},
                    'htcondor' : {'class' : 'HTCondorManager',
                                  'module': 'conpaas.services.htcondor.manager.manager'},
#""" BLUE_PRINT_INSERT_MANAGER 		do not remove this line: it is a placeholder for installing new services """
		    }

agent_services = {'web' : {'class' : 'WebServersAgent',
                           'module': 'conpaas.services.webservers.agent.internals'},
                  'scalaris' : {'class' : 'ScalarisAgent',
                                'module': 'conpaas.services.scalaris.agent.agent'},
                  'mapreduce' : {'class' : 'MapReduceAgent',
                                 'module': 'conpaas.services.mapreduce.agent.agent'},
                  'helloworld' : {'class' : 'HelloWorldAgent',
                                  'module': 'conpaas.services.helloworld.agent.agent'},
                  'mysql' : {'class' : 'MySQLAgent',
                             'module': 'conpaas.services.mysql.agent.internals'},
                  'xtreemfs' : {'class' : 'XtreemFSAgent',
                                'module': 'conpaas.services.xtreemfs.agent.agent'},
                  'selenium' : {'class' : 'SeleniumAgent',
                                'module': 'conpaas.services.selenium.agent.agent'},
                  'htcondor' : {'class' : 'HTCondorAgent',
                                'module': 'conpaas.services.htcondor.agent.agent'},
#""" BLUE_PRINT_INSERT_AGENT 		do not remove this line: it is a placeholder for installing new services """
		  }
