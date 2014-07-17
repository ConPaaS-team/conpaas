#!/usr/bin/env python
from base import Base

class Action(Base):
    role  = ""
    start = ""
    stop  = ""
    def __init__(self, hash={}):
        
        if 'ROLE' in hash:
            self.role = hash['ROLE']
        
        if 'START' in hash:
            self.start = hash['START']['Script']
        
        if 'STOP' in hash:
            self.stop = hash['STOP']['Script']
        
class EnvironmentVars(Base):
    
    def __init__(self, vars):
        #parse dictionary
        self.Variables = vars
        
    def replace(self, model_variables = {}):
        """
            model_variables = {"%master_address": "192.56.2.12"}
            
            Environment variable "$MASTER_IP": "%master_address" will be 
            transformed in something as "$MASTER_IP": "192.56.2.12"
            Replaces model variables with the values retrieved from configuration
        """        
        ev = {}
        for v in self.Variables:
            value = self.Variables[v][:]
            print value
            for mv in model_variables:
                if mv in value:
                    value = value.replace(mv, str(model_variables[mv]))
                    
            ev[v] = value
            
        return ev
                
                
                    
    def __str__(self):
        return str(self.Variables)
        
        
class DeployOperation(Base):
    accepted_params = [ 
            {
            'name' : 'Actions',
            'type' : Action, 
            'is_array' : True, 
            'is_required' : True
            },
            {
            'name' : 'EnvironmentVars',
            'type' : EnvironmentVars, 
            'is_array' : False, 
            'is_required' : True
            }
           ]     
    
    def get_start_script(self, role = None):
        script = None
        for action in self.Actions:
            if action.role == role:
                script = action.start
                break
        return script
    
    def get_stop_script(self, role = None):
        script = None
        for action in self.Actions:
            if action.role == role:
                script = action.stop
                break
                
        return script
       
class Activation(Base):
    EndpointRole = None
    def __init__(self, hash={}):
        if 'TARGET' in hash:
            self.EndpointRole = hash['TARGET']['ID']
        self.Command = hash['ExecuteCMD']
        self.EndPoint = None
        
        
    def getCommand(self, vars = {}):
        #replace arguments in execution command
        cmd = self.Command[:]
        for key in vars:
            if key in self.Command:
                cmd = cmd.replace(key, str(vars[key]))
                
        return cmd
        
        