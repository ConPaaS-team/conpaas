# -*- coding: utf-8 -*-

"""
    conpaas.core.services
    =====================

    ConPaaS core: map available services to their classes.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

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
                    'taskfarm' : {'class' : 'TaskFarmManager',
                                  'module': 'conpaas.services.taskfarm.manager.manager'},
		    'galera' : {'class' : 'GaleraManager',
                               'module': 'conpaas.services.galera.manager.manager'},

#                    'htcondor' : {'class' : 'HTCondorManager',
#                                  'module': 'conpaas.services.htcondor.manager.manager'},
                    'htc' : {'class' : 'HTCManager',
                                  'module': 'conpaas.services.htc.manager.manager'},
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
  		  'galera' : {'class' : 'GaleraAgent',
                             'module': 'conpaas.services.galera.agent.internals'},

#                  'htcondor' : {'class' : 'HTCondorAgent',
#                                'module': 'conpaas.services.htcondor.agent.agent'},
                  'htc' : {'class' : 'HTCAgent',
                                'module': 'conpaas.services.htc.agent.agent'},
#""" BLUE_PRINT_INSERT_AGENT 		do not remove this line: it is a placeholder for installing new services """
		  }
