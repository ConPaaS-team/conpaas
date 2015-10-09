#!/usr/bin/env python
from conpaas.core.appmanager.application.search_space import Variable

    
class Parameter(Variable):

    def __init__(self, hashmap={}): 
        Variable.__init__(self, hashmap)
        if 'Name' in hashmap:
            self.Name = hashmap['Name']
        else:
            raise Exception("Missing parameter name.")
        
            
    def get(self, params = {}):
        attr = {}
        for key in self.__dict__:
            attr[key] = self.__dict__[key].get(params)
            
        return attr
            
    def attributes(self):
        return [self.__dict__[key] for key in self.__dict__]
    
    
    def get_keys(self):
        
        val = self.get_id()
        
        if val != None:
            return {self.Name : val}
           
        return {}
        
    
    
