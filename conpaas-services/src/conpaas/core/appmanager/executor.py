#!/usr/bin/env python
import sys, inspect
# from conpaas.core.appmanager.resources.reservation import ReservationManager
from conpaas.core.appmanager.resources.utilisation import Monitor
from conpaas.core.appmanager.state import CostModel

class Executor:
    
    @staticmethod
    def execute_on_configuration(application, version_indexes, variables_order,  conf_variables, parameters):
        # application.manager.logger.debug("vi: %s, vo: %s, cv: %s, param:%s" % (version_indexes, variables_order,  conf_variables, parameters))
        ## FOR TEST ONLY - uses experiment traces instead of executing
        #success, conf_variables, cost, execution_time, gradient, utilisation = Executor._get_execution_trace(application, version_indexes, variables_order,  conf_variables, parameters)
        success, conf_variables, cost, execution_time, gradient, utilisation = Executor._execute_on_configuration(application, version_indexes, variables_order,  conf_variables, parameters)
        return  (success, conf_variables, cost, execution_time, gradient, utilisation)


    @staticmethod
    def _process_feedback(monitor, application, version_indexes, configuration, variables_order, conf_variables, feedback = None):
        #stop monitoring
        if not feedback :
            #stop monitor here
            #recommendation, utilisation = monitor.stop()
            recommendation, utilisation = monitor.get_monitoing()
        else:
            recommendation = monitor.get_recommendation(feedback["utilisation"])
            utilisation = feedback
        bottlenecks = monitor.get_bottleneck(utilisation)
            
        #regroup and assign recommendation to variables
        variable_keys = application.getResourceVar2KeyMap(version_indexes)
        #print "Resource Variable Map :", variable_keys
        # -1 to decrease, 0 to don't know and +1 to increase the value (default 0)
        rd = {}
        bn = {}
        for key in variables_order:
            rd[key] = 0
            bn[key] = False
                
        for rec in recommendation:
            for c in configuration:
                if rec == c["Address"]:
                    group_variables = application.getGroupIDVars(version_indexes, c["Group"])
                    for v in group_variables:
                        if variable_keys[v] in recommendation[rec].keys():
                            rd[v] += recommendation[rec][variable_keys[v]]
                            bn[v] = bn[v] or bottlenecks[rec][variable_keys[v]]
        
        #order values and zip to dict
        gradient = dict(zip(variables_order, [rd[v] for v in variables_order]))
        bottlenecks = dict(zip(variables_order, [bn[v] for v in variables_order]))
        
        return (utilisation, gradient, bottlenecks)

    @staticmethod
    def _execute_on_configuration(application, version_indexes, variables_order,  conf_variables, parameters):
        #get resource configuration
        print "Run on ", conf_variables
        roles, configuration, constraints = application.getResourceConfiguration(version_indexes, conf_variables)
        #print roles
        #print configuration
        
        monitor = Monitor(application.manager)
        reservation = application.manager.reserve_resources(configuration, constraints, monitor.target)
        application.manager.logger.debug("Reservation: %s" % reservation)
        released = False
        #print "Reservation ready :", reservation
        try:
            for i in range(len(configuration)):
                configuration[i]["Address"] = reservation[i]["Address"]
                configuration[i]["Role"]    = roles[i]
            
            all_variables = {}
            all_variables.update(parameters)
            all_variables.update(conf_variables)
                
            monitor.setup(configuration, reservation[0]['ID'])
            
            print "\nExecuting application on the following resources :\n", configuration, "\n"

            data = {"Done":False, "Implementations":version_indexes, "Configuration":configuration, "ConfVars":conf_variables, "Parameters":parameters }
            application.manager.add_experiment(data, Executor._is_profiling(application, parameters))

            #execute application
            successful_execution, execution_time = application.execute(version_indexes, configuration[:], all_variables)
            
            #This is HACK to prevent (reporting) failures during profiling 
            if Executor._is_profiling(application, parameters):
                successful_execution = True

            #this will stop also the monitor
            utilisation, gradient, bottlenecks = Executor._process_feedback(monitor, application, version_indexes, configuration, variables_order, conf_variables, None)
            
            success = {"Success"  : successful_execution, "Bottleneck" : bottlenecks}
            
            #release configuration
            application.manager.release_resources(reservation[0]['ID'])
            released = True
            # ReservationManager.release(reservation["ReservationID"])
            cost_unit = application.manager.get_cost(configuration, constraints)
            cost =  execution_time * cost_unit
            data["Monitor"] = utilisation['utilisation']
            data["Success"] = successful_execution
            data["Results"] = {"ExeTime" : execution_time, "TotalCost" : cost} 
            data["Done"] = True

            print "Cost: ",cost, " ET :", execution_time
            
            return  (success, conf_variables, cost, execution_time, gradient, utilisation)  
        
        except Exception, e:
            if not released:
                application.manager.release_resources(reservation[0]['ID'])
            raise e


    @staticmethod
    def _is_profiling(application, parameters):
        exe_input = application.getExecutionParameters(application.ExtrapolationArgs)
        if exe_input == parameters:
            return False
        return True
        # curframe = inspect.currentframe()
        # calframe = inspect.getouterframes(curframe, 3)
        # calfile = calframe[3][1]
        # if('profiler' in calfile):
        #     return True 
        # return False