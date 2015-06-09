#!/usr/bin/env python
from base import Base

from deployment import DeployOperation, Activation
from requirement import Resources, Argument

from context.parameters import VariableModel
from conpaas.core.appmanager.utils.generator import Combinations
#from utils.resources import RemoteConnection
from conpaas.core.appmanager.utils.mondata import UtilizationDataThread
from conpaas.core.appmanager.utils.resources import get_utilization
from conpaas.core.appmanager.slo import User

import time, subprocess, os, traceback
import copy

#from utils.resources import RemoteConnection
#import time


class PerformanceModel(Base):
    accepted_params = [
        {
        'name':'Installer',
        'is_array': False,
        'is_required': False
        },
        {
        'name':'Call',
        'is_array': False,
        'is_required': True
        }
                       
    ]
    
    InputArguments = {}
    
    
    def evaluate(self, configuration):
        #print "Evaluation of pm : ", configuration
        input_arguments = self.InputArguments
        #print input_arguments
        for key in configuration:
            os.environ[key[1:]] = str(configuration[key])   

        exe_time = None
        call = None
        try:
            call = self.Call
            "Set implementation arguments in the call."
            for arg in input_arguments:
                call = call.replace(arg, input_arguments[arg])
            #print "Call : ", call
            try:
                exe_time = float(subprocess.check_output([call], env=os.environ, shell = True))
            except:
                exe_time = float(subprocess.Popen([call], stdout=subprocess.PIPE, shell = True).communicate()[0])
        except:
            #print "\nEnvironment vars : ", os.environ
            print "\nCall :", call
            print "\n\n============   Exception : Performance Model not found or wrong parameters ============\n"
                #raise Exception("Performance Model not found or wrong parameters")
            import sys
            sys.exit()

        return exe_time



class ModelManagement:

    def hasPerformanceModel(self):
        found = False
        for key in self.__dict__:
            if isinstance(self.__dict__[key], PerformanceModel):
                found = True
                break
            elif issubclass(self.__dict__[key].__class__, ModelManagement):
                found  = found or self.__dict__[key].hasPerformanceModel()
            elif type(self.__dict__[key]) == list:
                for m in self.__dict__[key]:
                    if issubclass(m.__class__, ModelManagement):
                        found = found or  m.hasPerformanceModel()
        return found 
       
    

    def compute_cost(self, conf, et):
        CM = 0.0
        if "%numCores" in conf:
            CM = CM + conf["%numCores"] * 0.001 * et
        if "%numDFEs" in conf:
            CM = CM + conf["%numDFEs"] * 0.03 * et
        if "%adp_num_cpucores" in conf:
            CM = CM + conf["%adp_num_cpucores"] * 0.001 * et 
        if "%adp_num_dfes" in conf:
            CM = CM + conf["%adp_num_dfes"] * 0.03 * et 

        return CM
    
        
        
    def optimize_objectives(self, execution):
        results = []
           
        if hasattr(self, "PerformanceModel"):
            print "Searching the optimal configuration for implementation ", self.ImplementationID           
            #self.PerformanceModel.
            resource_model = VariableModel(self.Resources.getVariableMap())  
            
            arg_var = {}
            for i in range(len(self.Arguments)):
                arg_var[self.Arguments[i].ArgID] = execution.ExecutionArgs[i]["Value"]

            self.PerformanceModel.InputArguments = arg_var
            print "Constraints :", execution.Objectives.Constraints
            print "Optimize :",execution.Objectives.Optimize
            print "Implementation input params :",arg_var
            print "Implementation input params :",arg_var

            self.AllConfs = []
            self.OptimalConfs = []
            ##fork the search   
            
            conf = resource_model.lower_bound_values()
            keys = conf.keys()
            indices = []
            for i in range(len(keys)):
                indices.append(resource_model.get_values_range(keys[i]))

            c = Combinations(indices)
        
            for comb in c.generate():
                conf = {}
                #rebuild conf
                for i in range(len(comb)):
                    conf[keys[i]] = resource_model.get_value_at_index(keys[i], comb[i])
                    #print "Evaluate Configuration: ", conf
                    #evaluate configuration
                    self.evaluate_configuration(resource_model, execution, conf)

            #best_conf = self.lookup(resource_model, execution)
            
            #print "\n\nAll :", self.AllConfs
            #print "Configuration satisfying SLOs:", best_conf
            #print "Optimal Configurations: ", self.OptimalConfs
           
            results = [(self.AllConfs, self.OptimalConfs, self.OptimalConfs[0] if self.OptimalConfs != [] else None)]
        else:
            for member in self.__dict__:
                if issubclass(self.__dict__[member].__class__, ModelManagement):
                    results.extend(self.__dict__[member].optimize_objectives(execution))
                elif type(self.__dict__[member]) == list:
                    for obj in self.__dict__[member]:
                        if issubclass(obj.__class__,  ModelManagement):
                            results.extend(obj.optimize_objectives(execution))

        return results
        
        
    def evaluate_configuration(self, resource_model, execution, conf):
    
        all_vars = {}
        all_vars.update(self.PerformanceModel.InputArguments)
        all_vars.update(conf)
        if self.evaluateConstraints(all_vars):
            envvars = self.Deployment.EnvironmentVars.replace(conf) 
            for key in envvars:
                os.environ[key] = str(envvars[key])
            exe_time = self.PerformanceModel.evaluate(conf)
            cost = self.compute_cost(conf, exe_time)
            #print "EnvVars :", envvars
            print "Configuration :%s\tExeTime : %f\tCost : %f" % (conf, exe_time,  cost)
    
            self.AllConfs.append((conf, exe_time, cost))

            if execution.Objectives.validate({"%cost" : cost, "%execution_time" : exe_time}):
                self.OptimalConfs.append((conf, exe_time, cost))
        if "%execution_time" in execution.Objectives.Optimize:
            self.OptimalConfs.sort(key=lambda tup: tup[1])
        else:
            self.OptimalConfs.sort(key=lambda tup: tup[2])
        
        #print "Configuration : %s\n\tET : %s\n\tCost : %s"%(str(conf), str(exe_time), str(cost))


class Implementation(Base):
    accepted_params = [
            {
        'name':'ImplementationID',
        'is_array': False,
        'is_required': True
        },
        {
        'name':'ImplementationName',
        'is_array': False,
        'is_required': True
        },
        {
        'name':'Arguments',
        'type' : Argument,
        'is_array': True,
        'is_required': False
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
        'name':'Deployment',
        'type' : DeployOperation,
        'is_array': False,
        'is_required': True
        },
        {
        'name':'Activation',
        'type' : Activation,
        'is_array': False,
        'is_required': True
        }
        ]
    
    def __init__(self, params = {}):
        Base.__init__(self, params)
        
        self.Variables = self.getVariables()
       
        #print "vars :", self.Variables
        
        
    def deploy(self, reservation):
        # conn = RemoteConnection(environ_vars = self.Deployment.EnvironmentVars.replace(reservation["Variables"]))
            
        # for machine in reservation["Resources"]:
        #     conn.run(machine["IP"], script = self.Deployment.get_start_script(machine["Role"]))
        # #start monitoring daemon
        # cmd = ";".join(["wget http://public.rennes.grid5000.fr/~aiordache/HARNESS/mond", "chmod +x mond", "nohup python mond < /dev/null &> /dev/null &"])
        # conn.run(machine["IP"], cmd = cmd)
        pass

    def terminate(self, reservation):
        
        # conn = RemoteConnection(environ_vars = self.Deployment.EnvironmentVars.replace(reservation["Variables"]))
        # for machine in reservation["Resources"]:
        #     conn.run(machine["IP"], script = self.Deployment.get_stop_script(machine["Role"]))
        # #stop monitoring daemon
        # conn.run(machine["IP"], cmd = ";".join(["export p=`lsof -i:9292 | grep 'python' | awk '{print $2}'`", "kill -9 $p"]))
		pass
    def execute(self, reservation):
        # conn = RemoteConnection(environ_vars = self.Deployment.EnvironmentVars.replace(reservation["Variables"]))
            
        # cmd = self.Activation.getCommand(reservation["Variables"])
        # utilization_data = []
        # print "---- Application Execution ---- "
        # self.mond_ps = UtilizationDataThread(target = get_utilization, machines = map(lambda m : m["IP"], reservation["Resources"]))
        # self.mond_ps.start()

           
        # StartTime = time.time()
        # output = ""    
        # for machine in filter(lambda x : x["Role"] == self.Activation.EndpointRole, reservation["Resources"]):
        #     output = output + str(conn.run(machine["IP"], cmd = cmd))
            
        # EndTime = time.time()
            
        # utilization_data.extend(self.mond_ps.stop())
        # rtdata = {"Usage" : utilization_data, "STDOUT" : output}
        # return (EndTime - StartTime, rtdata)     

        StartTime = time.time()
        time.sleep(2)
        EndTime = time.time()            
        return EndTime - StartTime 
        
        
    def evaluateConstraints(self, variables = {}):
        #process_constraints
        for expr in self.GlobalConstraints:
            chain_comp = expr[:]
            for var in variables:
                chain_comp = chain_comp.replace(var, str(variables[var]))
            print "evaluating %s" % chain_comp
            if not eval(chain_comp):
                return False
        
        return True
        
    

class Module(Base):
    accepted_params = [
                        {
                        'name' : 'ModuleName',
                        'type' : str,
                        'is_array' : False,
                        'is_required' : True
                        },
                        {
                        'name' : 'ModuleType',
                        'type' : str,
                        'is_array' : False,
                        'is_required' : True
                        },
                        {
                        'name' : 'Implementations',
                        'type' : Implementation,
                        'is_array' : True,
                        'is_required' : True
                        }
                    ]

