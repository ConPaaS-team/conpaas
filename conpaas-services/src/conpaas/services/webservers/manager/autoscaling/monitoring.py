
"""
Monitoring Controller collects all the informantion extracted using Ganglia monitoring system.

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
from os import path, listdir
from conpaas.core.https.client import conpaas_init_ssl_ctx, jsonrpc_get, jsonrpc_post, https_post, https_get
from conpaas.core import log 
from conpaas.services.webservers.manager.autoscaling.performance import ServicePerformance, ServiceNodePerf, StatUtils
from conpaas.services.webservers.manager.autoscaling.cost_aware import Cost_Controller
from conpaas.services.webservers.manager import client


from collections import deque
import traceback
from datetime import datetime
from multiprocessing.pool import ThreadPool
import itertools

DEFAULT_NUM_CPU = 1.0
DEFAULT_RAM_MEMORY = '1034524.0'

class Monitoring_Controller:
  def __init__(self, logger, cost_controller, config_parser, config_file_path, manager_host, manager_port, process_state, ganglia_rrd_dir):
      self.cost_controller = cost_controller
      self.config_parser = config_parser
      self.manager_host = manager_host
      self.manager_port = manager_port
      self.logger = logger
      self.process_state = process_state
      self.ganglia_rrd_dir = ganglia_rrd_dir
      self.last_collect_time = time()
      
      self.stat_utils = StatUtils()
      
      try:
          self.config_parser.read(config_file_path)
      except:
          print >>sys.stderr, 'Failed to read configuration file'
          sys.exit(1)
    
      #initialize a memcache client
      memcache_addr = config_parser.get('manager', 'MEMCACHE_ADDR')
      
      if memcache_addr == '':
          print >>sys.stderr, 'Failed to find memcache address in the config file'
          sys.exit(1)
      
      self.memcache = memcache.Client([memcache_addr])
      self.perf_info = ServicePerformance()
      self._performance_info_set(self.perf_info)
      
      self.monitoring_metrics_web = ['web_request_rate', 'web_response_time', 'cpu_user', 'boottime']
      self.monitoring_metrics_backend = ['php_request_rate', 'php_response_time', 'cpu_user', 'cpu_system', 'cpu_num', 'mem_total', 'boottime']
      self.monitoring_metrics_proxy = ['web_request_rate_lb', 'web_response_time_lb', \
                                     'php_request_rate_lb', 'php_response_time_lb', 'cpu_user', 'boottime']
     

  def _performance_info_get(self):
    return self.memcache.get('performance_info')

  def _performance_info_set(self, perf_info):
    self.memcache.set('performance_info', perf_info)

  def nodes_info_update(self, killed_backends):
    #conpaas_init_ssl_ctx(self.certs_dir, 'manager')
    print('MANAGER %s' % self.manager_host) 
    print('PORT %s' % self.manager_port) 
    
    nodes = client.list_nodes(self.manager_host, self.manager_port)
    self.logger.debug('Got update info from manager')
    
    perf_info = self._performance_info_get()
    
    perf_info.reset_role_info()
    
    self.logger.debug('Updating nodes...')
    for node_id in nodes['proxy']:
      node = perf_info.serviceNodes.get(node_id)
      if node != None:
        node.registered_with_manager = True
        node.isRunningProxy = True
      else:
        perf_info.serviceNodes[node_id] = ServiceNodePerf(node_id, '', True, False, False, self.process_state)
    
    for node_id in nodes['web']:
      node = perf_info.serviceNodes.get(node_id)
      if node != None:
        node.registered_with_manager = True
        node.isRunningWeb = True
      else:
        perf_info.serviceNodes[node_id] = ServiceNodePerf(node_id, '', False, True, False, self.process_state)
    
    for node_id in nodes['backend']:
      node = perf_info.serviceNodes.get(node_id)
      if node != None:
        node.registered_with_manager = True
        node.isRunningBackend = True
      else:
        perf_info.serviceNodes[node_id] = ServiceNodePerf(node_id, '', False, False, True, self.process_state)
        
    self.logger.info('Filtering backend nodes killed_backends : '+str(killed_backends)+' '+str(perf_info.serviceNodes))    
    for id, node in perf_info.serviceNodes.items():
      if node.ip == '':
        response = client.get_node_info(self.manager_host, self.manager_port, id)
        node.ip = response['serviceNode']['ip']
      if node.registered_with_manager == False:
        del perf_info.serviceNodes[id]
      ####FIXME TO FILTER REMOVE OF BACKENDS #####
      if id in killed_backends:
          self.logger.info('Filtered backend  with id: '+str(id))
          try:
            del perf_info.serviceNodes[id]
          except:
            self.logger.warning('Backend already removed or not containing in serviceNodes: '+str(id))
      ###########################################
    self.logger.info('Filtered backend nodes killed_backends : '+str(killed_backends)+' '+str(perf_info.serviceNodes))    
      
    self._performance_info_set(perf_info)    
    
    self.logger.info('Updating nodes information from ConPaaS manager...')
    self.logger.info('Updated service nodes: %s' % str(perf_info.serviceNodes))
            
  def collect_monitoring_metric(self, node_ip, metric_name):
    timestamps = []
    param_values = []
     # Added this for EC2, where the RRD directory names in Ganglia are hosts and not IPs:
    ganglia_dir_name = ''
    
    if node_ip.find('amazonaws') > 0: # this is an IP address
      ganglia_dir_name = node_ip
    else: # this is a DNS name
      for ganglia_host in listdir(self.ganglia_rrd_dir):
        #self.logger.error('collect from ganglia host: ' + str(ganglia_host))  
        if ganglia_host.find('Summary') > 0:
          continue
        try:
            hostname, array, array_ip = socket.gethostbyaddr(node_ip)
        except:
            self.logger.warning('Found private ip when trying to get the hostname for ip: '+str(node_ip))
            ganglia_dir_name = node_ip
            break
        #self.logger.error('gethostbyaddr: ' + hostname)
        if ganglia_host == hostname:
          ganglia_dir_name = ganglia_host
          break
      
    rrd_file_name = self.ganglia_rrd_dir + ganglia_dir_name + '/' + metric_name + '.rrd'
    self.logger.error('rrd_file_name: ' + str(rrd_file_name))
#    logger.info('Searching in RRD file:' + rrd_file_name)
    if (not path.isfile(rrd_file_name)):
      self.logger.error('RRD file not found: ' + rrd_file_name)
      return []
    
    #logger.info('Getting monitoring info for node %s, parameter %s ...' % (node_ip, metric_name))
#    logger.info('last collect time: ' + str(int(self.last_collect_time)))
    collect_from = self.last_collect_time - (time() - self.last_collect_time)
    #collect_from = self.last_collect_time
    proc = Popen(['rrdtool', 'fetch', '-s', str(int(collect_from)), '-r', '15', \
                  str(rrd_file_name), 'AVERAGE'], stdout=PIPE, stderr=PIPE, close_fds=True)  
    stdout_req, stderr_req = proc.communicate()
    
    lines = stdout_req.splitlines()
    for line in lines:
      #logger.debug(line)
      tokens = line.split()
      if (line.find('sum') >=0 or len(tokens) < 2):
        continue;
      
      timestamps.append(int(tokens[0].replace(':', '')))
      
      if (tokens[1].find('nan') < 0):
        param_values.append(float(tokens[1]))
      else:
        param_values.append(-1)
   
    ## Cleaning the memory allocated by subprocess.Popen()
    try:
        proc.terminate()
    except OSError:
      #  logger.critical("Cannot kill the subprocess.popen rrdtool")
        # can't kill a dead proc
        pass

    
    #logger.debug('timestamps: ' + str(timestamps))
    #logger.debug('param values: ' + str(param_values))          
    return [timestamps, param_values]

  def init_collect_monitoring_data(self):
      self.perf_info = self._performance_info_get()
  
  def collect_monitoring_data(self):

    web_monitoring_data = {}
    backend_monitoring_data = {}
    proxy_monitoring_data = {}
    
    for web_node in self.perf_info.getWebServiceNodes():
      self.logger.info('Getting web monitoring info for %s ...' % web_node.ip)
      #if web_node.ip not in web_monitoring_data:
      web_monitoring_data[web_node.ip] = {}
      cpu_num = DEFAULT_NUM_CPU
      mem_total = DEFAULT_RAM_MEMORY
      self.logger.info('Getting web monitoring info 1')
      for it in range(len(self.monitoring_metrics_web)):
        self.logger.info('Getting web monitoring info 2')
        ret = self.collect_monitoring_metric(web_node.ip, self.monitoring_metrics_web[it])
        self.logger.info('Getting web monitoring info 3')
        if len(ret) == 0: # monitoring data was not found
          self.logger.info('Getting web monitoring info 4')
          return False
        if 'timestamps' not in web_monitoring_data[web_node.ip]:
          web_monitoring_data[web_node.ip]['timestamps'] = ret[0]
        web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]] = ret[1]
        
        if self.monitoring_metrics_web[it] == 'cpu_num' and web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0] != -1:
          cpu_num = backend_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0]
          
        if self.monitoring_metrics_web[it] == 'mem_total' and web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0] != -1:
          mem_total = str(backend_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0])
        
        if self.monitoring_metrics_web[it] == 'boottime' and web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0] != -1:
          self.cost_controller.update_vm_usage(web_node.ip, web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0], self.cost_controller.instance_type_detector(cpu_num, mem_total))                 
         
                    
    for backend_node in self.perf_info.getBackendServiceNodes():
      self.logger.info('Getting backend monitoring info for %s ...' % backend_node.ip)
      backend_monitoring_data[backend_node.ip] = {}
      cpu_num = DEFAULT_NUM_CPU
      mem_total = DEFAULT_RAM_MEMORY
      """ 
          It iterates over the array to get the metrics in the same order, they defined added. 
          It allows to detect the type of instance by analyzing the cpu, mem_total.
      """
      for it in range(len(self.monitoring_metrics_backend)):  
        ret = self.collect_monitoring_metric(backend_node.ip, self.monitoring_metrics_backend[it])
        if len(ret) == 0: # monitoring data was not found
          return False
        if 'timestamps' not in backend_monitoring_data[backend_node.ip]:
          backend_monitoring_data[backend_node.ip]['timestamps'] = ret[0]
        backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]] = ret[1]
        
        self.logger.info('There is a metric name: '+str(self.monitoring_metrics_backend[it]))
        if self.monitoring_metrics_backend[it] == 'cpu_num':
          if backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0] > 0:
              self.logger.info('There is a metric cpu_num with content: '+str(backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0]))
              cpu_num = str(backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0])
          else:
             ## This is done to clean the negative and worng values from the monitoring data
             self.logger.info('There is a metric cpu_num with content equal or minus to zero ')
             for value in backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]]:
                 if value > 0:
                     self.logger.info('There is a metric cpu_num with content: '+str(value))
                     cpu_num = value
                     break 
          
        if self.monitoring_metrics_backend[it] == 'mem_total':
          if backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0] > 0:
              self.logger.info('There is a metric mem_total with content: '+str(backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0]))
              mem_total = str(backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0])
          else:
             ## This is done to clean the negative and worng values from the monitoring data
             self.logger.info('There is a metric mem_total with content equal or minus to zero ')
             for value in backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]]:
                 if value > 0:
                     self.logger.info('There is a metric mem_total with content: '+str(value))
                     mem_total = value
                     break 
          
        if self.monitoring_metrics_backend[it] == 'boottime':
          if backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0] > 0:
              self.logger.info('There is a metric boottime with content: '+str(backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0]))
              self.cost_controller.update_vm_usage(backend_node.ip, backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0], self.cost_controller.instance_type_detector(cpu_num, mem_total))
          else:
             ## This is done to clean the negative and worng values from the monitoring data
             boottime = backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0]
             self.logger.info('There is a metric boottime with content equal or minus to zero ')
             for value in backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]]:
                 if value > 0:
                     self.logger.info('There is a metric boottime with content: '+str(value))
                     self.cost_controller.update_vm_usage(backend_node.ip, float(boottime), self.cost_controller.instance_type_detector(cpu_num, mem_total))
                     boottime = value
                     break 
             
             
    for proxy_node in self.perf_info.getProxyServiceNodes():
      self.logger.info('Getting proxy monitoring info for %s ...' % proxy_node.ip)
      proxy_monitoring_data[proxy_node.ip] = {}
      for it in range(len(self.monitoring_metrics_proxy)):
        ret = self.collect_monitoring_metric(proxy_node.ip, self.monitoring_metrics_proxy[it])
        if len(ret) == 0: # monitoring data was not found
          return False
        if 'timestamps' not in proxy_monitoring_data[proxy_node.ip]:
          proxy_monitoring_data[proxy_node.ip]['timestamps'] = ret[0]
        proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]] = ret[1]
        
        if self.monitoring_metrics_proxy[it] == 'cpu_num' and proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0] != -1:
          cpu_num = proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0]
          
        if self.monitoring_metrics_proxy[it] == 'mem_total' and proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0] != -1:
          mem_total = str(proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0])
        
        if self.monitoring_metrics_proxy[it] == 'boottime' and proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0] != -1:
          self.cost_controller.update_vm_usage(proxy_node.ip, proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0], self.cost_controller.instance_type_detector(cpu_num, mem_total))                 
          
        proxy_monitoring_data[proxy_node.ip] = self.stat_utils.filter_monitoring_data(proxy_monitoring_data[proxy_node.ip], self.monitoring_metrics_proxy)
       
    print proxy_monitoring_data
    print web_monitoring_data
    print backend_monitoring_data   
    self.last_collect_time = time()
    print "Done getting monitoring data..."
    return True 

  def collect_monitoring_data_web(self):

    web_monitoring_data = {}
       
    for web_node in self.perf_info.getWebServiceNodes():
      self.logger.info('Getting web monitoring info for %s ...' % web_node.ip)
      #if web_node.ip not in web_monitoring_data:
      web_monitoring_data[web_node.ip] = {}
      cpu_num = DEFAULT_NUM_CPU
      mem_total = DEFAULT_RAM_MEMORY
      for it in range(len(self.monitoring_metrics_web)):
        ret = self.collect_monitoring_metric(web_node.ip, self.monitoring_metrics_web[it])
        if len(ret) == 0: # monitoring data was not found
          return {}
        
        if 'timestamps' not in web_monitoring_data[web_node.ip]:
          web_monitoring_data[web_node.ip]['timestamps'] = ret[0]
        web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]] = ret[1]
        
        if self.monitoring_metrics_web[it] == 'cpu_num' and web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0] != -1:
          cpu_num = web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0]
          
        if self.monitoring_metrics_web[it] == 'mem_total' and web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0] != -1:
          mem_total = str(web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0])
        
        if self.monitoring_metrics_web[it] == 'boottime':
          self.cost_controller.update_vm_usage(web_node.ip, web_monitoring_data[web_node.ip][self.monitoring_metrics_web[it]][0], self.cost_controller.instance_type_detector(cpu_num, mem_total))                 
       
    return web_monitoring_data 
  
  def collect_monitoring_data_backend(self):
    backend_monitoring_data = {}
                        
    for backend_node in self.perf_info.getBackendServiceNodes():
      self.logger.info('Getting backend monitoring info for %s ...' % backend_node.ip)
      backend_monitoring_data[backend_node.ip] = {}
      cpu_num = DEFAULT_NUM_CPU
      mem_total = DEFAULT_RAM_MEMORY
      """ 
          It iterates over the array to get the metrics in the same order, they defined added. 
          It allows to detect the type of instance by analyzing the cpu, mem_total.
      """
      for it in range(len(self.monitoring_metrics_backend)):  
        ret = self.collect_monitoring_metric(backend_node.ip, self.monitoring_metrics_backend[it])
        if len(ret) == 0: # monitoring data was not found
          return {}
        if 'timestamps' not in backend_monitoring_data[backend_node.ip]:
          backend_monitoring_data[backend_node.ip]['timestamps'] = ret[0]
        backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]] = ret[1]
        
        #self.logger.info('There is a metric name: '+str(self.monitoring_metrics_backend[it]))
        if self.monitoring_metrics_backend[it] == 'cpu_num':
          if backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0] > 0:
              self.logger.info('There is a metric cpu_num with content: '+str(backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0]))
              cpu_num = backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0]
          else:
             ## This is done to clean the negative and worng values from the monitoring data
             self.logger.info('There is a metric cpu_num with content equal or minus to zero ')
             for value in backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]]:
                 if value > 0:
                     self.logger.info('There is a metric cpu_num with content: '+str(value))
                     cpu_num = value
                     break 
          
        if self.monitoring_metrics_backend[it] == 'mem_total':
          if backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0] > 0:
              self.logger.info('There is a metric mem_total with content: '+str(backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0]))
              mem_total = backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0]
          else:
             ## This is done to clean the negative and worng values from the monitoring data
             self.logger.info('There is a metric mem_total with content equal or minus to zero ')
             for value in backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]]:
                 if value > 0:
                     self.logger.info('There is a metric mem_total with content: '+str(value))
                     mem_total = value
                     break 
          
        if self.monitoring_metrics_backend[it] == 'boottime':
          if backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0] > 0:
              self.logger.info('There is a metric boottime with content: '+str(backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0]))
              self.cost_controller.update_vm_usage(backend_node.ip, backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0], self.cost_controller.instance_type_detector(cpu_num, mem_total))
          else:
             ## This is done to clean the negative and worng values from the monitoring data
             boottime = backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]][0]
             self.logger.info('There is a metric boottime with content equal or minus to zero ')
             for value in backend_monitoring_data[backend_node.ip][self.monitoring_metrics_backend[it]]:
                 if value > 0:
                     self.logger.info('There is a metric boottime with content: '+str(value))
                     boottime = value
                     break
             self.cost_controller.update_vm_usage(backend_node.ip, float(boottime), self.cost_controller.instance_type_detector(cpu_num, mem_total))
    
    return backend_monitoring_data 
                 
  def collect_monitoring_data_proxy(self):
    self.perf_info = self._performance_info_get()
    proxy_monitoring_data = {}          
             
    for proxy_node in self.perf_info.getProxyServiceNodes():
      self.logger.info('Getting proxy monitoring info for %s ...' % proxy_node.ip)
      proxy_monitoring_data[proxy_node.ip] = {}
      cpu_num = DEFAULT_NUM_CPU
      mem_total = DEFAULT_RAM_MEMORY
      for it in range(len(self.monitoring_metrics_proxy)):
        ret = self.collect_monitoring_metric(proxy_node.ip, self.monitoring_metrics_proxy[it])
        if len(ret) == 0: # monitoring data was not found
          return {}
        if 'timestamps' not in proxy_monitoring_data[proxy_node.ip]:
          proxy_monitoring_data[proxy_node.ip]['timestamps'] = ret[0]
        proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]] = ret[1]
        
        if self.monitoring_metrics_proxy[it] == 'cpu_num' and proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0] != -1:
          cpu_num = proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0]
          
        if self.monitoring_metrics_proxy[it] == 'mem_total' and proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0] != -1:
          mem_total = str(proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0])
        
        if self.monitoring_metrics_proxy[it] == 'boottime':
          self.cost_controller.update_vm_usage(proxy_node.ip, proxy_monitoring_data[proxy_node.ip][self.monitoring_metrics_proxy[it]][0], self.cost_controller.instance_type_detector(cpu_num, mem_total))                 
          
      proxy_monitoring_data[proxy_node.ip] = self.stat_utils.filter_monitoring_data(proxy_monitoring_data[proxy_node.ip], self.monitoring_metrics_proxy)
       
    self.last_collect_time = time()
    
    return proxy_monitoring_data 
  

