"""
Cost_controller is responsible for the management of the cost related activities to the provisioned resources.

@author: fernandez
"""

import sys
from subprocess import Popen, PIPE
import math
from time import time, sleep
from os import path, listdir
from datetime import datetime, timedelta
from conpaas.core import log
try:
    import simplejson as json
except ImportError:
    import json
import os.path
from os.path import join as pjoin 
    
PRICING_FILE_PATH = 'data/pricing.json'
RELEASE_BEFORE_MIN = 5
RELEASE_BEFORE_MAX = 20

class Cost_Controller:
    
    def __init__(self, logger, iaas_driver):
        self.vmes_usage={}
        self.logger=logger
        self.iaas_driver = iaas_driver
        self.cost_vmes_removal = 0
        self.total_cost = 0
        pricing_file_path = self.get_pricing_file_path()

        with open(pricing_file_path) as fp:
            content = fp.read()

        self.instances_type_price = json.loads(content)
       ## self.instances_type_price = {'EC2': { 'smallEC2':0.065, 'mediumEC2':0.13, 'c.mediumEC2':0.145, 'largeEC2':0.26}, 'OPENNEBULA' : {'smallDAS4':0.065, 'mediumDAS4':0.13, 'highcpu-mediumDAS4':0.145, 'largeDAS4':0.26} }
   
    def get_pricing_file_path(self):
        pricing_directory = os.path.dirname(os.path.abspath(__file__))
        pricing_file_path = pjoin(pricing_directory, PRICING_FILE_PATH)

        return pricing_file_path
    
    def get_instance_prices(self):
        return self.instances_type_price
    
    def instance_type_detector(self, cpu_num, mem_total):
       mem_total = str(mem_total)
       cpu_num = str(cpu_num)
       self.logger.info("instance_type_detector: cpu_num. "+str(cpu_num)+" mem_total: "+str(mem_total))
       if 'OPENNEBULA' in self.iaas_driver: 
           if cpu_num == '1.0':
               return 'small'
        
           if cpu_num == '6.0':
               return 'highcpu-medium'
           #3635248.0 
           if cpu_num == '4.0':
               return 'medium'
        
           if cpu_num >= '8.0':
               return 'large'
           else:
               return  'small'
       else:
           if cpu_num == '1.0' and mem_total >= '1781700.0' and mem_total < '2048000.0':
               return 'm1.small'
           #3635000 3932388.0
           if mem_total > '3635000' and mem_total < '3932480':
               return 'm1.medium'
           #7864548.0
           if mem_total > '7864290.0' and mem_total < '7864700.0':
               return 'm1.large'
          
           if cpu_num == '2.0' and mem_total >= '1781700.0' and mem_total < '2048000.0':
               return 'c1.medium'
           else:
               return 'm1.small'
    
    def update_vm_usage(self, ip, boottime, inst_type):
        # boottime=-1 means no monitoring data was collected.
        self.logger.info("update_vm_usage: adding one machine to the cost_aware system. "+str(ip)+" boottime: "+str(boottime) + " Instance type: " + str(inst_type))
        if boottime != -1:
            try:
                if self.vmes_usage[ip]:
                    self.vmes_usage[ip]= [boottime, inst_type]            
            except:
                self.vmes_usage[ip]= [boottime, inst_type]
                
    def remove_vm_usage(self, ip):
        try:
            self.cost_vmes_removal = self.cost_vmes_removal + self.calculate_cost(ip)
            del self.vmes_usage[ip]
        except Exception as e:
            self.logger.critical("ERROR trying to remove VM from cost_Aware data IP: "+str(ip)+ " message: "+str(e))
    
    def get_time_usage(self, time_secs):
        sec = timedelta(seconds=int(time_secs))
        d = datetime(1,1,1) + sec    
        time = "%d:%d:%d:%d" % (d.day-1, d.hour, d.minute, d.second)
        
        return time
    
    def cost_shutdown_constraint(self,ip):
        self.logger.info("cost_shutdown_constraint: Checking if it is possible to release "+str(ip)+" vm ")
        for ip_dict, (boottime, inst_type) in self.vmes_usage.iteritems():
            if ip_dict == ip:
                time_secs = time() - boottime
                sec = timedelta(seconds=int(time_secs))
                d = datetime(1,1,1) + sec
            
                # Changed to 35 for the experiments before 20.
                if (60 - d.minute) >= RELEASE_BEFORE_MIN and (60 - d.minute) < RELEASE_BEFORE_MAX:
                    self.logger.info("Releasing machine IP: "+str(ip_dict)+" Time to one hour: "+str(60 - d.minute))
                    return True
            
        return False
    
    def check_shutdown_constraint(self, backend_nodes, instance, number_vmes):
        self.logger.info("check_shutdown_constraint: Checking if it is possible to release "+str(number_vmes)+" vmes of type "+str(instance))
        array_backends = [node.ip for node in backend_nodes]
        
        for ip_dict, (boottime, inst_type) in self.vmes_usage.iteritems():
            if ip_dict in array_backends and inst_type == instance:
                time_secs = time() - boottime
                sec = timedelta(seconds=int(time_secs))
                d = datetime(1,1,1) + sec
                
                # Changed to 35 for the experiments before 20.
                if (60 - d.minute) >= RELEASE_BEFORE_MIN and (60 - d.minute) < RELEASE_BEFORE_MAX:
                    self.logger.info("Releasing machine IP: "+str(ip_dict)+" Time to one hour: "+str(60 - d.minute))
                    number_vmes = number_vmes - 1
                else:
                    self.logger.info("VM with IP: "+str(ip_dict)+" CANNOT be released, Time to one hour: "+str(60 - d.minute))
        
        if number_vmes <= 0:
            return True
        else:
            return False
            
    def print_vm_cost(self):
        self.total_cost = 0 
        for ip, (boottime,inst_type) in self.vmes_usage.iteritems(): 
            time_secs = time() - boottime
            sec = timedelta(seconds=int(time_secs))
            d = datetime(1,1,1) + sec
            inst_cost = self.instances_type_price[self.iaas_driver][inst_type]
            # Store type of instance
            cost = (( (d.day-1) * 24 ) + d.hour ) * inst_cost
            if d.minute > 0:
                cost = cost +  inst_cost
            
            self.total_cost +=  cost
            self.logger.info("IP: "+str(ip)+" Usage (DAYS:HOURS:MIN:SEC): "+self.get_time_usage(time_secs)+" Cost: "+str(cost)+"$")
        
        self.total_cost += self.cost_vmes_removal
        self.logger.info("Total cost infrastructure: "+str(self.total_cost))

    def get_type_instance(self,ip):
        for node_ip, (boottime,inst_type) in self.vmes_usage.iteritems(): 
            if node_ip == ip:
                return inst_type
        return ''
            
    def get_cost_vm(self,inst_type):
        for type, cost in self.instances_type_price[self.iaas_driver].iteritems(): 
            if type == inst_type:
                return float(cost)
                      
            
        
    def calculate_cost(self,ip):
        for ip_dict, (boottime,inst_type) in self.vmes_usage.iteritems():
            if ip_dict == ip:
                time_secs = time() - boottime
                sec = timedelta(seconds=int(time_secs))
                d = datetime(1,1,1) + sec
            
                inst_cost = self.instances_type_price[self.iaas_driver][inst_type]
                # Store type of instance
                cost = (( (d.day-1) * 24 ) + d.hour ) * inst_cost
                if d.minute > 0:
                    cost = cost +  inst_cost
            
                self.logger.info("IP: "+str(ip_dict)+" Usage: "+self.get_time_usage(time_secs)+" Cost: "+str(cost)+"$")
                
                return cost
        return 0

#log.init('/tmp/provisioning.log')
#logger = log.create_logger(__name__)
#cost = Cost_Controller(logger,'OPENNEBULA')
        
#print cost.instance_type_detector(1.0, str('3635248.0'))
            
        
        