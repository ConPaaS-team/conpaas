'''
Created on Jul 23, 2013

@author: Vlad
'''
import random

class Configuration:
    def __init__(self,types_list, cost_list, limit_list):
        self.keys = dict(zip(types_list, range(len(types_list))))
        self.averages = {}      # dictionary of averages with k as a machine type
        self.rav = {}      # dictionary of averages with k as a machine type
        self.notasks = {}      # dictionary of averages with k as a machine type
        self.throughput = {}    # dictionary of tasks with relevant time unit as k
        self.conf = {}
        self.costs = dict(zip(types_list,cost_list))
        self.limits = dict(zip(types_list,limit_list))
        self.ratios={}
        for k in self.keys:
            self.costs[self.keys[k]]=self.costs[k]
            del self.costs[k]
            self.limits[self.keys[k]]=self.limits[k]
            del self.limits[k]
            self.notasks[self.keys[k]] = 0
            self.averages[self.keys[k]] = 0
            self.rav[self.keys[k]] = 0
            self.conf[self.keys[k]]= 0
        random.seed()
        self.conf_dict = {}
        self.m = {}
    
    def relevant_time_unit(self):
        rk = random.choice(self.averages.keys())
        t=60
        self.throughput[rk] = round(t / self.averages[rk])
        self.unit = t
        
        for k in self.costs:
            self.costs[k] *= float(self.unit)/3600
        self.compute_throughput()
        
        return self.unit
    
    def compute_throughput(self):
        for k in self.averages:
            self.throughput[k] = round(self.unit / self.rav[k])
    
    def set_average(self,m_type,value, count):
        if self.keys[m_type] in self.averages.keys():
            self.averages[self.keys[m_type]]=value
            self.notasks[self.keys[m_type]] +=count
            if m_type=='small':
                self.rav[self.keys[m_type]]= value
            if m_type=='medium':
                self.rav[self.keys[m_type]]= value/4
            if m_type=='large':
                self.rav[self.keys[m_type]] = value/8

            
    def compute_ratios(self):
        for k in self.costs:
            self.ratios[k] = round(self.costs[k]/self.throughput[k], 5 )
    
    def compute_tmax(self):
        tmax = 0
        for k in self.throughput:
            tmax += self.limits[k]*self.throughput[k]
        return tmax
    
    def cost_conf(self):
        c = 0
        for k in self.costs:
            c += self.conf[k]*self.costs[k]
        return c
            
    def cheap_check(self,start,target):
        cheap_list = self.costs.values()
        sorted_list = sorted(self.costs.values())
        cheap = 0
        for p in sorted_list:
            kp = cheap_list.index(p)
            if start + self.throughput[kp] > target and kp in self.ratios.keys() :
                self.conf[kp]+=1
                cheap=1
                break
        return cheap
    def compute_configuration(self, target):
               
        for k in self.averages:
            self.conf[k]= 0
        self.compute_ratios()
        
        start = 0        
        
        while start < target and len(self.ratios)>0:
            if self.cheap_check(start, target) ==1:
                return self.conf
            
            r = self.ratios.values()
            m = min(r)
            for km in self.ratios:
                if self.ratios[km] == m:
                    break
            while self.limits[km] > self.conf[km]:
                start+=self.throughput[km]
                self.conf[km]+=1
                if start >= target:
                    return self.conf
                if self.cheap_check(start, target) == 1:
                    return self.conf
            del self.ratios[km]
        
        return self.conf
    
    def dynamic_configuration(self):
        
        tmax = self.compute_tmax()
        for k in self.limits:
            self.conf[k]=self.limits[k]
        t = tmax - 1
        self.conf_dict = {}
        self.conf_dict[tmax] = self.conf
        self.m = {}
        self.m[tmax] = self.cost_conf()
        while t >= 0:
            self.m[t]=self.m[t+1]
            km = -1 
            for k in self.throughput:   
                if tmax - self.throughput[k] >= t:
                    if self.m[t] > self.m[t+self.throughput[k]] - self.costs[k] and self.conf_dict[t+self.throughput[k]][k]>0:
                        self.m[t] = self.m[t+self.throughput[k]] - self.costs[k]
                        km = k
            if km > -1:
                self.conf_dict[t] = self.conf_dict[t+self.throughput[km]].copy()
                self.conf_dict[t][km] -= 1
            else:
                self.conf_dict[t] = self.conf_dict[t+1].copy()
            
            t-=1
        self.m[0]=0
        return self.m



