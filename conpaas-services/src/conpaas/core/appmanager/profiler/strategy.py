#!/usr/bin/env python

from conpaas.core.appmanager.core.context.parameters import VariableModel
from conpaas.core.appmanager.core.patterns.store import Traces
#from conpaas.core.appmanager.provisioner.resources import ReservationManager
#from conpaas.core.appmanager.provisioner.simulator import SimulatorManager
import math, random, copy
from scipy.optimize import anneal
from threading import Lock
from datetime import datetime
import time
import json
from multiprocessing import Pool#, Queue

from Queue import Queue


class BaseStrategy:
    
    def __init__(self, appmanager, implementation, save_to_log = False):  
        """
            Base Constructor.
            * Keeps the variable model for resources and for implementation arguments
            
        """
        
        if save_to_log:
            self.listed = False
        else: 
            self.listed = True
            self.EXPERIMENTS = []      
            
        self.implementation = implementation
        self.appmanager = appmanager

        # print "\n == In BaseStrategy =="

        self.generate_resource_model()
        # print "\n ~ ResModel ~"
        str(self.ResModel)

        print "\n ~ Mapping for variables ~"
        print self.ResVarMap, "\n"

        self.generate_arguments_model()
        print "\n ~ ArgModel ~"
        str(self.ArgModel)

        print "\n ~ Order ~"
        self.VarOrder = self.ResModel.get_keys()
        print self.VarOrder
        print "\n =====\n"
        

    def generate_resource_model(self):
        """
            Build resource variables map
        """
        self.ResModel = VariableModel(self.implementation.Resources.getVariableMap())  
        self.ResVarMap = self.implementation.Resources.get_keys()
        
        
    def generate_arguments_model(self):
        """
            Build arguments variables map
        """
        arg_var = []
        for arg in self.implementation.Arguments:
            arg_var.extend(arg.getVariableMap())
            
        self.ArgModel = VariableModel(arg_var)
        
        
        
           
    def execute(self, values, lock = None):
        """
            Implementation deployment and execution
            * acquire CONF
            * deploy implementation on CONF
            * execute application on CONF
            * release CONF
        """
        #lock and make local copies of the variables and work on the copies - useful when executed on threads
        #print values
        variables = self.assign_keys(values)

        #denormalize values
        variables = self.ResModel.denormalize(variables)

        #setup application arguments
        args = self.ArgModel.denormalize(self.ArgModel.nrandomize())
        # print "\nApplication arguments :", args
        data = {}   
        implementation = copy.deepcopy(self.implementation)
        
        data["ImplementationID"] = implementation.ImplementationID
        data["Index"] = len(self.EXPERIMENTS)
        data["Configuration"] = copy.deepcopy(variables)
        data["Arguments"] = args
        data["Done"] = False
        
        if self.listed:
            already_done = None

            for exp in self.EXPERIMENTS:
                if exp["Configuration"] == variables and exp["Arguments"] == args:
                    already_done = self.goodness(exp["Results"]["ExeTime"], exp["Results"]["TotalCost"])
                    break                
            if already_done != None:
                return already_done 
        self.appmanager.add_experiment(data)
        # Traces.Experiments[data["Index"]] = data 
        """
            Get the configuration structure from the implementation
        """
        print "variables %s " % variables
        
        configuration, roles = implementation.Resources.get_configuration(variables)
        print "configuration: %s, roles: %s" % (configuration, roles)
        

        """"
            Reserving resources
        """
        # reservation = self.module_manager.controller.prepare_reservation(configuration)
        #check cost reservation['Cost'] and contiune
        #cost = reservation['Cost']
        # reservation = self.module_manager.controller.create_reservation_test(reservation, self.module_manager.get_check_agent_funct(), 5555)
        reservation = self.appmanager.reserve_resources(configuration)


        # #reservation = ReservationManager.acquire_resources(configuration)
        if reservation == None:
            print "Experiment failed."
            return 0 
        """
           Add roles to the acquired machines
        """
        for i in range(len(reservation['Instances'])):
           reservation['Instances'][i]["Role"] = roles[i]

        # print "\n ~ Acquired Resources ~"
        # print reservation["Resources"]

        """"
            Execute Implementation
        """
        variables.update(args)
        #get manifest special variables, environment variables
        variables.update(implementation.Resources.get_special_variables(reservation['Instances']))

        reservation["Variables"] = variables
        #print "*** reservation: %s" % (reservation)

        # "Deploy implementation"
        # implementation.deploy(reservation)
        
        # # what anca calls deploy (no variables taken into consideration at this point)
        # self.module_manager._do_startup(self.cloud, reservation, args)
        
        # "Execute implementation"
        # start_time = time.time()
        # self.module_manager._do_run(args)
        # end_time = time.time()
        # execution_time = end_time - start_time
        execution_time, total_cost = self.appmanager.execute_application(reservation, args, True) 

        # # execution_time, utilization_data = implementation.execute(reservation)
        # total_cost = execution_time * reservation["Cost"]
        
        # """
        #     Releasing resources
        # """
        #reservation = ReservationManager.release_resources(reservation["ResID"])
        # genc:uncomment the following line 
        #debug if (delete when done)
        # if execution_time > 2:
        #     self.module_manager.controller.release_reservation(reservation['ConfigID'])

        "Save output and update experiments list"
        data["Results"] = {"ExeTime" : execution_time, "TotalCost" : total_cost} 
        data["Done"] = True
        # data["RuntimeData"] = utilization_data
        if self.listed:
            print "Add experiment to the Queue."
            self.EXPERIMENTS.append(data)
        # else:
        #     #save to logs
        #     fname = str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S'))
        #     print "Save to log : ", fname
        #     f = open("/home/aiordache/exps3/exp-%s" % fname, "w")
        #     f.write(unicode(json.dumps(data, ensure_ascii=False)))
        #     f.close()
        # print "GGG> data:%s, reservation: %s" % (data, reservation)
        print "Done experiment."
        "Returns evaluation of the execution based on cost and execution time"
        
        return self.goodness(data["Results"]["ExeTime"], data["Results"]["TotalCost"])

        
    def explore(self):
        raise NotImplementedError, "Must be implemented in the derived class - based on different exploration strategies"


    def goodness(self, performance, cost):
        """
            Evaluation of implementation execution
        """
        quality = cost * performance
        "Less is better"
        return quality


    def order_values(self, variables):
        ordered_values = []
        for i in range(len(self.VarOrder)):
            key = self.VarOrder[i]
            ordered_values.append(variables[key])
                    
        return ordered_values

    def assign_keys(self, values):
        """Isolate variable names of their values such that we apply mathematical methods on vectors and remap them back later 
        to the names"""
        print "in assign keys values: %s, varOrder: %s" % (values, self.VarOrder)
        variables = {}
        for i in range(len(self.VarOrder)):
            key = self.VarOrder[i]
            variables[key] = values[i] 
        
        return variables


class SimulatedAnnealingStrategy(BaseStrategy):
        
    def explore(self):
        print "\n ~ Running Simulated Annealing ~ "
        # result = anneal(
        #                 self.execute,# self.simulate
        #                 [0]*len(self.VarOrder), 
        #                 lower = float(self.ResModel.Interval[0]), 
        #                 upper = float(self.ResModel.Interval[1]),
        #                 T0 = 100, maxeval = 5, dwell = 1
        #                 )#, schedule = "boltzmann")#"fast") #default = fast   
        
        self.execute([0]*len(self.VarOrder))
        # self.execute([0,0,0])
        print "\n\nStrategy Done!\n"
        print "Num iterations :", len(self.EXPERIMENTS)
        # print solution
        #print 'Return Code: ', result
        #print self.EXPERIMENTS
        
        return self.EXPERIMENTS
        #return True
  
    def test_additional_configurations(self, configurations):
        
        self.EXPERIMENTS = []
        print "Additional experiments running..."
        for conf in configurations:
            print "Run configuration ", conf
            #normalize and order variables
            variables = self.order_values(self.ResModel.normalize(conf))
            self.simulate(variables) #self.execute
        
        return self.EXPERIMENTS
        
   
