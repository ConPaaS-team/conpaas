#!/usr/bin/env python

#from conpaas.core.appmanager.core.context.parameters import VariableModel
from conpaas.core.appmanager.utils.generator import Combinations
from conpaas.core.appmanager.profiler.strategy import * 
from conpaas.core.appmanager.core.patterns.store import Traces
from conpaas.core.appmanager.utils.math import MathUtils

import sys, os
    
        
class Profiler:
    
    def __init__(self, appmanager, cloud):
        self.appmanager = appmanager
        self.strategy = None
        self.cloud = cloud
        

    def run(self):        
        print "--->  Implementation Selection Process  <---"
        self.implementationsXmodule = []
        

        module_managers=[]
        for i in range(len(self.appmanager.manifest.Modules)):
            self.implementationsXmodule.append(len(self.appmanager.manifest.Modules[i].Implementations) - 1) 
            res = self.appmanager.create_service({'service_type':self.appmanager.manifest.Modules[i].ModuleType, 'app_tar': self.appmanager.app_tar})
            self.appmanager.dir_create_service(self.appmanager.manifest.Modules[i].ModuleType, res.obj['sid'])
            module_managers.append(self.appmanager.httpsserver.instances[int(res.obj['sid'])])
        
        print "Index of implementations per module :", self.implementationsXmodule
        c = Combinations(self.implementationsXmodule)

        for impl_comb in c.generate():
            implementations = []
            for i in range(len(impl_comb)):
                print "Selecting implemention %d from module %d" % (impl_comb[i], i)
                impl = self.appmanager.manifest.Modules[i].Implementations[self.implementationsXmodule[impl_comb[i]]]
                implementations.append(impl)  
            self.__profile(implementations, module_managers)    
        print "\nProfiling process ended!\n\n"

        # save profile 
        # self.appmanager.save_profile()

    
    
    def __profile(self, implementations, module_managers):
        """
            Profiling Routine
            * Search space for the smallest input size #the first value of each argument
            * Select Pareto experiments
            * Modify input size and test on the Pareto configurations 
        """
        
        #print "Profiling process id =", Thread.getName(self)
        implementation = implementations[0]
        module_manager = module_managers[0]
        arguments = implementation.Arguments
        #create strategy
        strategy = SimulatedAnnealingStrategy(implementation, module_manager, self.cloud)
        
        """
            Experiment with different input sizes.
            * generate combinations
        """
        experiments = []
        pareto_experiments = []
        
        print "~ Generate Argument Combinations ~"
        argument_combinations = Combinations(map(lambda arg: arg.get_range_size() - 1, arguments))
        
        for values in argument_combinations.generate():
            """
                Set the arguments for the current list of experiments.
            """
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

            if pareto_experiments == []:
                """
                    Apply the search strategy for the first combination
                """
                
                #explore parameter space with the first input size /first value for arguments                   
                experiments = strategy.explore()
                
                pareto_experiments = self.get_pareto_experiments(experiments)
                
                pareto_configurations = map(lambda exp: exp["Configuration"], pareto_experiments)
                print "Pareto Configurations per input size :", pareto_configurations
                
                print "Test different input sizes."
            else:
                """
                    Test different input sizes on the efficient configurations only
                """
                
                #test the pareto configurations with the current arguments
                pareto_experiments.extend(strategy.test_additional_configurations(pareto_configurations))
            break #genc delete this when you are done     
        
        # print "Total Pareto experiments : %d."% len(pareto_experiments)
        Traces.TrainingSet = experiments
        Traces.ParetoExperiments = pareto_experiments
        
        
        
        
    def get_pareto_experiments(self, exps):
        """
            Select experiments with the optimal cost-et trade-off        
        """
        cost = map(lambda x: x["Results"]["TotalCost"], exps)
        et = map(lambda x: x["Results"]["ExeTime"], exps)
        
        pcost, pet = MathUtils.pareto_frontier(cost, et)
        print "Pareto cost:", pcost
        print "Pareto et  :", pet
        print "Number experiments :", len(pcost)
        pex = []
        
        for exp in exps:
            for i in range(len(pcost)):
                if exp["Results"]["TotalCost"] == pcost[i] and exp["Results"]["ExeTime"] == pet[i]:
                    pex.append(exp)
                    
                    
        print "~ Pareto Experiments ~"
        print pex,"\n\n"
        return pex
                  
        
        
