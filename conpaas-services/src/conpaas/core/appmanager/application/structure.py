#!/usr/bin/env python
import sys
from conpaas.core.appmanager.application.base import Base
from conpaas.core.appmanager.application.implementation import Implementation
from conpaas.core.appmanager.application.elements.parameters import Parameter

from conpaas.core.appmanager.utils.math_utils import MathUtils
# from conpaas.core.appmanager.state import CostModel

class Module(Base):
    accepted_params = [
			{
			'name' : 'ModuleName',
			'type' : str,
			'is_array' : False,
			'is_required' : True
			},
			{
			'name' : 'ModuleType',
			'type' : str,
			'is_array' : False,
			'is_required' : True
			},
			{
			'name' : 'Implementations',
			'type' : Implementation,
			'is_array' : True,
			'is_required' : True
			},
			{
			'name' : 'Parameters',
			'type' : Parameter,
			'is_array' : True,
			'is_required' : False
			}
		]


class Application(Base):
	accepted_params = [ 
			{ 
			'name' : 'Name', 
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
			'name' : 'ExtrapolationArgs',
			'type' : str,
			'is_array' : True,
			'is_required' : False
			}, 
			{ 
			'name' : 'Modules',
			'type' : Module,
			'is_array' : True,
			'is_required' : True
			}
		]   
				
	def execute(self, version, configuration, variables = {}):
		#now what????
		# costs = []
		runtimes = []
		exit_code = []


		# curframe = inspect.currentframe()
		# calframe = inspect.getouterframes(curframe, 3)
		# calfile = calframe[3][1]
		# self.manager.logger.debug("INSPECT: %s" % calfile)
		
		for i in range(len(version)):
			selected_implementation = version[i]
			# data = {"Done":False, "ImplementationID":i, "Index":i, "Configuration":configuration, "Arguments":variables }
			# if('profiler' in calfile):
			# 	self.manager.add_experiment(data, True)
			# else:
			# 	self.manager.add_experiment(data, False)
				
			num_instances_per_group = self.Modules[i].Implementations[selected_implementation].Resources.get_num_instances(variables)
			machines = configuration[:sum(num_instances_per_group)]

			#deploy module
			self.Modules[i].Implementations[selected_implementation].deploy(self.manager, machines, variables)
						
			#launch in execution
			ec, runtime = self.Modules[i].Implementations[selected_implementation].execute(self.manager, machines, variables)
			# cost =  runtime * CostModel.calculate(configuration)
			# data["Results"] = {"ExeTime" : runtime, "TotalCost" : cost} 
			# data["Done"] = True
			#store runtime
			# costs.append(cost)
			runtimes.append(runtime)
			exit_code.append(ec)
			
		
			
		if runtimes == []:
			raise Exception("No module executed.")
		
		#return True/False for successful execution and execution time
		# return (False if sum(exit_code) > 0 else True, max(runtimes), max(costs))
		return (False if sum(exit_code) > 0 else True, max(runtimes))
			
	def cleanup(self, version, configuration, variables = {}):
		for i in range(len(version)):
			selected_implementation = version[i]
			num_instances_per_group = self.Modules[i].Implementations[selected_implementation].Resources.get_num_instances(variables)
			machines = configuration[:sum(num_instances_per_group)]
			#cleanup will also check if the execution was successful 
			self.Modules[i].Implementations[selected_implementation].cleanup(self.manager,machines, variables)

	def getGroupIDVars(self, version, groupID):
		variables = []
		for i in range(len(version)):
			selected_implementation = version[i]
			variables.extend(self.Modules[i].Implementations[selected_implementation].Resources.get_group_vars(groupID))
		
		return variables
		
		
	def getResourceConfiguration(self, version, variables):
		configuration = []
		roles = []
		for i in range(len(version)):
			selected_implementation = version[i]
			subconf, role, constraints = self.Modules[i].Implementations[selected_implementation].Resources.get_configuration(variables)
			configuration.extend(subconf)
			roles.extend(role)
		return (roles, configuration, constraints)
		
	
	def get_Vars(self, version = []):
		variables = []
		
		for i in range(len(version)):
			selected_implementation = version[i]
			for param in self.Modules[i].Parameters:
				variables.extend(param.get_Vars())
			variables.extend(self.Modules[i].Implementations[selected_implementation].get_Vars())
		
		variables = list(set(variables))
		return variables
	
	def get_Parameter_Vars(self):
		variables = []
		for i in range(len(self.Modules)):
			for param in self.Modules[i].Parameters:
				variables.extend(param.get_Vars())
		variables = list(set(variables))
		return variables
		
	
	def get_Resource_Vars(self, version = []):
		variables = []
		for i in range(len(version)):
			selected_implementation = version[i]
			variables.extend(self.Modules[i].Implementations[selected_implementation].Resources.get_Vars())
		
		variables = list(set(variables))
		return variables
		
	def getResourceVariableMap(self, version = []):
		variables = []
		for i in range(len(version)):
			selected_implementation = version[i]
			variables.extend(self.Modules[i].Implementations[selected_implementation].Resources.getVariableMap())
		return variables
		
	def getResourceVar2KeyMap(self, version = []):
		variables = {}
		for i in range(len(version)):
			selected_implementation = version[i]
			variables.update(self.Modules[i].Implementations[selected_implementation].Resources.get_var2key_map())
		return variables
		
		
	def getParameterVariableMap(self):
		variables = []
		for i in range(len(self.Modules)):
			for param in self.Modules[i].Parameters:
				variables.extend(param.getVariableMap())
				
		return variables
		
	def getExecutionParameters(self, value_list):
		variables = {}
		#get the parameters for the last module
		for i in range(len(self.Modules[-1].Parameters)):
			param = self.Modules[-1].Parameters[i]
			pid = param.get_id()
			variables[pid] = value_list[i]
		return variables	
		
	def generate_app_versions(self):
		print "--->  Generate Application Versions  <---"
		components_index = []
		for i in range(len(self.Modules)):
			components_index.append(len(self.Modules[i].Implementations) - 1) 

		#print "Component's index interval [ 0, ", max(components_index),"]"
		versions = []

		for item in MathUtils.generate_combinations(components_index):
			versions.append(item)
			
		return versions
    
