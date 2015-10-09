#!/usr/bin/env python
from conpaas.core.appmanager.application.base import Base
from conpaas.core.appmanager.application.search_space import Variable
import copy 

class Attributes(Base):
	
	def __init__(self, hashmap={}):
		
		self.items = {}
		for key in hashmap:
			self.items[key] = Variable(hashmap[key])

	def get_key2var_map(self):
		result = {}
		for key in self.items:
			#get variable id (if != None)
			item = self.items[key].get_id()
			if item:
				result[key] = item
		return result
		
	def get_var2key_map(self):
		result = {}
		for key in self.items:
			#get variable id (if != None)
			item = self.items[key].get_id()
			if item:
				result[item] = key
		return result

	def get(self, variables):
		result = {}
		for key in self.items:
			#get variable id (if != None)
			item = self.items[key].get_id()
			if item:
				result[key] = variables[item]
		return result


class Group(Base):
	accepted_params = [ 
			{ 
			'name' : 'Group', 
			'type' : str, 
			'is_array' : False, 
			'is_required' : True
			}, 
			{ 
			'name' : 'Role', 
			'type' : str, 
			'is_array' : False, 
			'is_required' : False
			}, 
			{ 
			'name' : 'Type',
			'type' : str,
			'is_array' : False,
			'is_required' : True
			}, 
			{ 
			'name' : 'NumInstances',
			'type' : Variable,
			'is_array' : False,
			'is_required' : False
			},
			{ 
			'name' : 'Attributes',
			'type' : Attributes,
			'is_array' : False,
			'is_required' : False
			}
		]   
	def __init__(self, hashmap = {}):
		self.Role = "Worker"
		if not("NumInstances" in hashmap):
			self.NumInstances = Variable({"Value" : 1})
		Base.__init__(self, hashmap)	

	def get_var2key_map(self):      
		result = {}
		for key in self.__dict__:
			item = self.__dict__[key]
			if issubclass(item.__class__, Variable) or isinstance(item, Variable):
				iid = item.get_id()
				if iid:
					result[iid] = str(key)
			elif key == "Attributes":
				result.update(item.get_var2key_map())

		return result

	def get_configuration(self, variables):
		"""
			returns its JSON description
		"""        
		subconf = {}

		for key in self.__dict__:
			item = self.__dict__[key]
			if key in ["NumInstances", "Role", "Super"]:
				continue
			if issubclass(item.__class__, Variable) or isinstance(item, Variable):
				iid = item.get_id()
				if iid:
					subconf[key] = variables[iid]
				else:
					subconf[key] = item.Value
					
			elif key == "Attributes":    
				subconf[key] = item.get(variables)
			else:
				subconf[key] = item
		
		num = self.get_num_instances(variables)
		configuration = []
		for i in range(num):
			configuration.append(copy.deepcopy(subconf))
		roles = [self.Role] * num
		return roles, configuration
	
	def get_num_instances(self, variables):
		#extend NumInstances
		num = self.NumInstances.get_id()
		if num:
			num = variables[num]
		else:
			num = self.NumInstances.Value
		return num
	
class Constraint(Base):
	accepted_params = [ 
			{ 
			'name' : 'Source', 
			'type' : str, 
			'is_array' : False, 
			'is_required' : True
			}, 
			{ 
			'name' : 'Target', 
			'type' : str, 
			'is_array' : False, 
			'is_required' : True
			}, 
			{ 
			'name' : 'ConstraintType',
			'type' : str,
			'is_array' : False,
			'is_required' : True
			}
	]
	def __init__(self, hashmap = {}):
		try:
			self.Source = hashmap["Source"]
			self.Target = hashmap["Target"]
			self.ConstraintType = hashmap["ConstraintType"]
		except:
			raise Exception("Missing Source, Target or ConstraintType from Constraints field.")
			

		remaining_keys = filter(lambda x:not (x in ["Source", "Target", "ConstraintType"]), hashmap.keys())

		for key in remaining_keys:
			print "Processing ", key," = ", hashmap[key]
			try:
				self.__dict__[key] = Variable(hashmap[key])
			except:
				self.__dict__[key] = hashmap[key]
	def get_var2key_map(self):      
		result = {}
		for key in self.__dict__:
			item = self.__dict__[key]
			if issubclass(item.__class__, Variable) or isinstance(item, Variable):
				iid = item.get_id()
				if iid:
					result[iid] = str(key)
			else:
				result[key] = item

		return result

	def get_configuration(self, variables):
		"""
			returns its JSON description
		""" 
		result = {}
		for key in self.__dict__:
			item = self.__dict__[key]
			if issubclass(item.__class__, Variable) or isinstance(item, Variable):
				iid = item.get_id()
				if iid and iid in variables.keys():
					result[key] = variables[iid]
			else:
				result[key] = item

		return result




class Resources(Base):    
	accepted_params = [ 
			{ 
			'name' : 'Groups',
			'type' : Group,
			'is_array' : True,
			'is_required' : True
			}, 
			{ 
			'name' : 'Constraints',
			'type' : Constraint,
			'is_array' : True,
			'is_required' : False
			}
	]    
	
	def get_group_vars(self, groupid):
		for gr in self.Groups:
			if gr.Group == groupid:
				return gr.get_Vars()			
	
	
	def get_var2key_map(self):
		"""
			returns a mapping of resource components
				{%master_cores : Cores, %master_ram : RAM }
		"""
		d = {}
		
		for group in self.Groups:
			d.update(group.get_var2key_map())
			
		for constr in self.Constraints:
			d.update(constr.get_var2key_map())
		return d


	def get_configuration(self, variables):
		configuration = []
		roles = []
		constraints = []
		for gr in self.Groups:
			role, subconfig = gr.get_configuration(variables)
			roles.extend(role)
			configuration.extend(subconfig)
		
		for constr in self.Constraints:
			constraints.append(constr.get_configuration(variables))
		return configuration, roles, constraints
			

	def get_num_instances(self, variables):
		num = []
		for gr in self.Groups:
			num.append(gr.get_num_instances(variables))
		return num
