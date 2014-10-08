#!/usr/bin/env python

from base import Base


class Metric(Base):
    accepted_params = [ 
            { 
            'name' : 'Range',
            'type' : int,
            'is_array' : True,
            'is_required' : False
            }, 
            { 
            'name' : 'Values',
            'type' : int,
            'is_array' : True,
            'is_required' : False
            }
            ]   
     
    def __init__(self, hash={}):
        if 'Value' in hash:
            
            self.Value = hash['Value']
        else:
            self.Value = None
        
        self.is_dynamic = False
        if type(self.Value) == str or type(self.Value) == unicode:
            self.Value = str(self.Value)
            if str(self.Value).startswith(self.VAR_SIGN):
                self.variables = [str(self.Value)]
                self.is_dynamic = True
        
        Base.__init__(self, hash)
        
        #initialize the value from range or values field ( first value)
        if "Range" in self.__dict__:
            self.currentValue = self.Range[0]
        elif "Values" in self.__dict__: 
            self.currentValue = self.Values[0]
        else:
            self.currentValue = self.Value
            
            
                
    def print_str(self, index = 0):
        sep = "  :  " 
        i = '\n'+('  '* index)
        s = ""
        return " " + str(self.Value) #+ "Value" + sep 
      
      
      
    def get(self, vars = {}):
        if self.Value in vars.keys():
            self.currentValue = vars[self.Value]
        return self.currentValue


    
    def getVariableMap(self):
        
        """
            Override Base method
        """
        
        if self.is_dynamic:
            if "Range" in self.__dict__:
                interval = self.Range
                discrete_set = False
            elif "Values" in self.__dict__: 
                interval = self.Values
                discrete_set = True
            else:
                interval = [self.currentValue, self.currentValue]
                discrete_set = False
                
            return [{ self.Value : interval, "DiscreteSet" : discrete_set}] 
        else:
            return []
        
    
class Attribute(Base):
    accepted_params = [ 
            {
            'type' : Metric, 
            'is_array' : False, 
            'is_required' : True
            }  ]    
   
    def __init__(self, params={}):
        for key in params:
            self.__dict__[key] = Metric(params[key])
            
    def get(self, vars = {}):
        attr = {}
        for key in self.__dict__:
            attr[key] = self.__dict__[key].get(vars)
        return attr
            
    def attributes(self):
        return [self.__dict__[key] for key in self.__dict__]
    
    def get_keys(self):
        """
            returns {Cores: %master_cores, RAM : %master_ram}
        """
        d = {}
        for key in self.__dict__:
            if str(self.__dict__[key].Value).strip().startswith(self.VAR_SIGN):
                d[str(self.__dict__[key].Value).strip()] = str(key).strip()
        return d
    


class Device(Base):
    accepted_params = [ 
            { 
            'name' : 'Role', 
            'type' : str, 
            'is_array' : False, 
            'is_required' : True
            },
            { 
            'name' : 'GroupID',
            'type' : str,
            'is_array' : False,
            'is_required' : True
            }, 
            { 
            'name' : 'Type',
            'type' : str,
            'is_array' : False,
            'is_required' : True
            }, 
            { 
            'name' : 'NumInstances',
            'type' : Metric,
            'is_array' : False,
            'is_required' : True
            },
            { 
            'name' : 'Attributes',
            'type' : Attribute,
            'is_array' : False,
            'is_required' : False
            },
            { 
            'name' : 'Addresses',
            'type' : str,
            'is_array' : False,
            'is_required' : False
            }
            ]   
    
    def get_keys(self):
        """
            returns {Cores: %master_cores, RAM : %master_ram}
        """        
        d = {}
        for key in self.__dict__:
            item = self.__dict__[key]
            if issubclass(item.__class__, Metric) or isinstance(item, Metric):
                if str(item.Value).strip().startswith(self.VAR_SIGN):
                    d[item.Value.strip()] = str(key) 
            elif key == "Attributes":
                d.update(item.get_keys())
        
        return d
    
    def get_configuration(self, variables):
        """
            returns its JSON description
        """        
        d = {"Type" : self.Type, "GroupID":self.GroupID}
      
        for key in self.__dict__:
            item = self.__dict__[key]
            if issubclass(item.__class__, Metric) or isinstance(item, Metric):
                d[key] = item.get(variables)
            elif key == "Attributes":    
                d["Attributes"] = item.get(variables)
        return d
    
class Resources(Base):    
    accepted_params = [ 
            { 
            'name' : 'Roles', 
            'type' : str, 
            'is_array' : True, 
            'is_required' : True
            }, 
            { 
            'name' : 'Devices',
            'type' : Device,
            'is_array' : True,
            'is_required' : True
            }, 
            { 
            'name' : 'MinBandwidth',
            'type' : int,
            'is_array' : False,
            'is_required' : False
            }
            ]    
    def get_keys(self):
        """
            returns a mapping of resource components
                {%master_cores : Cores, %master_ram : RAM }
        """
        d = {}
        
        for dev in self.Devices:
            d.update(dev.get_keys())
        return d
    
    
    def get_configuration(self, variables):
        machines = []
        machineroles = []
        
        # for dev in self.Groups:
        #     machines.append(dev.get_configuration(variables))
        #     machines[-1].update({"GroupID": str(len(machines) - 1)})
        #     machineroles = machineroles + [dev.Role] * dev.Num.get()
        for dev in self.Devices:
            machines.append(dev.get_configuration(variables))
            #machines[-1].update({"GroupID": str(len(machines) - 1)})
            machineroles = machineroles + [dev.Role] * dev.NumInstances.get()
        
        configuration = { 
            "Resources" : machines,
            "Distances" : [] 
        }
        
        return configuration, machineroles
            
    def get_special_variables(self, machinelist):
        variables = {}
        for dev in self.Devices:
            if dev.__dict__.has_key("Addresses") and dev.Addresses.startswith(self.VAR_SIGN):
                #find machines
                value = reduce(lambda y,z : y + ";" + z, map(lambda w : w["IP"], filter(lambda x:x["Role"] == dev.Role, machinelist)))
                variables.update({dev.Addresses : value.strip(";")})
    
        return variables
    
class Argument(Base):
    accepted_params = [ 
            { 
            'name' : 'ArgID', 
            'type' : str,
            'is_array' : False, 
            'is_required' : True
            }, 
            { 
            'name' : 'ArgName',
            'type' : str,
            'is_array' : False,
            'is_required' : False
            }, 
#             { 
#             'name' : 'Type',
#             'type' : str,
#             'is_array' : False,
#             'is_required' : True
#             }, 
#             { 
#             'name' : 'InitValue',
#             'is_array' : False,
#             'is_required' : True
#             },
            { 
            'name' : 'Values',
            'is_array' : True,
            'is_required' : False
            },
            { 
            'name' : 'Range',
            'is_array' : True,
            'is_required' : False
            }           
            ]
    
    def __init__(self, hash={}):
        if 'ArgID' in hash:
            self.argid = str(hash['ArgID'])
        else:
            raise Exception("ArgID missing from the arguments")
        
        self.variables = [str(self.argid)]
        
        Base.__init__(self, hash)
    
    
    def getVariableMap(self):
        
        """
            Override Base method
        """
        
        if "Range" in self.__dict__:
            interval = self.Range
            discrete_set = False
        elif "Values" in self.__dict__: 
            interval = self.Values
            discrete_set = True
        else:
            raise Exception("missing value range for argument")
        return [{ self.argid : interval, "DiscreteSet" : discrete_set}] 

    def get_range_size(self):
        """
            Retrieves number of possible values the argument may take.
        """
        if "Range" in self.__dict__:
            return self.Range[-1] - self.Range[0] + 1
        else:
            return len(self.Values) 
        
    def get_value_at_index(self, index):
        """
            Retrieves arguments value found at index in Values/Range
        """
        if "Range" in self.__dict__:
            return max(min(self.Range[0] + index, self.Range[-1]), self.Range[0])
        else:
            return self.Values[min(max(index, 0), len(self.Values))] 

    def set_values(self, values):
        """
            Set arguments value found at index in Values/Range
        """
        if "Range" in self.__dict__:
            self.Range = values
        else:
            self.Values = list(set(values)) 
    