#!/usr/bin/env python
import httplib2, json, sys, os
import threading, subprocess, time

class Monitor:
    
    UNDERUSED = 60.0
    OVERUSED  = 90.0 
    KEYWORD = "_UTILIZATION"
    
    def __init__(self, manager, configuration, var_fields):
        self.retriever = None
        self.manager = manager
        self.data = []
        
        self.fields_to_monitor = var_fields
        self.feedback = False
        data = {}
        for resource in configuration:
            attrs = resource["Attributes"].keys()
            if resource["Type"] in data.keys():
                keys_already_set = [a.replace(self.KEYWORD, "") for a in data[resource["Type"]].keys()]
                for attr in attrs:
                    if not(attr in var_fields):
                        continue
                    if not (attr.upper() in keys_already_set):
                            data[resource["Type"]][attr.upper() + self.KEYWORD] =  { "PollTimeMultiplier": 1 }
            else:
                data[resource["Type"]] = {}
                for attr in resource["Attributes"]:
                    if not(attr in var_fields):
                        continue
                    data[resource["Type"]][attr.upper() + self.  KEYWORD] =  { "PollTimeMultiplier": 1 }

        data["PollTime"] = 2
        self.target = data
    
    # def calculateCpuUsage(self, proc_data, tot_data):
    #     result = []
    #     for i in range(len(proc_data)-1):
    #     # for i in range(len(proc_data)):
    #         # print "DEBUG: %s %s %s" % (tot_data[i+1], tot_data[i], (tot_data[i+1] - tot_data[i]))
    #         util = 100 * ((proc_data[i+1] - proc_data[i]) / (tot_data[i+1] - tot_data[i]))
    #         # util = 100 * (proc_data[i]) / (tot_data[i])
    #         result.append(round(util, 2))
    #     return result

    # def calculateMemoryUsage(self, proc_data, tot_data):
    #     result = []
    #     for i in range(len(proc_data)):
    #         # print "DEBUG: %s %s %s" % (tot_data[i+1], tot_data[i], (tot_data[i+1] - tot_data[i]))
    #         util = 100 * (proc_data[i]) / (tot_data[i])
    #         result.append(round(util, 2))
    #     return result
        

    def setup(self, resources, reservation_id):
        self.resources = resources
        self.reservationID = reservation_id


    
    def get_monitoing(self):
        mdata = self.manager.get_monitoring(self, self.reservationID)
        feedback = {}
        for key in mdata:
            feedback[key] = {}
            for skey in mdata[key]:
                field = filter(lambda v: v.upper() + self.KEYWORD == skey, self.fields_to_monitor)[0]
                if len(mdata[key][skey]) == 0:
                    vals = []
                else:
                    vals = map(lambda v :v.split(",")[-1], mdata[key][skey].split("\n"))
                feedback[key][field] = []
                for v in vals:
                    try:
                        value = float(v)
                        feedback[key][field].append(value)
                    except:
                        continue
                # print "feedback ", key, field, " :", feedback[key][field][:10]

        recommendation = self.get_recommendation(feedback)
        result = {"resources" : self.resources, "utilisation" : feedback}
        return recommendation, result

    def get_recommendation(self, result):
        def __smaller(vals, v):
            i = 0
            while i < len(vals) and vals[i] <= v:
                i += 1
            return i

        recommendation = {}
        #get if resource needs to be increased or not
        for addr in result:
            recommendation[addr] = {}
            for attr in result[addr]:
                vals = result[addr][attr][:]
                vals = sorted(vals)
                if vals == []:
                    recommendation[addr][attr] = 0
                elif __smaller(vals, self.UNDERUSED) * 100.0 / len(vals) > 50:
                    recommendation[addr][attr] = -1
                elif (len(vals) - __smaller(vals, self.OVERUSED)) * 100.0 / len(vals) > 30:
                    recommendation[addr][attr] = +1
                else:
                    recommendation[addr][attr] = 0

        print "\ncrs_direction :", recommendation
        return recommendation

    def get_bottleneck(self, data):
        """
        data = {
            "utilisation":
            {
                        "10.158.4.49": {"Cores": [0.5, 0.6, 0.6, 0.7], "Swap": [0.0, 0.08, 0.08, 0.08, 0.08], "Memory": [4.4, 94.43, 94.46, 94.54, 94.58, 94.61, 94.64, 94.69]},
                        "10.158.4.50": {"Cores": [14.1, 14.0, 14.0, 14.0], "Swap": [0.0, 0.0, 0.0, 0.0, 0.0], "Memory": [4.37, 22.15, 57.36, 57.37, 57.36, 57.37, 57.43]}
            },
            "resources":
            [
                        {"Attributes": {"Cores": 7, "Memory": 2048}, "Type": "Machine", "GroupID": "id0", "Role": "MASTER", "Address": "10.158.4.49"},
                        {"Attributes": {"Cores": 1, "Memory": 2048}, "Type": "Machine", "GroupID": "id1", "Role": "SLAVE", "Address": "10.158.4.50"}
            ]
        }
        """
        botneck = {}
        #get if resource needs to be increased or not
        for addr in data["utilisation"]:
            attrs = []
            for r in data["resources"]:
                if r["Address"] == addr:
                    attrs = r["Attributes"].keys()
                    attrs = filter(lambda x:x in self.fields_to_monitor, attrs)
                    break
            #res_attrs = filter(lambda x: x["Address"] == addr, data["resources"])[0]["Attributes"].keys()
            res_attrs = attrs
            botneck[addr] = {}
            for attr in res_attrs:
               
                vals = data["utilisation"][addr][attr][:]

                i = len(vals) - 1
                counter = 0
                while i > 0 and vals[i] > 90:
                    counter += 1
                    i -= 1
                #if the last 10 utilisation values > 90% ====> it may be a bottleneck causing failure
                if counter > 10 or (len(vals) < 10 and counter > 3):
                    botneck[addr][attr] = True
                else:
                    botneck[addr][attr] = False
        return botneck
    
            
    
#####   TEST PURPOSE  #######
if __name__ == "__main__":
    print "Testing Monitor"
    # conf = [
    #           {'Attributes': {'Cores': 7, 'Memory': 8192}, 'Type': 'Machine', 'Group': 'id0', 'Role': 'MASTER', 'Address': '10.158.0.79'}, 
    #           {'Attributes': {'Cores': 7, 'Memory': 6144}, 'Type': 'Machine', 'Group': 'id1', 'Role': 'SLAVE', 'Address': '10.158.0.80'}
    #       ]
    # mon = Monitor(conf)
    
    # usage = {
    #   "utilisation": 
    #   {
    #               "10.158.4.49": {"Cores": [0.5, 0.6, 0.6, 0.7], "Swap": [0.0, 0.08, 0.08, 0.08, 0.08], "Memory": [4.4, 94.43, 94.46, 94.54, 94.58, 94.61, 94.64, 94.69]},
    #               "10.158.4.50": {"Cores": [14.1, 14.0, 14.0, 14.0], "Swap": [0.0, 0.0, 0.0, 0.0, 0.0], "Memory": [4.37, 22.15, 57.36, 57.37, 57.36, 57.37, 57.43]}
    #   }, 
    #   "resources": 
    #   [
    #               {"Attributes": {"Cores": 7, "Memory": 2048}, "Type": "Machine", "Group": "id0", "Role": "MASTER", "Address": "10.158.4.49"}, 
    #               {"Attributes": {"Cores": 1, "Memory": 2048}, "Type": "Machine", "Group": "id1", "Role": "SLAVE", "Address": "10.158.4.50"}
    #   ]
    # }
    
    # print mon.get_bottleneck(usage)
    
    # sys.exit()
    # mon.run()
    
    # time.sleep(10)
    
    # data = mon.stop()
    
    # print "\n Recommendation :", mon.process_usage(data)
        
############################


