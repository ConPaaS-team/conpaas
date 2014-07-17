#!/usr/bin/env python

import os, sys
import json
from conpaas.core.appmanager.core.application import Application
import urllib

from conpaas.core.appmanager.core.base import Base
   
    
class Objective(Base):   
    class Targets:
        EXECUTION_TIME = "%execution_time"
        BUDGET = "%budget"
    
    def __init__(self, data):
        if not ("Constraints" in data or "Optimization" in data):
            raise Exception("Invalid SLOs.")
        
        self.Constraints = data["Constraints"]
        self.Optimize = data["Optimization"]
            
        
class SLOs(Base):
    '''
    classdocs
    '''
    accepted_params = [ 
            { 
            'name' : 'ManifestUrl', 
            'type' : str,
            'is_array' : False, 
            'is_required' : True
            }, 
            { 
            'name' : 'ExecutionArgs',
            'type' : dict,
            'is_array' : True,
            'is_required' : True
            }, 
            { 
            'name' : 'Objective',
            'type' : Objective,
            'is_array' : False,
            'is_required' : False
            }
            ]
    
    def __init__(self, data={}):
        Base.__init__(self, data)
   


class SLOParser:
	@staticmethod
	def parse(data):	
		if type(data) != dict or (not ("SLO" in data)):
			print "Invalid SLOs : SLO field not found"
			sys.exit(1)
		slos = SLOs(data["SLO"])
		
		#print "---  SLOs  -------------------------"
		#print slos
		#print "------------------------------------"
		
		return slos




class ManifestParser:
    REQUIRED_FIELDS = ["Name", "Modules"]
    @staticmethod
    def parse(data):
        data = ManifestParser.convert(data)        
        return Application(data)


    @staticmethod
    def load(path):
        #print "Parsing manifest..."
        manifest = urllib.urlopen(path)
        #manifest = open(path, "r")
        data = manifest.read()
        data = json.loads(data)
        
        data = ManifestParser.convert(data)
#         print "::::::::::::::::::::::  DATA :::::::::::::::::::::::: "
#         print data
#         print "::::::::::::::::::::::::::::::::::::::::::::::::::::::"    
        
        app = Application(data)
        #print "Done!"
        #print "---  Application  ------------------"
        #print app
        #print "------------------------------------"
         
        return app

    @staticmethod
    def convert(data):
        """
            Used for the conversion from unicode hashmap to a python str hashmap
        """
        #if isinstance(data, dict):
        #    return {ManifestParser.convert(key): ManifestParser.convert(value) for key, value in data.iteritems()}
        #elif isinstance(data, list):
        if isinstance(data, list):
            return [ManifestParser.convert(element) for element in data]
        elif isinstance(data, unicode):
            return data.encode('utf-8')
        else:
            return data

    @staticmethod
    def __validate(data = {}):
        """
            Checking if user provided the Applications, relationships and the SLOs for the execution
        """
        #check for the required parameters describing an application
        
        print data.keys()
        for rf in ManifestParser.REQUIRED_FIELDS:
            if not data.has_key(rf):
                raise Exception("Missing field from manifest : <%s>." % rf)
              
              
"""data = {
        "ManifestURL": "/home/anca/workspace/Client/manifest.json",
        "ExecutionArgs": [
            {
                "Value": 500
            }
        ],
        "Objective": {
            "Constraints": [
                "%budget <= 100"
            ],
            "Optimization": "%execution_time"
        }
    }

sl = SLOs(data)

print sl
"""


#data = ManifestParser(manifest)
#data = ManifestParser().load({})
#print data
#print '\nENDEXE'

