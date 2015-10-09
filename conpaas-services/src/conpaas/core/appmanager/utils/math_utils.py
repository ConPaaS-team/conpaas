#!/usr/bin/env python
import os, sys
from pprint import pprint
import math
import time


class MathUtils:

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
			self.values = map(lambda r: MathUtils.Value(start = 0, stop = r),  values)
			
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
							



	@staticmethod
	def pareto_frontier(Xs, Ys, maxX = False, maxY = False):
		myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
		p_front = [myList[0]]    
		for pair in myList[1:]:
			if maxY: 
				if pair[1] >= p_front[-1][1]:
					p_front.append(pair)
			else:
				if pair[1] <= p_front[-1][1]:
					p_front.append(pair)
		p_frontX = [pair[0] for pair in p_front]
		p_frontY = [pair[1] for pair in p_front]
		return p_frontX, p_frontY
		


	@staticmethod
	def pareto_frontier_data(data):
		myList = sorted(data, key=lambda element: (element[1], element[2]))
		p_front = [myList[0]]    
		for pair in myList[1:]:
			t_pair = [pair[1], pair[2]]
			f_pair = [p_front[-1][1], p_front[-1][2]]
			if t_pair[1] <= f_pair[1]:
				p_front.append(pair)
		return p_front


	@staticmethod
	def generate_combinations(items):
		c = MathUtils.Combinations(items)
		return c.generate()
        

if __name__ =="__main__":
	c = MathUtils.generate_combinations([3,3,3])
	i = 0
	for item in c:
		i = i  + 1
		print item
	print "Done!"
	print "Num =",i     
