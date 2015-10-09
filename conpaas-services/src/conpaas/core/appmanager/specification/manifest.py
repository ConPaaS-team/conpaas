#!/usr/bin/env python
from conpaas.core.appmanager.application.structure import Application
import urllib, os, sys, json, ast


   
class ManifestParser:
    
    REQUIRED_FIELDS = ["Name", "Modules"]
    @staticmethod
    def load(path):
		if type(path) == str:
			print "Parsing manifest :", path
			if path.startswith("http"):
				manifest = urllib.urlopen(path)
			else:
				manifest = open(path, "r")
			data = manifest.read()
			data = ast.literal_eval(data)
			#data = json.loads(data)
		application = Application(data)
		 
		return application


    @staticmethod
    def parse(manifest):
        data = ast.literal_eval(manifest)
        #data = json.loads(data)
        application = Application(data)
        return application
   
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
              
              



#data = ManifestParser(manifest)
#data = ManifestParser().load({})
#print data
#print '\nENDEXE'

