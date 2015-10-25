#!/usr/bin/env python
from conpaas.core.appmanager.application.base import Base
from conpaas.core.appmanager.application.search_space import VariableMapper
# from conpaas.core.appmanager.resources.connection import RemoteConnection
from conpaas.core.appmanager.utils.monitor import MonitorDataThread
from conpaas.core.appmanager.application.elements.resources import Resources


import time, sys, os, simplejson

class Implementation(Base):
    accepted_params = [
        {
        'name':'ImplementationName',
        'is_array': False,
        'is_required': True
        },
        {
        'name':'Resources',
        'type' : Resources,
        'is_array': False,
        'is_required': True
        },
        {
        'name':'GlobalConstraints',
        'type' : str,
        'is_array': True,
        'is_required': True
        },
        {
        'name':'EnvironmentVars',
        'type' : dict,
        'is_array': False,
        'is_required': False
        },
        {
        'name':'Tarball',
        'type' : str,
        'is_array': False,
        'is_required': True
        },
        {
        'name':'DeploymentArgs',
        'type' : str,
        'is_array': False,
        'is_required': False
        },
        {
        'name':'ExecutionArgs',
        'type' : str,
        'is_array': False,
        'is_required': False
        }
    ]
    
    def __init__(self, hashmap = {}):
        Base.__init__(self, hashmap)
        self.Variables = self.get_Vars()
    def __process_args(self, args, variables):
        arg_str = args[:]

        for v in variables:
            if v in arg_str:
                arg_str = arg_str.replace(v, str(variables[v]))

        return arg_str

    def __process_environ_vars(self, machines, variables):
        result = {}
        env_vars = self.EnvironmentVars
        for key in env_vars:
            vars = env_vars[key]
            result[key] = ""
            values = vars.split(";")
            for val in values:
                if val.startswith("address(") and val.endswith(")"):
                   keyword = val[8:]
                   keyword = keyword[:-1]
                   gather_info = []
                   for machine in machines:
                      for k in machine:
                         if machine[k] == keyword:
                            gather_info.append(machine["Address"])
                   result[key] = result[key] + ";".join(map(lambda item: str(item), gather_info)) + ";"
                else:
                   new_value = val
                   for v in variables:
                       if v in new_value:
                           new_value = new_value.replace(v, str(variables[v]))
                   result[key] = result[key] + new_value + ";"
            if result[key].endswith(";"):
               result[key] = result[key][:-1]    
        return result

    def deploy(self, manager, machines, variables):
        print "....... Application Deployment ......."
        env_vars = self.__process_environ_vars(machines, variables)
        
        instances={}
        instances['Instances'] = machines
        #don't want to see experiments trace in the output
        #redirect to null 
        backup = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
        module_manager = manager.module_managers[0]
        manager.frontend = module_manager._do_startup({'cloud':manager.cloud, 'configuration':instances, 'args': self.__process_args(self.DeploymentArgs, variables), 'env_vars':env_vars ,'code_conf':manager.config})

        # conn = RemoteConnection(environ_vars = env_vars)
        # #print "Run deployment scripts."    
        # #general cmds
        # cmds = ["curl -O %s" % self.Tarball, "tar xzf %s" % self.Tarball.split("/")[-1]]
        # cmds.extend(["mkdir -p /var/cache/harness/;", "echo '%s' > /var/cache/harness/instances.json" % simplejson.dumps(instances)])

        # cmds.extend(["chmod +x init.sh", "chmod +x start.sh"])

        # cmds.append(". init.sh %s" % (self.__process_args(self.DeploymentArgs, variables)))
        
        # print "Running cmd on all machines :", cmds
        
        # for cmd in cmds:
        #   print
        #   print "Running cmd %s" %cmd
        #   for machine in machines:
        #       conn.run(machine["Address"], cmd)
                
        # time.sleep(3)
        
        #restore stdout    
        sys.stdout = backup
            
        print "Deployment finished."

    def cleanup(self, manager, machines, variables):
        module_manager = manager.module_managers[0]
        manager.frontend = module_manager._do_cleanup()
        
    def execute(self, manager, machines, variables):
        env_vars = self.__process_environ_vars(machines, variables)
        print env_vars
        
        # conn = RemoteConnection(environ_vars = env_vars)
        print "---- Application Execution ---- "
        
        #don't want to see experiments trace in the output
        #redirect to null 
        backup = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
        args = self.__process_args(self.ExecutionArgs, variables)
        # cmd = ". start.sh %s" % self.__process_args(self.ExecutionArgs, variables)
        # success  = []
        StartTime = time.time()
        module_manager = manager.module_managers[0]
        success = module_manager._do_run(True, args, env_vars)
        manager.logger.info("success: %s" % success)
        # for machine in machines:
        #   exit_code, _ = conn.run(machine["Address"], cmd)
        #   success.append(exit_code)
        EndTime = time.time()
        #restore stdout    
        sys.stdout = backup
        
        print "Execution finished."
        return (sum(success) ,(EndTime - StartTime)) 

