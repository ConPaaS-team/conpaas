"""
@author: fernandez
"""

from conpaas.services.webservers.manager.autoscaling.performance import ServicePerformance, ServiceNodePerf, StatUtils

MAX_WEIGHT_VALUE = 3000
STANDARD_WEIGHT_VALUE = 200
PERCENTAGE_PERFORMANCE_DIFF = 30
MAX_CPU_USAGE_WEIGHTS = 77
MIN_CPU_USAGE_WEIGHTS = 10

"""
  The Dynamic_Load_Balancer distribute the incoming requests across the backends taken into consideration their performance capacities ( cpu_usage ).
"""
class Dynamic_Load_Balancer:
  
 def __init__(self, logger, manager_host, manager_port, client):
     self.manager_host = manager_host
     self.manager_port = manager_port
     self.updated_backend_weights = {}
     self.updated_backend_weights_id = {}
     
     self.stat_utils = StatUtils()
     
     self.client_manager = client
     self.logger= logger

 def get_updated_backend_weights_id(self, vm_ip):
     return  self.updated_backend_weights_id[vm_ip]
 
 def remove_updated_backend_weights(self, server_id):
     del self.updated_backend_weights[server_id]

 def remove_updated_backend_weights_id(self, vm_ip):
     del self.updated_backend_weights_id[vm_ip]
 
 """ 
 TODO: Perhaps we may want to calculate the percent_factor using cpu_usage and response time
 """
 def adjust_node_weights(self, monitoring, backend_monitoring_data):
    """
    Adjusts the weights of the servers based on the latest monitoring data.
    """
    self.logger.info('Adjusting node weights...')
    try:
        
        perf_info = monitoring._performance_info_get()      
        backend_nodes = perf_info.getBackendServiceNodes()
    
        # Compute the average cpu usage of each backend node, and the maximum among all the nodes
        avg_nodes_usage = {}
        max_node_usage = 0
        for backend_node in backend_nodes:   
            
            node_usage =  self.stat_utils.compute_weight_average(backend_monitoring_data[backend_node.ip]['cpu_user'])
            #node_usage =  self.stat_utils.compute_weight_average_response(self.backend_monitoring_data[backend_node.ip]['php_response_time'], self.slo, self.weight_slow_violation)
                
            self.logger.debug('Current weight for node %s is: %s and avg cpu usage: %s' % (backend_node.vmid, str(backend_node.weightBackend), str(node_usage)))
            avg_nodes_usage[backend_node.vmid] = node_usage
            if node_usage > max_node_usage:
                max_node_usage = node_usage 
    
        self.logger.debug('Weight calculation: maximum cpu usage is %s' % str(max_node_usage))
        weight_changes = False
        
        ## Limit the maximum weight for all the elements:
        for vmid in self.updated_backend_weights:
             if self.updated_backend_weights[vmid] > MAX_WEIGHT_VALUE:
                 for vmid_aux in self.updated_backend_weights:
                     self.updated_backend_weights[vmid_aux] = STANDARD_WEIGHT_VALUE
        
        
        # Compute the weight adjustment for each node
        for backend_node in backend_nodes:
            node_usage = avg_nodes_usage[backend_node.vmid]
            # When a node has just been added, the monitoring data might be 0

            if max_node_usage > MIN_CPU_USAGE_WEIGHTS:
                
                if node_usage == 0:
                    node_usage = max_node_usage
            
            
                # How much faster is this node compared with the slowest node  
                percent_factor = (max_node_usage / node_usage) * 100
                
                # We ignore differences of less than 30%. For each 30% difference
                # we'll increase the weight of the faster server with 10%.
                percent_multiplier = int((percent_factor - 100) / PERCENTAGE_PERFORMANCE_DIFF)
                weight_value = 0
                if( node_usage > MAX_CPU_USAGE_WEIGHTS and percent_multiplier < 1):
                    self.logger.debug('Node with cpu usage > 77 ')
                    try:
                         if self.updated_backend_weights[backend_node.vmid]:
                             weight_value = int(self.updated_backend_weights[backend_node.vmid] - 10)
                    except:
                         weight_value = int(backend_node.weightBackend - 10)
                else:
                    self.logger.debug('Percent multiplier for node %s is: %s' % (backend_node.vmid, str(percent_multiplier)))
                    ## Verify if there is any change in the weights, otherwise we won't call the update_nodes_weight function
                    try:
                         if self.updated_backend_weights[backend_node.vmid]:
                             weight_value = int(self.updated_backend_weights[backend_node.vmid] * \
                                                (100 + 15 * percent_multiplier) / 100)                
                    except:
                        weight_value = int(backend_node.weightBackend * \
                            (100 + 15 * percent_multiplier) / 100)
                        
                    ## Added to avoid Requests rejections from Nginx when weight values are low and there is not reason to do that.
                    if percent_multiplier == 0:
                        try:
                            if self.updated_backend_weights[backend_node.vmid] and self.updated_backend_weights[backend_node.vmid] < 500:
                                weight_value = int(self.updated_backend_weights[backend_node.vmid] + 10)
                        except:
                            if backend_node.weightBackend < 500:
                                weight_value = int(backend_node.weightBackend + 10)
                        
                
                try:
                    
                    if self.updated_backend_weights[backend_node.vmid] and self.updated_backend_weights[backend_node.vmid] == weight_value:
                        self.logger.debug('Same weight than previous iteration for node: %s to: %s' % (backend_node.vmid, str(self.updated_backend_weights[backend_node.vmid])))
                    else:
                        weight_changes = True
                        self.logger.debug('Updating weight for node: %s to: %s' % (backend_node.vmid, str(self.updated_backend_weights[backend_node.vmid])))
                        self.updated_backend_weights[backend_node.vmid] = weight_value
                        self.updated_backend_weights_id[backend_node.ip] = backend_node.vmid
                except Exception:
                    weight_changes = True
                    self.logger.debug('Adding weight for node: %s ' % (backend_node.vmid))
                    self.updated_backend_weights[backend_node.vmid] = weight_value
                    self.updated_backend_weights_id[backend_node.ip] = backend_node.vmid
             
                #updated_backend_weights[backend_node.vmid] = backend_node.compute_node_weight('backend', self.slo * 0.8 )
        if weight_changes:
                self.logger.debug('Updating weights for the nodes: %s ' % (str(self.updated_backend_weights)))
                
                try:      
                    ret = self.client_manager.update_nodes_weight(self.manager_host, self.manager_port, web={}, backend=self.updated_backend_weights)
                except Exception:
                    tb = traceback.format_exc()
                    self.logger.error('Could not update node weight, exception stack trace: %s' % tb)  
                        
    except Exception as ex:
       self.logger.error("Could not update node weight, exception stack trace: " + str(ex))
    
    self.logger.info('Adjusting node weights finished.')    
