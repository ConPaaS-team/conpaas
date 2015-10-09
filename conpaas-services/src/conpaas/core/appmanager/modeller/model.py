#!/usr/bin/env python 

import math, sys
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from scipy import stats
import numpy as np
def poly1(x, a, b):
		return a * x + b
def poly2(x, a, b, c):
		return a *x**2 + b*x +c
def poly3(x, a, b, c, d):
		return a *x**3 + b*x**2 +c*x +d
		
def func_exp(x, a, b, c):
	return a * np.exp(b * x) + c

def func_log(x, a, b, c):
	return a * np.log(b * x) + c
	
def func_power(x, a, b, c):
	return a * b**x + c
	
class FunctModel:
	#functions to fit
	FORM = [poly1, poly2, poly3, func_log, func_exp]
	
	def __init__(self):
		self.F = None
		self.Fcode = None
		self.R_square = None
	
	def restore(self, params):
		#params = {"Fcode"  :0, "R_square" : 1.0, "F" : [  2.00000000e+00,  -2.18051290e-12]}
		if params in  [None, {}]:
			return
		    
		self.Fcode = params ["Fcode"]
		self.R_square = params["R_square"]
		
		popt = params["F"]
		
		self.F = (self.FORM[self.Fcode], popt)
		
			
	def save_state(self):
		if self.F == None:
			return None
		params = {}
		params["F"] = list(self.F[1])
		params ["Fcode"] = self.Fcode
		params["R_square"] = self.R_square
		
		return params
		
		
	def _fit(self, x, y, ftype = 0):
		
		f = None
		tries = 5
		while True:
			if tries <= 0:
				break
			func = self.FORM[ftype]
			try:
				#print "Try func", func, ftype
				print x, y
				popt, pcov = curve_fit(func, np.array(x), np.array(y))
				print popt
				f = (func, popt)
			except:
				#print "Failed fitting ", func
				tries -= 1
				f = None
				continue
			break
		#print "Model found : ",f
		return f
	
	"""
		x, fx - training set
		v, fv - validation set
	"""
	def fit(self, x, fx):
		best_model = None
		fcode = None
		r_square = None
		i = 0
		skip = 0
		while (i < len(self.FORM)):
			print "Fitting ", i
			model = self._fit(x, fx, ftype = i)
			if model == None:
				#skip - fit failed for this form
				i = i + 1
				continue
			#compute R^2 for the training samples
			y_true = fx
			y_pred = map(lambda xi : model[0](xi, *model[1]), x)
			
			#print "Predicted :",y_pred
			if np.isnan(y_pred).any() or None in y_pred:
				print "very bad fit. "
				skip = skip + 1
				if skip == 6:
					skip = 0
					i = i + 1
				continue
			skip = 0
			try:			
				r_2 = r2_score(y_true, y_pred)
			except:
				r_2 = None
			#keep the one that fits training data the best
			if r_2 != None and (r_square == None or r_2 > r_square):
				r_square = r_2
				best_model = model
				fcode = i
			#next fitting function	
			i = i + 1
		
		self.R_square = r_square
		self.F = best_model
		self.Fcode = fcode
		return self.R_square


	def validate(self, validation_set):
		sq_error = 0
		print "Len valid :", len(validation_set)
		#validate model and get MSE
		
		hh = []
		for et1, real_e in validation_set:
			hypotetic = self.F[0](et1, *self.F[1])
			
			#compute the percentage from the real result which represents the loss
			sq_error += (100.0 * np.sqrt((real_e - hypotetic) ** 2)) / real_e
			hh.append(hypotetic)
		
		print map(lambda x:x[1], validation_set)
		print hh
		sq_error = sq_error / len(validation_set)
		
		return sq_error

	def predict(self, x):
		y = map(lambda et:self.F[0](et, *self.F[1]), x)
		return y

	def score(self, x, y):
		y_true = y
		y_pred = map(lambda xi : self.F[0](xi, *self.F[1]), x)
		return r2_score(y_true, y_pred)

#### TEST PURPOSE ####  

if __name__ == "__main__":
	m = FunctModel()
	#print m.fit([1,2,3,4,5,6], [2,4,6,8,10,12])
	#print m.Fcode
	#print m.F
	
	s = {"Fcode"  :0, "R_square" : 1.0, "F" : [  2.00000000e+00,  2.18051290e-12]}
	
	m.restore(s)
	
	print m.predict([8])
#################
