#!/usr/bin/env python

from conpaas.core.appmanager.core.base import Base
class Objectives:
        EXECUTION_TIME = "%execution_time"
        COST = "%budget"

class User:
    Keywords = [ "%budget", "%execution_time"]
    Objectives = None
    #Constraint = []
    
    @staticmethod
    def process_constraints(constraints = [], optimization = None):
        pass
        
    @staticmethod
    def validate(cost = 0, execution_time = 0):
        
        keywords = {
                        "%budget" : cost,
                        "%execution_time" : execution_time
                    }
        #replace cost and evaluate constraint
        for constr in User.Objectives.Constraints:
            constraint = constr
            for kw in keywords.keys():
                constraint = constraint.replace(kw, str(keywords[kw]))
            
            if not eval(constraint):
                return False
        return True
    
    
class Objective(Base):   
    
    
    def __init__(self, data):
        if not ("Constraints" in data or "Optimization" in data):
            raise Exception("Invalid SLOs.")
        
        self.Constraints = map(lambda x: str(x), data["Constraints"])
        self.Optimize = data["Optimization"]
            
    def validate(self, properties):
        valid = True
        
        for k in properties:
            
            for c in self.Constraints:
                if k in c:
                    s = c.replace(k, str(properties[k]))
                    if not eval(s):
                        valid = False
                        break
            if not valid:
                break
        return valid 
            
            
    
class SLOs(Base):
    '''
    classdocs
    '''
    accepted_params = [ 
            { 
            'name' : 'ManifestUrl', 
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
            'name' : 'ExecutionArgs',
            'type' : dict,
            'is_array' : True,
            'is_required' : True
            }, 
            { 
            'name' : 'Objective',
            'type' : Objective,
            'is_array' : False,
            'is_required' : False
            }
            ]
    
    def __init__(self, data={}):
        self.PerformanceModel = None
        Base.__init__(self, data)



class SLOParser:
    @staticmethod
    def parse(data):    
        if type(data) != dict or (not ("SLO" in data)):
            print "Invalid SLOs : SLO field not found"
            sys.exit(1)
        slos = SLOs(data["SLO"])
        
        return slos


"""data = {
        "ManifestURL": "/home/anca/workspace/Client/manifest.json",
        "ExecutionArgs": [
            {
                "Value": 500
            }
        ],
        "Objective": {
            "Constraints": [
                "%budget <= 100"
            ],
            "Optimization": "%execution_time"
        }
    }

sl = SLOs(data)

print sl
"""


    