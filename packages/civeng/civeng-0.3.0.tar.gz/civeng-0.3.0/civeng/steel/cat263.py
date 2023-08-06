
from .params import steel_grade_dict
from .szs import Database
from .params import gamma_m1, gamma_m2, e, g
from .params import I, C, T, L, F, ROR, R
from ..results import Results
from math import pi, sqrt
import copy

code = 'SIA 262:13'




class Profile():

	def __init__(self, entries):
		self.shape = entries['shape']
		size = entries['size']
		self.steel_grade = entries['steel_grade']

		self.gamma_m1 = entries['gamma_m1']
		self.gamma_m2 = entries['gamma_m2']

		db = Database()
		data = db.select_row_dict(self.shape, size)

		if self.shape in I+C:
			self.a = float(data['a'])
			self.av = float(data['av'])
			self.aw = float(data['aw'])
			self.iy = float(data['iy'])*1e6
			self.wely = float(data['wely'])*1e3
			self.wy = float(data['wy'])*1e3
			self.wply = float(data['wply'])*1e3
			self.iy_ = float(data['iy_'])
			self.iz = float(data['iz'])*1e6
			self.welz = float(data['welz'])*1e3
			self.wplz = float(data['wplz'])*1e3
			self.iz_ = float(data['iz_'])
			self.k = float(data['k'])*1e6
			self.h = float(data['h'])
			self.b = float(data['b'])
			self.tw = float(data['tw'])
			self.tf = float(data['tf'])
			if self.shape == 'INP':
				self.r = self.tw
			elif self.shape == 'UNP':
				self.r = self.tf
			else:
				self.r = float(data['r'])
			self.h1 = float(data['h1'])
			self.k_ = float(data['k_'])
			self.a_ = float(data['a_'])
			if self.shape in ['INP', 'UNP']:
				self.h2 = self.h1
			else:
				self.h2 = float(data['h2'])

			t = max(self.tw, self.tf)

		if self.shape in L:
			self.a = float(data['a'])
			self.iy = float(data['iy'])*1e6
			self.wely = float(data['wely'])*1e3
			self.iy_ = float(data['iy_'])
			self.a_ = float(data['a_'])
			self.t = float(data['t'])
			self.a1 = float(data['a1'])
			if self.shape == 'LNP2':
				self.iz = float(data['iz'])*1e6
				self.welz = float(data['iz'])*1e3
				self.iz_ = float(data['iz_'])

			t = self.t

		if self.shape in F:
			self.a = float(data['a'])
			self.i = float(data['i'])
			self.wel = float(data['wel'])
			self.wpl = float(data['wel'])
			self.i_ = float(data['i_'])
			if self.shape == 'RND':
				self.d = float(data['d'])
				t = self.d
			elif self.shape == 'VKT':
				self.b = float(data['b'])
				t = self.d

		if self.shape == 'ROR':
			self.a = float(data['a'])
			self.i = float(data['i'])*1e6
			self.wel = float(data['wel'])*1e3
			self.wpl = float(data['wpl'])*1e3
			self.i_ = float(data['i_'])
			self.d = float(data['d'])
			self.d_ = float(data['d_'])
			self.t = float(data['t'])

			t = self.t

		if t <= 40:
			self.fy, self.tau_y, self.fu = steel_grade_dict[self.steel_grade][0]
		elif t <= 100:
			self.fy, self.tau_y, self.fu = steel_grade_dict[self.steel_grade][1]


notation = {
	'n': ('', 'n', '-', '', ''),
	'epsilon': ('Abminderungsfaktor', '\u03B5', '-', '', ''),
	'f42': ('Stabilitätskriterium', 'f.42', '-', '5.1.4.2', 42),
	'f44': ('Biegung um beide Achsen und Normalkraft', 'f.44', '-', '5.1.6.1', 44),
	'nrd': ('Normalkraftwiderstand', 'N.Rd', 'kN', '5.1.2.1', 38),
	'mvrd': ('Einachsige Biegung und Querkraft', 'M.\u03BD,Rd', 'kNm', '5.1.5.2', 43),
	'myrd': ('Biegewiderstand um die y-Achse', 'M.y,Rd', 'kNm', '5.1.3.1', 40),
	'mzrd': ('Biegewiderstand um die z-Achse', 'M.z,Rd', 'kNm', '5.1.3.1', 40),
	'n': ('', 'n', '-', '', ''),
	'vrd': ('Querkraftwiderstand', 'V.Rd', 'kN', '5.1.4.1', 41),
	'av__': ('wirksame Schubfläche', 'A.v', 'mm^2', '5.1.4.3', 43),
	'mynrd': ('Biegung um y-Achse mit Normalkraft', 'M.y,N,Rd', 'kNm', '5.1.6.2', 45),
	'zeta_y': ('', '\u03B6.y', '-', '5.1.6.2'),
	}

def power(unit):

	index = {
		'a': (0, 1),
		'f': (0, 2),
		'm': (6, 1),
		'n': (3, 1),
		'v': (3, 1),
	}
	return index.get(unit[0], (0, 3))


def p_decorate(func):

	def func_wrapper(self, *args):
		if self.add == True:
			name = func.__name__
			term = func(self)
			
			if args:
				comp_val = args[0]
				ratio = round(comp_val/term, 2)
				if ratio > 1.0:
					self.messages[name] = None
			else:
				ratio = None

			if name not in self.resultsf:
				desc, label, unit, ff, f = notation[name]
				p, r = power(name)
				self.resultsf[name] = {
					'name': name,
					'result': round(term*10**(-p), r),
					'label': label,
					'unit': unit,
					'ff': ff,
					'f': f,
					'code': code,
					'description': desc,
					'ratio2': ratio,
				}

			return term
		else:
			return func(self)
	return func_wrapper



class Slenderness():
	add = True

	def csc(self):
		if self.shape in I+C:
			self.bt = self.h1/self.tw
			csc = self.tab_5a()

		elif self.shape in L:
			b, t = self.a1, self.t
			csc = self.tab_5b()
			
		elif self.shape in F:
			csc = self.full()

		elif self.shape in ROR:
			d, t = self.d, self.t
			csc = self.tab_5a_ror()
			
		elif self.shape in R:
			b, t = self.h-3*self.t, self.t
			csc = self.tab_5a()
			
		return csc

	def csc_x(self):
		if self.shape in I+C:
			pass

	@p_decorate
	def epsilon(self):
		steel_grade = int(self.steel_grade[1:])
		return sqrt(steel_grade/self.fy)

	def tab_5a(self):
		bt = self.bt
		eps = self.epsilon()

		csc = 'n/a'

		if self.ned > 0:
			if bt <= 33*eps:
				csc = 1
			elif bt <= 38*eps:
				csc = 2
			elif bt <= 42*eps:
				csc = 3
			else:
				csc = 4

		if self.myed > 0:
			if bt <= 72*eps:
				csc = 1
			elif bt <= 83*eps:
				csc = 2
			elif bt <= 124*eps:
				csc = 3
			else:
				csc = 4

		if self.ned > 0 and self.myed > 0:
			sigma_sup = self.ned-self.myed/self.wely
			sigma_inf = self.ned+self.myed/self.wely
			psi = min(sigma_sup, sigma_inf)/max(sigma_sup, sigma_inf)
			alpha = 1-abs(psi)

			if psi > -1:
				if bt <= (36*eps)/(13*alpha-1):
					csc = 1
				elif bt <= (456*eps)/(13*alpha-1):
					csc = 2
				elif bt <= (42*eps)/(0.67+0.33*psi):
					csc = 3
				else:
					csc = 4

			else:
				if bt <= 36*eps/alpha:
					csc = 1
				elif bt <= 41.5*eps/alpha:
					csc = 2
				elif bt <= 32*eps*(1-psi)*sqrt(-psi):
					csc = 3
				else:
					csc = 4

		self.add_rslt('csc', str(csc), 'csc', '-', '4.3.1.3', 't5')
		print('csc(cat263): {}'.format(csc))
		return csc

	def tab_5a_ror(self):
		dt = self.d/self.t
		if dt <= 50*e**2:
			csc = 1
		elif dt <= 70*e**2:
			csc = 2
		elif dt <= 90*e**2:
			csc = 3
		else:
			csc = 4
	
	def tab_5b(self):
		if self.ned > 0:
			pass


	def full(self):
		csc = 1
		







class Components(Profile, Results):

	prefix = 'components'
	selection = ''

	def __init__(self, entries, add=True):
		self.add = add

		Profile.__init__(self, entries)
		self.entries = entries
		if 'lk' in entries:
			self.lk = entries['lk']
		else:
			self.lk = entries['ld']

		self.ld = self.lk
		self.psi_y = entries['psi']  # !!!!!!!!!!!!!!!!!!!!
		self.psi_z = entries['psi']  #!!!!!!!!!!!!!!!!!!!!!!
		
		self.ned = entries['ned']*1e3
		self.ved = entries['ved']*1e3
		self.myed = entries['myed']*1e6
		self.mzed = entries['mzed']*1e6

	@p_decorate
	def nrd(self):
		"""(39)"""
		if self.csc in (1, 2, 3):
			return self.fy*self.a/self.gamma_m1
		else:
			pass

	def mrd(self, w):
		return self.fy*w/self.gamma_m1

	@p_decorate
	def myrd(self):
		"""(40)"""
		if self.csc in (1, 2):
			return self.mrd(self.wply)
		elif self.csc == 3:
			return self.mrd(self.wely)
		else:
			pass

	@p_decorate
	def mzrd(self):
		"""(40)"""
		if self.csc in (1, 2):
			return self.mrd(self.wplz)
		elif self.csc == 3:
			return self.mrd(self.welz)
		else:
			pass

	@p_decorate
	def vrd(self):
		"""(41)"""
		return self.tau_y*self.av/self.gamma_m1

	@p_decorate
	def f42(self):
		"""5.1.4.2 Stabilitätskriterium"""
		return 1/((self.h-self.tf)/self.tw/sqrt((4*e)/self.fy))  # <= 1.0

	@p_decorate
	def av__(self):
		"""(42a)"""
		return self.a-2*self.b*self.tf+(self.tw+2*self.r)*self.tf

	@p_decorate
	def mvrd(self):
		"""(43)"""
		if self.shape in I:
			t1, t2, hw = self.tf, self.tw, self.h2
		else:
			t = self.t
			t1, t2, hw = t, 2*t, self.h-3*t

		return self.b*t1*self.fy*(self.h-t1)/self.gamma_m1+hw**2*t2*self.fy/ \
			(4*self.gamma_m1)*(1-(self.ved/self.vrd())**2)

	@p_decorate
	def f44(self):
		"""(44)"""
		return 1/(self.ned/self.nrd()+ self.myed/self.myrd()+ self.mzed/self.mzrd())

	@p_decorate
	def mynrd(self):
		"""(45)"""
		if self.shape in I:
			a = self.a__(self.b, self.tf)
		else:
			a = self.a__(self.b, self.t)
		zeta = self.zeta_(a, 'y')
		term = self.myrd()*zeta*(1-self.n())
		if term >= self.myrd():
			term = self.myrd()
		return term

	def mznrd(self):
		if self.shape in I:
			a = self.a__(self.b, self.tf)
			zeta = self.zeta_(a, 'z')
			if self.n() > a:
				""" (46) """
				term = self.mzrd()*(1-((self.n()-a)/(1-a))**2)
				f = 46
			else:
				""" (47) """
				term = self.mzrd()
				f = 47
		else:
			a = self.a__(self.h, self.t)
			zeta = self.zeta_(a, 'z')

			term = self.mrdy()*self.zeta*(1-self.n())
			f = 45
			if term >= self.mrdy():
				term = self.mrdy()

		self.add_rslt('mznrd', round(term*1e-6, 1), 'M.z,N,Rd', 'kNm', '5.1.6.2', f)
		return term

	def n(self):
		return self.ned/self.nrd()

	def a__(self, bh, t):
		return (self.a-2*bh*t)/self.a

	def zeta_(self, a, axis):
		term = 1/(1-0.5*a)
		self.add_rslt('zeta_'+axis, round(term, 3), '\u03B6.'+axis, '-', '5.1.6.2')
		return term

	def f48(self, ned, myed, mzed):
		if self.shape in self.profiles_I:
			alpha = 2
			beta = 5*ned*1e3/self.nrd()
			if beta <= 1.1:
				beta = 1.1
		elif self.shape in self.profiles_R:
			alpha = 1.66/(1-1.13*(ned*1e3/self.nrd())**2)
			beta = alpha
			if alpha >= 6.0:
				alpha = 6.0
				beta = alpha
		else:
			alpha, beta = 1.0, 1.0
		term = (myed*1e6/self.mynrd(ned))**alpha+(mzed*1e6/self.mznrd(ned))**beta
		self.add_rslt('f48', round(term, 3), 'f48', '-', '5.1.6.4', 48)
		return term

	def f49(self, ned, myed, axis):

		def zeta_(a, axis):
			term = 1/(1-0.5*a)
			if term >= 1+0.2*self.n(ned):
				term = 1+0.2*self.n(ned)
			return term

		if self.shape in self.profiles_I:
			if axis == 'y':
				a = self.a__(self.b, self.tf)
				zeta = zeta_(a, 'y')
			else:
				zeta = 1.0
		elif self.shape in self.profiles_R:
			if axis == 'y':
				a = self.a__(self.b, self.t)
				zeta = zeta_(a, 'y')
			else:
				a = self.a__(self.h, self.t)
				zeta = zeta_(a, 'z')
		else:
			zeta = 1.0
		self.add_rslt('zeta_'+axis, round(zeta, 3), '\u03B6.'+axis, '-', '5.1.6.2')

		ncr = e*getattr(self, 'i'+axis)*pi/self.lk**2
		omega = 0.6+0.4*getattr(self, 'psi_'+axis)
		if omega <= 0.4:
			omega = 0.4
		nkrd = getattr(NkRd(self.entries), 'nkrd_'+axis)()
		term = ned*1e3/nkrd + \
			   (1/(1-ned*1e3/ncr))*(omega*myed*1e6/(self.myrd()*zeta))
		self.add_rslt('f49_'+axis, round(term, 3), 'f49.'+axis, '-', '5.1.9.1', 49)
		return term

	def omega(self, psi, axis):
		term = 0.6+0.4*getattr(self, 'psi_'+axis)
		if term <= 0.4:
			term = 0.4
		self.add_rslt('omega_'+axis, round(term, 3), '\u03C9.'+axis, '-')
		return term

	def ncr(self, axis):
		term = e*getattr(self, 'i'+axis)*pi/self.lk**2
		self.add_rslt('ncr_'+axis, round(term*1e-3, 3), 'N.cr,'+axis, '-')
		return term

	def f50(self, ned, myed, mzed):
		def omega(psi, axis):
			term = 0.6+0.4*getattr(self, 'psi_'+axis)
			if term <= 0.4:
				term = 0.4
			return term
		def ncr(axis):
			term = e*getattr(self, 'i'+axis)*pi/self.lk**2
			return term

		nkrd_ = NkRd(self.entries)
		nkrd = min(nkrd_.nkrd_y(), nkrd_.nkrd_z())

		term = ned*1e3/nkrd + \
			   omega(self.psi_y, 'y')/(1-ned*1e3/ncr('y'))*myed*1e6/MDRd(self.entries).mdrd() +\
			   omega(self.psi_z, 'z')/(1-ned*1e3/ncr('z'))*mzed*1e6/self.mzrd()

		self.add_rslt('f50', round(term, 3), 'f50', '-', '5.1.10.1', 50)
		return term

	def f51(self):
		beta = 0.4+self.ned/self.nrd()+self.b/(self.h-self.tf)
		if beta <= 1.0:
			beta = 1.0
		
		nkrd_ = NkRd(self.entries)
		nkrd = min(nkrd_.nkrd_y(), nkrd_.nkrd_z())

		omega_y = self.omega(self.psi_y, 'y')
		mdrd = MDRd(self.entries).mdrd()

		myredrd = mdrd*(1-self.ned/nkrd)*(1-self.ned/self.ncr('y'))
		if myredrd >= omega_y*mdrd:
			myredrd = omega_y*mdrd
		mzredrd = self.mzrd()*(1-self.ned/nkrd)*(1-self.ned/self.ncr('z'))

		term = (self.omega(self.psi_y, 'y')*self.myed/myredrd)**beta + \
			(self.omega(self.psi_z, 'z')*self.mzed/mzredrd)**beta
		
		if isinstance(term, complex):
			term = 0

		self.add_rslt('f51', round(term, 3), 'f51', '-', '5.1.10.2', 50)

		return term



	@p_decorate
	def f52_myrd(self):
		"""(52)"""
		return self.fy*self.wely/self.gamma_m1



class MCR(Profile, Results):
	"""SIA 263:13, Anhang B: Ideelles Kippmoment MCR 

	:param geometry: Wheter the profile ist double_symmetric or general
	:param ld: Kipplänge
	:param psi: Verhältnis des kleineren Endmoments zum grösseren

	"""
	selection = ''

	def __init__(self, entries):
		Profile.__init__(self, entries)
		if 'ld' in entries:
			self.ld = entries['ld']
		else:
			self.ld = entries['lk']
		self.psi_y = entries['psi']  # !!!!!!!!!!!!!!!!!!!!!!!

	def eta(self):
		"""B.6 Berücksichtigt Lagerung und Biegebeanspruchung"""
		term = 1.75-1.05*self.psi_y+0.3*self.psi_y**2
		if term <= -0.5:
			term = -0.5
		self.add_rslt('eta', round(term, 2), '\u03C8', '-', 'B.6', 95)
		return term

	def lk(self):
		"""B.5 Reduzierte Kipplänge"""
		term = self.ld/sqrt(self.eta())
		self.add_rslt('lk', round(term, 1), 'L.K', 'mm', 'B.5', 94)
		return term

	def i(self, geometry = 'double_symmetric'):
		"""B.5 Trägheitsradius des Druckgurtes"""

		if geometry == 'double_symmetric':
			term = sqrt((self.iz/2)/(self.b*self.tf+self.aw/6))
		else:
			hc = (self.h-self.tf)/2
			izfc = self.b**3*self.tf/12
			izwc = self.tw**3*(hc/3-self.tf/2)/12
			afc = self.b*self.tf
			awc = self.tw*(hc/3-self.tf/2)
			term = sqrt((izfc+izwc)/(afc+awc))

		term = round(term)
		self.add_rslt('id', term, 'i.D', 'mm', 'B.5', 94)
		return term

	def lambda_k(self):
		"""B.5 Schlankheit des Druckgurtes"""
		term = self.lk()/self.i()
		self.add_rslt('lambda_k', round(term), '\u03BB', '-', 'B.5', 94)
		return term

	def sigma_dw(self):
		"""B.5 Wölbanteil sigma_dw der ideellen Kippspannung"""
		# Ziffer 5.6.2.3 ist nicht berücksichtigt
		term = pi**2*e/self.lambda_k()**2
		self.add_rslt('sigma_dw', round(term, 1), '\u03A3.Dw', 'N/mm^2', 'B.5', 94)
		return term

	def c(self):
		"""B.4 Hilfswert C"""
		term = pi/(self.wely)*sqrt(g*self.k*e*self.iz)
		term = round(term*1e-3)*1e3
		self.add_rslt('c', term*1e-3, 'C', 'kN/mm', 'B.4', 93)
		return term

	def sigma_dv(self):
		"""B.4 Saint-Venantsche Anteil sigma_dv der ideellen Kippspannung"""
		# Ziffer 5.6.2.3 ist nicht berücksichtigt
		term = self.eta()*self.c()/self.ld
		self.add_rslt('sigma_dv', round(term, 1), '\u03A3.Dv', 'N/mm^2', 'B.4', 93)
		return term

	def sigma_crd(self):
		"""B.3 Ideelle Kippspannung"""
		term = sqrt(self.sigma_dv()**2+self.sigma_dw()**2)
		self.add_rslt('sigma_crd', round(term, 1), '\u03A3.cr,D', 'N/mm^2', 'B.3', 92)
		return term

	def mcr(self):
		"""B.1 Ideelles Kippmoment"""
		term = self.wely*self.sigma_crd()
		self.add_rslt('mcr', round(term, 1), 'M.cr', 'kNm', 'B.1', 91)
		return term


class MDRd(Profile, Results):
	""" SIA 213:13, 4.5.2 Kippen von Biegeträgern 

	:param production: Wheter the profile is rolled or welded
	
	"""

	def __init__(self, entries):
		Profile.__init__(self, entries)
		self.production = entries['production']
		self.sigma_crd = MCR(entries).sigma_crd()
		self.w = getattr(self, entries['w'])
		self.sub_code = entries['sub_code']
		self.entries = entries

	def alpha_d(self):
		"""4.5.2.3 Imperfektionsbeiwerte"""
		if self.production == 'rolled':
			term = 0.21
		else:
			term = 0.49
		self.add_rslt('alpha_d', term, '\u03B1.D', '-', '4.5.2.3')
		return term

	def lambda_d_(self):
		"""4.5.2.3 Kippschlankheit"""
		term = sqrt(self.fy/round(self.sigma_crd)*(round(self.w/self.wely, 2)))
		self.add_rslt('lambda_d_', round(term, 4), '\u03BB.D', '-', '4.5.2.3')
		return term
	
	def phi_d(self):
		"""4.5.2.3"""
		lambda_d_ = self.lambda_d_()
		term = 0.5*(1+self.alpha_d()*(lambda_d_-0.4)+lambda_d_**2)
		self.add_rslt('chi_d', round(term, 1), '\u03D5.D', '-', '4.5.2.3')
		return term

	def chi_d(self):
		"""4.5.2.3 Abminderungsfaktor"""
		phi_d = self.phi_d()
		term = 1/(phi_d+sqrt(phi_d**2-self.lambda_d_()**2))
		if term >= 1.0:
			term = 1.0
		self.add_rslt('chi_d', round(term, 4), '\u03C7.D', '-', '4.5.2.3', 10)
		return term

	def mdrd(self):
		"""4.5.2.2 Kippwiderstand MD,Rd """
		if self.sub_code == 'sia263':
			chi = self.chi_k()
		else:
			chi = self.chi_d()
		print('chi: {}, {}'.format(chi, self.lambda_d_()))
		term = chi*self.w*self.fy/gamma_m1
		self.add_rslt('mdrd', round(term*1e-6, 1), 'M.D.Rd', 'kNm', '4.5.2.2', 9)
		return term

	# 
	def phi_k(self):
		a = 0.21
		term = 0.5*(1+a*(self.lambda_d_()-0.2)+self.lambda_d_()**2)
		self.add_rslt('phi_k_y', round(term, 2), '\u03A6.K,y', '4.5.1.4')
		return term

	def chi_k(self):
		term = 1/(self.phi_k()+sqrt(self.phi_k()**2-self.lambda_d_()**2))
		if term >= 1.0:
			term = 1.0
		self.add_rslt('chi_k_y', round(term, 4), '\u03C8.K,y', '4.5.1.4', 8)
		return term


class NkRd(Profile, Results):
	""" SIA 263:13, 4.5.1 Knicken """
	
	def __init__(self, entries):
		Profile.__init__(self, entries)
		if 'lk' in entries:
			self.lk = entries['lk']
		else:
			self.lk = entries['ld']
		self.production = entries['production']
		
	def alpha(self, axis):
		a, b, c, d = 0.21, 0.34, 0.49, 0.76
		shapes = ['IPE', 'PEA', 'INP', 'HEA', 'HEB', 'HEM']

		if self.production == 'rolled':
			if self.shape in shapes and axis == 'y':
				if (self.h-self.tf)/self.b > 1.2 and self.tf <= 40:
					term = a
				elif self.tf <= 100:
					term = b
				else:
					term = d
				self.add_rslt('alpha_y', term, '\u03B1.y', '-', '4.5.1.4')

			elif self.shape in shapes and axis == 'z':
				if (self.h-self.tf)/self.b > 1.2 and self.tf <= 40:
					term = b
				elif self.tf <= 100:
					term = c
				else:
					term = d
				self.add_rslt('alpha_z', term, '\u03B1.z', '-', '4.5.1.4')

			elif self.shape in ['RRW']:
				term = a
				self.add_rslt('alpha', term, '\u03B1', '-', '4.5.1.4')
			else:
				pass

		else:
			pass
		self.add_rslt('alpha', term, '\u03B1', '-', '4.5.1.4')
		return term
				
	def lambda_k_y(self):
		term = self.lk/self.iy_/(pi*sqrt(e/self.fy))
		self.add_rslt('lambda_k_y', round(term, 1), '\u03BB.K,y', '4.5.1.4')
		return term

	def lambda_k_z(self):
		term = self.lk/self.iz_/(pi*sqrt(e/self.fy))
		self.add_rslt('lambda_k_z', round(term, 1), '\u03BB.K,z', '4.5.1.4')
		return term

	def phi_k_y(self):
		term = 0.5*(1+self.alpha('y')*(self.lambda_k_y()-0.2)+self.lambda_k_y()**2)
		self.add_rslt('phi_k_y', round(term, 2), '\u03A6.K,y', '4.5.1.4')
		return term

	def phi_k_z(self):
		term = 0.5*(1+self.alpha('z')*(self.lambda_k_z()-0.2)+self.lambda_k_z()**2)
		self.add_rslt('phi_k_z', round(term, 2), '\u03A6.K,z', '4.5.1.4')
		return term

	def chi_k_y(self):
		term = 1/(self.phi_k_y()+sqrt(self.phi_k_y()**2-self.lambda_k_y()**2))
		if term >= 1.0:
			term = 1.0
		self.add_rslt('chi_k_y', round(term, 4), '\u03C8.K,y', '4.5.1.4', 8)
		return term

	def chi_k_z(self):
		term = 1/(self.phi_k_z()+sqrt(self.phi_k_z()**2-self.lambda_k_z()**2))
		if term >= 1.0:
			term = 1.0
		self.add_rslt('chi_k_z', round(term, 4), '\u03C8.K,z', '4.5.1.4', 8)
		return term
	
	def nkrd_y(self):
		term = self.chi_k_y()*self.fy*self.a/gamma_m1
		self.add_rslt('nkrd_y', round(term*1e-3, 1), 'N.K,y,Rd', 'kN', '4.5.1.3', 7)
		return term
	
	def nkrd_z(self):
		term = self.chi_k_z()*self.fy*self.a/gamma_m1
		self.add_rslt('nkrd_z', round(term*1e-3, 1), 'N.K,z,Rd', 'kN', '4.5.1.3', 7)
		return term


