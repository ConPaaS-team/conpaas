# #!/usr/bin/env python
# import time, copy
# import subprocess
# import os, sys, traceback
# from pprint import pprint
# import httplib2
# import simplejson

# import thread
# # from config import config_parser

# class SingletonParent(object):
#     """
#     Implement Pattern: SINGLETON
#     """

#     # lock object
#     __lockObj = thread.allocate_lock()

#     # the unique instance
#     __instance = None

#     def __new__(cls, *args, **kargs):
#         cls._instance = object.__new__(cls)
#         return cls._instance

#     def __init__(self):
#         pass

#     @classmethod
#     def getInstance(cls, *args, **kargs):
#         """
#         Static method to have a reference to **THE UNIQUE** instance
#         """
#         # Critical section start
#         cls.__lockObj.acquire()
#         try:
#             if cls.__instance is None:
#                 # (Some exception may be thrown...)
#                 # Initialize **the unique** instance
#                 cls.__instance = object.__new__(cls, *args, **kargs)

#                 """
#                     DO YOUR STUFF HERE
#                 """

#         finally:
#             # Exit from critical section whatever happens
#             cls.__lockObj.release()
#         # Critical section end

#         return cls.__instance
        
        
        
    
# class CrossResourceSchedulerConnection(SingletonParent):
#     # def __init__(self, url = config_parser.get("main", "crs_url")): #for development use the 2nd CRS instance, the first is running profiling
#     def __init__(self, url = "http://10.1.0.2:56789"): #for development use the 2nd CRS instance, the first is running profiling
#         SingletonParent.__init__(self)
#         self.conn = httplib2.Http()
#         self.url = url 
        
#     def __make_request(self, url, method = 'POST', content = {}):
#         #print "Conn ID =", id(self)
#         #print "\nRequest :", url, content
#         data, response = self.conn.request(self.url + url , method,
#                           simplejson.dumps(content),
#                           headers={'Content-Type': 'application/json'})
#         try:
#             print "DEBUG: response: %s" % response
#             response = simplejson.loads(response)
#             if  'result' not in response:
#             	raise Exception(response['error']['message'])
#             else:
#             	response = response['result']
            	
#         except:
#             print traceback.print_exc()
#             sys.exit()
#             # return response
        
#         #print "Response :", response
#         return response
    
    
#     def createReservation(self, configuration, monitor):
#         data = {}
#         data['Allocation'] = configuration
#         if len(monitor) > 0:
#         	data['Monitor'] = monitor

#         print "DEBUG: reservation REQ: %s" % data
#         response = self.__make_request("/createReservation", content=data)
#         return response["ReservationID"][0]

#     def releaseReservation(self, reservationID):
#         response = self.__make_request("/releaseReservation",method="DELETE", content={"ReservationID" : [reservationID]})
#         if response is {}:
#             return True
    
#     def checkReservation(self, reservationID):
#         response = self.__make_request("/checkReservation", content={"ReservationID" : [reservationID]})
#         return response
    
#     def getMetrics(self, reservationID, address, entry=1):
#     	response = self.__make_request("/getMetrics", content={"ReservationID" : reservationID, "Address":address, "Entry":entry})
#         return response
        
#     #for development only
#     def reset(self):
#         response = self.__make_request("/reset")
#         return response



# class ReservationManager:
    
# 	@staticmethod
# 	def reserve(configuration, monitor):
# 		"Reserve resource configuration."
# 		conf_copy  = copy.deepcopy(configuration)
# 		# for dev in conf_copy:
# 		# 	if dev['Type'] == 'Machine':
# 		# 		dev['Attributes']['Image'] = config_parser.get("main", "agent_image")

# 		reservationID = ReservationManager.__create_reservation(conf_copy, monitor)  
# 		addresses = ReservationManager.__check_reservation(reservationID)
		
# 		# print "Sleep 3s while machines are booting."
# 		# time.sleep(3)	
# 		return {"ReservationID" : reservationID, "Addresses" : addresses}

# 	@staticmethod
# 	def release(reservationID):
# 		"""
# 			Release the reservation
# 		"""
# 		print "Releasing resources..."
# 		provisioner = CrossResourceSchedulerConnection()
# 		provisioner.releaseReservation(reservationID)


# 	@staticmethod
# 	def reset():
# 		provisioner = CrossResourceSchedulerConnection()
# 		provisioner.reset()

# 	@staticmethod
# 	def monitor(reservationID, address):
# 		provisioner = CrossResourceSchedulerConnection()
# 		result = provisioner.getMetrics(reservationID, address)
# 		if result == None:
# 			raise Exception()
# 		return result['Metrics']	


# 	@staticmethod
# 	def __create_reservation(configuration, monitor):
# 		provisioner = CrossResourceSchedulerConnection()
# 		result = provisioner.createReservation(configuration, monitor)
# 		if result == None:
# 			raise Exception()
# 		return result


# 	@staticmethod
# 	def __check_reservation(reservationID):
		
# 		provisioner = CrossResourceSchedulerConnection()
# 		ready = False
# 		while not ready:	
# 			result = provisioner.checkReservation(reservationID)
# 			ready = result["Instances"][reservationID]["Ready"]
			
# 		#{
# 		#	"Instances": {
# 		#		"resID1": {
# 		#			"Ready": "True",
# 		#			"Address": [
# 		#				"192.168.13.172",
# 		#				"192.168.13.173",
# 		#				"pbrpc://192.168.13.172/volume_name1" 
# 		#			]
# 		#		}
# 		#	}
# 		#}        
# 		return result["Instances"][reservationID]["Address"]    

			


# ##### TEST PURPOSE #####

# if __name__ == "__main__":
	
# 	ReservationManager.reset()
# 	sys.exit()
# 	res = ReservationManager.reserve(
# 	   [
# 		  {"Group":"id0",
# 			 "Type":"Machine",
# 			 "NumInstances":3,
# 			 "Attributes":{
# 				"Cores":8,
# 				"Memory":4096,
# 			 }}])
# 	print res
# 	ReservationManager.release(res["ReservationID"])
# #######################
