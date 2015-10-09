#!/usr/bin/env python
from conpaas.core.appmanager.application.search_space import VariableMapper
from conpaas.core.appmanager.executor import Executor
from conpaas.core.appmanager.modeller.methodology import ModellingMethod
from conpaas.core.appmanager.state import State

import sys, os, json, traceback



class Extrapolator:
	StateID = 1
	def __init__(self, application, version, variables, solutions, input_size):
		self.application = application
		self.strategy    = None
		self.version     = version
		self.version_indexes = map(lambda x: int(x), version.split("."))
		
		self.profiling_solutions = solutions
		self.benchmark_solutions = solutions[-1]["Configurations"]
		self.benchmark_input	 = solutions[-1]["Input"]
		#print self.version_indexes
		self.variables 	 = variables
		
		self.newinput = input_size
		print "Variables in extrapolator :", self.variables
		self.mapper = VariableMapper(self.application.getResourceVariableMap(self.version_indexes))
	
		self.strategy = ModellingMethod(self.benchmark_solutions, self.execute_application, self.mapper, self.benchmark_input) #
		data = self.restore()
		if data == []:
			#to init state
			self.save_state()
		
		
	def restore(self):
		#load state
		data = State.get_data(self.version, self.StateID)
				
		for inputsize in data:
			try:
				algdata = inputsize["Methodology"]
			except:		
				inputsize = {
					"Input" : self.newinput,
					"BenchmarkInput" : self.benchmark_input,
					"Methodology" : {},
				}
				State.checkpoint(self.version, self.StateID, data)
				continue
				
			if not(algdata in[ None, {}, [] ]):
				self.benchmark_input = inputsize["BenchmarkInput"]
				self.benchmark_solutions = None
				for sol in self.profiling_solutions:
					if sol["Input"] == self.benchmark_input:
						self.benchmark_solutions = sol["Configurations"]
				
				if not self.benchmark_solutions:
					#the benchmark input from the save file doesn't have any solution explored
					self.benchmark_input = self.profiling_solutions[-1]["Input"]
					self.benchmark_solutions = self.profiling_solutions[-1]["Configurations"]
				
				self.strategy.update_state(algdata)
				#if profiling with the input size was finished go to the next one
				if not self.strategy.stop_condition():
					break
		return data			
		
		
	def run(self):
		print "Extrapolating for [", self.newinput, "]",
		self.restore()
		if self.strategy.stop_condition():
			print "... already done."
			return 0
		print "..."
		while not self.strategy.stop_condition():
			try:				
				ret = self.strategy.run_step()
			except:
				traceback.print_exc()
				print 'An exception/exit signal occurred. Exiting'
				raise Exception("Exit")
				break
			self.save_state()
			
			print "Return code : ", 0 if ret is 0 else 1, "(0 - stop condition was met)"
			if ret is 0:
				print "Extrapolating Done. "
				break
		
		
		
	def save_state(self):
		print "Save state to file."
		data = State.get_data(self.version, self.StateID)		
		algdata = self.strategy.get_state()
		info = {
				"Input" : self.newinput,
				"BenchmarkInput" : self.benchmark_input,
				"Methodology"   : algdata
				}
		q = False
		for inputsize in data:
			if inputsize["Input"] == self.newinput:
				inputsize.update(info)
				q = True
		if not q:
			data.append(info)
			
		State.checkpoint(self.version, self.StateID, data)
	
	
	def execute_application(self, variables, input_size = None):
		#configuration
		print variables
		#if an input is specified, execute app with it otherwise run with the modelling input
		if not input_size:
			input_size = self.newinput
			
		success, conf, cost, execution_time, gradient, utilisation = Executor.execute_on_configuration(self.application, self.version_indexes, self.variables,  variables, input_size)
		
		print gradient
		#execute application should return the variables, cost and time of execution and feedback based on monitoring
		return (success, self.variables, cost, execution_time, gradient, utilisation)
		
		
		
	def get_explored_solutions(self):
		
		return self.strategy.get_all_solutions()
		
	def get_model(self):
		return self.strategy.get_model()
