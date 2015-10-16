#!/usr/bin/env local
from pprint import pprint

from conpaas.core.appmanager.modeller.model import FunctModel
from conpaas.core.appmanager.utils.math_utils import MathUtils
from conpaas.core.appmanager.executor import Executor
from conpaas.core.appmanager.profiler.profiler import Profiler
from conpaas.core.appmanager.modeller.extrapolator import Extrapolator
from conpaas.core.appmanager.application.search_space import VariableMapper

from conpaas.core.appmanager.state import State, CostModel

import copy



class SLOEnforcer:
	StateID = 2
	def __init__(self, application, versions):
		self.application = application
		self.versions = versions


	def set_slo(self, slo):
		self.slo = slo


	def get_aggregated_pareto(self, exps):
		info = self._predict_performance(exps)
		best_confs = self._select_best(info)
		if best_confs:
			self.application.manager.logger.debug("best confs: %s" % best_confs) 
			return self._convert_to_cps_format(best_confs)
		return []
		

	def aggregate(self, data):
		exps_bm = data
		versions = map(lambda c: "-".join(map(lambda x:str(x), c["Implementations"])), exps_bm)
		versions = list(set(versions))

		exps = {}
		for v in versions:
			exps[v] = []
			for c in exps_bm:
				if c["Implementations"] == map(lambda x:int(x), v.split("-")):
					exps[v].append(c)
		return exps

	def select_versions(self, exps):
		benchmarked = exps["experiments"]
		extrapolated = exps["extrapolations"]

		bm = self.aggregate(benchmarked)
		extr = self.aggregate(extrapolated)

		return bm, extr


	def _predict_performance(self, exps):
		info = {}

		bmarked, extr = self.select_versions(exps)
		self.versions = extr.keys()

		for version in self.versions:
			info[version] = {}
			info[version]["InputProfiled"] = []
			if len(bmarked) > 0:
				info[version]["InputProfiled"] = map(lambda x: { "conf" : x["ConfVars"], "params": x["Parameters"], "monitor":x["Monitor"], "et" : x["Results"]["ExeTime"], "tested"  :True , "Configuration" : x["Configuration"]}, bmarked[version]) 
			info[version]["InputCurrent"] = map(lambda x: { "conf" : x["ConfVars"], "params": x["Parameters"], "monitor":x["Monitor"], "et" : x["Results"]["ExeTime"], "tested"  :True , "Configuration" : x["Configuration"]}, extr[version])
			open('/tmp/debug', 'a').write('profiled: %s \n' % info[version]["InputProfiled"])
			# print "\n\n------------------  CONFIGURATIONS  ----------------------\n"
			# print "~~~  Benchmarked  ~~~"
			# for c in bmarked[version]:
			# 	print c["ConfVars"]
			
			# print "~~~  Extrapolated ~~~"
			# for c in extr[version]:
			# 	print c["ConfVars"]
			# print "\n--------------------------------------------------------------\n"
			if len(info[version]["InputProfiled"]) > len(info[version]["InputCurrent"]):
				#predict the performance of the untested profiled configurations with the current input
				confs_tested = map(lambda x:x["conf"], info[version]["InputCurrent"])
				benchmarked =  map(lambda x:x["conf"], info[version]["InputProfiled"])
				not_tested_confs = filter(lambda x:not(x in confs_tested), benchmarked)
				
				#use model to predict the cost and et of the confs not tested with the current input			
				x_fit = []
				y_fit = []

				for conf in confs_tested:
					tested_prof = filter(lambda c : c["conf"] == conf, info[version]["InputProfiled"])
					tested_curr = filter(lambda c : c["conf"] == conf, info[version]["InputCurrent"])
					if len(tested_prof) > 0:
						x_fit.append(tested_prof[0]["et"])
					if len(tested_curr) > 0:
						y_fit.append(tested_curr[0]["et"])
				
				if len(x_fit) != len(y_fit):
					return info
				
				model = FunctModel()
				model.fit(x_fit,y_fit)


				x = []
				for i in range(len(not_tested_confs)):
					conf = not_tested_confs[i]
					#predict
					index = benchmarked.index(conf) 
					x.append(info[version]["InputProfiled"][index]["et"])
					
				print "x = ",x
				fx = model.predict(x)
				
				predicted_confs = map(lambda i : {"conf" : not_tested_confs[i], "Configuration":filter(lambda c : c["conf"] == not_tested_confs[i], info[version]["InputProfiled"])[0]["Configuration"], "et" : fx[i], "tested" : False}, range(len(fx)) )
				
				info[version]["InputCurrent"].extend(predicted_confs)
					
		return info
				
			
	def _select_best(self, info):
		all_confs = {}
		pareto = {}
		for version in self.versions:
			version = map(lambda x: int(x), version.split("-"))
			v  = ".".join(map(lambda s: str(s), version))
			data = info[v]["InputCurrent"][:]
			
			print data
			
			#update the cost
			for c in data:
				# self.application.manager.logger.debug("##### version: %s, conf: %s" % (version, c["conf"]))
				# self.application.manager.logger.debug("##### version: %s, conf: %s" % (type(version), type(c["conf"])))
				_, conf, _constr  = self.application.getResourceConfiguration(version, c["conf"])
				# conf = c["Configuration"]
				cost = self.application.manager.get_cost(conf, _constr)
				#update the dict
				c["cost"] = cost * c["et"]
				c["Version"] = version
			open('/tmp/debug', 'a').write('extrapolated: %s \n' % data)
			all_confs[v] = data[:]
			
			pareto[v] = self._get_pareto_experiments(data)[:]
		
		# if len(pareto) > 0:
		# 	pareto = reduce(lambda x,y: x+y, pareto.values())
		# open('/tmp/debug', 'a').write('pareto: %s \n' % pareto)
		return self._get_pareto_experiments(reduce(lambda x,y: x+y, pareto.values()))
		
	def _get_pareto_experiments(self, exps):
	# def get_pareto_experiments(self, exps):
		"""
			Select experiments with the optimal cost-et trade-off        
		"""
		print exps
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
	
	def _convert_to_cps_format(self, exps):
		cps_exps = []
		for exp in exps:
			cps_exp = {
						"Done":True, 
						"Success":True, 
						"ConfVars":exp["conf"], 
						"Implementations": exp["Version"],
						"Results":{"TotalCost": exp["cost"], "ExeTime":exp["et"]}
						}	
			if 'monitor' in exp:
				cps_exp["Monitor"] = exp["monitor"]
			if 'Configuration' in exp:
				cps_exp["Configuration"] = exp["Configuration"]
			if 'params' in exp:
				cps_exp["Parameters"] = exp["params"]
			
			cps_exps.append(cps_exp)
		return cps_exps


	def select_valid_configurations(self, exps):
		
		if "%execution_time" in self.slo.Objective.Optimize:
			pareto_exp = filter(lambda x: self.slo.Objective.validate(cost = x["Results"]["TotalCost"]), exps)
			
			#sort pareto frontier based on execution time and select the first
			sorted_exps = sorted(pareto_exp, key=lambda x:x["Results"]["ExeTime"])
			 
		else:
			pareto_exp = filter(lambda x: self.slo.Objective.validate(execution_time = x["Results"]["ExeTime"]), exps)
			#sort pareto frontier based on cost and select the first
			sorted_exps = sorted(pareto_exp, key=lambda x:x["Results"]["TotalCost"])
		
		return sorted_exps

	# def set_models(self, models):
	# 	self.models = models	

		
	# def execute_application(self):
	# 	print "\n\n~~~~~~~~~~~~~~~~~~~~~~ SLO VALIDATION PHASE ~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"
	# 	parameters = self.application.getExecutionParameters(self.slo.ExecutionArguments)
	# 	#predict performance on untested configurations
	# 	info = self._predict_performance(parameters)
					
	# 	best_confs = self._select_best(info)
		
	# 	def minimize_objective(target, best_confs):
	# 		minim = None
	# 		best_version = None
	# 		best_conf = None
	# 		for key in best_confs.keys():
	# 			best = best_confs[key]
	# 			if best == None:
	# 				continue
	# 			if minim == None:
	# 				minim = best[target]
	# 				best_version = key
	# 				best_conf = best
					
	# 			elif minim > best[target]:
	# 					minim = best[target]
	# 					best_version = key
	# 					best_conf = best
	# 		if best_conf == None:
	# 			return None	
	# 		return (best_version, best_conf)
			
	# 	#get (version, configuration) with the bestest objective
	# 	if "%execution_time" in self.slo.Objective.Optimize:
	# 		bestest = minimize_objective("et", best_confs)
	# 	else:
	# 		bestest = minimize_objective("cost", best_confs)
	# 	if bestest == None:
	# 		print "Failed finding a configuration to satisfy objective!"
	# 		raise Exception("No known configuration validating the slo.")
	# 		return
		
	# 	variable_order = bestest[1]["conf"].keys()
	# 	configuration = bestest[1]["conf"]
	# 	print "\n\n======================= RESULTS ==========================="
	# 	print "Best Version :", bestest[0]
	# 	print "Best Configuration :", bestest[1]
	# 	print "===========================================================\n\n"
		
	# 	#Uncomment here to run the final execution according to the slo
	# 	#success, conf, cost, execution_time, gradient, utilisation = Executor.execute_on_configuration(self.application, map(lambda x: int(x), bestest[0].split(".")), variable_order,  configuration, parameters)
	# 	#print "Done"
	# 	return {"Version" : bestest[0], "Configuration" : bestest[1]}
		

	# def _predict_performance(self, parameters):
	# 	info = {}
	# 	for v in self.versions:
	# 		version = ".".join(map(lambda s: str(s), v))
			
	# 		variables, solutions_identified_in_profiling, constraints = Profiler(self.application, version).get_explored_solutions()
	# 		modeller = Extrapolator(self.application, version, variables, solutions_identified_in_profiling, parameters)
			
	# 		solutions_benchmark_input, solutions_current_input = modeller.get_explored_solutions()
			
	# 		info[version] = {
	# 							"InputProfiled" : map(lambda x: { "conf" : x["conf"], "et" : x["et"], "tested"  :True }, solutions_benchmark_input),
	# 							"InputCurrent"  :  map(lambda x: { "conf" : x["conf"], "et" : x["et"], "tested"  :True }, solutions_current_input),
	# 							"Variable_order" : variables
	# 						}
			
	# 		print "\n\n------------------  CONFIGURATIONS  ----------------------\n"
	# 		print "~~~  Benchmarked  ~~~"
	# 		for c in solutions_benchmark_input:
	# 			print c["conf"]
			
	# 		print "~~~  Extrapolated ~~~"
	# 		for c in solutions_current_input:
	# 			print c["conf"]
	# 		print "\n--------------------------------------------------------------\n"
	# 		if len(info[version]["InputProfiled"]) > len(info[version]["InputCurrent"]):
	# 			#get the mapper for the variables
	# 			mapper = VariableMapper(self.application.getResourceVariableMap(v))
			
	# 			#predict the performance of the untested profiled configurations with the current input
	# 			confs_tested = map(lambda x:x["conf"], info[version]["InputCurrent"])
	# 			benchmarked = map(lambda x:x["conf"], info[version]["InputProfiled"])
	# 			not_tested_confs = filter(lambda x:not(x in confs_tested), benchmarked)
				
	# 			#use model to predict the cost and et of the confs not tested with the current input
	# 			model, constraints = self.models[version]
				
	# 			#filter the configs not tested based on constraints to reduce the confs space
	# 			not_tested_confs = filter(lambda z : all(map(lambda zz : True if not(zz in constraints.keys()) else mapper.isvalid(zz, z[zz], constraints[zz]), z.keys())), not_tested_confs)
				
	# 			x = []
	# 			for i in range(len(not_tested_confs)):
	# 				conf = not_tested_confs[i]
	# 				#predict
	# 				index = benchmarked.index(conf) 
	# 				x.append(info[version]["InputProfiled"][index]["et"])
				
	# 			print "x = ",x
	# 			fx = model.predict(x)
				
	# 			predicted_confs = map(lambda i : {"conf" : not_tested_confs[i], "et" : fx[i], "tested" : False}, range(len(fx)) )
				
	# 			info[version]["InputCurrent"].extend(predicted_confs)
					
	# 	return info
				
			
	# def _select_best(self, info):
	# 	#search for the configurations validating the slo constraints
	# 	valid = {}
	# 	all_confs = {}
	# 	pareto = {}
	# 	best_choice = {}
	# 	for version in self.versions:
	# 		v  = ".".join(map(lambda s: str(s), version))
	# 		data = info[v]["InputCurrent"][:]
			
	# 		print data
			
	# 		#update the cost
	# 		for c in data:
	# 			_, conf, _  = self.application.getResourceConfiguration(version, c["conf"])
	# 			print conf
				
	# 			cost = CostModel.calculate(conf)
	# 			#update the dict
	# 			c["cost"] = cost
				
		
	# 		all_confs[v] = data[:]
			
	# 		pareto[v] = self._get_pareto_experiments(data)[:]
	# 		valid[v] = self._select_valid_configurations(pareto[v])
	# 		if len(valid[v]) > 0:
	# 			best_choice[v]  = valid[v][0]
	# 		else:
	# 			best_choice[v] = None
		
	# 	return best_choice
			
			
	# def _select_valid_configurations(self, exps):
		
	# 	if "%execution_time" in self.slo.Objective.Optimize:
	# 		pareto_exp = filter(lambda x: self.slo.Objective.validate(cost = x["Results"]["TotalCost"]), exps)
			
	# 		#sort pareto frontier based on execution time and select the first
	# 		sorted_exps = sorted(pareto_exp, key=lambda x:x["Results"]["TotalCost"])
			 
	# 	else:
	# 		pareto_exp = filter(lambda x: self.slo.Objective.validate(execution_time = x["Results"]["ExeTime"]), exps)
	# 		#sort pareto frontier based on cost and select the first
	# 		sorted_exps = sorted(pareto_exp, key=lambda x:x["Results"]["ExeTime"])
		
	# 	return sorted_exps
			
		
	# # def _get_pareto_experiments(self, exps):
	# def get_pareto_experiments(self, exps):
	# 	"""
	# 		Select experiments with the optimal cost-et trade-off        
	# 	"""
	# 	cost = map(lambda x: x["Results"]["TotalCost"], exps)
	# 	et = map(lambda x: x["Results"]["ExeTime"], exps)

	# 	pcost, pet = MathUtils.pareto_frontier(cost, et)
	# 	print "Pareto cost:", pcost
	# 	print "Pareto et  :", pet
	# 	print "Total Number experiments :", len(exps)
	# 	print "Number Pareto experiments :", len(pcost)
	# 	pex = []

	# 	for exp in exps:
	# 		for i in range(len(pcost)):
	# 			if exp["Results"]["TotalCost"] == pcost[i] and exp["Results"]["ExeTime"] == pet[i]:
	# 				pex.append(exp)
					
	# 	return pex
		
    
