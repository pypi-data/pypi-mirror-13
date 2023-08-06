
import unittest
from civeng.steel.props import Square

class SquareTest(unittest.TestCase):
	
	def setUp(self):
		self.entries = (40, 40, 3)
	
	def testCalculation(self):
		rrk = Square(*self.entries)

		print(rrk.m())
		print(rrk.a())
		print(rrk.i())
		print(rrk.wel())


if __name__ == "__main__":
	unittest.main() 