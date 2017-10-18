#!/usr/bin/python
#------------------------------------------------------------------------------
#
#	Copyright 2011-2016 Andrew Lamoureux
#
#	This file is a part of autils.
#
#	autils is free software: you can redistribute it and/or modify
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

from groups import Group, GroupElem
import ZZn
from algos import ExponentiationBySquaring

# multiplicative group of integers modulo n
class ZZn(GroupElem):
	def __init__(self, a, n):
		if a<0:
			a += n
		if a>n:
			a = a % n
		self.elem = a
		# BUG BUG: for now, assume n is prime because no totient calculation has occurred yet
		self.n = n
		self.modulus = n
		self.G = Group(n-1)

	def group(self):
		return self.G

	def order(self):
		for d in sorted(DivisorsGivenFactors(self.G.order_factors())):
			if self**d == ZZn(1, self.n):
				return d

		return -1

	def one(self):
		return ZZn(1, self.n)

	# we represent the group action multiplicatively
	def __mul__(self, rhs):
		return ZZn((self.elem * rhs.elem) % self.n, self.n)
	def __div__(self, rhs):
		return self * (rhs**-1)
	def __pow__(self, e):
		result = None
		# b^(-e) = (b^(-1))^e
		if e < 0:
			new_e = InverseMod(self.elem, self.n)
			e = -1*e
		else:
			new_e = self.elem

		temp = ZZn(new_e, self.n) 

		return ExponentiationBySquaring(temp, e)

	# generic group operation
	def groupAction(self, rhs):
		return self * rhs

	# other
	# equality test: compare integer element and modulus
	def __eq__(self, rhs):
		return (self.elem == rhs.elem) and (self.n == rhs.n)
	def __ne__(self, rhs):
		return not (self == rhs)
	# return the integer element
	def lift(self):
		return self.elem
	#  
	def __str__(self):
		return 'Mod(%d, %d)' % (self.elem, self.n)
	def __repr__(self):
		return self.__str__()

	# simple bucketizer
	def bucketize(self, n):
		return self.elem % n

