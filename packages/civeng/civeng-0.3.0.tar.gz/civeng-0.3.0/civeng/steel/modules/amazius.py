
from ..cat263 import Components, MDRd, NkRd, Profile, Slenderness
from ..params import I, R
from ...results import Results


class Amazius(Profile, Results, Slenderness):
	code = 'SIA 263:13'
	selection = []

	def __init__(self, entries):
		Profile.__init__(self, entries)

		self.selection = ['csc']
		self.cat = Components(entries)
		self.cross_section_class = '1 + 2'
		self.ned = entries['ned']*1e3
		self.ved = entries['ved']*1e3
		self.myed = entries['myed']*1e6
		self.mzed = entries['mzed']*1e6
		self.shape = entries['shape']
		self.entries = entries

		self.csc_y = self.csc()
		print('csc_y: {}'.format(self.csc()))

	def add_sel(self, sel):
		if sel not in self.selection:
			self.selection.append(sel)
		

	def compute(self):

		if self.csc_y == 1 or self.csc_y == 2 or self.csc_y == 3:
			self.cat.nrd(self.ned)
			self.add_sel('nrd')

		if self.csc_y == 1 or self.csc_y ==2:
			self.cat.myrd(self.myed)
			self.add_sel('myrd')
		elif self.csc_y == 3:
			pass
			
		return  self.get_results()

	def class_1(self):
		self.cat.nrd(self.ned)
		self.cat.myrd(self.myed)
		self.cat.mzrd(self.mzed)
		self.cat.vrd(self.ved)
		self.cat.f42(1)
		self.cat.av__()
		
		if self.ved > 0 and self.shape in I+R:
			self.cat.mvrd(self.myed)
			self.add_sel('mvrd')

		if self.ned > 0 and self.myed > 0 and self.mzed > 0:
			self.cat.f44(1)
			self.add_sel('f44')

		if self.ned > 0 and self.myed > 0:
			self.cat.mynrd(self.myed)
			self.add_sel('mynrd')
			
		if self.ned > 0 and self.mzed >0:
			self.cat.mznrd()
			self.add_sel('mznrd')

#		if self.ved > 0:
#			self.cat.mvrd(self.ved)
#			self.add_sel('mvrd')
#			self.cat.f42()
#			self.add_sel('f42')
#						
#		if self.ned > 0 and self.myed > 0:
#			self.cat.f49(self.ned, self.mzed, 'y')
#			self.add_sel('f49_y')
#		
#		if self.ned > 0 and self.mzed > 0:
#			self.cat.f49(self.ned, self.mzed, 'z')
#			self.add_sel('f49_z')
#
#		if self.ned > 0 and self.myed > 0 and self.mzed > 0:
#			self.cat.f44(self.ned, self.myed, self.mzed)
#			self.add_sel('f44')
#
#			self.cat.f48(self.ned, self.myed, self.mzed)
#			self.add_sel('f48')
#
#			self.cat.f50(self.ned, self.myed, self.mzed)
#			self.add_sel('f50')
#		
#		if self.ned > 0:
#			self.cat.mynrd(self.ned)
#			self.add_sel('mynrd')
#
#			self.cat.mznrd(self.ned)
#			self.add_sel('mznrd')

	def vrd(self):
		pass



 
