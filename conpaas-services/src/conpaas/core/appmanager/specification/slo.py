#!/usr/bin/env python
from conpaas.core.appmanager.application.base import Base
import urllib, os, sys, json, ast

class Objective:       
    
	def __init__(self, data):
		if not ("Constraints" in data or "Optimize" in data):
			raise Exception("Invalid SLOs.")
		
		self.Constraints = map(lambda x: str(x), data["Constraints"])
		self.Optimize = data["Optimize"]
			
	def validate(self, cost = 0, execution_time = 0):
		
		keywords = {
						"%cost" : cost,
						"%execution_time" : execution_time
					}
		#replace cost and evaluate constraint
		for constr in self.Constraints:
			constraint = constr
			for kw in keywords.keys():
				constraint = constraint.replace(kw, str(keywords[kw]))
			
			if not eval(constraint):
				return False
		return True
    
class SLO(Base):
	'''
	classdocs
	'''
	accepted_params = [ 
			{ 
			'name' : 'ManifestURL', 
			'type' : str,
			'is_array' : False, 
			'is_required' : False
			},
			{ 
			'name' : 'ExecutionArguments',
			'is_array' : True,
			'is_required' : False
			}, 
			{ 
			'name' : 'Objective',
			'type' : Objective,
			'is_array' : False,
			'is_required' : False
			}
			]
			
	def __init__(self, data={}):
		print data.keys()
		Base.__init__(self, data)


class SLOParser:
	@staticmethod
	def parse(path):
		if type(path) == str:
			print "Parsing SLO file :", path
			if path.startswith("http"):
				slo = urllib.urlopen(path)
			else:
				slo = open(path, "r")
			data = slo.read()
			
			print data
			data = ast.literal_eval(data)
		else:
			data = path
		if type(data) != dict or (not ("SLO" in data)):
			print "Invalid SLOs : SLO field not found"
			sys.exit(1)
		slos = SLO(data["SLO"])

		return slos


"""data = {
        "ManifestURL": "/home/anca/workspace/Client/manifest.json",
        "ExecutionArguments": [ 500 ],
        "Objective": {
            "Constraints": [
                "%budget <= 100"
            ],
            "Optimize": "%execution_time"
        }
    }

sl = SLOs(data)

print sl
"""

