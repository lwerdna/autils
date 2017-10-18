#!/usr/bin/python
#------------------------------------------------------------------------------
#
#	This file is a part of autils. 
#
#	Copyright 2011-2016 Andrew Lamoureux
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#------------------------------------------------------------------------------

from F_p import PrimeField, F_p

from algos import MultiplicationByDoubling

# abstract elliptic curve class
# curves with different representations and underlying fields or whatever can
# extend this...
class EllipticCurve(object):
	def __init__(self, field, coeffs):
		self.K = field

		# y^2 + a1*xy + a3*y = x^3 + a2*x^2 + a4*x + a6
		self.a1, self.a2, self.a3, self.a4, self.a6 = coeffs

	def HasseBound(self):
		# basically the number of points on the curve differs from the number of field
		# elements by at most 2*sqrt(#F)
		order = self.K.order()
		a_p = 2 * LongSqrt(order)
		lower = order + 1 - a_p
		upper = order + 1 + a_p
		return [lower, upper]

	def isAnomalous(self, order=0):
		'''
		anomalous curves have the same number of points as there are
		elements in their underlying field
		said differently, their trace a_p == 1 since #E = #F + 1 - a_p
		'''
		if not order:
			order = self.order()

		return self.K.order() == order

	def isSupersingular(self, order=0):
		'''
		supersingular curves have order divisible by the underlying
		field's characteristic
		'''
		if not order:
			order = self.order()

		return not (order % self.K.characteristic)

	def __str__(self):
		terms_lhs = ['y^2']
		terms_rhs = ['x^3']

		if self.a1:
			terms_lhs.append('(%s)*xy' % self.a1)
		if self.a3:
			terms_lhs.append('(%s)*y' % self.a3)
		if self.a2:
			terms_rhs.append('(%s)*x^2' % self.a2)
		if self.a4:
			terms_rhs.append('(%s)*x' % self.a4)
		if self.a6:
			terms_rhs.append('(%s)' % self.a6)

		return '%s = %s over %s' % (' + '.join(terms_lhs), ' + '.join(terms_rhs), str(self.K))

	def __repr__(self):
		return 'EllipticCurve(%s, [%s,%s,%s,%s,%s])' % \
					(repr(self.K), repr(self.a1), repr(self.a2), repr(self.a3), \
					repr(self.a4), repr(self.a6))

# member of the rational points (the group of points)
class ECPoint(object):
	def __add__(self, rhs): # eg: P+Q
		pass
	def __sub__(self, rhs): # eg: P-Q = P+(-Q)
		pass
	def __mul__(self, rhs): # eg: P*5
		pass
	def __inv__(self, rhs): # eg: -P
		pass
	def __eq__(self, rhs):  # eg: if P==Q
		pass
	def __neq__(self, rhs): # eg: if P!=Q
		pass
	def isId(self):		 # is this point the point-at-infinity, [0]?
		pass
	def zero(self):		   # return [0]
		pass

# kglib type A curves/points:
# over finite field, cartesian (non-projective) coordinates
# characteristic not 2 or not 3 (so only a4, a6 non-zero by change of variables)
# SIMPLEST CASE!
class ECurveA(EllipticCurve):
	# send [a1,a2,a3,a4,a6]
	def __init__(self, field, coeffs):
		# the underlying field
		super(ECurveA, self).__init__(field, coeffs)

		if self.a1 or self.a2 or self.a3:
			raise NotImplemented("ECurveA is for simplified Wierstrass with only a4, a6 nonzero")

		if (self.a4 and (self.a4.K.characteristic <= 3)) or \
			(self.a6 and (self.a6.K.characteristic <= 3)):
			raise ValueError("ECurveA must be over field of characteristic > 3")

	def isOnCurve(self, P):
		return self.isOnCurve(P.x, P.y)

	def __str__(self):
		return 'y^2 = x^3 + (%s)*x + (%s) over (%s)' % (str(self.a4), str(self.a6), str(self.K))
 
#
class ECPointA(ECPoint):
	# python None indicates [0]
	def __init__(self, E, x, y):
		self.E = E
		self.x = x
		self.y = y

		if not self.isOnCurve():
			print str(self)
			raise ValueError("point is not on curve!")

	def isOnCurve(self):
		x = self.x
		y = self.y
	   
		if self.isId():
			return True
 
		if y**2 + self.E.a1*x*y + self.E.a3*y == \
			x**3 + self.E.a2*x*x + self.E.a4*x + self.E.a6:
			return True
		else:
			print "LHS: " + str(y**2 + self.E.a1*x*y + self.E.a3*y)
			print "RHS: " + str(x**3 + self.E.a2*x*x + self.E.a4*x + self.E.a6)
			return False

	def __add__(self, rhs):
		if self.isId():
			return rhs
		if rhs.isId():
			return self
		# case: adding inverse points
		if self == -rhs:
			return self.zero()
		# case: point doubling
		if self == rhs:
			t = ((self.x**2)*3 + self.E.a4)/(self.y*2)
			x = t*t - self.x*2
			y = t*(self.x - x) - self.y
			return ECPointA(self.E, x, y)
		# case: normal (non-doubling)
		else: 
			m = (rhs.y - self.y)/(rhs.x - self.x)
			x = m**2 - self.x - rhs.x
			y = m*(self.x - x) - self.y
			return ECPointA(self.E, x, y)

	def isId(self):
		return (type(self.x) == type(None)) and (type(self.y) == type(None))

	def __eq__(self, rhs):
		return (self.x == rhs.x) and (self.y == rhs.y) 

	def __mul__(self, rhs):
		if self.isId():
			return copy.copy(self)
		return MultiplicationByDoubling(self, rhs)

	def __neg__(self):
		return ECPointA(self.E, self.x, -self.y)
	
	def __sub__(self, rhs):
		return self + (-rhs) 
	   
	def zero(self):
		return ECPointA(E, None, None)
		 
	def __str__(self): 
		if self.x == None and self.y == None:
			return '(0) on %s' % str(self.E)
		else:
			return '(%s, %s) on %s' % (str(self.x), str(self.y), str(self.E))

	def __repr__(self):
		return 'ECPointA(%s, %s, %s)' % (repr(self.E), repr(self.x), repr(self.y))

# TODO: 
# counting points
# Shanks-Mestre (used by Pari/GP
# Baby-step Giant-step
# Schoof

###############################################################################
# main()
###############################################################################
if __name__ == '__main__':

	print "Elliptic Curve Tests..."

	print "small test: y^2 = x^3 + x over F_23"	
	# work over F_23
	F = PrimeField(23)
	
	# elliptic curve Wierstrass parameters
	# y^2 = x^3 + x
	ai = map(lambda x: F_p(F, x), [0, 0, 0, 1, 0])
	
	# the curve itself
	E = ECurveA(F, ai)
	print E
	
	# a point
	Px, Py = F_p(F,9), F_p(F,5)
	P = ECPointA(E, Px, Py)
	print P
	   
	Qx, Qy = F_p(F,9), F_p(F,18)
	Q = ECPointA(E, Qx, Qy)
	print Q
	print Q+P
	 
	for i in range(10):
		Q = P*i
		print "P*%d: %s" % (i, str(Q))
	
	print "medium test: y^2 = x^3 + -4x over F_5186715201442783011196302036546738736427436330054065589317"
	# bigger parameters now
	# should print (verified with sage):
	#(0 : 1 : 0)
	#(920019632805867328128779577194949110656005543293392670030 : 247924023714148178898329740691786895218087166284853058178 : 1)
	#(1347368923186712640648783809374613834547443961974834387610 : 4112389959757745391454835779367729479686292529710684578030 : 1)
	#(5136072150299522727048713884921549466888394167843055557753 : 670759223811902288870805701970579108550537352829254733458 : 1)
	#(1523758263928574765292370494195845945669929150675275480810 : 1825086083694868727663500708139317408289339684224336360203 : 1)
	#(3225035031647916196326675568092081315499746913291130727961 : 3862609992862923384096473215341563562672049055673897245136 : 1)
	#(3033242856509374779459856267026730920528641019566242363839 : 2837374515709986657488201449785133510656808342978441386115 : 1)
	#(3525594817842830522356194144342983169660348146136984362694 : 4038421835327402660163567259258456243712931147482944846450 : 1)
	#(657723557911816259375376113617675555124843796900715252667 : 3806015207794008162697117778821888037361827943817320145382 : 1)
	#(1660669180506570899843379425665210350557400564111037059779 : 3557313439153671053486603110953622413957092959496717974886 : 1)
	F = PrimeField(5186715201442783011196302036546738736427436330054065589317)
	ai = map(lambda x: F_p(F, x), [0, 0, 0, -4, 0])
	E = ECurveA(F, ai)
	print E
	Px, Py, Qx, Qy = map(lambda x: F_p(F,x), [ \
		920019632805867328128779577194949110656005543293392670030, \
		247924023714148178898329740691786895218087166284853058178, \
		1655646638614857830673453525865145510699045501734303194406, \
		4260089289459941068169905641641773579714103470632308043647 \
	  ])
	P = ECPointA(E, Px, Py)
	print 'P: ', P
	Q = ECPointA(E, Qx, Qy)
	print 'Q: ', Q
	for i in range(10):
		Q = P*i
		print "P*%d: %s" % (i, str(Q))

	print "large test: secp521r1"
	F = PrimeField(0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)

	zero = F_p(F, 0)
	a4 = F_p(F, 0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC)
	a6 = F_p(F, 0x51953EB9618E1C9A1F929A21A0B68540EEA2DA725B99B315F3B8B489918EF109E156193951EC7E937B1652C0BD3BB1BF073573DF883D2C34F1EF451FD46B503F00)
	E = ECurveA(F, [zero, zero, zero, a4, a6])

	Px = F_p(F, 0xC6858E06B70404E9CD9E3ECB662395B4429C648139053FB521F828AF606B4D3DBAA14B5E77EFE75928FE1DC127A2FFA8DE3348B3C1856A429BF97E7E31C2E5BD66)
	Py = F_p(F, 0x11839296A789A3BC0045C8A5FB42C7D1BD998F54449579B446817AFBD17273E662C97EE72995EF42640C550B9013FAD0761353C7086A272C24088BE94769FD16650)
	G = ECPointA(E, Px, Py)

	ident = ECPointA(E, None, None)
	order = 0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409

	assert G*order == ident
	assert G*(order-1) != ident
	assert G*(order+1) == G

	print 'PASSED!'
