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

class Field(object):
	def __init__(self, characteristic, degree):
		self.characteristic = characteristic
		self.degree = degree
	def order(self):
		return self.characteristic ** self.degree
	def zero(self):
		pass
	def one(self):
		pass
	def __eq__(self, rhs):
		return (self.characteristic == rhs.characteristic) and \
			(self.degree == rhs.degree)
	def __ne__(self, rhs):
		return not (self == rhs)
	def __str__(self):
		return 'F_{%d^%d}' % (self.characteristic, self.degree)
	def __repr__(self):
		return 'Field(%d, %d)' % (self.characteristic, self.degree)

# abstract field element type
class FieldElem(object):
	def __init__(self, K):
		self.K = K
	def __add__(self, rhs):
		pass
	def __sub__(self, rhs):
		pass
	def __mul__(self, rhs):
		pass
	def __div__(self, rhs):
		pass
	def __neg__(self):		  # eg: -a s.t. a + (-a) = 0
		pass
	def __pow__(self, exp):	 # eg: a**(-1) == a^(-1)
		pass
	def __eq__(self, rhs):
		pass
	def __ne__(self, rhs):
		pass
	def __nonzero__(self):	  # eg: if a:
		pass

	# when passed to certain generic algorithms (like exponentiation by
	# squaring), a generic means to get the identity is necessary
	def zero(self):
		return self.K.zero()
	def one(self):
		return self.K.one()

