#!/usr/bin/env local
from slo import User,Objectives
from conpaas.core.appmanager.utils.math import MathUtils
# from conpaas.core.appmanager.provisioner.resources import ReservationManager
from pprint import pprint

class SLOEnforcer:
    
	def __init__(self, application):
		self.application = application

		"""
			Load mathematical model and check configurations
		"""
		#print "Load Performance Model"
		
	def get_pareto_experiments(self, exps):
		"""
			Select experiments with the optimal cost-et trade-off        
		"""
		if len(exps) == 0:
			return []
			
		cost = map(lambda x: x["Results"]["TotalCost"], exps)
		et = map(lambda x: x["Results"]["ExeTime"], exps)

		pcost, pet = MathUtils.pareto_frontier(cost, et)
		print "Pareto cost:", pcost
		print "Pareto et  :", pet
		print "Number experiments :", len(pcost)
		pex = []

		for exp in exps:
			for i in range(len(pcost)):
				if exp["Results"]["TotalCost"] == pcost[i] and exp["Results"]["ExeTime"] == pet[i]:
					pex.append(exp)
					
					
		#print "~ Pareto Experiments ~"
		#print pex,"\n\n"
		
		"""import matplotlib.pyplot as plt
		plt.figure(1) 
		ax = plt.subplot(111)
		ax.plot(cost, et, 'bo')
		ax.plot(pcost, pet, 'ro')
		ax.set_ylabel('ExeTime')
		ax.set_xlabel('Cost')
		plt.show()
		"""
		return pex
		
	def slo_based_execution(self, slo, perf_model):
		results = None
		conf = None
		#the app has several implementations. We assume it has only 1 module.
		n = self.application.Modules[0].Implementations
		
		experiments = []
		for i in range(len(perf_model)):
			for exp in perf_model[i]:
				exp["ImplIndex"] = i
			experiments.extend(perf_model[i])
		
		
		while conf is None:
			print len(experiments)
			pareto_exp = self.get_pareto_experiments(experiments)
			conf = self.select_configuration(slo, pareto_exp)
			
			if conf is None:
				break
			#run the app
			print "Selecting implementation %s for execution." % self.application.Modules[0].Implementations[conf["ImplIndex"]].ImplementationName
			try:
				variables = {}
				variables.update(conf["Configuration"])
				variables.update(conf["Arguments"])
				variables["ImplIndex"] = conf["ImplIndex"]
				
				# results = self.execute_application(variables)
				break
			except:
				import traceback
				traceback.print_exc()
				print "Execution on", conf["Configuration"], " failed. Probably resource reservation was not possible. Try another one."
				experiments = filter(lambda c : c != conf, experiments)
				print len(experiments)
				conf = None
				if experiments == []:
					break
			#break
		
		if conf == None:
			print "Failed satisfying SLOs with the provided PM."
		else:
			print "Application executed successfully with the following results :", results
		
		
		
	def select_configuration(self, slo, model):
		if "%execution_time" in User.Objectives.Optimize:
		# if "%execution_time" in slo.Optimize:
			pareto_exp = filter(lambda x: User.validate(cost = x['Results']["TotalCost"]), model)
			#sort pareto frontier based on execution time and select the first
			sorted_exps = sorted(pareto_exp, key=lambda x:x['Results']["ExeTime"])
			 
		else:
			pareto_exp = filter(lambda x: User.validate( execution_time = x['Results']["ExeTime"]), model)
			#sort pareto frontier based on cost and select the first
			sorted_exps = sorted(pareto_exp, key=lambda x:x['Results']["TotalCost"])
		
			
		#pprint(sorted_exps)
		try:
			conf = sorted_exps[0]
		except:
			#raise Exception("No slo-compliant configuratin found")
			return None
		return conf
			

	# def execute_application(self, configuration):
	# 	variables = configuration
	# 	implementation = self.application.Modules[0].Implementations[configuration["ImplIndex"]]
	# 	del configuration["ImplIndex"]
	# 	configuration, roles = implementation.Resources.get_configuration(configuration)
	# 	""""
	# 		Reserving resources
	# 	"""
	# 	reservation = ReservationManager.acquire_resources(configuration)
	# 	if reservation == None:
	# 		print "Experiment failed."
	# 		return 0 
	# 	"""
	# 		Add roles to the acquired machines
	# 	"""
	# 	for i in range(len(reservation["Resources"])):
	# 		reservation["Resources"][i]["Role"] = roles[i]
		
	# 	print "\n ~ Acquired Resources ~"
	# 	print reservation["Resources"]
		
	# 	""""
	# 		Execute Implementation
	# 	"""
	# 	#get manifest special variables, environment variables
	# 	variables.update(implementation.Resources.get_special_variables(reservation["Resources"]))
		
	# 	reservation["Variables"] = variables
	# 	"Deploy implementation"
	# 	implementation.deploy(reservation)
		
	# 	"Execute implementation"
	# 	execution_time, utilization_data = implementation.execute(reservation)
	# 	total_cost = execution_time * reservation["Cost"]
		
		
	# 	"""
	# 		Releasing resources
	# 	"""
	# 	reservation = ReservationManager.release_resources(reservation["ResID"])
		
	# 	"Save output and update experiments list"
	# 	data = {}
	# 	data["Results"] = {"ExeTime" : execution_time, "TotalCost" : total_cost} 
	# 	data["RuntimeData"] = utilization_data
		
	# 	print "Done experiment."
	# 	return data










        
