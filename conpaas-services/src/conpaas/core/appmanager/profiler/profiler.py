#!/usr/bin/env python

#from conpaas.core.appmanager.core.context.parameters import VariableModel
from conpaas.core.appmanager.utils.generator import Combinations
from conpaas.core.appmanager.profiler.strategy import * 
from conpaas.core.appmanager.core.patterns.store import Traces
from conpaas.core.appmanager.utils.math import MathUtils

import sys, os
    
        
class Profiler:
    
    def __init__(self, appmanager):
        self.appmanager = appmanager
        self.strategy = None
        

    def run(self):        
        print "--->  Implementation Selection Process  <---"
        self.implementationsXmodule = []

        for i in range(len(self.appmanager.manifest.Modules)):
            self.implementationsXmodule.append(len(self.appmanager.manifest.Modules[i].Implementations) - 1) 
            res = self.appmanager.create_service({'service_type':self.appmanager.manifest.Modules[i].ModuleType, 'app_tar': self.appmanager.app_tar})
            self.appmanager.dir_create_service(self.appmanager.manifest.Modules[i].ModuleType, res.obj['sid'])
            self.appmanager.module_managers.append(self.appmanager.httpsserver.instances[int(res.obj['sid'])])
        
        print "Index of implementations per module :", self.implementationsXmodule
        c = Combinations(self.implementationsXmodule)
 
        profile = []        
        for impl_comb in c.generate():
            implementations = []
            for i in range(len(impl_comb)):
                print "Selecting implemention %d from module %d" % (impl_comb[i], i)
                impl = self.appmanager.manifest.Modules[i].Implementations[impl_comb[i]]
                implementations.append(impl)  
            profile.append(self.__profile(implementations))
        print "\nProfiling process ended!\n\n"
        return profile
        # save profile 
        # self.appmanager.save_profile()

    
    
    def __profile(self, implementations):
        """
            Profiling Routine
            * Search space for the smallest input size #the first value of each argument
            * Select Pareto experiments
            * Modify input size and test on the Pareto configurations 
        """
        experiments = []
        for implementation in implementations:
            arguments = implementation.Arguments
            strategy = SimulatedAnnealingStrategy(self.appmanager, implementation)
            argument_combinations = Combinations(map(lambda arg: arg.get_range_size() - 1, arguments))
            
            for values in argument_combinations.generate():
                new_args = []
                for i in range(len(arguments)):
                    new_args.append(copy.deepcopy(arguments[i]))
                    #get the argument value
                    val = arguments[i].get_value_at_index(values[i])
                    #set range or values as only having this value
                    new_args[-1].set_values([val, val])
                
                #change input size here
                strategy.implementation.Arguments = new_args
                #update arguments model
                strategy.generate_arguments_model()
                print "arg model %s" % strategy.ArgModel

                experiments = strategy.explore()
                # self.appmanager.performance_model['experiments']

                break #TODO(genc): this is to stop trying different inputs, take care when this is decided
            
        # return experiments
