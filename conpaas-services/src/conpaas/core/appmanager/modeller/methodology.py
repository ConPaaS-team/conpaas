#!/usr/bin/env python

from conpaas.core.appmanager.modeller.model import FunctModel
from conpaas.core.appmanager.utils.math_utils import MathUtils
from conpaas.core.appmanager.state import solution
import numpy, random, copy, time
import matplotlib.pyplot as plt
import math, sys, os, json
import simplejson
from sklearn.cross_validation import cross_val_score, KFold, ShuffleSplit, LeavePLabelOut


class ModellingMethod:	
		
	def __init__(self, solutions, execution_function, variable_mapper, profiling_input):
		#functions to call when running the app on a configuration
		self.app_execution_function_call = execution_function
		self.benchmark_input = profiling_input
		self.variable_mapper = variable_mapper
		#dicts
		self.profiling_solutions = solutions
		#solutions not tested during profiling but discovered during modelling
		#solution objects
		self.additional_solutions = []
		self.training_set = []
		self.failed_set = []
		#dicts
		self.selected_solutions = []
		self.testing_set = []
		#start from linear model
		self.model = FunctModel()
		self.max_evals = 7
		self.iterations = 0
		self.init_steps = 3
		
		self.constraints = {}
		#start the modelling process by seleting a number of optimal/non-optimal configurations to test on the big size input
		self.selected_solutions = self.select_training_configurations()
		self.testing_set = self.selected_solutions[:]
		
		
		
	def update_state(self, params = {}): 
		
		print "Update state ... params=", params.keys()
		if params == {}:
			return
		self.max_evals = params["max_evals"]
		self.init_steps = params["init_steps"]
		self.iterations = params["iterations"]
		self.constraints = params["constraints"]
		self.training_set = map(lambda s: solution(s), params["training_set"])
		self.testing_set = params["testing_set"]
		self.additional_solutions = map(lambda s: solution(s), params["additiona_small_input_solutions"])
		self.selected_solutions = params["selected_configurations"]
		self.failed_set = map(lambda s: solution(s), params["failed_set"])
		
		self.model.restore(params["mathematical_model"])
		
		
	def get_state(self):
		
		result = { 
					"max_evals" : self.max_evals, 
					"init_steps": self.init_steps,
					"iterations"  : self.iterations,
					"constraints"  :self.constraints,
					"additiona_small_input_solutions":map(lambda sol: sol.get(), self.additional_solutions),
					"training_set" : map(lambda sol: sol.get(), self.training_set), 
					"testing_set" : self.testing_set,
					"failed_set" : map(lambda sol: sol.get(), self.failed_set),
					"selected_configurations" : self.selected_solutions,
					"mathematical_model" : self.model.save_state()
		}
		if self.constraints == []:
			self.constraints = {}
		return result

	def _get_constraints(self):
		constr = []
		for key in self.constraints:
			constr.append("%s > %s" % (key, str(self.constraints[key]))) 
		return constr
	
	def _update_constraints(self, key, value):
		if key in self.constraints.keys():
			self.constraints[key] = max([self.constraints[key], value])
		else:
			self.constraints[key] = value
			
	def _apply_constraints(self):
		result = []
		for conf in self.testing_set:
			c = copy.deepcopy(conf)
			for key in self.constraints:
				if not self.variable_mapper.isvalid(key, c[key], self.constraints[key]):
					c[key] = self.variable_mapper.get_next_value_from(key, self.constraints[key])
			if all(c.values()) and (not (c in result)):
				result.append(c)
		return result
			
	def _process_bottleneck(self, failed_conf, bottlenecks = {}):
		
		if any(bottlenecks.values()):
			new_conf = copy.deepcopy(failed_conf)
			#derive the new configuration
			for key in bottlenecks.keys():
				if bottlenecks[key]:
					#store bound in constraints
					self._update_constraints(key, failed_conf[key])
					#get a higher value for the bottleneck resource
					new_conf[key] = self.variable_mapper.get_next_value_from(key, failed_conf[key])#self.variable_mapper.get_maximum_value_of(key)#
					
					if new_conf[key] == None:
						raise Exception("Field %s has no valid value for extrapolation." %(key))
						return None
			#run conf
			print "Generated ", new_conf, " from ", failed_conf
			#run the new conf
			success, var_order, cost, et, direction, monitor = self.app_execution_function_call(new_conf)
			print success
			if success["Success"]:
				self.training_set.append(solution({"conf" : new_conf, "x" : None, "cost" : cost, "et" : et, "gradient" : direction, "monitor" : monitor, "success" : success["Success"]}))
				self.iterations += 1
				bottleneck_detected = True
				print "Bottleneck detected!!!"
				print "Constraints updated :", self.constraints
				return new_conf
			else:
				self.failed_set.append(solution({"conf" : new_conf, "x" : None, "cost" : cost, "et" : et, "gradient" : direction, "monitor" : monitor, "success" : success["Success"]}))	
				return self._process_bottleneck(new_conf, bottlenecks = success["Bottleneck"])
		else:
			#can't detect the bottleneck from the utilisation 
			print "Unknown failure."
			
			bottleneck_detected = False
			print "Test neighbor configurations to detect the bottleneck."
			#run additional experiments to identify the bottleneck
			for variable in failed_conf.keys():
				print "Checking variable = ",variable 
				#current_value = self.variable_mapper.get_maximum_value_of(variable)
				current_value = self.variable_mapper.get_next_value_from(variable, failed_conf[variable])
				nconf = None
				print "Constraints : ",self.constraints
				while current_value != None and self.variable_mapper.isvalid(variable, current_value, failed_conf[variable]):
					if nconf == None:
						nconf = copy.deepcopy(failed_conf)
					#print "Testing", current_value, " for", variable
					#get a higher value for the bottleneck resource
					nconf[variable] = current_value
					constraints = self._get_constraints()
					constrs = []
					for c in constraints:
						for key in nconf.keys():
							c = c.replace(key, str(nconf[key]))
						constrs.append(c)
					print "Constraints checked :", constrs
					if all(map(lambda c: eval(c), constrs)):

						break
					else:
						nconf = None
					if nconf == None:
						current_value = self.variable_mapper.get_next_value_from(variable, current_value)
						print "Next value to test for ", variable , " is", current_value
						continue
					else:
						break
					
				if nconf == None or nconf[variable] == failed_conf[variable]:
					nconf = None
					continue
				
				print "Generated ", nconf, " from ", failed_conf
				#run the new conf
				success, var_order, cost, et, direction, monitor = self.app_execution_function_call(nconf)
				print success
				if success["Success"]:
					self.training_set.append(solution({"conf" : nconf, "x" : None, "cost" : cost, "et" : et, "gradient" : direction, "monitor" : monitor, "success" : success["Success"]}))
					self.iterations += 1
					self._update_constraints(variable, failed_conf[variable])
					bottleneck_detected = True
					print "Bottleneck detected!!!"
					print "Constraints updated :", self.constraints
					break
				else:
					self.failed_set.append(solution({"conf" : nconf, "x" : None, "cost" : cost, "et" : et, "gradient" : direction, "monitor" : monitor, "success" : success["Success"]}))	
					nconf = self._process_bottleneck(nconf, bottlenecks =  success["Bottleneck"])
					if nconf != None:
						bottleneck_detected = True
						break
			if not bottleneck_detected:
				print "Dead-end solution."
				return None
				
			return nconf
				

	
	def run_step(self):
		#self.check_state()
		if self.stop_condition():
			return 0
		print "\n\n =======>>>> Configurations already tested :"
		for c in map(lambda s : s.get()["conf"],self.training_set):
			print c
		print "==================================================================\n"
		
		print "\n\n =======>>>> Configurations left for test :"
		for c in self.testing_set:
			print c
		print "==================================================================\n"		
		
		print "Running extrapolating step..."		
		conf_to_test = self.testing_set[0]
		
		#remove configuration from the testing set
		self.testing_set = self.testing_set[1:]
		
		print "Testing conf:", conf_to_test
		success, var_order, cost, et, direction, monitor = self.app_execution_function_call(conf_to_test)
		print success
		if success["Success"]:
			self.training_set.append(solution({"conf" : conf_to_test, "x" : None, "cost" : cost, "et" : et, "gradient" : direction, "monitor" : monitor, "success" : success["Success"]}))
			self.iterations += 1
		else:
			self.failed_set.append(solution({"conf" : conf_to_test, "x" : None, "cost" : cost, "et" : et, "gradient" : direction, "monitor" : monitor, "success" : success["Success"]}))
			
			bottlenecks = success["Bottleneck"]
			print "Looking for bottlenecks"
			#look for a working configuration 
			new_conf = self._process_bottleneck(conf_to_test,  bottlenecks)
			print "\n\n~~~~~~~~~~~~~~~ New configuration has been found.~~~~~~~~~~~~~~~~~~~~~~~~"
			#apply constraints on the testing set and remove the bottlenecked ones
			self.testing_set = self._apply_constraints()
			if new_conf != None:
				print "Found a Bottleneck...updating configuration list"
				self.testing_set = filter(lambda c: c != new_conf, self.testing_set)
				
				benchmarked = [new_conf] + self.testing_set
				
				pf =  map(lambda x:x["conf"], self.profiling_solutions + map(lambda y : y.get(), self.additional_solutions))
				small_input = self.benchmark_input
				#if new_conf hasn't been discovered during profiling we must test the small input size 
				for c in benchmarked:
					if not (c in pf):
						#run the small input on the new configuration
						success, var_order, cost, et, direction, monitor = self.app_execution_function_call(c, small_input)
						print success
						if success["Success"]:
							self.additional_solutions.append(solution({"conf" : c, "x" : None, "cost" : cost, "et" : et, "gradient" : direction, "monitor" : monitor, "success" : success["Success"]}))
						else:
							print "Invalid solution for benchmarking input. Remove the current tested solution."
							#self.testing_set = filter(lambda x: x != c, self.testing_set)						
		self.generate_model()
		print "Failed : ", len(self.failed_set)	
		return 1
		
	def stop_condition(self):
		#print "iter : ",self.iterations, "max eval : ", self.max_evals
		#print self.iterations >= self.max_evals
		#print self.iterations > 0 and self.testing_set == []
		if self.testing_set == []:
			return True
		return self.iterations >= self.max_evals or (self.iterations > 0 and self.testing_set == [])
		
	def generate_model(self):
		#need at least 2 points to create a model
		if self.iterations < 2 and len(self.testing_set) > 0:
			return
		
		train_confs =  map(lambda sol:sol.conf, self.training_set)
		
		print "~~~   Training set :\n", train_confs
		#add small input execution time from the profiling
		all_benchmarked_confs = map(lambda z : (z["conf"], z["et"]), self.profiling_solutions)
		#add et from confs discovered during modelling and not during profiling
		#print "additional :", map(lambda z : z.conf, self.additional_solutions)
		all_benchmarked_confs.extend(map(lambda z : (z.conf, z.et), self.additional_solutions))
		print "~~~   Benchmarked set :\n", all_benchmarked_confs
		xtrain, ytrain = [], [] 
		for c in train_confs:
			try:
				the_one = filter(lambda z: c == z[0], all_benchmarked_confs)[0]
			except:
				print "Missing benchmark of ",c
				continue
			#z = tuple of (conf, et)
			xtrain.append(the_one[1])
			
			#now append the big size input et
			the_one = filter(lambda sol:c == sol.conf, self.training_set)[0]				
			ytrain.append(the_one.et)
			
		print xtrain,  ytrain
		self.model.fit(xtrain, ytrain)
		
		#scores.append(self.model.score(xtest, ytest))
	
	def select_training_configurations(self):
		#1/3 cost pareto optimal 
		#1/3 et pareto optimal
		#1/3 non-pareto
		
		profiled_solutions = filter(lambda c :c["success"], self.profiling_solutions)
		num = self.max_evals
		pex = self.get_pareto_experiments(profiled_solutions)
		exps = []
		if len(pex) < 2 * (num/3):
			exps.extend(pex[:])
		else:
			exps.extend(pex[:num/3])
			exps.extend(pex[-(num/3):])
			
		while len(exps) < num and len(exps) < len(profiled_solutions):
			left_exps = filter(lambda e: not(e["conf"] in map(lambda x:x["conf"], exps)), profiled_solutions)
			e = left_exps[random.randint(0,len(left_exps ) - 1)]
			#print map(lambda x:x["Configuration"], pex)
			#print e["Configuration"]
			if not(e["conf"] in map(lambda x:x["conf"], exps)):
				exps.append(e)
		print "done selecting test configurations : "
		return map(lambda e:e["conf"], exps)
		
	def get_pareto_experiments(self, exps):
		"""
			Select experiments with the optimal cost-et trade-off        
		"""
		cost = map(lambda x: x["cost"], exps)
		et = map(lambda x: x["et"], exps)

		pcost, pet = MathUtils.pareto_frontier(cost, et)
		print "Pareto cost:", pcost
		print "Pareto et  :", pet
		print "Total Number experiments :", len(exps)
		print "Number Pareto experiments :", len(pcost)
		pex = []

		for exp in exps:
			for i in range(len(pcost)):
				if exp["cost"] == pcost[i] and exp["et"] == pet[i]:
					pex.append(exp)	
		return pex
		
	def get_model(self):
		if self.model.F == None:
			#fit a model based on data gathered so far
			self.generate_model()
			print self.model.F
			print self.model.Fcode
		return (self.model, self.constraints)
	
	def get_all_solutions(self):
		
		small_input_exps	= self.profiling_solutions + map(lambda sol: sol.get(), self.additional_solutions)
		big_input_exps  	=  map(lambda sol: sol.get(), self.training_set)
		
		return (small_input_exps, big_input_exps)
