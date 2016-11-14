# -*- coding: utf-8 -*-

"""
    conpaas.core.services
    =====================

    ConPaaS core: map available services to their classes.

    :copyright: (C) 2010-2016 by Contrail Consortium.
"""

manager_services = {'php'        : {'class' : 'PHPManager',
                                     'module': 'conpaas.services.webservers.manager.internal.php'},
                    'java'       : {'class' : 'JavaManager',
                                    'module': 'conpaas.services.webservers.manager.internal.java'},
                    'helloworld' : {'class' : 'HelloWorldManager',
                                    'module': 'conpaas.services.helloworld.manager.manager'},
                    'xtreemfs'   : {'class' : 'XtreemFSManager',
                                    'module': 'conpaas.services.xtreemfs.manager.manager'},
                    'mysql'      : {'class' : 'MySQLManager',
                                    'module': 'conpaas.services.mysql.manager.manager'},
                    'generic'    : {'class' : 'GenericManager',
                                    'module': 'conpaas.services.generic.manager.manager'},
#""" BLUE_PRINT_INSERT_MANAGER      do not remove this line: it is a placeholder for installing new services """
}

agent_services = {'web'        : {'class' : 'WebServersAgent',
                                  'module': 'conpaas.services.webservers.agent.internals'},
                  'helloworld' : {'class' : 'HelloWorldAgent',
                                  'module': 'conpaas.services.helloworld.agent.agent'},
                  'xtreemfs'   : {'class' : 'XtreemFSAgent',
                                  'module': 'conpaas.services.xtreemfs.agent.agent'},
                  'mysql'      : {'class' : 'MySQLAgent',
                                  'module': 'conpaas.services.mysql.agent.internals'},
                  'generic'    : {'class' : 'GenericAgent',
                                  'module': 'conpaas.services.generic.agent.agent'},
#""" BLUE_PRINT_INSERT_AGENT      do not remove this line: it is a placeholder for installing new services """
}
