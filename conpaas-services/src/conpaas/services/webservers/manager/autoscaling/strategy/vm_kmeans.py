

"""

VM_Classification clusters the VM instance types based on their performance characteristics.

@author: fernandez
"""

import math, random
from operator import itemgetter
try:
    import simplejson as json
except ImportError:
    import json
import os.path
from os.path import join as pjoin


#DAS4_COMPUTE_UNITS = { 'smallDAS4':1, 'mediumDAS4':3, 'highcpu-mediumDAS4':5, 'largeDAS4':7}
#EC2_COMPUTE_UNITS = { 'smallEC2':1, 'mediumEC2':2, 'c.mediumEC2':5, 'largeEC2':4}

COMPUTE_UNITS_FILE_PATH = 'data/compute_units.json'

class VM:
    def __init__(self, features, reference=None):
        self.features = features
        self.n = len(features)
        self.reference = reference
    def __repr__(self):
        return str(self.features)

class Cluster:
    def __init__(self, vmes):
        if len(vmes) == 0: raise Exception("ILLEGAL: empty cluster")
        self.vmes = vmes
        self.n = vmes[0].n
        for p in vmes:
            if p.n != self.n: raise Exception("ILLEGAL: wrong dimensions")
        self.centroid = self.calculateCentroid()
        
    def __repr__(self):
        return str(self.vmes)
    
    def update(self, vmes):
        old_centroid = self.centroid
        self.vmes = vmes
        self.centroid = self.calculateCentroid()
        return self.getDistance(old_centroid, self.centroid)
    
    def calculateCentroid(self):
        reduce_coord = lambda i:reduce(lambda x,p : x + p.features[i],self.vmes,0.0)    
        centroid_coords = [reduce_coord(i)/len(self.vmes) for i in range(self.n)] 
        return VM(centroid_coords)
    
    def getDistance(self, a, b):
        if a.n != b.n: raise Exception("ILLEGAL: non comparable points")
        ret = reduce(lambda x,y: x + pow((a.features[y]-b.features[y]), 2),range(a.n),0.0)
        return math.sqrt(ret)

class VM_Classification:
    def __init__(self):
        self.vmes = []
        self.vmes_capacities = {}
        
        compute_units_file_path = self.get_compute_units_file_path()

        with open(compute_units_file_path) as fp:
            content = fp.read()

        self.compute_units = json.loads(content)
      
    
    def get_compute_units_file_path(self):
        compute_units_directory = os.path.dirname(os.path.abspath(__file__))
        compute_units_file_path = pjoin(compute_units_directory, COMPUTE_UNITS_FILE_PATH)

        return compute_units_file_path
    
    def compute_units_instance(self, iaas_driver, inst_type):
        return self.compute_units[iaas_driver][inst_type]
    
    def clustering_vmes(self, iaas_driver, capacity_inst_type):
       self.vmes = []
       try:
        
        # clusters small medium and large
        k = 3
        cutoff = 0.5
    
        capacity_inst_type= self.initialize(capacity_inst_type,self.compute_units[iaas_driver])
        for name in capacity_inst_type:
            capacity = capacity_inst_type[name]
            if self.compute_units[iaas_driver][name]:
                self.vmes.append( VM([self.compute_units[iaas_driver][name], capacity]) )
        
        vm_clusters = self.kmeans(self.vmes, k, cutoff)
        return vm_clusters 
       except Exception as e:
            raise Exception("clustering_vmes: Error clustering the vm by performance "+str(e))
                        
    def initialize(self, capacity_inst_type, compute_units):
        capacity_base = 0
        compute_unit_base = None
        compute_unit = 1
        """ 
          We take the first element in the list, normally a small or micro instance type and we calculate
         a classification a priori based on the compute units from each vm type. The capacity is calculated
         for those vm'es types with 0 capacity.
         """
            
        capacity_inst_type_list = sorted(capacity_inst_type.items(), key=itemgetter(1), reverse=True)
        
        
        for (name, capacity) in capacity_inst_type_list:
                if capacity > 0 and compute_unit_base == None:
                    capacity_base = capacity
                    compute_unit_base = name
                elif capacity <= 0:
                    if compute_units[name]:
                        compute_unit = compute_units[name]
                       # capacity_inst_type[name] = (capacity_base * (float(compute_units[compute_unit_base]) / compute_unit)) / (compute_units[compute_unit_base])
                        capacity_inst_type[name] = (capacity_base * (float(compute_units[compute_unit_base]) / compute_unit)) 
        
        self.vmes_capacities = capacity_inst_type
        return capacity_inst_type         
    
    def get_capacities_vmes(self):
        return self.vmes_capacities
                
    def get_iaas_compute_units(self, iaas_driver):
        return self.compute_units[iaas_driver]
        
    def get_num_compute_units(self, iaas_driver, vm_name):
        return self.compute_units[iaas_driver][vm_name]
    
    def kmeans(self, vmes, k, cutoff):
        initial = random.sample(vmes, k)
        clusters = [Cluster([p]) for p in initial]
        while True:
            lists = [ [] for c in clusters]
            for p in vmes:
                smallest_distance = self.getDistance(p,clusters[0].centroid)
                index = 0
                for i in range(len(clusters[1:])):
                    distance = self.getDistance(p, clusters[i+1].centroid)
                    if distance < smallest_distance:
                        smallest_distance = distance
                        index = i+1
                lists[index].append(p)
            biggest_shift = 0.0
            for i in range(len(clusters)):
                shift = clusters[i].update(lists[i])
                biggest_shift = max(biggest_shift, shift)
            if biggest_shift < cutoff: 
                break
        return clusters

    def getDistance(self, a, b):
        if a.n != b.n: raise Exception("ILLEGAL: non comparable points")
        ret = reduce(lambda x,y: x + pow((a.features[y]-b.features[y]), 2),range(a.n),0.0)
        return math.sqrt(ret)

"""
def main():
    capacity_inst_type = {}
    capacity_inst_type = {'m1.medium':0,'m1.small':14,'c1.medium':0,'m1.large':0}
    classification = VM_Classification()
   # capacity_inst_type =  sorted(capacity_inst_type.items(), key=itemgetter(1), reverse=True)
    vm_clusters = classification.clustering_vmes('EC2', capacity_inst_type)
    for i,c in enumerate(vm_clusters): 
           for p in c.vmes:
              print " Cluster: ",i,"\t Point :", p   

if __name__ == "__main__": 
    main()    
    """
