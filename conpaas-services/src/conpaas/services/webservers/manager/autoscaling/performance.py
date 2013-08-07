"""

@author: fernandez
"""

from conpaas.services.webservers.manager.autoscaling import log

PATH_LOG_FILE = '/tmp/provisioning.log'
log.init(PATH_LOG_FILE)
logger = log.create_logger('Autoscaling')

DEFAULT_REQUEST_RATE_PREDICTION = 1.2

class ServiceNodePerf(object):
  """ 
  This class will contain performance info about the nodes (i.e. the performance profiles).
  A dictionary with objects of this type will be stored in the memcache and will be accessed by 
  the provisioning and profiling managers.
  """
  
  # Default weight for nodes in load balancing. This is also defined in internal.py,
  # we should merge them into a single definition
  DEFAULT_NODE_WEIGHT = 100
  
  def __init__(self, vmid, ip, runProxy, runWeb, runBackend, provisioningState):
    self.vmid = vmid
    self.ip = ip
    
    self.isRunningProxy = runProxy
    self.isRunningWeb = runWeb
    self.isRunningBackend = runBackend
    
    # default values for weights in the beginning 
    self.weightWeb = self.DEFAULT_NODE_WEIGHT
    self.weightBackend = self.DEFAULT_NODE_WEIGHT
    
    self.provisioning_state = provisioningState
    self.registered_with_manager = True
    
    self.online_web_profile = []
    self.oweb_coeffs = []
    
    self.online_backend_profile = []
    self.oback_coeffs = []
    
    
  def update_online_web_coefficients(self):
    self.oweb_coeffs = []
     
    if len(self.online_web_profile) <= 1:
      return
     
    for i in range(0, len(self.online_web_profile) - 1):
      x1 = self.online_web_profile[i][0]
      y1 = self.online_web_profile[i][1]
        
      x2 = self.online_web_profile[i+1][0]
      y2 = self.online_web_profile[i+1][1]
  
      a = (y2 - y1) / (x2 - x1)
      b = y1 - a * x1
        
      self.oweb_coeffs.append([a, b])
      
    logger.debug('Updated coefficients for online web profiling: ' + str(self.oweb_coeffs))

  def update_online_backend_coefficients(self):
    self.oback_coeffs = []
     
    if len(self.online_backend_profile) <= 1:
      return
     
    for i in range(0, len(self.online_backend_profile) - 1):
      x1 = self.online_backend_profile[i][0]
      y1 = self.online_backend_profile[i][1]
        
      x2 = self.online_backend_profile[i+1][0]
      y2 = self.online_backend_profile[i+1][1]
  
      a = (y2 - y1) / (x2 - x1)
      b = y1 - a * x1
        
      self.oback_coeffs.append([a, b])
      
    logger.debug('Updated coefficients for online web profiling: ' + str(self.oback_coeffs))
      
  def update_online_web_profile(self, web_profile):
    self.online_web_profile = web_profile
    self.update_online_web_coefficients()
  
  def update_online_backend_profile(self, backend_profile):
    self.online_backend_profile = backend_profile
    self.update_online_backend_coefficients()
               
  def compute_resp_time_prediction(self, request_rate, profile, coeffs):
      
    if len(coeffs) < 2:
      return -1
      
    idx = 0
    profile_len = len(profile)
    for i in range(0, profile_len - 1):
      if (request_rate >= profile[i][0] and request_rate <= profile[i+1][0]):
        idx = i
        break
        
    if request_rate > profile[profile_len-1][0]:
      idx = profile_len - 2
    
    prediction = coeffs[idx][0] * request_rate  + coeffs[idx][1]
    logger.debug('Response time prediction: index ' + str(idx) + ' predicted value: ' + str(prediction))  
    return prediction 

  def response_time_online_prediction(self, tier_type, request_rate):
    if tier_type == 'web':
      return self.compute_resp_time_prediction(request_rate, self.online_web_profile, self.oweb_coeffs)
    else:
      return self.compute_resp_time_prediction(request_rate, self.online_backend_profile, self.oback_coeffs)
     
  def compute_req_rate_prediction(self, target_resp_time, profile, coeffs):
      
    if len(profile) < 2:
      return DEFAULT_REQUEST_RATE_PREDICTION
      
    idx = 0
    profile_len = len(profile)
    for i in range(0, profile_len - 1):
      if (target_resp_time >= profile[i][1] and target_resp_time <= profile[i+1][1]):
        idx = i
        break
        
    if target_resp_time > profile[profile_len-1][1]:
      idx = profile_len - 2
      
    #return int(round((target_resp_time  - coeffs[idx][1]) / coeffs[idx][0]))
    predicted_req_rate = (target_resp_time  - coeffs[idx][1]) / coeffs[idx][0]
    
    #if we got an incorrect value, use the default:
    if predicted_req_rate <= 0:
      predicted_req_rate = DEFAULT_REQUEST_RATE_PREDICTION
    logger.debug('Request rate prediction: index ' + str(idx) + ' predicted value: ' + str(predicted_req_rate)) 
    return predicted_req_rate

  def req_rate_online_prediction(self, tier_type, target_resp_time):
    if tier_type == 'web':
      return self.compute_req_rate_prediction(target_resp_time, self.online_web_profile, self.oweb_coeffs)
    else:
      return self.compute_req_rate_prediction(target_resp_time, self.online_backend_profile, self.oback_coeffs)
   
  def compute_node_weight(self, tier_type, target_resp_time):
    predicted_req_rate = self.req_rate_online_prediction(tier_type, target_resp_time)

    weight = int(round(10 * predicted_req_rate))
    return weight
  
     
  def __repr__(self):
    return 'ServiceNodePerf(vmid=%s, ip=%s, proxy=%s, web=%s, backend=%s)' % (str(self.vmid), self.ip, str(self.isRunningProxy), str(self.isRunningWeb), str(self.isRunningBackend))
    
class ServicePerformance(object):
  def __init__(self):
    self.serviceNodes = {}
    self.profilingNodes = {}
    self.idleNodes = {}
   
  def getProxyServiceNodes(self):
    return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningProxy ]
  
  def getWebServiceNodes(self):
    return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningWeb ]
  
  def getBackendServiceNodes(self):
    return [ serviceNode for serviceNode in self.serviceNodes.values() if serviceNode.isRunningBackend ]
  
  def getProfilingNodes(self):
    return [ profilingNode for profilingNode in self.profilingNodes.values() ]

  def reset_role_info(self):
    for node in self.serviceNodes.values():
      node.registered_with_manager = False
      node.isRunningProxy = node.isRunningBackend = node.isRunningWeb = False
    
    for node in self.profilingNodes.values():
      node.registered_with_manager = False
      node.isRunningProxy = node.isRunningBackend = node.isRunningWeb = False
      
class StatUtils(object):
  def __init__(self):
    self.old_monitoring_data_resp = []
    self.old_monitoring_data_cpu = []
    
    self.old_monitoring_data = []
    
  def compute_average(self, list):
    sum = 0.0
    noDataValues = 0
    for value in list:
      if value < 0: 
        value = 0.0
        noDataValues = noDataValues + 1
      sum += value
    elements = len(list) - noDataValues 
    if sum == 0:
     return 0.0 
    return float(sum) / float(elements) 
  
  
  def compute_weight_average(self, list):
    sum = 0.0
    sum_weights = 0.0
    weights = [w for w in range(len(list))]
    for it in range(len(list)):
      # No monitoring data ..
      if list[it] < 0:
        list[it] = 0.0
        weights[it] = 0

      sum += (list[it] * weights[it])
      sum_weights += weights[it]
    if sum == 0:
     return 0.0
    return float(sum) / float(sum_weights)

  def compute_weight_average_response(self, list, slo, weight_slow_violation):
    sum = 0.0
    sum_weights = 0.0
    weights = [w for w in range(len(list))]
    for it in range(len(list)):
      # No monitoring data ..
      factor = 1
      if list[it] < 0:
        list[it] = 0.0
        weights[it] = 0
      elif list[it] > slo:
          factor = weight_slow_violation
          
      sum += (list[it] * weights[it] * factor)
      sum_weights += weights[it] * factor
    if sum == 0:
     return 0.0
    return float(sum) / float(sum_weights)

  def filter_response_data (self, new_monitoring_data):
       list_filtered = []
       if len(new_monitoring_data) <= 1 and len(self.old_monitoring_data_resp) == 0 :
           self.old_monitoring_data_resp = new_monitoring_data
           return new_monitoring_data
       
       for data in new_monitoring_data:
            if not data in self.old_monitoring_data_resp:
                list_filtered.append(data)
       
       self.old_monitoring_data_resp = []
       self.old_monitoring_data_resp = list_filtered
       return self.old_monitoring_data_resp
   

  def filter_monitoring_data (self, new_monitoring_data, monitoring_metrics):

       if len(new_monitoring_data) <= 1 or len(self.old_monitoring_data) == 0 :
           self.old_monitoring_data = new_monitoring_data
           return new_monitoring_data
       
       for index, timestamp in  enumerate(new_monitoring_data['timestamps']):
            if timestamp in self.old_monitoring_data['timestamps']:
                del new_monitoring_data['timestamps'][index]
                for metric in monitoring_metrics:
                    del new_monitoring_data[metric][index]
                #del new_monitoring_data['php_response_time_lb'][index]
                #del new_monitoring_data['php_request_rate_lb'][index]
                #del new_monitoring_data['cpu_user'][index]
                #del new_monitoring_data['web_request_rate_lb'][index]
                #del new_monitoring_data['web_response_time_lb'][index]

       self.old_monitoring_data_resp = []
       self.old_monitoring_data_resp = new_monitoring_data
       return self.old_monitoring_data_resp

  def filter_cpu_data (self, new_monitoring_data):
       list_filtered = []
       if len(new_monitoring_data) <= 1 and len(self.old_monitoring_data_cpu) == 0 :
           self.old_monitoring_data_cpu = new_monitoring_data
           return new_monitoring_data
       
       for data in new_monitoring_data:
            if not data in self.old_monitoring_data_cpu:
                list_filtered.append(data)
       
       self.old_monitoring_data_cpu = []
       self.old_monitoring_data_cpu = list_filtered
       return self.old_monitoring_data_cpu
   
#sta = StatUtils()
#monitoring_metrics_proxy = ['web_request_rate_lb', 'web_response_time_lb', \
 #                                    'php_request_rate_lb', 'php_response_time_lb', 'cpu_user']
#proxy_data_1 = {u'10.100.2.67': {'cpu_user': [8.6066666667000007, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.17999999999999999, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.12, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.19333333333, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.29999999999999999, 0.29999999999999999, -1, -1], 'php_request_rate_lb': [0.0, 0.0, 0.27155466667, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 0.97498693332999997, 0.97498693332999997, 4.6722739999999998, 4.9102040000000002, 4.6055659999999996, 4.9164870000000001, 4.344106, 3.7350759999999998, 4.4150109999999998, 4.8974190000000002, 4.1264560000000001, 4.1264560000000001, 4.2452829999999997, 4.5001300000000004, 4.5001300000000004, 4.8351350000000002, 4.5397467999999996, 4.5397467999999996, 5.57843, 5.4013910000000003, 4.3455360000000001, -1, -1], 'web_response_time_lb': [0.0, 0.0, 42.733333332999997, 277.76666667000001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 32.071111999999999, 32.071111999999999, 331.178223, 326.93478399999998, 390.259613, 338.55856299999999, 479.53192100000001, 281.982147, 306.32406600000002, 295.82052599999997, 397.11322000000001, 397.11322000000001, 351.14953600000001, 386.03613052999998, 386.03613052999998, 397.90194700000001, 414.59056607000002, 414.59056607000002, 248.072159, 346.846161, 264.57406600000002, -1, -1], 'web_request_rate_lb': [0.0, 0.0, 0.27155466667, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 2.0366599999999999, 0.99375760000000002, 0.99375760000000002, 6.7414230000000002, 6.1882020000000004, 6.8425560000000001, 7.4757540000000002, 6.1870599999999998, 7.4701529999999998, 7.224564, 7.7432169999999996, 7.0549080000000002, 7.0549080000000002, 7.2102430000000002, 6.4542671333000001, 6.4542671333000001, 6.8497750000000002, 6.9161111333000003, 6.9161111333000003, 6.4417590000000002, 7.021808, 7.1108770000000003, -1, -1], 'timestamps': [1363996770, 1363996785, 1363996800, 1363996815, 1363996830, 1363996845, 1363996860, 1363996875, 1363996890, 1363996905, 1363996920, 1363996935, 1363996950, 1363996965, 1363996980, 1363996995, 1363997010, 1363997025, 1363997040, 1363997055, 1363997070, 1363997085, 1363997100, 1363997115, 1363997130, 1363997145, 1363997160, 1363997175, 1363997190, 1363997205, 1363997220, 1363997235, 1363997250, 1363997265, 1363997280, 1363997295, 1363997310, 1363997325, 1363997340, 1363997355, 1363997370, 1363997385, 1363997400, 1363997415, 1363997430, 1363997445, 1363997460, 1363997475, 1363997490], 'php_response_time_lb': [0.0, 0.0, 42.799999999999997, 278.19999999999999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 165.77254239999999, 165.77254239999999, 1406.5142820000001, 1501.5889890000001, 1501.8857419999999, 1501.6437989999999, 1501.712158, 1502.0, 1501.5, 1501.9053960000001, 1501.758057, 1501.758057, 1501.6983640000001, 1501.5460123, 1501.5460123, 1501.625, 1501.9315836999999, 1501.9315836999999, 1501.666626, 1501.9250489999999, 1504.8029790000001, -1, -1]}}
#proxy_data_2 = {u'10.100.2.67': {'cpu_user': [0.19333333333, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.10000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.29999999999999999, 0.29999999999999999, 0.24666666667000001, 0.24666666667000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 0.20666666667, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, -1, -1], 'php_request_rate_lb': [2.0366599999999999, 2.0366599999999999, 0.97498693332999997, 0.97498693332999997, 4.6722739999999998, 4.9102040000000002, 4.6055659999999996, 4.9164870000000001, 4.344106, 3.7350759999999998, 4.4150109999999998, 4.8974190000000002, 4.1264560000000001, 4.1264560000000001, 4.2452829999999997, 4.5001300000000004, 4.5001300000000004, 4.8351350000000002, 4.5397467999999996, 4.5397467999999996, 5.57843, 5.4013910000000003, 4.3455360000000001, 5.1004019332999997, 5.1004019332999997, 4.0563900000000004, 5.9808106667000001, 4.9257799999999996, 4.9257799999999996, 4.9297972666999996, 4.9862380000000002, 4.9397900666999996, 4.3961171332999998, 5.2764252666999996, 4.8436221333000002, 4.8305736000000001, 5.3203192667000003, 6.1173526000000003, 5.1313950000000004, 4.4127888000000004, 3.9462329333000001, 4.9303617332999998, 5.3219652667000004, 4.8811970000000002, 4.9386872000000004, 3.9806000667000001, 4.4173127333000002, -1, -1], 'web_response_time_lb': [0.0, 0.0, 32.071111999999999, 32.071111999999999, 331.178223, 326.93478399999998, 390.259613, 338.55856299999999, 479.53192100000001, 281.982147, 306.32406600000002, 295.82052599999997, 397.11322000000001, 397.11322000000001, 351.14953600000001, 386.03613052999998, 386.03613052999998, 397.90194700000001, 414.59056607000002, 414.59056607000002, 248.072159, 346.846161, 264.57406600000002, 330.85745220000001, 330.85745220000001, 237.649124, 404.62391746999998, 385.77874800000001, 385.77874800000001, 384.67887819999999, 373.56775747, 425.33456027, 301.79624412999999, 263.07980433, 345.44047819999997, 272.15719926999998, 114.69993927, 127.6299222, 93.995092, 91.0031192, 57.778877332999997, 70.469742933000006, 69.681743600000004, 90.447554066999999, 88.372351266999999, 76.091151400000001, 66.384089532999994, -1, -1], 'web_request_rate_lb': [2.0366599999999999, 2.0366599999999999, 0.99375760000000002, 0.99375760000000002, 6.7414230000000002, 6.1882020000000004, 6.8425560000000001, 7.4757540000000002, 6.1870599999999998, 7.4701529999999998, 7.224564, 7.7432169999999996, 7.0549080000000002, 7.0549080000000002, 7.2102430000000002, 6.4542671333000001, 6.4542671333000001, 6.8497750000000002, 6.9161111333000003, 6.9161111333000003, 6.4417590000000002, 7.021808, 7.1108770000000003, 6.6779988667000003, 6.6779988667000003, 7.5807950000000002, 6.7129089332999996, 7.5217999999999998, 7.5217999999999998, 7.5255986000000004, 7.5347346667000004, 6.9837931332999998, 7.8774575333000003, 7.6596255332999998, 7.2243415332999996, 5.6483380667, 5.4756054667000003, 6.6669099333000004, 6.9453864000000003, 7.4672422666999996, 7.1623893333000002, 7.3710671333000004, 5.7925437999999998, 7.3501445332999999, 6.2169723333000002, 6.2112254667000002, 5.3902014666999998, -1, -1], 'timestamps': [1363997130, 1363997145, 1363997160, 1363997175, 1363997190, 1363997205, 1363997220, 1363997235, 1363997250, 1363997265, 1363997280, 1363997295, 1363997310, 1363997325, 1363997340, 1363997355, 1363997370, 1363997385, 1363997400, 1363997415, 1363997430, 1363997445, 1363997460, 1363997475, 1363997490, 1363997505, 1363997520, 1363997535, 1363997550, 1363997565, 1363997580, 1363997595, 1363997610, 1363997625, 1363997640, 1363997655, 1363997670, 1363997685, 1363997700, 1363997715, 1363997730, 1363997745, 1363997760, 1363997775, 1363997790, 1363997805, 1363997820, 1363997835, 1363997850], 'php_response_time_lb': [0.0, 0.0, 165.77254239999999, 165.77254239999999, 1406.5142820000001, 1501.5889890000001, 1501.8857419999999, 1501.6437989999999, 1501.712158, 1502.0, 1501.5, 1501.9053960000001, 1501.758057, 1501.758057, 1501.6983640000001, 1501.5460123, 1501.5460123, 1501.625, 1501.9315836999999, 1501.9315836999999, 1501.666626, 1501.9250489999999, 1504.8029790000001, 1504.2562743000001, 1504.2562743000001, 1501.786865, 1501.9774738999999, 1501.6621090000001, 1501.6621090000001, 1501.6677486999999, 1501.7413655, 1481.1096843, 1152.4522704999999, 878.4198854, 829.90510240000003, 894.78423667000004, 542.63731919999998, 319.30373513000001, 258.98950252999998, 231.58031700000001, 214.67121233, 303.98381339999997, 231.58753146999999, 250.64234087, 318.66685113, 229.57654052999999, 257.59433612999999, -1, -1]}}
#for ip, items in proxy_data_1.iteritems():
#    print len(sta.filter_monitoring_data(items, monitoring_metrics_proxy))  

#for ip, items in proxy_data_2.iteritems():
#    print len(sta.filter_monitoring_data(items, monitoring_metrics_proxy))  
