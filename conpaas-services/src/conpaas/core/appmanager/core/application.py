#!/usr/bin/env python

from base import Base
from module import Module

class Application(Base):
    accepted_params = [ 
            { 
            'name' : 'ApplicationName', 
            'type' : str,
            'is_array' : False, 
            'is_required' : True
            }, 
            { 
            'name' : 'Author',
            'type' : str,
            'is_array' : False,
            'is_required' : False
            }, 
            { 
            'name' : 'PerformanceModel',
            'type' : str,
            'is_array' : False,
            'is_required' : False
            },
            { 
            'name' : 'Modules',
            'type' : Module,
            'is_array' : True,
            'is_required' : True
            }
            ]
    
    def __init__(self, data={}):
        Base.__init__(self, data)
        if "PerformanceModel" not in self.__dict__:
            self.PerformanceModel = None
        
    
    