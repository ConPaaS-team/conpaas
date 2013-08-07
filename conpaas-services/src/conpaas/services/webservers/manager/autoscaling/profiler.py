"""
@author: fernandez
"""
import itertools

class Profiler:
    
    def __init__(self,  logger_autoscaling, slo, cost_controller , max_cpu_usage, min_cpu_usage, upper_thr_slo, lower_thr_slo):
        self.max_cpu_usage = max_cpu_usage
        self.min_cpu_usage = min_cpu_usage
        self.upper_thr_slo = upper_thr_slo
        self.lower_thr_slo = lower_thr_slo
        self.logger = logger_autoscaling
        
        self.machines = {}
        self.slo = slo
        
        self.vm_type_ideal_throughput = {}
        self.vm_type_max_throughput = {}
        self.max_iterations = 6
        
        self.cost_controller = cost_controller
  
    def get_vm_type_ideal_throughput(self, inst_type):
        return self.vm_type_ideal_throughput[inst_type]
  
    def calculate_ideal_throughput(self, inst_type):
      self.logger.debug("calculate_ideal_throughput: starting the computation for instance "+ str(inst_type))
      try:
          if self.machines[inst_type]:
              resp_times_filtered = []
              cpu_user_values_filtered = []
              req_rates_filtered = []
              array_monitoring_data = self.machines[inst_type]
              
              self.logger.info("calculate_ideal_throughput: Adapting to the  threshold values.")
              for it in range(array_monitoring_data[4][0]):
                   for resp_time, cpu_usage, req_rate in itertools.izip(array_monitoring_data[0][it], array_monitoring_data[1][it], array_monitoring_data[2][it]):
                       ## Add cpu_usage as we found data with 0.10 cpu_usage; and 80% when having 500ms, and request rate upper than 0.5
                      #FIXME: Changed resp_time as lower value are used in large and highcpu-medium instances
                      # if resp_time > (0.4 * self.slo) and resp_time <= (0.75 * self.slo) and cpu_usage < 75 and cpu_usage > 25 and req_rate > 0.5:
                       if resp_time > (0.4 * self.slo) and resp_time <= (self.upper_thr_slo * self.slo) and cpu_usage < self.max_cpu_usage and cpu_usage > self.min_cpu_usage and req_rate > 0.5:
                           resp_times_filtered.append(resp_time)
                           cpu_user_values_filtered.append(cpu_usage)
                           req_rates_filtered.append(req_rate)

                      
               # Get the average of Resp times between 50% and 75% of the SLO 
              self.logger.info("calculate_ideal_throughput: Calculating the average of response time:" + str(resp_times_filtered)) 
              self.logger.info("calculate_ideal_throughput: Calculating the average of cpu :" + str(cpu_user_values_filtered))
              self.logger.info("calculate_ideal_throughput: Calculating the average of req_rate :" + str(req_rates_filtered)) 
              
              cpu_user_avg = 0
              #cpu_sys_avg = 0
              req_rate_avg = 0
              #resp_time_avg = 0
              if len(resp_times_filtered) == 0 or len(cpu_user_values_filtered)==0 or len(req_rates_filtered)==0:
                   
                 try:
                    if self.vm_type_ideal_throughput[inst_type]:
                      max_throughput = self.vm_type_ideal_throughput[inst_type]
                 except Exception:
                      self.logger.error("calculate_ideal_throughput: ERROR cannot find inst_type in "+ str(self.vm_type_ideal_throughput))
                      max_throughput = 0
                      
              else:
                   # Get the average of CPU user and Req. rate between 50% and 75% of the SLO
                #  resp_time_avg = self.stat_utils.compute_average(resp_times_filtered)   
                  cpu_user_avg =  self.stat_utils.compute_average(cpu_user_values_filtered) 
                  req_rate_avg =   self.stat_utils.compute_average(req_rates_filtered)
                  max_throughput = float(cpu_user_avg) / req_rate_avg  
                  self.vm_type_ideal_throughput[inst_type] = max_throughput      
                  
              self.logger.info("Ideal throughput of inst_type: "+inst_type+"  Cpu speed: "+str(max_throughput)+" cpu_avg: "+str(cpu_user_avg)+" req_avg: "+str(req_rate_avg))   
              return  max_throughput
      except Exception as e:
          self.logger.error("calculate_ideal_throughput: ERROR calculating ideal throughput "+ str(e))
          return 0

    def get_vm_type_max_throughput(self, inst_type):
        return self.vm_type_max_throughput[inst_type]
    
    def calculate_max_instance_throughput(self, inst_type, array_monitoring_data):
      self.logger.debug("calculate_max_instance_throughput: starting the computation for instance "+ str(inst_type))
      try:
              max_resp_time = max_cpu = max_req_rate = 0
              
              self.logger.info("calculate_max_instance_throughput: Adapting to the  threshold values.")
              for it in range(array_monitoring_data[4][0]):
                   for resp_time, cpu_usage, req_rate in itertools.izip(array_monitoring_data[0][it], array_monitoring_data[1][it], array_monitoring_data[2][it]):
                       if resp_time > (0.5 * self.slo) and resp_time <= (self.upper_thr_slo * self.slo) and cpu_usage < 80 and cpu_usage > self.min_cpu_usage and req_rate > 0.5:
                           if (max_resp_time < resp_time):
                               max_resp_time = resp_time
                               max_cpu = cpu_usage
                               max_req_rate = req_rate 
              
              #if max_resp_time == 0 or max_cpu or max_req_rate==0:
                   
              #   try:
              #      if self.vm_type_max_throughput[inst_type]:
              #        max_throughput = self.vm_type_max_throughput[inst_type]
              #   except Exception:
              #        self.logger.error("calculate_max_instance_throughput: ERROR cannot find inst_type in "+ str(self.vm_type_max_throughput))
              #        max_throughput = 0
                      
              else:
                  try:
                      
                    if self.vm_type_max_throughput[inst_type]:
                       (cpu_inst, req_inst) = self.vm_type_max_throughput[inst_type]
                       if req_inst <= max_req_rate:
                           self.vm_type_max_throughput[inst_type] = (max_cpu,max_req_rate)
                           
                  except Exception as e:
                    self.vm_type_max_throughput[inst_type] = (max_cpu,max_req_rate)      
                  
              self.logger.info("Max throughput of inst_type: "+inst_type+"  Cpu: "+str(max_cpu)+" Resp time: "+str(max_resp_time)+" Req: "+str(max_req_rate))   
              
      except Exception as e:
          self.logger.error("calculate_max_instance_throughput: ERROR calculating max throughput "+ str(e))


    def store_workload(self, inst_type, ip, backend_monitoring_data):
      array_monitoring_data = [[0 for i in range(6)] for j in range(5)]
      
      if ( len(self.machines) == 0 ):
          num_iterations = array_monitoring_data[4][0]
          array_monitoring_data[0][num_iterations] =  backend_monitoring_data[ip]['php_response_time'] 
          array_monitoring_data[1][num_iterations] = backend_monitoring_data[ip]['cpu_user'] 
          array_monitoring_data[2][num_iterations] =  backend_monitoring_data[ip]['php_request_rate']
          array_monitoring_data[3][num_iterations] =  backend_monitoring_data[ip]['cpu_system']
          num_iterations = num_iterations + 1  
          array_monitoring_data[4][0] =  num_iterations
          self.logger.debug("store_machine_workload: Data to add instance "+ str(inst_type)+"  --> "+ str(array_monitoring_data))
          self.machines[inst_type] = array_monitoring_data

          ## Gather information about the maximum throughput of one instance type.
          self.calculate_max_instance_throughput(inst_type, array_monitoring_data)
      else:
          try:
              if self.machines[inst_type]:
                  array_monitoring_data = self.machines[inst_type]
                  num_iterations = array_monitoring_data[4][0]
                  if array_monitoring_data[4][0] == self.max_iterations:
                      num_iterations = 0
                  
                  array_monitoring_data[0][num_iterations] =  backend_monitoring_data[ip]['php_response_time'] 
                  array_monitoring_data[1][num_iterations] = backend_monitoring_data[ip]['cpu_user'] 
                  array_monitoring_data[2][num_iterations] =  backend_monitoring_data[ip]['php_request_rate']
                  array_monitoring_data[3][num_iterations] =  backend_monitoring_data[ip]['cpu_system']
                  num_iterations = num_iterations + 1  
                  array_monitoring_data[4][0] =  num_iterations
                  
                  self.machines[inst_type] = array_monitoring_data
                  
                  ## Gather information about the maximum throughput of one instance type.
                  self.calculate_max_instance_throughput(inst_type, array_monitoring_data)
                  self.logger.debug("store_machine_workload: Data to add instance "+ str(inst_type)+"  --> "+ str(array_monitoring_data))
                     
          except:
              num_iterations = array_monitoring_data[4][0]
              array_monitoring_data[0][num_iterations] =  backend_monitoring_data[ip]['php_response_time'] 
              array_monitoring_data[1][num_iterations] = backend_monitoring_data[ip]['cpu_user'] 
              array_monitoring_data[2][num_iterations] =  backend_monitoring_data[ip]['php_request_rate']
              array_monitoring_data[3][num_iterations] =  backend_monitoring_data[ip]['cpu_system']
              num_iterations = num_iterations + 1  
              array_monitoring_data[4][0] =  num_iterations
              
              self.machines[inst_type] = array_monitoring_data
              
              ## Gather information about the maximum throughput of one instance type.
              self.calculate_max_instance_throughput(inst_type, array_monitoring_data)
              self.logger.debug("store_machine_workload: Data to add instance "+ str(inst_type)+"  --> "+ str(array_monitoring_data))

   
    def store_instance_workload(self, backend_nodes, backend_monitoring_data):
      inst_type_ip = {}
      
      for backend_node in sorted(backend_nodes):
          if (len(backend_monitoring_data[backend_node.ip]['php_response_time']) > 20):
              name =  self.cost_controller.get_type_instance(backend_node.ip)   
              inst_type_ip[name]= backend_node.ip
      
      for type, ip in inst_type_ip.iteritems():        
          self.store_workload(type, ip, backend_monitoring_data)  
          

