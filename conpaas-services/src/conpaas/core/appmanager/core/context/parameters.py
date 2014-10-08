#!/usr/bin/env python
from pprint import pprint
import random

        
class VariableModel():
    '''
        Mapping model for manifest/system variables
    '''
    def __init__(self, variables):
        '''
        Constructor
        
         Mapping discrete variables to continuous ones     
        '''
        
        "All variables are normalized to [0,1] range"
        self.Interval = [0.0,1.0]
        
        self.vars = {}
        
        for varr in variables:
            
            key = filter(lambda k: k != "DiscreteSet", varr.keys())[0]
            self.vars[key] = {"Continuous" : not(varr["DiscreteSet"]), "Values" : varr[key], "Type" : type(varr[key][0])}
            
            #compute unit
            if self.vars[key]["Continuous"]:
                self.vars[key]["unit"] = (self.Interval[1] - self.Interval[0])/(self.vars[key]["Values"][-1] - self.vars[key]["Values"][0] + 1)
            else:
                self.vars[key]["unit"] = (self.Interval[1] - self.Interval[0])/len(self.vars[key]["Values"])
            
        
    def nrandomize(self, keys = None):
        
        values = {}
        if keys == None:
            keys = self.vars.keys()
        for key in keys:
            values[key] = random.uniform(0, 1)
             
        return values     
        
        
    
    def denormalize(self, variables):
        #print "Values to deMap = ", variables
        values = {}
        
        for key in variables:
            variables[key] = max(min(variables[key],self.Interval[1]),self.Interval[0])
        
            #print "Value to Convert =", variables[key]
            increase_rate = round(float(variables[key]) / float(self.vars[key]["unit"]))
            
            if self.vars[key]["Continuous"]:
                values[key] = self.vars[key]["Type"](max(min( self.vars[key]["Values"][0] + increase_rate, self.vars[key]["Values"][-1]),self.vars[key]["Values"][0]))
                
            else:
                index = int(increase_rate)
                values[key] = self.vars[key]["Type"](self.vars[key]["Values"][max(min(index, len(self.vars[key]["Values"]) - 1),0)])
                
        #print "Result :", values
        return values
    
    
        
    def normalize(self, variables):
        #print "Map ", variables
        values = {}
        
        for key in variables:
            if self.vars[key]["Continuous"]:
                values[key] = self.Interval[0] + (variables[key] - self.vars[key]["Values"][0]) * self.vars[key]["unit"]
            else:
                values[key] = self.Interval[0] + self.vars[key]["Values"].index(variables[key]) * self.vars[key]["unit"]
        #print "Result : ", values
        return values
    
    
    def __str__(self):
        print "Mapping Interval", self.Interval
        pprint(self.vars)
        print
        return str(self.vars)
        
    def get_keys(self):
        return self.vars.keys()
    
    
    def lower_bound_values(self):
        
        variables = {}
        #get first value for all the variables
        for v in self.vars:
            variables[v] = self.vars[v]["Values"][0]
            
        return variables
    
    
    def upper_bound_values(self):
        
        variables = {}
        #get first value for all the variables
        for v in self.vars:
            variables[v] = self.vars[v]["Values"][-1]
            
        return variables
    
    def get_next_value_from(self,key, value):
        if self.vars[key]["Continuous"]:
            if value + 1 <= self.vars[key]["Values"][-1]:
                return value + 1
        else:
            index = self.vars[key]["Values"].index(value) + 1
            if index < len(self.vars[key]["Values"]):
                return self.vars[key]["Values"][index]
        return None

    def get_previous_value_from(self, key, value):
        if self.vars[key]["Continuous"]:
            if value - 1 >= self.vars[key]["Values"][0]:
                return value - 1
        else:
            index = self.vars[key]["Values"].index(value) - 1
            if index >= 0:
                return self.vars[key]["Values"][index]
        return None
    

    def get_values_range(self, key):
        if self.vars[key]["Continuous"]:
            return self.vars[key]["Values"][-1] - self.vars[key]["Values"][0]
        else: 
            return len(self.vars[key]["Values"]) - 1

    def get_value_at_index(self, key, index):
        if self.vars[key]["Continuous"]:
            return self.vars[key]["Values"][0] + index
        else: 
            return self.vars[key]["Values"][index]

