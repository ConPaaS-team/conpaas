

"""

Strategy_Finder is in charge of the discovery of a proper scaling plan according to the customer preferences.

@author: fernandez
"""

import math
from conpaas.services.webservers.manager.autoscaling.performance import ServicePerformance, ServiceNodePerf, StatUtils
from conpaas.services.webservers.manager.autoscaling.cost_aware import Cost_Controller
from conpaas.core import log
from conpaas.services.webservers.manager.autoscaling.strategy.counter import Counter
#from conpaas.services.webservers.manager.autoscaling.prediction.prediction_models_test import Prediction_Models
from conpaas.services.webservers.manager.autoscaling.prediction.prediction_models import Prediction_Models
from conpaas.services.webservers.manager.autoscaling.strategy.vm_kmeans import VM_Classification


from conpaas.services.webservers.manager.autoscaling.performance import ServicePerformance, ServiceNodePerf, StatUtils


from decimal import Decimal 
import itertools

from multiprocessing.pool import ThreadPool

try:
    import simplejson as json
except ImportError:
    import json
import os.path
from os.path import join as pjoin 
    
COMPUTE_UNITS_FILE_PATH = 'data/compute_units.json'

class Strategy_Finder:
    
  def __init__(self, logger, iaas_driver, cost_controller, slo_fulfillment_degree, cost_policy, weight_slow_violation):
        self.logger = logger
              
        self.cost_controller = cost_controller
        self.stat_utils = StatUtils()
          
        self.scaling_decision = []
        self.other_possible_combinations = []
        
        self.iaas_driver = iaas_driver
        
        self.performance_predictor = Prediction_Models(logger)
        
        self.forecast_req_rate_model_selected = 0 
        self.forecast_req_rate_predicted = 0
        self.forecast_cpu_model_selected = 0
        self.forecast_cpu_predicted = 0
        
        self.forecast_list_cpu = {}
        self.forecast_list_req_rate = {}
        self.strategy_max_performance = 0
        
        self.slo_fulfillment_degree = slo_fulfillment_degree
        
        self.weight_slow_violation = weight_slow_violation
        
        self.classification = VM_Classification()
        
        self.slo_violation_penalty = 0.001
        
        self.req_complexity_rate = 0
        
        self.capacity_inst_type = {}
        
        self.pool_predictors = ThreadPool(processes=5)
        self.min_performance_throughput = 30
        self.max_performance_throughput = 70
        
        self.nodes = []

        """ 
           This policy removes candidate strategies on which resources cannot be removed,
            as they started its hour_timing.
         """ 
        self.cost_policy = cost_policy
        
        compute_units_file_path = self.get_compute_units_file_path()

        with open(compute_units_file_path) as fp:
            content = fp.read()

        self.vm_inst_types = []
        self.vm_inst_types = json.loads(content)[iaas_driver].keys()    
        ## Order to have always small instances in the position [0]
        self.vm_inst_types = sorted(self.vm_inst_types, reverse=True)

        
        #if 'OPENNEBULA' in self.iaas_driver:
         #   self.vm_inst_types = ['smallDAS4','highcpu-mediumDAS4', 'mediumDAS4', 'largeDAS4']
        #else:
         #   self.vm_inst_types = ['smallEC2','mediumEC2','c.mediumEC2', 'largeEC2']


  def set_slo_fulfillment_degree(self, slo_fulfillment_degree):
      slo_fulfillment_levels = ["low","medium_down","medium_up","medium","medium_up","high"]
      if slo_fulfillment_degree in slo_fulfillment_levels: 
          self.slo_fulfillment_degree = slo_fulfillment_degree
      else:
          self.slo_fulfillment_degree = "low"
      
  def get_vm_inst_types(self):
      return self.vm_inst_types
    
  def get_compute_units_file_path(self):
    compute_units_directory = os.path.dirname(os.path.abspath(__file__))
    compute_units_file_path = pjoin(compute_units_directory, COMPUTE_UNITS_FILE_PATH)

    return compute_units_file_path

  def insert_combination (self, cpu_capacity, combination):
    exist = 0
    for decision, (cpu_value) in self.scaling_decision:
        if len(decision) == len(combination):
            times = 0
            for vm in combination:
                if not vm in decision:
                    break
                else:
                    times += 1
            if times == len(combination):
                exist = 1
    
    if exist == 0:
        self.scaling_decision.append((combination, (cpu_capacity)))
        #self.logger.info("Optimal_Scaler: adding a possible scaling decisions: "+str(combination))
  
  def get_strategy_with_medium_capacity(self):
      capacities = [ cpu_capacity for decision, (cpu_capacity) in self.scaling_decision]
      capacities = sorted(capacities)
      if len(capacities) > 1:
          return capacities[ ( (len(capacities) - 1)/ 2 ) ]
      else:
          return  capacities[0]
      
  def get_compute_units(self,inst_type):             
      return self.classification.compute_units_instance(self.iaas_driver, inst_type)
      
  def prediction_evaluation(self, cpu_data, req_rate_data):
    self.logger.info("prediction_evaluation: Predicting future values for cpu_data "+str(cpu_data)+" request rate list "+str(req_rate_data))
    try: 
            data_cpu_filtered = cpu_data
            data_req_rate_filtered = req_rate_data
           # for cpu, req_rate in itertools.izip(cpu_data, req_rate_data):
            #    if cpu > 0 and req_rate > 0:
             #       data_cpu_filtered.append(cpu)
              #      data_req_rate_filtered.append(req_rate)
                    
           # self.logger.debug("OptimalScaler: Request rate filtered before prediciton: "+str(data_req_rate_filtered))  
           # self.logger.debug("OptimalScaler: Cpu usage filtered before prediciton: "+str(data_cpu_filtered))           
            
            async_result_req_ar =  self.pool_predictors.apply_async(self.performance_predictor.auto_regression, (data_req_rate_filtered,20))
            async_result_req_lr =  self.pool_predictors.apply_async(self.performance_predictor.linear_regression, (data_req_rate_filtered,20))
            async_result_req_exp_smoothing =  self.pool_predictors.apply_async(self.performance_predictor.exponential_smoothing, (data_req_rate_filtered,2))
            
          #  async_result_req_arma =  self.pool_predictors.apply_async(self.performance_predictor.arma, (data_req_rate_filtered,8))
            
            async_result_cpu_ar =  self.pool_predictors.apply_async(self.performance_predictor.auto_regression, (data_cpu_filtered,20))
            async_result_cpu_lr =  self.pool_predictors.apply_async(self.performance_predictor.linear_regression, (data_cpu_filtered,20))
            async_result_cpu_exp_smoothing =  self.pool_predictors.apply_async(self.performance_predictor.exponential_smoothing, (data_cpu_filtered,12))
           # async_result_cpu_arma =  self.pool_predictors.apply_async(self.performance_predictor.arma, (data_cpu_filtered,20))
            async_result_cpu_var =  self.pool_predictors.apply_async(self.performance_predictor.vector_auto_regression, (data_cpu_filtered,data_cpu_filtered,20))
           
            
            self.forecast_list_req_rate[1] = async_result_req_lr.get()
            self.forecast_list_req_rate[2] = async_result_req_exp_smoothing.get()
            self.forecast_list_req_rate[0] = async_result_req_ar.get()
          #  self.forecast_list_req_rate[0] = async_result_req_arma.get()
            
            self.forecast_list_cpu[1] = async_result_cpu_lr.get()
            self.forecast_list_cpu[2] = async_result_cpu_exp_smoothing.get()
            self.forecast_list_cpu[0] = async_result_cpu_ar.get()
      #      self.forecast_list_cpu[0] = async_result_cpu_arma.get()
            self.forecast_list_cpu[0] = async_result_cpu_var.get()
            
            try:
               self.logger.debug("Getting the forecast cpu usage for the best model in the previous iteration "+str(self.forecast_cpu_model_selected)) 
               weight_avg_predictions = self.stat_utils.compute_weight_average(self.forecast_list_cpu[self.forecast_cpu_model_selected])
               
               if weight_avg_predictions > 0:
                   self.forecast_cpu_predicted  = weight_avg_predictions      
               self.logger.debug("Prediction cpu usage for model "+str(self.forecast_cpu_model_selected)+"--  Prediction cpu value: "+str(self.forecast_cpu_predicted))
               
               self.logger.debug("Getting the forecast request rate for the best model in the previous iteration "+str(self.forecast_req_rate_model_selected)) 
               weight_avg_predictions = self.stat_utils.compute_weight_average(self.forecast_list_req_rate[self.forecast_req_rate_model_selected])
               
               if weight_avg_predictions > 0:
                   self.forecast_req_rate_predicted  = weight_avg_predictions      
               self.logger.debug("Prediction request rate for model "+str(self.forecast_req_rate_model_selected)+"--  Prediction req. rate: "+str(self.forecast_req_rate_predicted))
      
            except Exception as e:  
                self.logger.warning("Warning trying to predict a future value for the model." + str(e))

        
    except Exception as e:
        self.logger.error("OptimalScaler: Error trying to predict the future cpu_usage and req_rate values. "+ str(e))

  def get_req_rate_prediction(self):
      return self.forecast_req_rate_predicted

  def get_cpu_prediction(self):
      return self.forecast_cpu_predicted
    
  def get_cpu_prediction_model(self):
      return self.forecast_cpu_model_selected

  def get_req_rate_prediction_model(self):
      return self.forecast_req_rate_model_selected

  def calculate_error_prediction_cpu(self, cpu_usage):
    min_error_prediction = 1000000
    forecast_model = 0
 #   forecast_cpu = 0
    try:
           weight_avg_current = self.stat_utils.compute_weight_average(cpu_usage)
           
      #     try:
       #        weight_avg_predictions = self.stat_utils.compute_weight_average(self.forecast_list_cpu[0])
        #       prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
           
         #      if min_error_prediction > prediction_error and prediction_error > 0:
          #         forecast_model = 0
           #        min_error_prediction = prediction_error
                  # forecast_cpu  = weight_avg_predictions      
            #   self.logger.debug("OptimalScaler: Prediction error ARMA with cpu_usage: "+str(weight_avg_current)+" --  Prediction cpu_usage: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
      
           #except Exception as e:  
           #     self.logger.warning("OptimalScaler: Warning trying to predict the cpu error estimate for ARMA." + str(e))
           try:
                  
               weight_avg_predictions = self.stat_utils.compute_weight_average(self.forecast_list_cpu[0])
               prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
           
               if min_error_prediction > prediction_error and prediction_error > 0:
                    forecast_model = 0
                    min_error_prediction = prediction_error
                   # forecast_cpu  = weight_avg_predictions
               self.logger.debug("OptimalScaler: Prediction error AR with cpu_usage: "+str(weight_avg_current)+" --  Prediction cpu_usage: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
           
           except Exception as e:  
                self.logger.warning("OptimalScaler: Warning trying to predict the cpu error estimate for AR." + str(e))
       
           try: 
               weight_avg_predictions = self.stat_utils.compute_weight_average(self.forecast_list_cpu[1])
               prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
           
               if min_error_prediction > prediction_error and prediction_error > 0:
                   forecast_model = 1
                   min_error_prediction = prediction_error
                  # forecast_cpu  = weight_avg_predictions
               self.logger.debug("OptimalScaler: Prediction error LR with cpu_usage: "+str(weight_avg_current)+" --  Prediction cpu_usage: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
           
           except Exception as e:  
                self.logger.warning("OptimalScaler: Warning trying to predict the cpu error estimate for LR." + str(e))
       
           try:
               
              # cpu_usage = [x for x in cpu_usage[0:12]]
               weight_avg_predictions = self.stat_utils.compute_weight_average(self.forecast_list_cpu[2])
               prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
               if min_error_prediction > prediction_error and prediction_error > 0:
                   forecast_model = 2
                   min_error_prediction = prediction_error
                  # forecast_resp  = weight_avg_predictions
               self.logger.debug("OptimalScaler: Prediction error EXP. SMOOTHING with cpu_usage: "+str(weight_avg_current)+" --  Prediction cpu_usage: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
           except Exception as e:  
                self.logger.warning("OptimalScaler: Warning trying to predict the cpu error estimate for EXP. SMOOTHING." + str(e))
       
           self.forecast_cpu_model_selected = forecast_model
         #  self.forecast_cpu_predicted = forecast_cpu 

    except Exception as ex:
        self.logger.error("OptimalScaler: Error trying to predict the cpu error estimate for the different models. " + str(ex.message))

  def calculate_error_prediction_req_rate(self, req_rate):
    min_error_prediction = 1000000
    forecast_model = 0
    #forecast_req_rate = 0
    try:
           weight_avg_current = self.stat_utils.compute_weight_average(req_rate)
           
       #    try:
        #       weight_avg_predictions = self.stat_utils.compute_weight_average(self.forecast_list_req_rate[0])
         #      prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
           
          #     if min_error_prediction > prediction_error and prediction_error > 0:
           #        forecast_model = 0
            #       min_error_prediction = prediction_error
                   #forecast_req_rate  = weight_avg_predictions      
           #    self.logger.debug("OptimalScaler: Prediction error ARMA with req_rate: "+str(weight_avg_current)+" --  Prediction req_rate: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
      
     #      except Exception as e:  
      #          self.logger.warning("OptimalScaler: Warning trying to predict the req_rate error estimate for ARMA." + str(e))
           try:
                  
               weight_avg_predictions = self.stat_utils.compute_weight_average(self.forecast_list_req_rate[0])
               prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
           
               if min_error_prediction > prediction_error and prediction_error > 0:
                    forecast_model = 0
                    min_error_prediction = prediction_error
                   # forecast_req_rate  = weight_avg_predictions
               self.logger.debug("OptimalScaler: Prediction error AR with req_rate: "+str(weight_avg_current)+" --  Prediction req_rate: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
           
           except Exception as e:  
                self.logger.warning("OptimalScaler: Warning trying to predict the req_rate error estimate for AR." + str(e))
       
           try: 
               weight_avg_predictions = self.stat_utils.compute_weight_average(self.forecast_list_req_rate[1])
               prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
           
               if min_error_prediction > prediction_error and prediction_error > 0:
                   forecast_model = 1
                   min_error_prediction = prediction_error
                   #forecast_req_rate  = weight_avg_predictions
               self.logger.debug("OptimalScaler: Prediction error LR with req_rate: "+str(weight_avg_current)+" --  Prediction req_rate: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
           
           except Exception as e:  
                self.logger.warning("OptimalScaler: Warning trying to predict the req_rate error estimate for LR." + str(e))
       
           try:
               
               php_resp_data = [x for x in req_rate[0:12]]
               weight_avg_predictions = self.stat_utils.compute_weight_average(self.forecast_list_req_rate[2])
               prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
               if min_error_prediction > prediction_error and prediction_error > 0:
                   forecast_model = 2
                   min_error_prediction = prediction_error
                  # forecast_req_rate  = weight_avg_predictions
               self.logger.debug("OptimalScaler: Prediction error EXP. SMOOTHING with req_rate: "+str(weight_avg_current)+" --  Prediction req_rate: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
           except Exception as e:  
                self.logger.warning("OptimalScaler: Warning trying to predict the req_rate error estimate for EXP. SMOOTHING." + str(e))
       
           self.forecast_req_rate_model_selected = forecast_model
          # self.forecast_req_rate_predicted = forecast_req_rate 

    except Exception as ex:
        self.logger.error("OptimalScaler: Error trying to predict the req_rate error estimate for the different models. " + str(ex.message))


  def calculate_cpu_capacity(self, combination, inst_name=None):
      capacity = 0
      
      if inst_name != None:
          capacity = ( float(self.forecast_req_rate_predicted * self.req_complexity_rate) / float(len(combination) + 1) ) * self.capacity_inst_type[inst_name]
      
      for x in combination:
          capacity += ( float(self.forecast_req_rate_predicted * self.req_complexity_rate) / float( len(combination) + 1) ) * self.capacity_inst_type[x]

      return float(capacity) / float(len(combination) + 1)
   
  def add_new_resources (self, possible_combinations, max_performance_throughtput ):
    # self.logger.info( "add_new_resources: Adding additional resoruces starting ...")

     try:
      for x in self.vm_inst_types:
       if self.capacity_inst_type[x] > 0:
         cpu_capacity = self.calculate_cpu_capacity(possible_combinations, x)  
         if  cpu_capacity > max_performance_throughtput:
             #if performance_margin > 0 and performance_margin < (0.1 * 700):
             #    performance_margin = 0 
             aux = []
             for it in possible_combinations:
                 aux.append(it)
             aux.append(x)
             self.add_new_resources( aux, max_performance_throughtput)         
         elif cpu_capacity < max_performance_throughtput and cpu_capacity > self.min_performance_throughput:
             aux = []
             for it in possible_combinations:
                 aux.append(it)
             aux.append(x)
           #  self.logger.debug("horizontal_scaling_strategy: cpu_capacity "+str(cpu_capacity)+" combination "+str(aux)+" capacity inst: "+str(self.capacity_inst_type[x]))
             self.insert_combination(cpu_capacity, aux)
     # self.logger.info( "horizontal_scaling_strategy: Horizontal scaling strategy finished.")        
     except Exception as e:
         raise Exception("horizontal_scaling_strategy: Error calculating horizontal scaling strategy "+str(e))        
    
  def filter_scaling_strategy (self, current_combination, proposed_combination ):
      
      diff_combo = Counter(proposed_combination)
      diff_combo.subtract(current_combination)
          
      reject_strategy = False
      if self.cost_policy:
        for vm_type, count in diff_combo.items():
            if count < 0 :
                if not self.cost_controller.check_shutdown_constraint(self.nodes, vm_type, math.fabs(count)):
                    self.logger.info( "filter_scaling_strategy: Proposed strategy cannot be chosen due to the shutdown constraint: "+str(diff_combo))
                    return True
                    
               
  def replace_scaling_strategy_recursive (self, original_combination, current_combination, max_performance_throughtput, iterator ):
     if len(current_combination) > 6:
        searching_range = 6
     else:
         searching_range = len(current_combination)
         
     for cb in xrange(searching_range):
         if (cb > iterator):
             for x in self.vm_inst_types:
                 
                 if self.capacity_inst_type[x] > 0:
               #  if x != current_combination[cb]:
                 
                     combination = []
                     for it in xrange(searching_range):
                        if it != cb:
                            combination.append(current_combination[it]) 
                     
                     cpu_capacity = self.calculate_cpu_capacity(combination, x) 
                     combination.append(x)
                     
                     if not self.filter_scaling_strategy(original_combination, combination):
                     
                       if cpu_capacity < max_performance_throughtput and cpu_capacity > self.min_performance_throughput:
                           # self.logger.debug("vertical_scaling_strategy_recursive: cpu_capacity "+str(cpu_capacity)+" combination "+str(combination)+" capacity inst: "+str(self.capacity_inst_type[x]))
                           self.insert_combination(cpu_capacity, combination)
                     
                       if cb < (searching_range -1) :
                           self.replace_scaling_strategy_recursive(original_combination, combination, max_performance_throughtput, cb )
                       elif cpu_capacity > max_performance_throughtput:
                           self.add_new_resources( combination, max_performance_throughtput)
                         
  """
      This function calculates possible scaling strategies considering the current scaling strategy and replacing their resources for other with
      better hardware configuration.
  """    
  def replace_scaling_strategy (self,  current_combination, max_performance_throughtput ):
     self.logger.info( "replace_scaling_strategy: Vertical scaling strategy starting ...")
     
     if len(current_combination) > 6:
        searching_range = 6
     else:
         searching_range = len(current_combination)    
     try: 
       for cb in xrange(searching_range):
         for x in self.vm_inst_types:
            if self.capacity_inst_type[x] > 0:
                #  if x != current_combination[cb]:
                combination = []                
                for it in xrange(searching_range):
                   if it != cb:
                      combination.append(current_combination[it])               
                 
                cpu_capacity = self.calculate_cpu_capacity(combination, x)
                combination.append(x)
                
                if not self.filter_scaling_strategy(current_combination, combination):
                
                   if cpu_capacity < max_performance_throughtput and cpu_capacity > self.min_performance_throughput:
                       # self.logger.debug("calculate_scaling_in_strategy: cpu_capacity "+str(cpu_capacity)+" combination "+str(combination)+" capacity inst: "+str(self.capacity_inst_type[x]))
                       self.insert_combination(cpu_capacity, combination)
                
                   if cb < (searching_range -1) :
                       self.replace_scaling_strategy_recursive(current_combination, combination, max_performance_throughtput, cb )
                   elif cpu_capacity > max_performance_throughtput:
                       self.add_new_resources( combination, max_performance_throughtput)
                    
       self.logger.info( "replace_scaling_strategy: Vertical scaling strategy finished ")
     except Exception as e:
         raise Exception("replace_scaling_strategy: Error calculating vertical scaling strategy "+str(e))
     
  def calculate_scaling_strategy (self, current_combination, max_performance_throughtput ):
     try:
         self.propose_new_scaling_strategy(max_performance_throughtput)
         self.replace_scaling_strategy(current_combination, max_performance_throughtput)
     except Exception as e:
         raise Exception("calculate_scaling_strategy: Error calculating scaling combination "+str(e)) 
  """
  This function calculates possible scaling strategies without considering the current scaling strategy
  """
  def propose_new_scaling_strategy (self, max_performance_throughtput ):
     self.logger.info( "propose_new_scaling_strategy: Starting to calculate scaling IN strategies starting ...")

     try: 
       for x in self.vm_inst_types:
            if self.capacity_inst_type[x] > 0:

                cpu_capacity = self.forecast_req_rate_predicted * self.req_complexity_rate * self.capacity_inst_type[x]
                combination = []
                combination.append(x)           
                 
                if cpu_capacity < max_performance_throughtput and cpu_capacity > self.min_performance_throughput:
                  #  self.logger.debug("calculate_scaling_in_strategy: cpu_capacity "+str(cpu_capacity)+" combination "+str(combination)+" capacity inst: "+str(self.capacity_inst_type[x]))
                    self.insert_combination(cpu_capacity, combination)
                
                if cpu_capacity > max_performance_throughtput:
                    self.add_new_resources( combination, max_performance_throughtput)
                    
       self.logger.info( "propose_new_scaling_strategy: Calculated scaling IN strategies. ")
     except Exception as e:
         raise Exception("propose_new_scaling_strategy: Error calculating consolation scaling combination "+str(e))     
  
  def calculate_cost_strategy(self, cpu_capacity, number_machines, diff_strategy, new_strategy ):
      self.logger.info("calculate_cost_strategy:  new strategy "+ str(new_strategy)+ " difference strategy "+ str(diff_strategy)+" capacity: "+str(cpu_capacity))
      network_cost = 2
      os_activities_cost = 5
      storage_cost = 1
      no_changes = True

      penalty_config_remove = 2
      num_vmes_to_remove = 0
      # Calculate performance gain, infrastructure cost and configuration cost ( remove machines and add machines -- related with os activities, network cost)
      performance_capacity = cpu_capacity
      infra_cost = 0
      configuration_cost = 0
      for vm_type, count in new_strategy.items():
          if count > 0:
              infra_cost = infra_cost + (self.cost_controller.get_cost_vm(vm_type) * count)
              configuration_cost +=  (count * (network_cost + os_activities_cost + storage_cost))
     
      for vm_type, count in diff_strategy.items():
          #if count == 0:
          #    remove_vms = old_strategy[vm_type]
          #    configuration_cost = configuration_cost + penalty_config_removle - (remove_vms * (network_cost + os_activities_cost + storage_cost))
          if count < 0:
              num_vmes_to_remove += math.fabs(count)
              configuration_cost = configuration_cost + (math.fabs(count) *penalty_config_remove) - (math.fabs(count) * (network_cost + os_activities_cost + storage_cost))
              no_changes = False
          if count > 0:
              no_changes = False  
      
      if ((num_vmes_to_remove == number_machines) or no_changes):
          self.logger.info ("This strategy cannot be selected as it remove the main VM. ")
          return -1
      
      ###################################
      configuration_cost = float(1)/configuration_cost
      cost = infra_cost 
      slo_fulfillment_cost = ( (  float(performance_capacity) / self.max_performance_throughput ) * 100 * self.slo_violation_penalty )
      cost_strategy =  float(slo_fulfillment_cost) / cost        
      self.logger.info ("Strategy cost: "+str(cost_strategy)+ "-- slo_fulfillment_cost: "+str(slo_fulfillment_cost)+"-- Performance_capacity: "+str(performance_capacity)+" -- Infra cost: "+str(infra_cost)+" -- Config cost: "+str(configuration_cost))
    
      return cost_strategy

 # This function determine the type of instance to be added depending of the PERFORMANCE IMPROVEMENT + COST of a new VM.
  def remove_backend_vm_candidate(self, backend_nodes, backend_monitoring_data):
      vm_candidate = ''
      min_performance_index = 100000
      max_performance_index = 0
      vmes_perf = {}
      vmes_inst_types = []  
      try: 
       for backend_node in backend_nodes:  
          avg_cpu_user_node = self.stat_utils.compute_weight_average(backend_monitoring_data[backend_node.ip]['cpu_user'])
          avg_resp_time_user_node = self.stat_utils.compute_weight_average(backend_monitoring_data[backend_node.ip]['php_response_time'])
          avg_req_rate_user_node = self.stat_utils.compute_weight_average(backend_monitoring_data[backend_node.ip]['php_request_rate'])
          
          inst_type = self.cost_controller.get_type_instance(backend_node.ip)
          vmes_inst_types.append(inst_type)
          
          # Performance Improvement recommended considering a generic index of improvement...
          # Medium instance =   cpu >= 85 + slo violation >= 750 + req_rate > 5.0
          
          performance_index = (avg_cpu_user_node*30) + (avg_resp_time_user_node * 0.40) + (avg_req_rate_user_node * 120) 
          vmes_perf[backend_node.ip] = (performance_index, self.get_compute_units(inst_type))
          if performance_index > max_performance_index:
              max_performance_index = performance_index
       
       ## Release the machine with the LOWEST workload and closest time to the end of its hourly.
       min_cp_units = 100
       for ip in vmes_perf: 
          # It probably remove the bigger type of instance, in other words, to remove before huge, large, medium than small instances.
          (performance_idx, cp_units) = vmes_perf[ip]
          if 'high' in self.slo_fulfillment_degree or 'medium' in self.slo_fulfillment_degree:  
              if self.cost_controller.cost_shutdown_constraint(ip) and performance_idx < max_performance_index and cp_units < min_cp_units:
                  vm_candidate = ip
                  min_performance_index = performance_idx
          else:
              if self.cost_controller.cost_shutdown_constraint(ip) and performance_idx < max_performance_index:
                  vm_candidate = ip
                  min_performance_index = performance_idx
                      
       # Remove the VM from the cost controller data
       if (len(vm_candidate) > 0):
           self.cost_controller.remove_vm_usage(vm_candidate)
       else:
           return vm_candidate      
      except Exception as e:
          self.logger.error("remove_backend_vm_candidate: ERROR removing a VM ")      
      return vm_candidate
  

  def remove_vmes_type_candidate(self, backend_nodes, backend_monitoring_data, inst_type_to_remove, num_vmes_to_remove ):
      self.logger.info("remove_vm_type_candidate: Starting to remove several vmes "+str(num_vmes_to_remove)+" VMES with instance type: "+str(inst_type_to_remove))  
      vm_candidate = backend_nodes[0].ip
      
      vmes_candidate = []
      try:
          
       while num_vmes_to_remove > 0:
        min_performance_index = 100000
        for backend_node in backend_nodes:  
          if not backend_node.ip in vmes_candidate and num_vmes_to_remove > 0:
              avg_cpu_user_node = self.stat_utils.compute_weight_average(backend_monitoring_data[backend_node.ip]['cpu_user'])
              avg_resp_time_user_node = self.stat_utils.compute_weight_average(backend_monitoring_data[backend_node.ip]['php_response_time'])
              avg_req_rate_user_node = self.stat_utils.compute_weight_average(backend_monitoring_data[backend_node.ip]['php_request_rate'])
          
              inst_type = self.cost_controller.get_type_instance(backend_node.ip)
          
              if inst_type == inst_type_to_remove:
                # Performance Improvement recommended considering a generic index of improvement...
                # Medium instance =   cpu >= 85 + slo violation >= 750 + req_rate > 5.0
                
                performance_index = (avg_cpu_user_node*30) + (avg_resp_time_user_node * 0.50) + (avg_req_rate_user_node * 100) 
                self.logger.info("remove_vm_type_candidate: Calculating performance index "+str(performance_index)+" ip: "+str(backend_node.ip) )
                # It probably removes the bigger type of instance, in other words, to remove before huge, large, medium than small instances.
                if self.cost_controller.cost_shutdown_constraint and performance_index < min_performance_index:
               # if performance_index < min_performance_index:
                    vmes_candidate.append(backend_node.ip)
                    min_performance_index = performance_index
                    num_vmes_to_remove = num_vmes_to_remove - 1
      
       # Remove the VMES from the cost controller data
       for ip in vmes_candidate:
            self.cost_controller.remove_vm_usage(ip)
        
       return vmes_candidate    
      except Exception as e:
          self.logger.error("remove_vm_type_candidate: ERROR removing "+str(num_vmes_to_remove)+" VMES with instance type: "+str(inst_type_to_remove))       
          return vmes_candidate
  
  # This function determine the type of instance to be added depending of the PERFORMANCE IMPROVEMENT + COST of a new VM.
  def remove_vm_type_candidate(self, backend_nodes, backend_monitoring_data, inst_type_to_remove ):
      vm_candidate = backend_nodes[0].ip
      min_performance_index = 100000
      try:
        for backend_node in backend_nodes:  
          avg_cpu_user_node = self.stat_utils.compute_weight_average(backend_monitoring_data[backend_node.ip]['cpu_user'])
          avg_resp_time_user_node = self.stat_utils.compute_weight_average(backend_monitoring_data[backend_node.ip]['php_response_time'])
          avg_req_rate_user_node = self.stat_utils.compute_weight_average(backend_monitoring_data[backend_node.ip]['php_request_rate'])
          
          inst_type = self.cost_controller.get_type_instance(backend_node.ip)
          
          if inst_type == inst_type_to_remove:
              # Performance Improvement recommended considering a generic index of improvement...
              # Medium instance =   cpu >= 85 + slo violation >= 750 + req_rate > 5.0
          
              performance_index = (avg_cpu_user_node*30) + (avg_resp_time_user_node * 0.50) + (avg_req_rate_user_node * 100) 
          
              # It probably remove the bigger type of instance, in other words, to remove before huge, large, medium than small instances.
              if self.cost_controller.cost_shutdown_constraint and performance_index < min_performance_index:
                  vm_candidate = backend_node.ip
                  min_performance_index = performance_index
      
        # Remove the VM from the cost controller data
        self.cost_controller.remove_vm_usage(vm_candidate)
      except Exception as e:
          self.logger.error("remove_vm_type_candidate: ERROR removing a VM "+str(inst_type_to_remove))       
      return vm_candidate
  
  
    # This function determine the type of instance to be added depending of the PERFORMANCE IMPROVEMENT + COST of a new VM.
  def add_backend_vm_candidate(self, backend_nodes):
    instance_candidate = self.vm_inst_types[0]
    avg_cpu_backends = avg_req_rate_backends = avg_resp_time_backends = 0
      
    for backend_node in backend_nodes:  
        avg_cpu_user_node = self.stat_utils.compute_weight_average(self.backend_monitoring_data[backend_node.ip]['cpu_user'])
        avg_cpu_backends += avg_cpu_user_node
          
        avg_resp_time_user_node = self.stat_utils.compute_weight_average(self.backend_monitoring_data[backend_node.ip]['php_response_time'])
        avg_resp_time_backends += avg_resp_time_user_node
          
        avg_req_rate_user_node = self.stat_utils.compute_weight_average(self.backend_monitoring_data[backend_node.ip]['php_request_rate'])
        avg_req_rate_backends += avg_req_rate_user_node           
      
    return instance_candidate
 
 
  def obtain_cpu_forecast(self):
      ## If not data for prediction, we use linear regression model
      if self.forecast_cpu_predicted == 0:
          self.forecast_cpu_model_selected = 2
          self.forecast_cpu_predicted = self.stat_utils.compute_weight_average(self.forecast_list_cpu[2])
          iterator = 0 
          while self.forecast_cpu_predicted < 2 and iterator < 3:
              self.forecast_cpu_predicted = self.stat_utils.compute_weight_average(self.forecast_list_cpu[iterator])
              self.forecast_cpu_model_selected = iterator
              iterator += 1 
      else:
          self.forecast_cpu_predicted = self.stat_utils.compute_weight_average(self.forecast_list_cpu[self.forecast_cpu_model_selected])
      
      if self.forecast_cpu_predicted > 100:
         self.forecast_cpu_predicted = 100
      ## The difference with the new response time is shared among the current number of servers.
      self.logger.info("get_cpu_forecast_model: Number of machines to share the cpu_usage prediction: "+str(self.forecast_cpu_predicted)+ " Model selected: "+str(self.forecast_cpu_model_selected))
      return self.forecast_cpu_predicted
 
  def obtain_req_rate_forecast(self):
      ## If not data for prediction, we use linear regression model
      if self.forecast_req_rate_predicted == 0:
          self.forecast_req_rate_model_selected = 2
          self.forecast_req_rate_predicted = self.stat_utils.compute_weight_average(self.forecast_list_req_rate[2])
          iterator = 0 
          while self.forecast_req_rate_predicted < 2 and iterator < 3:
              self.forecast_req_rate_predicted = self.stat_utils.compute_weight_average(self.forecast_list_req_rate[iterator])
              self.forecast_req_rate_model_selected = iterator
              iterator += 1 
      else:
          self.forecast_req_rate_predicted = self.stat_utils.compute_weight_average(self.forecast_list_req_rate[self.forecast_req_rate_model_selected])
          
      ## The difference with the new response time is shared among the current number of servers.
      self.logger.info("get_req_rate_forecast_model: Number of machines to share the req_rate prediction: "+str(self.forecast_req_rate_predicted)+ " Model selected: "+str(self.forecast_req_rate_model_selected))  
      return self.forecast_req_rate_predicted
  
  def get_request_complexity_rate(self, combination_machines, cpu_usage, req_rate):
     complexity_rate = 0
     for name in combination_machines:
        complexity_rate += ( float(req_rate)/ float(len(combination_machines))) * self.capacity_inst_type[name]
     complexity_rate = float(complexity_rate) / float(len(combination_machines))
     
     complexity_rate = ( float(cpu_usage) / complexity_rate)
    
     return complexity_rate
 
  def calculate_adaptive_scaling(self, backend_nodes, combination_machines, cpu_capacity_now, req_rate_now, max_performance_throughput, min_performance_throughput, capacity_inst_type, cpu_data_last_hour, req_rate_data_last_hour):
    self.logger.info( "calculate_adaptive_scaling: calculating the optimal strategy to provision: "+str(cpu_capacity_now)+" req_rate "+str(req_rate_now) +" with max perf: "+str(max_performance_throughput))
    
    strategy = []
    final_combination = []
    self.strategy_max_performance = 0
    self.scaling_decision = []
    self.nodes = []
    self.nodes = backend_nodes
    
    self.max_performance_throughput = max_performance_throughput
    self.min_performance_throughput = min_performance_throughput
    
    #If max_performance is lower than min performance, it could create a huge loop.
    if (self.max_performance_throughput < self.min_performance_throughput and self.max_performance_throughput > 10):
          self.min_performance_throughput = self.max_performance_throughput - 5
    elif self.max_performance_throughput < 10:
          raise Exception("calculate_adaptive_scaling: MAX performance is lower than 10, aborting operation.")
    
    try:       
    
      """ Classification of the vm instance type by analizing or establishing 
          its max throughput from the monitoring data or compute_units * capacity_previous_vm
        """ 
      vm_clusters = self.classification.clustering_vmes(self.iaas_driver, capacity_inst_type)
      self.capacity_inst_type = self.classification.get_capacities_vmes()
      self.logger.info( "calculate_adaptive_scaling: capacity_inst_types "+str(self.capacity_inst_type))
      
      try:
          self.prediction_evaluation(cpu_data_last_hour, req_rate_data_last_hour)
          self.req_complexity_rate = self.get_request_complexity_rate(combination_machines,  self.obtain_cpu_forecast(), self.obtain_req_rate_forecast())
      except Exception as e:
          self.logger.error("calculate_adaptive_scaling: Error trying to predict req_rate and cpu_usage future values")
          self.logger.info("calculate_adaptive_scaling: Proceeding to calculate the req. complexity rate using current values.")
          self.req_complexity_rate = self.get_request_complexity_rate(combination_machines, cpu_capacity_now, req_rate_now)
          self.forecast_cpu_predicted = cpu_capacity_now
          self.forecast_req_rate_predicted = req_rate_now 
      
      self.logger.info( "calculate_adaptive_scaling: Cpu capacity predicted "+str(self.forecast_cpu_predicted)+" Forecast req_rate: "+str( self.forecast_req_rate_predicted)+" Req_complexity rate: "+str( self.req_complexity_rate ))
   
      self.calculate_scaling_strategy(combination_machines, max_performance_throughput)
      
      self.logger.info( "calculate_adaptive_scaling: Find the best scaling decision: "+str(self.scaling_decision))     
          
      if 'low' in self.slo_fulfillment_degree:
          selected_cost_strategy = 0
      else:
          selected_cost_strategy = 100000
      
      current_combo = Counter(combination_machines)
      #medium_capacity = self.get_strategy_with_medium_capacity()
      strategies = []
      
      for combination, (cpu_capacity) in self.scaling_decision:
          diff_combo = Counter(combination)
          diff_combo.subtract(current_combo)
          new_combo = Counter(combination)
          
          reject_strategy = False
          ## FILTER THE SCALING DECISIONS ##
          if self.cost_policy:
              for vm_type, count in diff_combo.items():
                  if count < 0:
                      if not self.cost_controller.check_shutdown_constraint(backend_nodes, vm_type, math.fabs(count)):
                          reject_strategy = True
                          self.logger.info( "calculate_adaptive_scaling: Strategy cannot be chosen due to the shutdown constraint: "+str(diff_combo))
                      
          if not reject_strategy:
              cost_strategy = self.calculate_cost_strategy(cpu_capacity, len(combination_machines), diff_combo, new_combo)
              
              if cost_strategy != -1:
                  strategies.append((cost_strategy, (diff_combo)))
                  if 'high' in self.slo_fulfillment_degree and selected_cost_strategy > cost_strategy:
                      selected_cost_strategy = cost_strategy
                      final_combination = diff_combo
                  
                  if 'low' in self.slo_fulfillment_degree and selected_cost_strategy < cost_strategy:
                      self.logger.info( "calculate_adaptive_scaling: Low combination "+str(diff_combo))
                      selected_cost_strategy = cost_strategy
                      final_combination = diff_combo
      
      if 'medium' in self.slo_fulfillment_degree:
          strategies = sorted(strategies)
          selected_cost_strategy, final_combination = strategies[ ( (len(strategies) - 1)/ 2 ) ]
          
      if 'medium_up' in self.slo_fulfillment_degree:
          strategies = sorted(strategies)
          size = (len(strategies) ) /2
          position = (size ) / 2 
          selected_cost_strategy, final_combination = strategies[ (size + position ) ]
          
      if 'medium_down' in self.slo_fulfillment_degree:
          strategies = sorted(strategies)
          size = (len(strategies) ) /2
          position = (size ) / 2 
          selected_cost_strategy, final_combination = strategies[ (size - position ) ]
      
      self.logger.info( "calculate_adaptive_scaling: Found the best scaling combination "+str(len(final_combination)))
      
      ## Get the list of removal and addition operations over the current configuration ##
      if len(final_combination) > 0:    
          for vm_type, count in final_combination.items():
              if count > 0:
                  strategy.append( ('add', (vm_type, count)) )
              elif count < 0:
                  strategy.append( ('remove', (vm_type, math.fabs(count))) )

      else:
          self.logger.info( "calculate_adaptive_scaling: the final combination is not initialized. ")
          strategy.append( ('add', (self.vm_inst_types[0], 1)) )
      
      #print( "calculate_optimal_scaling: the optimal strategy is: "+str(strategy))
      self.logger.info( "calculate_adaptive_scaling: the optimal strategy is: "+str(strategy))
    except Exception as e:
        strategy.append( ('add', (self.vm_inst_types[0], 1)) )
        self.logger.error("calculate_adaptive_scaling: ERROR calculating the optimal strategy. "+str(e))
        self.logger.info( "calculate_adaptive_scaling: the optimal strategy is: "+str(strategy))
    return strategy


"""
log.init('/tmp/provisioning.log')
logger = log.create_logger(__name__)

cpu_capacity_now = 77.1103495237
req_rate_now =  21.9655486288 
#machines = ['smallDAS4','smallDAS4','smallDAS4','smallDAS4','smallDAS4','smallDAS4']
machines = ['small','small','small','medium','small','highcpu-medium','small','small','small','large']
## Response time over the capacity to provision
max_performance_throughput = 24
min_performance_throughput = 25
capacity_inst_type = {'small':16.948815723978793, 'medium':8.4744078619893966, 'highcpu-medium':3.3897631447957588, 'large':4.2372039309946983}

proxy_data_last_hour = [545.69562172999997, 545.69562172999997, 441.606628, 554.30688499999997, 526.01910399999997, 491.614868, 491.6653968, 446.27877799999999, 635.60095200000001, 468.16665599999999, 516.57464600000003, 574.65771500000005, 483.42341286999999, 570.04074273000003, 561.98468826999999, 453.65597773000002, 538.62559252999995, 526.16086859999996, 523.20369019999998, 505.96257500000002, 476.82776873, 553.71298847000003, 493.00422393000002, 480.28483260000002, 503.52328499999999, 568.49365807000004, 524.23978633000002, 508.84982093000002, 613.43579107000005, 548.45334500000001, 613.54003120000004, 491.78946960000002, 568.56158027000004, 571.48976679999998, 567.41963733, 547.53992479999999, 505.06610506999999, 540.71610099999998, 544.65902086999995, 503.42377499999998]
req_rate_data_last_hour = [16.695537999999999, 16.695537999999999, 18.189114, 18.412656999999999, 17.325749999999999, 19.692634999999999, 18.972180067, 21.905076999999999, 14.148123999999999, 18.777467999999999, 17.841688000000001, 17.240235999999999, 19.770084532999999, 17.762196932999998, 18.098334866999998, 19.626281533, 19.251116667000002, 19.427029133000001, 18.678852466999999, 17.387211666999999, 18.716564999999999, 16.911638799999999, 18.573069799999999, 20.252419466999999, 18.545598999999999, 16.777595933000001, 18.3376044, 18.7648808, 16.323291666999999, 16.662968466999999, 15.885371666999999, 20.051085532999998, 16.933206599999998, 16.678704332999999, 16.718633532999998, 17.241867599999999, 19.008421866999999, 18.301489533000002, 17.332130332999999, 17.689810067]
cpu_data_last_hour = [12.968710123761291, 12.045175374333436, 13.299074707040612, 14.157111409593872, 12.916905924358069, 11.948878580729311, 12.253559163397009, 12.783024902360376, 13.259119466229738, 13.517056884785646, 13.860635172500611, 14.435431722088621, 14.460155029295654, 13.794925537109375, 12.606280517578126, 13.133436279296875, 13.862753906249999, 13.390195312500001, 13.530623372366637, 13.55076416015625, 13.52784912109375, 13.25841634124585, 13.028142496776734, 13.336978759765625, 13.698874918620971, 13.447457275390626, 12.802264404296874, 12.839682617187499, 13.187479248046873, 12.623699951172853, 11.929654947885766, 12.514261881572203, 13.183179524596838, 13.000252278573242, 13.413894042968749, 13.404158528678735, 12.789139811280947, 12.93058349609375, 13.182653808604528, 23.927074381343751, 26.512377929687499, 23.474253743494508, 23.762827555598388, 21.738722737796873, 20.062038981124878, 21.921065673828124, 22.506134033203125, 23.216481933593748, 22.141812744140623, 20.683477783204101, 19.675634765630775, 19.098445638171203, 21.58716959641168, 22.700664062391994, 21.688954264406249, 21.333193359379553, 21.558011881405946, 19.79627848315625, 19.752958170566465, 20.092142741069484, 20.587090657576418, 20.26444335944408, 21.201560872387539, 23.658177897112608, 31.505064697453125, 35.699981689453125, 37.999988199882196, 38.34636271165936, 35.675315755178346, 36.404727376147697, 37.661254882826171, 40.343863932458945, 38.001667480277284, 37.795519205755802, 37.755097656155947, 37.504861653728028, 35.545933431007789, 33.918498535266849, 33.611215820301368, 33.121662190845029, 30.204765218096412, 31.359166666662503, 15.174286295498241, 18.470497233118799, 23.621304931640623, 25.133043212890627, 24.326697184350341, 22.450963134701478, 23.735482584644629, 22.681146647168553, 24.342922363247776, 23.726484374967839, 23.642494303421692, 23.427176920503726, 23.908339029843205, 24.368121744833616, 22.567405599077844, 22.872874348946191, 21.955171712336547, 19.022296142588562, 18.918493245420716, 20.903662923219912, 24.611416015551804, 24.164335937492893, 24.164335937492893, 18.949761962890626, 24.024493408203124, 22.435280354798831, 23.569177246093751, 21.886962890625, 24.891834309818908, 20.280156249950316, 19.574493815025942, 20.12017089848068, 20.12017089848068, 21.352642822265626, 21.773738199942628, 21.773738199942628, 20.070255533847593, 20.193523762970948, 20.115481770827966, 20.115481770827966, 27.217795409987428, 27.217795409987428, 26.945654296875002, 25.248937988281249, 30.255114746093753, 29.920068359375001, 29.81816731776172, 29.709863281250001, 23.751257324218749, 33.402807617187499, 30.628552246093751, 28.258142089843751, 28.616595865894727, 32.174260253785157, 32.039567870898679, 32.161200358090866, 28.809265136876956, 34.44313720721582, 28.698729654868409, 30.242176106728515, 27.748766276229492, 25.697473958555907, 36.382856445269653, 36.206166992185061, 30.53955078125, 26.482547200348634, 31.855469563989502, 31.71986409500769, 28.072640787783328, 30.475313313708078, 24.613721516800904, 26.414215494721315, 28.680037434719239, 33.079997558712279, 27.649654134350097, 27.870077311242184, 30.527284342207764, 28.313210449097291, 27.685663248709595, 28.754234212291628]

list_cpu = cpu_data_last_hour
list_req_rate = req_rate_data_last_hour

#list_cpu = [458.24850500000002, 461.54809567000001, 460.65900240000002, 474.60502307000002, 480.65465867, 466.41224567, 442.16476460000001, 469.56639619999999, 480.78247699999997, 467.88605553000002, 465.65277099999997, 449.61819487000002, 449.06991620000002, 449.54956099999998, 476.09070860000003, 511.01344619999998, 445.33874539999999, 433.26447587000001, 483.7437726, 478.870563, 493.74761560000002, 442.91928080000002, 449.91933212999999, 472.38562000000002, 482.80751140000001, 477.146704, 457.70957827000001, 487.225932, 487.75607300000001, 490.53954067000001, 558.627881, 524.19101966999995, 491.01383433000001, 515.37299567000002, 499.0010006, 497.47164466999999, 512.03360207000003, 544.10522060000005, 551.20673799999997, 518.86596880000002]

#2013-04-26 09:11:54,736 INFO __main__ IP: 10.100.4.179 Usage (DAYS:HOURS:MIN:SEC): 0:1:5:42 Cost: 0.065$
#2013-04-26 09:11:54,736 INFO __main__ IP: 10.100.4.181 Usage (DAYS:HOURS:MIN:SEC): 0:0:45:12 Cost: 0.065$
#2013-04-26 09:11:54,736 INFO __main__ IP: 10.100.4.180 Usage (DAYS:HOURS:MIN:SEC): 0:1:01:42 Cost: 0.065$
#2013-04-26 09:11:54,736 INFO __main__ IP: 10.100.4.183 Usage (DAYS:HOURS:MIN:SEC): 0:0:24:42 Cost: 0.065$
nodea = ServiceNodePerf(vmid='i-3e5c8056', ip='1.1.1.1', runProxy=False, runWeb=False, runBackend=True, provisioningState='RUNNING')
nodeb = ServiceNodePerf(vmid='i-3e5c8057', ip='1.1.1.2', runProxy=False, runWeb=False, runBackend=True, provisioningState='RUNNING')
nodec = ServiceNodePerf(vmid='i-3e5c8058', ip='1.1.1.3', runProxy=False, runWeb=False, runBackend=True, provisioningState='RUNNING')
noded = ServiceNodePerf(vmid='i-3e5c8059', ip='1.1.1.4', runProxy=False, runWeb=False, runBackend=True, provisioningState='RUNNING')
nodee = ServiceNodePerf(vmid='i-3e5c8060', ip='1.1.1.5', runProxy=False, runWeb=False, runBackend=True, provisioningState='RUNNING')
nodef = ServiceNodePerf(vmid='i-3e5c8061', ip='1.1.1.6', runProxy=False, runWeb=False, runBackend=True, provisioningState='RUNNING')
nodeg = ServiceNodePerf(vmid='i-3e5c8062', ip='1.1.1.7', runProxy=False, runWeb=False, runBackend=True, provisioningState='RUNNING')
nodeh = ServiceNodePerf(vmid='i-3e5c8063', ip='1.1.1.8', runProxy=False, runWeb=False, runBackend=True, provisioningState='RUNNING')
nodei = ServiceNodePerf(vmid='i-3e5c8064', ip='1.1.1.9', runProxy=False, runWeb=False, runBackend=True, provisioningState='RUNNING')

#backend_nodes = {'i-3e5c8056':nodea, 'i-3e5c8057':nodeb, 'i-3e5c8058':nodec, 'i-3e5c8059':noded,'i-3e5c8060':nodee,'i-3e5c8061':nodef,'i-3e5c8062':nodeg,'i-3e5c8063':nodeh,'i-3e5c8064':nodei}
backend_nodes = {nodea, nodeb, nodec, noded, nodee, nodef, nodeg, nodeh, nodei}
cost_controller = Cost_Controller(logger, 'OPENNEBULA')
cost_controller.update_vm_usage('1.1.1.1',1371716045.0,'small')
cost_controller.update_vm_usage('1.1.1.2',1371729750.0,'small')
cost_controller.update_vm_usage('1.1.1.3',1371936685.0,'medium')
cost_controller.update_vm_usage('1.1.1.4',1371715449.0,'small')
cost_controller.update_vm_usage('1.1.1.5',1371719768.0,'highcpu-medium')
cost_controller.update_vm_usage('1.1.1.6',1371727231.0,'small')
cost_controller.update_vm_usage('1.1.1.7',1371727236.0,'small')
cost_controller.update_vm_usage('1.1.1.8',1371936685.0,'small')
cost_controller.update_vm_usage('1.1.1.9',1371936685.0,'large')
#1366199826.0
#1366201056.0
cost_controller.print_vm_cost()
optimal = Strategy_Finder(logger, False, 'OPENNEBULA', cost_controller, 'high', True, 2)



optimal.calculate_adaptive_scaling( backend_nodes, machines, cpu_capacity_now, req_rate_now, max_performance_throughput, min_performance_throughput, capacity_inst_type, list_cpu, list_req_rate )
"""
    