"""

Central component of this autoscaling system.

@author: fernandez
"""

import httplib, json
import sys
from subprocess import Popen, PIPE
import memcache
import math
import socket
from ConfigParser import ConfigParser
from time import time, sleep
import os
from conpaas.core.https.client import conpaas_init_ssl_ctx, jsonrpc_get, jsonrpc_post, https_post, https_get
from conpaas.services.webservers.manager.autoscaling import log 
from conpaas.services.webservers.manager.autoscaling.performance import ServicePerformance, ServiceNodePerf, StatUtils
from conpaas.services.webservers.manager.autoscaling.cost_aware import Cost_Controller
from conpaas.services.webservers.manager import client
from conpaas.services.webservers.manager.autoscaling.dynamic_load_balancer import Dynamic_Load_Balancer
from conpaas.services.webservers.manager.autoscaling.profiler import Profiler
#from conpaas.services.webservers.manager.autoscaling.prediction.prediction_models_test import Prediction_Models
from conpaas.services.webservers.manager.autoscaling.prediction.prediction_models import Prediction_Models
from conpaas.services.webservers.manager.autoscaling.strategy.adaptive_strategy import Strategy_Finder

from conpaas.services.webservers.manager.autoscaling.monitoring import Monitoring_Controller

from collections import deque
import traceback
from datetime import datetime
from multiprocessing.pool import ThreadPool
import itertools
from threading import Thread



PATH_LOG_FILE = '/tmp/provisioning.log'
log.init(PATH_LOG_FILE)
logger = log.create_logger('Autoscaling')

MANAGER_HOST = 'localhost'
MANAGER_PORT = 443 

PS_IDLE = 'IDLE'
PS_RUNNING = 'RUNNING'

TIME_BTW_SCALING_PREDICTIONS =  1800
TIME_BTW_SCALING_ACTIONS =  600

MAX_CPU_USAGE = 75
MIN_CPU_USAGE = 25
UPPER_THRS_SLO = 0.75
LOWER_THRS_SLO = 0.35

## This two boundaries represents the percentage according to the SLO for which the prediction will be triggered.
UPPER_THRS_PREDICTION = 0.6 
LOWER_THRS_PREDICTION = 0.4 

## This variable represents the number of times the system will retry a scaling operation (remove,add)
NUM_RETRIES_SCALING_ACTION = 3


## This variable is used during the analysis of monitoring data to increase the awareness of our system when having isolated SLO violations.
WEIGHT_SLO_VIOLATION = 2

MIN_NUM_BACKENDS = 1
MIN_NUM_WEBS = 1

class Queue:
    def __init__(self, lst=[], size=0):
        self.q = deque(lst)
        self.size = size
    def push(self, seq):
        if self.q.__len__() <= self.size:
          self.q.append(seq)
        else:
          self.q.popleft()
          self.q.append(seq)
    
  
class ProvisioningManager:
  """
  The ProvisioningManager takes decisions about adding and removing nodes from the service.
  """
  
## FIXME: CHANGED TO BE ADAPTED TO QCOW2 BOOTING TIME. ###
  time_between_changes = TIME_BTW_SCALING_ACTIONS
  time_between_scaling_predictions = TIME_BTW_SCALING_PREDICTIONS
##########################################################
  

  ganglia_rrd_dir = '/var/lib/ganglia/rrds/conpaas/'
  
  def __init__(self, config_parser):
   try: 
    self.slo = 700
    
    self.weight_slow_violation = WEIGHT_SLO_VIOLATION
    
    self.web_monitoring_data = {}
    self.backend_monitoring_data = {}
    self.proxy_monitoring_data = {}
    
    
    self.last_change_time = 0
    self.last_scaling_operation = 0
    self.calculate_scaling_error = False
    
    self.predictor = Prediction_Models(logger)
    self.trigger_prediction = 0
    
    ## FIXME: Size is 5 due to an excessive number of items to be predicted, please repair this part.
    ##, as we want to store the monitoring data during 60min, considering 5min between iterations
    self.predictorScaler_cpu_usage_1h = Queue( [] , 5)
    self.predictorScaler_req_rate_1h = Queue( [] , 5)
    
    self.forecast_model_selected = 0 
    self.forecast_resp_predicted = 0
    self.forecast_list = {}
    
    self.pool_predictors = ThreadPool(processes=5)
    
    self.killed_backends = []

    self.trigger_weight_balancing = False
    self.autoscaling_running = True
    
    self.iaas_driver = config_parser.get('iaas', 'DRIVER').upper()
    
    self.cost_controller = Cost_Controller(logger, self.iaas_driver)
    
    ## Parameters to establish a preference for selecting the most appropriate resource.
    self.optimal_scaling = Strategy_Finder(logger, self.iaas_driver, self.cost_controller, 'low', True, self.weight_slow_violation) 
  
    self.stat_utils = StatUtils()
    
    self.monitoring =  Monitoring_Controller( logger, self.cost_controller, config_parser, '/root/config.cfg', MANAGER_HOST, MANAGER_PORT, PS_RUNNING, self.ganglia_rrd_dir)

    self.dyc_load_balancer = Dynamic_Load_Balancer(logger, MANAGER_HOST, MANAGER_PORT, client)
    
    self.profiler = Profiler(logger, self.slo, self.cost_controller, MAX_CPU_USAGE, MIN_CPU_USAGE, UPPER_THRS_SLO, LOWER_THRS_SLO )
 
   except Exception as e:
      logger.critical('Scaler: Error when initializing the ProvisioningManager in scaler.py \n' + str(e))
   

  def log_monitoring_data(self):
    logger.debug('**** Web monitoring data: *****\n' + str(self.web_monitoring_data))
    logger.debug('**** Backend monitoring data: *****\n' + str(self.backend_monitoring_data))
    logger.debug('**** Proxy monitoring data: *****\n' + str(self.proxy_monitoring_data))
              
     
    
  def prediction_evaluation_proxy(self, proxy_ip, php_resp_data):
    
    try:        
            forecast_list_aux = {}
            php_resp_filtered = []
            for i in php_resp_data:
                if i > 0:
                    php_resp_filtered.append(i)
            
            logger.debug("PhP response time list data: "+str(php_resp_filtered))           
           
            async_result_ar =  self.pool_predictors.apply_async(self.predictor.auto_regression, (php_resp_filtered,30))
            async_result_lr =  self.pool_predictors.apply_async(self.predictor.linear_regression, (php_resp_filtered,30))
            async_result_exp_smoothing =  self.pool_predictors.apply_async(self.predictor.exponential_smoothing, (php_resp_filtered,12))
            async_result_var =  self.pool_predictors.apply_async(self.predictor.vector_auto_regression, (php_resp_filtered, php_resp_filtered, 30))
          #  async_result_arma =  self.pool_predictors.apply_async(self.predictor.arma, (php_resp_filtered,30))
                                           
            forecast_list_aux[1] = async_result_lr.get()
            forecast_list_aux[2] = async_result_exp_smoothing.get()
            forecast_list_aux[3] = async_result_var.get()
            forecast_list_aux[0] = async_result_ar.get()
           # forecast_list_aux[0] = async_result_arma.get()
            
            try:
               logger.debug("Getting the forecast response time for the best model in the previous iteration "+str(self.forecast_model_selected)) 
               weight_avg_predictions = self.stat_utils.compute_weight_average(forecast_list_aux[self.forecast_model_selected])
               
               if weight_avg_predictions > 0:
                   self.forecast_resp_predicted  = weight_avg_predictions      
               logger.debug("Prediction value for model "+str(self.forecast_model_selected)+"--  Prediction php_resp_time: "+str(self.forecast_resp_predicted))
      
            except Exception as e:  
                logger.warning("Warning trying to predict a future value for the model." + str(e))
               
            self.forecast_list[proxy_ip] = forecast_list_aux
    except Exception as e:
        logger.error("Error trying to predict the future response_time values. "+ str(e))\
        

        
  def store_predictorScaler_workload(self, cpu_usage, req_rate):
      list_cpu = []
      list_req_rate = []
      for cpu, req_rate in itertools.izip(cpu_usage, req_rate):
          if cpu > 10 and req_rate > 0:
              list_cpu.append(cpu)
              list_req_rate.append(req_rate)
      logger.debug("store_predictorScaler_workload: Filtered cpu "+str(list_cpu))
      logger.debug("store_predictorScaler_workload: Filtered req_rate "+str(list_req_rate))        
      self.predictorScaler_cpu_usage_1h.push(list_cpu)
      self.predictorScaler_req_rate_1h.push(list_req_rate)
     ## logger.debug("store_proxy_workload: Proxy historic data "+ str(self.historic_proxy_1h.q))
    
  def calculate_error_prediction(self, php_resp_data, ip):
    forecast_list_aux = {}
    min_error_prediction = 1000000
    forecast_model = 0
    forecast_resp = 0
    try:    
             
           logger.debug("calculate_error_prediction: with ip: "+str(ip))
        #   php_resp_data = self.proxy_monitoring_data[ip]['php_response_time_lb']
           #php_resp_data = [x for x in php_resp_data[0:30]]         
           forecast_list_aux = self.forecast_list[ip] 
           logger.debug("calculate_error_prediction: once obtained the forecast_list. ")
           weight_avg_current = self.stat_utils.compute_weight_average_response(php_resp_data, self.slo, self.weight_slow_violation)
       #    try:
        #       weight_avg_predictions = self.stat_utils.compute_weight_average(forecast_list_aux[0])
         #      prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
           
          #     if min_error_prediction > prediction_error and prediction_error > 0:
           #        forecast_model = 0
            #       min_error_prediction = prediction_error
                  # forecast_resp  = weight_avg_predictions      
             #  logger.debug("Prediction error ARMA with php_resp_time: "+str(weight_avg_current)+" --  Prediction php_resp_time: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
      
           #except Exception as e:  
            #    logger.warning("Warning trying to predict the error estimate for ARMA." + str(e))
           try:
                  
               weight_avg_predictions = self.stat_utils.compute_weight_average(forecast_list_aux[0])
               prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
           
               if min_error_prediction > prediction_error and prediction_error > 0:
                    forecast_model = 0
                    min_error_prediction = prediction_error
                    #forecast_resp  = weight_avg_predictions
               logger.debug("Prediction error AR with php_resp_time: "+str(weight_avg_current)+" --  Prediction php_resp_time: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
           
           except Exception as e:  
                logger.warning("Warning trying to predict the error estimate for AR." + str(e))
       
           try: 
               weight_avg_predictions = self.stat_utils.compute_weight_average(forecast_list_aux[1])
               prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
           
               if min_error_prediction > prediction_error and prediction_error > 0:
                   forecast_model = 1
                   min_error_prediction = prediction_error
                   #forecast_resp  = weight_avg_predictions
               logger.debug("Prediction error LR with php_resp_time: "+str(weight_avg_current)+" --  Prediction php_resp_time: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
           
           except Exception as e:  
                logger.warning("Warning trying to predict the error estimate for LR." + str(e))
       
           try:
               
              # php_resp_data = [x for x in php_resp_data[0:12]]
               weight_avg_predictions = self.stat_utils.compute_weight_average(forecast_list_aux[2])
               prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
               
               if min_error_prediction > prediction_error and prediction_error > 0:
                   forecast_model = 2
                   min_error_prediction = prediction_error
                   #forecast_resp  = weight_avg_predictions
               logger.debug("Prediction error EXP. SMOOTHING with php_resp_time: "+str(weight_avg_current)+" --  Prediction php_resp_time: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
           except Exception as e:  
                logger.warning("Warning trying to predict the error estimate for EXP. SMOOTHING." + str(e))
                
           try:
               
              # php_resp_data = [x for x in php_resp_data[0:12]]
               weight_avg_predictions = self.stat_utils.compute_weight_average(forecast_list_aux[3])
               prediction_error = math.fabs( weight_avg_current - weight_avg_predictions )
               
               if min_error_prediction > prediction_error and prediction_error > 0:
                   forecast_model = 3
                   min_error_prediction = prediction_error
                   #forecast_resp  = weight_avg_predictions
               logger.debug("Prediction error VAR with php_resp_time: "+str(weight_avg_current)+" --  Prediction php_resp_time: "+str(weight_avg_predictions)+" Error: "+str(prediction_error))
           except Exception as e:  
                logger.warning("Warning trying to predict the error estimate for VAR." + str(e))
       
           self.forecast_model_selected = forecast_model
    
    except Exception as ex:
        logger.error("Error trying to predict the error estimate for the different models. " + str(ex))

  def obtain_prediciton_decision(self, greater, slo):
    logger.info("Obtain_prediciton_decision model: " + str(self.forecast_model_selected) + " Php resp: "+str(self.forecast_resp_predicted) + " SLO: "+str(slo))
    if self.forecast_resp_predicted == 0:
        logger.critical("Forecast_resp_predicted: ERROR all the prediction models failed predicting a future value. ")
        return True
    
    if (greater and  self.forecast_resp_predicted > slo):
        logger.info("Forecast_resp_predicted is greater than slo. ")
        return True
    elif not greater and self.forecast_resp_predicted < slo:
        logger.info("Forecast_resp_predicted is lower than slo. ")
        return True
    else:
        logger.info("Forecast_resp_predicted don't do anything. ")
        return False
    
  def calculate_strategy(self, avg_cpu_backends_now, backend_nodes, req_rate_backends, cpu_usage_backends):
      logger.info("calculate_strategy: req_rate_backends  "+str(req_rate_backends)+" cpu: "+str(cpu_usage_backends))
      max_performance_throughtput = MAX_CPU_USAGE
      min_performance_throughtput = MIN_CPU_USAGE
      
      ## In cloud infrastructures, VMes perform close to the SL O violation with cpu usage quite lower than 75.
      if avg_cpu_backends_now < MAX_CPU_USAGE:
          max_performance_throughtput = avg_cpu_backends_now
      
      capacity_inst_type = {}
      combination_machines = []

      ## Initialize the maximum capacity for each type of instance based on the monitoring data ###
      for name, cost in self.cost_controller.get_instance_prices()[self.iaas_driver].iteritems():
          capacity_max_inst_type = self.profiler.calculate_ideal_throughput(name)
          logger.info("Calculate max capacity instance "+str(name)+" : "+str(capacity_max_inst_type))
          capacity_inst_type[name] = capacity_max_inst_type
      
      for backend_node in backend_nodes:
          inst_type =  self.cost_controller.get_type_instance(backend_node.ip) 
          combination_machines.append(inst_type)

      list_req_rate_data = []
      for value in self.predictorScaler_req_rate_1h.q:
            list_req_rate_data.extend(value)
      list_cpu_data = []
      for value in self.predictorScaler_cpu_usage_1h.q:
            list_cpu_data.extend(value)        
       
      logger.info("calculate_strategy: list_cpu_data  "+str(list_cpu_data))
      strategy = self.optimal_scaling.calculate_adaptive_scaling(backend_nodes, combination_machines, cpu_usage_backends, req_rate_backends, max_performance_throughtput, min_performance_throughtput, capacity_inst_type, list_cpu_data, list_req_rate_data)
             
      logger.info("calculate_strategy: Final strategy: "+str(strategy))
       
      return strategy        
   
  def consolidate_vmes(self, nodes):
       logger.info("consolidate_vmes: Initializing consolidate ")
        
       ## Check if the rest of nodes can support the req_rate of another VM, then we release it.
       for node in nodes:
           req_rate = self.stat_utils.compute_weight_average(self.stat_utils.filter_cpu_data(self.backend_monitoring_data[node.ip]['php_request_rate']))
           inst_type = self.cost_controller.get_type_instance(node.ip)
           try:
             compute_units = self.optimal_scaling.get_compute_units(inst_type)
           
             ## Verify if we can remove the machine
             if self.cost_controller.cost_shutdown_constraint(node.ip):
               
               for node_aux in nodes:
                   if not node_aux.ip in node.ip:
                       inst_type_check = self.cost_controller.get_type_instance(node_aux.ip)
                       try:
                           (cpu_inst, req_rate_inst) = self.profiler.get_vm_type_max_throughput(inst_type_check)
                           if req_rate_inst > 0:
                                req_rate_check = self.stat_utils.compute_weight_average(self.stat_utils.filter_cpu_data(self.backend_monitoring_data[node_aux.ip]['php_request_rate']))
                                if ( (req_rate_inst - req_rate_check) >= req_rate):
                                    return node.ip
                           ## No maximum data so lets check other possibilities        
                           else:
                                if self.optimal_scaling.get_compute_units(inst_type_check) > compute_units:
                                    return node.ip
                       except:
                                if self.optimal_scaling.get_compute_units(inst_type_check) > compute_units:
                                    return node.ip
       
           except Exception as ex:
                logger.critical("consolidate_vmes: ERROR when trying to remove a vm with ip: "+str(node.ip))
      
       ## There is not any possible vm to be released...
       return ''
 
    
  def decide_actions(self):
    n_web_to_add = n_web_to_remove = 0
    n_backend_to_add = n_backend_to_remove = 0
    
    avg_web_req_rate_lb = avg_web_resp_time_lb = 0
    avg_backend_req_rate_lb = avg_backend_resp_time_lb = 0
    avg_cpu_user_backend = avg_cpu_web = 0
    backends_req_rate = 0
    
    ret = {'add_web_nodes': 0, 'remove_web_nodes': 0, 'add_backend_nodes': 0, 'remove_backend_nodes': 0, 'vm_backend_instance': 'small', 'vm_web_instance': 'small', 'node_ip_remove':''}
    
    perf_info = self.monitoring._performance_info_get()
    web_nodes = perf_info.getWebServiceNodes()
    backend_nodes = perf_info.getBackendServiceNodes()
    proxy_nodes = perf_info.getProxyServiceNodes()
    
    self.profiler.store_instance_workload(backend_nodes, self.backend_monitoring_data)
    
    current_time = time()
    if (current_time - self.last_change_time < self.time_between_changes):
      self.trigger_weight_balancing = True  
      logger.info('Configuration was recently updated, not making any decisions for now...')
      return ret    
    
    # For the moment we assume only 1 proxy node
    for proxy_node in proxy_nodes:
      if ( self.trigger_prediction == 1):
          self.calculate_error_prediction(self.proxy_monitoring_data[proxy_node.ip]['php_response_time_lb'],proxy_node.ip)
          self.trigger_prediction = 0
      
        
      avg_web_resp_time_lb =  self.stat_utils.compute_weight_average_response(self.proxy_monitoring_data[proxy_node.ip]['web_response_time_lb'], self.slo, self.weight_slow_violation)
      avg_web_req_rate_lb =  self.stat_utils.compute_weight_average(self.proxy_monitoring_data[proxy_node.ip]['web_request_rate_lb'])
      logger.debug('Found average value for proxy web request rate: %s web response time: %s' \
                   % (str(avg_web_req_rate_lb), str(avg_web_resp_time_lb)))
      
      if avg_web_resp_time_lb > UPPER_THRS_SLO * self.slo:
        n_web_to_add = 1
        
      if avg_web_resp_time_lb < LOWER_THRS_SLO * self.slo:
        n_web_to_remove = 1
     
      
      avg_backend_req_rate_lb = self.stat_utils.compute_weight_average(self.proxy_monitoring_data[proxy_node.ip]['php_request_rate_lb'])
      #proxy_backends_filtered_data = self.stat_utils.filter_response_data(self.proxy_monitoring_data[proxy_node.ip]['php_response_time_lb'])
      proxy_backends_filtered_data = self.proxy_monitoring_data[proxy_node.ip]['php_response_time_lb']
      avg_backend_resp_time_lb = self.stat_utils.compute_weight_average_response(proxy_backends_filtered_data, self.slo, self.weight_slow_violation ) 
      logger.debug('Found average value for proxy backend request rate: %s backend response time: %s' \
                    % (str(avg_backend_req_rate_lb), str(avg_backend_resp_time_lb)))
      
      
      ##### TRIGGER PREDICTION EVALUATION #######
      if (avg_backend_resp_time_lb > UPPER_THRS_PREDICTION * self.slo ):
          self.trigger_prediction = 1
          self.prediction_evaluation_proxy(proxy_node.ip, proxy_backends_filtered_data)
          
      if (avg_backend_resp_time_lb < LOWER_THRS_PREDICTION * self.slo ):
          self.trigger_prediction = 1
          self.prediction_evaluation_proxy(proxy_node.ip, proxy_backends_filtered_data)
      ############################################
      
      if avg_backend_resp_time_lb > UPPER_THRS_SLO * self.slo and self.obtain_prediciton_decision( True, UPPER_THRS_SLO * self.slo):
        n_backend_to_add = 1
           
      if avg_backend_resp_time_lb < 10 or (avg_backend_resp_time_lb < LOWER_THRS_SLO * self.slo and self.obtain_prediciton_decision( False, LOWER_THRS_SLO * self.slo)):
        n_backend_to_remove = 1
        
    #### CPU AVERAGE VERIFICATION #####         
    for web_node in web_nodes:
      avg_cpu_web_node = self.stat_utils.compute_weight_average(self.web_monitoring_data[web_node.ip]['cpu_user'])
      logger.info('Average CPU usage per Web with IP '+web_node.ip+' '+str(avg_cpu_web_node))
      avg_cpu_web += avg_cpu_web_node
    
    avg_cpu_web = float(avg_cpu_web) / len(web_nodes)
    
    req_rate_backends_list = []
    cpu_backends_list = []
    sum_php_req_rate_backends = 0
    
    for backend_node in backend_nodes:
      cpu_backends = self.stat_utils.filter_cpu_data(self.backend_monitoring_data[backend_node.ip]['cpu_user'])
      avg_cpu_user_node = self.stat_utils.compute_weight_average(cpu_backends)
      req_rate_backends = self.stat_utils.filter_cpu_data(self.backend_monitoring_data[backend_node.ip]['php_request_rate'])
      php_req_rate_node = self.stat_utils.compute_weight_average(req_rate_backends)
      sum_php_req_rate_backends += php_req_rate_node
      
      logger.info('Average CPU usage per Backend with IP '+backend_node.ip+' '+str(avg_cpu_user_node)+ ' Req_rate:' +str(php_req_rate_node))
      if avg_cpu_user_node > MAX_CPU_USAGE:
          self.trigger_weight_balancing = True
      avg_cpu_user_backend += avg_cpu_user_node  
      
      if len(req_rate_backends_list) ==0:
          req_rate_backends_list = req_rate_backends
      else: 
          req_rate_backends_list =  [(req_rate_list_a + req_rate_list_b) for req_rate_list_a, req_rate_list_b in itertools.izip_longest(req_rate_backends_list, req_rate_backends, fillvalue=0)]
      
      if len(cpu_backends_list) == 0:
          cpu_backends_list = cpu_backends
      else: 
          cpu_backends_list =  [(cpu_list_a + cpu_list_b) / 2 for cpu_list_a, cpu_list_b in itertools.izip_longest(cpu_backends_list, cpu_backends, fillvalue=0)]    
       
    avg_cpu_user_backend = float(avg_cpu_user_backend) / len(backend_nodes)
    
    ### Check the cpu usage to add or remove backends... As shown in the plots, there is a correlation between cpu usage and sla violations. ###
    if (avg_cpu_user_backend > MAX_CPU_USAGE):
        n_backend_to_add = 1
        n_backend_to_remove = 0    
    elif (len(backend_nodes) > 1)  and (avg_cpu_user_backend < 35) and (n_backend_to_add == 0):
        n_backend_to_remove = 1    
        n_backend_to_add = 0
    
    if (avg_cpu_web > MAX_CPU_USAGE) and (len(web_nodes) < MIN_NUM_BACKENDS + 1):
       n_web_to_add = 1
       n_web_to_remove = 0
    elif (len(web_nodes) > 1)  and (avg_cpu_web < MIN_CPU_USAGE) and (n_web_to_add == 0):
        n_backend_to_remove = 1    
        n_backend_to_add = 0
    
    logger.info('Total average CPU usage (user) backend: %f' % avg_cpu_user_backend)
    logger.info('Total average CPU usage (user) web: %f' % avg_cpu_web)
    
    self.store_predictorScaler_workload(cpu_backends_list, req_rate_backends_list)
    
    #######################################################################   
    
    if (current_time - self.last_scaling_operation >= self.time_between_scaling_predictions and self.calculate_scaling_error):
      logger.info('ProvisioningV3_proxy: Calculating the prediction error of our last scaling action...')
      list_data_cpu = list_data_req_rate = []
      for value in self.predictorScaler_cpu_usage_1h.q:
            list_data_cpu.extend(value)

      for value in self.predictorScaler_req_rate_1h.q:
            list_data_req_rate.extend(value)  
            
      self.optimal_scaling.calculate_error_prediction_cpu(list_data_cpu)
      self.optimal_scaling.calculate_error_prediction_req_rate(list_data_req_rate)
      
      self.calculate_scaling_error = False
      logger.info("ProvisioningV3_proxy: Prediction cpu model: "+str(self.optimal_scaling.get_cpu_prediction_model())+" and Cpu prediction: "+str(self.optimal_scaling.get_cpu_prediction()))
      logger.info("ProvisioningV3_proxy: Prediction req_rate model: "+str(self.optimal_scaling.get_req_rate_prediction_model())+" and Req_rate prediction: "+str(self.optimal_scaling.get_req_rate_prediction()))
    
    ### CONDITIONS TO ABORT A WEB OR BACKEND REMOVAL OPERATION ###
    
    abort_backend_removal = 0
    abort_web_removal = avg_cpu_after_removal =0
    consolidate_vm = ''
    
    if  len(backend_nodes) > MIN_NUM_BACKENDS and n_backend_to_remove > 0:
       avg_cpu_after_removal = ( float(avg_cpu_user_backend) / (len(backend_nodes) - 1)) + avg_cpu_user_backend
       logger.info("ProvisioningV3: Prediction avg_cpu_after_removal: "+str(avg_cpu_after_removal))
       
    if  len(backend_nodes) > MIN_NUM_BACKENDS and n_backend_to_remove > 0 and avg_cpu_user_backend > 35: 
       
        if len(backend_nodes) == (MIN_NUM_BACKENDS + 1):
            inst_type_1 = self.cost_controller.get_type_instance(backend_nodes[0].ip)
            inst_type_2 = self.cost_controller.get_type_instance(backend_nodes[1].ip)
            if not inst_type_1 in inst_type_2:
                consolidate_vm = self.consolidate_vmes(backend_nodes)
        else:       
            consolidate_vm = self.consolidate_vmes(backend_nodes)
        logger.info("ProvisioningV3: consolidate_vm "+str(consolidate_vm))
    
 #   if(  (avg_backend_req_rate_lb / len(backend_nodes) > 1.3 and avg_cpu_user_backend > 40 )
  #        or (avg_cpu_user_backend > 40 and self.obtain_prediciton_decision( True, 0.5 * self.slo) ) 
   #       or (avg_backend_req_rate_lb / len(backend_nodes) > 1.3 and avg_backend_resp_time_lb > 0.5 * self.slo) ):
    #    abort_backend_removal = 1  
        
    if(  ( avg_cpu_after_removal > MAX_CPU_USAGE and len(consolidate_vm) == 0)
          or (avg_cpu_user_backend > 40 and self.obtain_prediciton_decision( True, 0.5 * self.slo) ) 
          or (avg_backend_req_rate_lb / len(backend_nodes) > 1.3 and avg_backend_resp_time_lb > 0.5 * self.slo) ):
        abort_backend_removal = 1     
        
    if( (avg_web_req_rate_lb  >= 4.0 and avg_cpu_web > 40) or (avg_web_req_rate_lb  >= 4.0 and avg_web_resp_time_lb > 0.5 * self.slo) ):
        abort_web_removal = 1 
        
    if (len(backend_nodes) == MIN_NUM_BACKENDS or n_backend_to_add != 0 or abort_backend_removal == 1): 
      n_backend_to_remove = 0
    if (len(web_nodes) == MIN_NUM_WEBS or n_web_to_add != 0 or abort_web_removal == 1):
      n_web_to_remove = 0

    ##################################################################
    
    ret['add_web_nodes'] = n_web_to_add
    ret['remove_web_nodes'] = n_web_to_remove
    ret['add_backend_nodes'] = n_backend_to_add
    ret['remove_backend_nodes'] = n_backend_to_remove
    
    ##### DECIDE VM CANDIDATE OR INSTANCE TPYE TO ADD OR REMOVE #####
    
    if n_web_to_add > 0:
        ret['vm_web_instance'] = self.optimal_scaling.get_vm_inst_types()[0]
    
    if n_web_to_remove > 0:
        ret['node_ip_remove'] = web_nodes[0].ip
    
    
    if n_backend_to_remove > 0:
        self.trigger_prediction = 0
        if len(consolidate_vm) == 0:
            ret['node_ip_remove'] = self.optimal_scaling.remove_backend_vm_candidate(backend_nodes, self.backend_monitoring_data)
        else:
            ret['node_ip_remove'] = consolidate_vm
    
    if n_backend_to_add > 0:
        self.trigger_prediction = 0
        strategy = self.calculate_strategy(avg_cpu_user_backend, backend_nodes, sum_php_req_rate_backends, avg_cpu_user_backend)
        self.calculate_scaling_error = True
        self.last_scaling_operation = time()
        ret['vm_backend_instance'] = strategy
                
    self.cost_controller.print_vm_cost()
      
    logger.info('Provisioning decisions: %s' % str(ret))
    return ret

          
  def execute_actions(self, actions):
    n_backend_to_add = actions['add_backend_nodes']
    n_backend_to_remove = actions['remove_backend_nodes']
    n_web_to_add = actions['add_web_nodes']
    n_web_to_remove = actions['remove_web_nodes']
    
    vm_web_type = actions['vm_web_instance']
    ip=actions['node_ip_remove']
    
    strategy = []
    strategy = actions['vm_backend_instance']
    
    if ( n_backend_to_add> 0 and len(strategy) > 0 or n_web_to_add > 0):
      logger.info('Adding nodes: %d , backend strategy: %s ' % (n_web_to_add, str(strategy) ))
      if n_backend_to_add > 0:
          concurrent_ops = False
          perf_info = self.monitoring._performance_info_get()
          backend_nodes = perf_info.getBackendServiceNodes()
          
          for op, (vm_type, num) in sorted(strategy):
            if 'add' in op:                
                if not concurrent_ops:
                    concurrent_ops = True
                num_retries = NUM_RETRIES_SCALING_ACTION
                added_node = False
                while not added_node and num_retries > 0:
                    try:
                        logger.info('Adding backend nodes, quantity: %s , vm_type: %s ' % (str(num), str(vm_type) ))
                        nodes = client.add_nodes(MANAGER_HOST, MANAGER_PORT, web=0, backend=num, cloud='default', vm_backend_instance=vm_type, vm_web_instance=vm_web_type)
                        added_node = True
                    except Exception as ex:
                        logger.warning('Error when trying to add a node: '+str(ex))
                        num_retries = num_retries - 1
                        logger.warning('Node cannot be added at this time, retrying in 1min. Number of additional retries: '+str(num_retries))
                        added_node = False
                        sleep(100)
                    
            if 'remove' in op:
                logger.info('Removing backend nodes, quantity: %s , vm_type: %s ' % (str(num), str(vm_type) ))
                vmes_ip = []
                vmes_ip = self.optimal_scaling.remove_vmes_type_candidate(backend_nodes, self.backend_monitoring_data, vm_type, num)
                    
                for vm_ip in vmes_ip:
                    if concurrent_ops:
                        ## Before I used 60, but it seems it is not enough for the system to recognize the changes... 
                        sleep(100)
                    num_retries = NUM_RETRIES_SCALING_ACTION 
                    removed_node = False
                    while not removed_node and num_retries > 0:
                        try:
                            nodes = client.remove_nodes(MANAGER_HOST, MANAGER_PORT, web=0, backend=1, node_ip=vm_ip)
                            remove_node = True

                            server_id = self.dyc_load_balancer.get_updated_backend_weights_id(vm_ip)
                            self.killed_backends.append(server_id)
                            self.dyc_load_balancer.remove_updated_backend_weights(server_id)
                            self.dyc_load_balancer.remove_updated_backend_weights_id(vm_ip)

                        except Exception as ex:
                            logger.warning('Error when trying to remove a node: '+str(ex)) 
                            num_retries = num_retries - 1
                            logger.warning('Node cannot be removed at this time, retrying in 1min. Number of additional retries: '+str(num_retries))
                            removed_node = False
                            sleep(100)
                            
          self.last_change_time = time()
            
      if n_web_to_add > 0:
           num_retries = NUM_RETRIES_SCALING_ACTION       
           added_node = False 
           while not added_node and num_retries > 0: 
              try:    
                  logger.info('Adding a web node: %d , inst type: %s ' % (n_web_to_add, str(vm_web_type) ))
                  vm_backend_type=self.optimal_scaling.get_vm_inst_types()[0]
                  nodes = client.add_nodes(MANAGER_HOST, MANAGER_PORT, web=n_web_to_add, backend=0, cloud='default', vm_backend_instance=vm_backend_type, vm_web_instance=vm_web_type)
                  added_node = True 
              except Exception as ex:         
                  logger.warning('Error when trying to add a web node: '+str(ex))
                  num_retries = num_retries - 1
                  logger.warning('Web node cannot be added at this time, retrying in 1min. Number of additional retries: '+str(num_retries))
                  added_node = False
                  sleep(100)
                      
           self.last_change_time = time()    
          
    if ((n_backend_to_remove > 0 or n_web_to_remove > 0) and len(ip) > 0):
      logger.info('Removing web nodes: %d , backend nodes: %d ' % (n_web_to_remove, n_backend_to_remove))
      nodes = client.remove_nodes(MANAGER_HOST, MANAGER_PORT, web=n_web_to_remove, backend=n_backend_to_remove, node_ip=ip)
      if n_backend_to_remove > 0:
        try:
          server_id = self.dyc_load_balancer.get_updated_backend_weights_id(ip)
          self.killed_backends.append(server_id)
          self.dyc_load_balancer.remove_updated_backend_weights(server_id)
          self.dyc_load_balancer.remove_updated_backend_weights_id(ip)
        except:
          logger.warning("Backend weight cannot be deleted for the backend with ip "+str(ip))
      self.last_change_time = time()
      logger.info('After triggering the remove operation web nodes: %d , backend nodes: %d ' % (n_web_to_remove, n_backend_to_remove))
      self.last_change_time = time()
      
  def collect_monitoring_data(self):
      self.monitoring.init_collect_monitoring_data()
               
      self.web_monitoring_data = self.monitoring.collect_monitoring_data_web()
      self.backend_monitoring_data = self.monitoring.collect_monitoring_data_backend()
      self.proxy_monitoring_data = self.monitoring.collect_monitoring_data_proxy()
      
      if len(self.proxy_monitoring_data) == 0 or len(self.backend_monitoring_data) == 0 or len(self.web_monitoring_data) == 0:
          return False
      
      return True
  
  def stop_provisioning(self):
      self.autoscaling_running = False
      #try:
       #   os.remove(PATH_LOG_FILE)
      #except OSError as e:
       #   logger.critical('stop_provisioning: Error when removing the autoscaling log '+str(e))
  
  def do_provisioning(self,slo,cooldown_time, slo_fulfillment_degree):
    step_no = 0 
    self.slo = slo
    self.time_between_changes = cooldown_time*60
    self.autoscaling_running = True 
    self.optimal_scaling.set_slo_fulfillment_degree(slo_fulfillment_degree)
    logger.info('Autoscaling: Starting with QoS autoscaling: '+str(slo_fulfillment_degree))
    
    try: 
     while self.autoscaling_running:
      step_no += 1
      tstart = datetime.now()  
      
      print 'Synchronizing node info with manager...'
      self.monitoring.nodes_info_update(self.killed_backends)
      print "Collecting monitoring data..."

      ret = self.collect_monitoring_data()
      
      if not ret:
          logger.warning('Monitoring data was not properly retrieved, will retry later...')
          sleep(60)
          continue
      else:
          self.log_monitoring_data()  
      
          actions = self.decide_actions()
          self.execute_actions(actions)
      
      
          n_backend_to_add = actions['add_backend_nodes']
          n_backend_to_remove = actions['remove_backend_nodes']
          n_web_to_add = actions['add_web_nodes']
          n_web_to_remove = actions['remove_web_nodes']
      
          # Adjust node weights every 3 steps
          if ( (step_no % 2 == 0 and n_backend_to_add == 0 and n_backend_to_remove == 0 \
             and n_web_to_add == 0 and n_web_to_remove == 0) or self.trigger_weight_balancing ):
              logger.info('Calling adjust_node_weights ...')
              Thread(target=self.dyc_load_balancer.adjust_node_weights(self.monitoring, self.backend_monitoring_data)).start()
              self.trigger_weight_balancing = False
    
      
          tend = datetime.now()
          logger.info('--> EXECUTION TIME SCALING DECISION: %s ' % str(tend-tstart))
          
          sleep(300)
    
      
     logger.info('Autoscaling: Terminated.')
    except Exception as ex:
        logger.critical('Autoscaling: Error in the autoscaling system '+str(ex))
