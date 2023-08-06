 
import inspect
import re
from math import sqrt
from sympy.printing.mathml import print_mathml, mathml
from sympy import sympify, latex, Integral, Limit

def multipleReplace(text, wordDict):
	for key in wordDict:
		text = text.replace(key, str(wordDict[key]))
	return text

def foo3(a):
	x = 2
	term = 'sqrt(x + a)'
	print('locals: {}'.format(locals()))
	new = multipleReplace(term, locals())
	print('replaced: {}'.format(new))
	#term = sympify(new)

	print(latex(Limit(str(new), x, 1)))
	
foo3(2)