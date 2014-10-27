#!/usr/bin/env python

import os, sys
from pprint import pprint
import math
import time
        
class Value:
    def __init__(self, start = 0, stop = 0, items = None, step = 1):
        self.start = start
        self.stop = stop
        self.step = step
        self.value = None
        
    def next(self):
        if self.value == None:
            self.value = self.start
        elif self.value + self.step > self.stop:
            self.value = None
        else:
            self.value = self.value + self.step
        return self.value

    
class Combinations:
    def __init__(self, values = []):
        self.attr_num = len(values)
        self.values = map(lambda r: Value(start = 0, stop = r),  values)
        
    def generate(self, stepsize = 1):
        #for item in self.__explore(self.values[:]):
        #    print item
        
        return self.__explore(self.values[:])
        
    def __explore(self, vector):
        if len(vector) == 1:
            while vector[0].next() != None:
                yield [vector[0].value]
            return
        elif len(vector) < 1:
            yield []
            return
        item = vector[0]
        while item.next() != None:
            if item.next != None:
                for items in self.__explore(vector[1:]):
                    yield [item.value] + items
                        
        
# c = Combinations([3,3,3])
# 
# 
# i = 0
# for item in c.generate(stepsize = 3):
#     i = i  + 1
#     print item
#     
#         
# print "Done!"
# print "Num =",i     
