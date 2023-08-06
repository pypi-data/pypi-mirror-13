
from .params import rho
from math import pi

class Square:

	def __init__(self, h, b, t):
		self.h = h
		self.b = b
		self.t = t

	def m(self):
		return self.a()*1e-6*rho

	def a(self):
		return self.t**2*(4*(self.h/self.t-4)+3*pi)

	def i(self):
		i_h = self.t*(self.h-4*self.t)**3/12 * 2
		i_b = (self.b-4*self.t)*self.t**3/12 * 2
		i_t = (pi/8-8/(9*pi))*15*self.t**4 * 2
		az_b = (self.b-4*self.t)*self.t * ((self.h-self.t)/2)**2 * 2
		az_t = pi/2*3*self.t**2 * ((self.h/2-2*self.t)+self.t)**2 * 2
		return i_h+i_b+i_t+az_b+az_t
	
	def wel(self):
		return self.i()/(self.h/2)
