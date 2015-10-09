#!/usr/bin/env python
import os, json

class solution(object):
	def __init__(self, param = {"conf" : None, "x": None, "cost": None, "et" : None, "gradient" : None, "monitor" : None, "success" : None}):
		self.conf = param["conf"]
		self.x = param["x"]
		self.cost = param["cost"]
		self.et = param["et"]
		if "gradient" in param.keys():
			self.gradient = param["gradient"]
		else:
			self.gradient = None
		if "monitor" in param.keys():
			self.monitor = param["monitor"]
		else:
			self.monitor = None
		if "success" in param.keys():
			self.success = param["success"]
		else:
			self.success = None

	def get(self):
		return {"x": self.x, "cost" : self.cost, "conf" : self.conf, "et" : self.et, "gradient" : self.gradient, "monitor" : self.monitor, "success" : self.success}
	
class CostModel:

    #cpu_cost = 0.04 #eurocents per Ghz
    c_mem = 0.0186323 #eurocents per GB
    c_cores = 0.0396801 #eurocents per core
    C = 0.0417027

    @staticmethod
    def cost_machine(machine = {}):
        """
            Currently, only the num of cores and the RAM are considered
        """
        cost = 0
        attrs = machine["Attributes"]
        for attr in attrs:
            if attr.upper() == "MEMORY" :
                cost = cost + CostModel.c_mem * attrs[attr] / 1024.0
            elif attr.upper() == "CORES" :
                cost = cost + CostModel.c_cores * attrs[attr]

        cost =  cost + CostModel.C
        return cost

    @staticmethod
    def calculate(configuration):
        total_cost = 0
        for vm in configuration:
			if vm["Type"] == "Machine":
				total_cost = total_cost  + CostModel.cost_machine(vm)
        return total_cost


class State:
	
	class Bundle:
		log = None
		data = {}
		CurrentState = 0
	"""
		0 - Blacbox Profiling with static input
		1 - Blackbox profiling with variable input
		2 - Prediction ready
	"""
	Logs = {}
	Mapping = {0: "StaticInputProfiling", 1 : "VariableInputProfiling", 2: "Model"}
	
	@staticmethod
	def load(version, logfile):
		State.Logs[version] = State.Bundle()
		State.Logs[version].log = logfile
		try:	
			f = open(State.Logs[version].log, "r")
		except:
			d = State.Logs[version].log.split("/")
			dir_path = "/".join(d[:-1])
			if not os.path.exists(dir_path):
				os.makedirs(dir_path)
			
			State.Logs[version].CurrentState = 0
			State.save(version)
			return
		text = f.read()
		State.Logs[version].data = json.loads(text)
		f.close()
		
		if State.Logs[version].data == {}:
			return None
			
		State.Logs[version].CurrentState = len(State.Logs[version].data.keys()) - 2
		
		return State.Logs[version].data[State.Mapping[State.Logs[version].CurrentState]]
	
	@staticmethod
	def save(version):
		f = open(State.Logs[version].log, "w")
		json.dump(State.Logs[version].data, f)		
		f.close()
		
	@staticmethod	
	def checkpoint(version, state, info = []):
		State.Logs[version].CurrentState = state
		State.Logs[version].data["CurrentState"] = State.Mapping[State.Logs[version].CurrentState]
		State.Logs[version].data.update({State.Mapping[State.Logs[version].CurrentState]: info})
		State.save(version)
		
	@staticmethod	
	def get_data(version, state):
		if State.Logs[version].data != {}:
			if state in State.Mapping.keys():
				value = State.Mapping[state]
				
				if not (value in State.Logs[version].data.keys()):
					State.Logs[version].data[value] = []
				else:
					return State.Logs[version].data[State.Mapping[state]]
		return []
		
	@staticmethod	
	def get_current_state(version):
		return State.Logs[version].CurrentState
	
	@staticmethod
	def change_state(version):
		State.Logs[version].CurrentState = State.Logs[version].CurrentState + 1
	@staticmethod
	def set_state(version, state_id):
		State.Logs[version].CurrentState = state_id
	
	
#### TEST PURPOSE ####	
if __name__ == "__main__":
	
	cp = State("test.pf")
	
######################
