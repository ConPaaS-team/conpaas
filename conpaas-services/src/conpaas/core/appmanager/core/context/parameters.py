#!/usr/bin/env python
from pprint import pprint
import random

        
class VariableModel():
    '''
    classdocs
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
                self.vars[key]["unit"] = (self.Interval[1] - self.Interval[0])/(self.vars[key]["Values"][-1] - self.vars[key]["Values"][0])
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
        #print "Values to Convert = ", variables
        values = {}
        
        for key in variables:
            variables[key] = max(min(variables[key],self.Interval[1]),self.Interval[0])
        
            #print "Value to Convert =", variables[key]
            increase_rate = variables[key] / self.vars[key]["unit"]
            
            if self.vars[key]["Continuous"]:
                values[key] = self.vars[key]["Type"](max(min( self.vars[key]["Values"][0] + increase_rate, self.vars[key]["Values"][-1]),self.vars[key]["Values"][0]))
                
            else:
                index = int(increase_rate)
                values[key] = self.vars[key]["Type"](self.vars[key]["Values"][max(min(index, len(self.vars[key]["Values"]) - 1),0)])
                
            
        return values
    
    
        
    def normalize(self, variables):
        
        values = {}
        
        for key in variables:
            if self.vars[key]["Continuous"]:
                values[key] = self.Interval[0] + (variables[key] - self.vars[key]["Values"][0]) * self.unit
            else:
                values[key] = self.Interval[0] + self.vars[key]["Values"].index(variables[key]) * self.unit
            
        return values
    
    
    def __str__(self):
        #print "Mapping Interval", self.Interval
        #pprint(self.vars)
        #print
        return str(self.vars)
        
    def get_keys(self):
        return self.vars.keys()