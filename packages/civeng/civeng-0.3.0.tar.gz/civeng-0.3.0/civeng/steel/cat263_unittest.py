

class MDRdTest(unittest.TestCase):
	"""SIA 263:13, 4.5.2 Kippen von Biegeträgern
	C4/06, 3.2 Anwendungsbeispiel zum Kippnachweis
	"""

	def setUp(self):
		self.entries = {
			'steel_grade': 'S 235',
			'shape': 'IPE',
			'size': '600',
			'psi': 0.5,
			'ld': 4000,
			'production': 'rolled',
			'w': 'wply',
			'sub_code': 'sia263e',
			
		}

	def testCalculation(self):
		mcr = MCR(self.entries)  # requires ld, psi
		self.assertEqual(round(mcr.eta(), 2), 1.30)
		self.assertEqual(round(mcr.i('double_symmetric')), 56)
		self.assertEqual(round(mcr.sigma_dw()), 528)
		self.assertEqual(round(mcr.c()), 998000)
		self.assertEqual(round(mcr.sigma_dv()), 324)
		self.assertEqual(round(mcr.sigma_crd()), 620)
		printf('MCR', mcr.get_results())
		
		mdrd = MDRd(self.entries)
		self.assertEqual(mdrd.alpha_d(), 0.21)
		self.assertEqual(round(mdrd.lambda_d_(), 3), 0.66)
		self.assertEqual(round(mdrd.chi_d(), 4), 0.9166)

		print('mdrd: {}'.format(mdrd.mdrd()))
		printf('MdRd', mdrd.get_results())

class NKRdTest(unittest.TestCase):
	"""SIA 263:13, 4.5.1 Knicken
	C4/06, 2.2 Anwendungsbeispiel
	"""
	
	def setUp(self):
		self.entries = {
			'steel_grade': 'S 275',
			'shape': 'HEA',
			'size': '180',
			'lk': 4000,  # [mm]
			'production': 'rolled',
		}

	def testCalculation(self):
		nkrd = NkRd(self.entries)
		self.assertEqual(nkrd.alpha('z'), 0.49)
		self.assertEqual(round(nkrd.lambda_k_z(), 2), 1.02)
		self.assertEqual(round(nkrd.nkrd_z()*1e-3, 0), 627)
		print('NkRd: {}'.format(nkrd.phi_k_z()))
		print('NkRd: {}'.format(nkrd.chi_k_z()))
		print('NkRd: {}'.format(nkrd.nkrd_z()))
		printf('NkRd', nkrd.get_results())


class TablesTest(unittest.TestCase):
	"""SIA 263:13, 4.5.1 Knicken
	C4/06, 2.2 Anwendungsbeispiel
	"""
	
	def setUp(self):
		self.db = Database()

	def testCalculation(self):
		profiles = self.db.select_tables()
		print(profiles)

		for p in profiles:
			header = self.db.select_header(p)
			print(header)
			table = self.db.select_table(p)

			def convert(s):
				s = str(s)
				if s.isdigit():
					if '.' in s:
						return float(s)
					else:
						return float(s)
				else:
						return s
					
			for row in table:
				#rowf = [convert(x) for x in row]


				s = ''
				i = 0
				for h in header:
					if h == 'dmax':
						s += '{'+str(i)+':>9}'
					else:
						s += '{'+str(i)+':>9}'
					i += 1

				print(s.format(*row))
					

class TablesTest2(unittest.TestCase):
	"""SIA 263:13, 4.5.1 Knicken

	"""

	def setUp(self):
		self.db = Database()
		self.entries = {
			'steel_grade': 'S 235',
			'shape': 'HEA',
			'size': '180',
			'lk': 4000,  # [mm]
			'production': 'rolled',
		}

	def testCalculation(self):
		profiles = self.db.select_tables()

		for p in profiles:
			print(p, self.entries['steel_grade'])
			self.entries['shape'] = p
			header = self.db.select_header(p)
			table = self.db.select_table(p)
			
			length = [0, 1, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]
			s = ''
			for i, _ in enumerate(length):
				s += '{'+str(i)+':>6}'
			print(s.format(*length))

			
			for i, row in enumerate(table):
				self.entries['size'] = row[0]
				row_dict = dict(zip(header, row))

				nkrd = []
				
				for l in length:
					self.entries['lk'] = l*1e3
					nkrd.append(round(NkRd(self.entries).nkrd_y()*1e-3))
				
				if i % 5 == 0:
					print('')

				
				
				print(s.format(*nkrd))
				
				
				
				


if __name__ == "__main__":
	unittest.main() 
