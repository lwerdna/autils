#!/usr/bin/python
#------------------------------------------------------------------------------
#
#    Copyright 2011-2013 Andrew Lamoureux
#
#    This file is a part of alib.
#
#    alib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#------------------------------------------------------------------------------
#    extension field elements, F_{c^d} where c is the characteristic
#    and d is the degree
#------------------------------------------------------------------------------

# elements represented as a polynomial ring over prime field elements
class F_c_d(FieldElem):
    def __init__(self, K, e):
        self.K = K
        self.e = PolyRing(e)

    def zero(self): # we call the additive identity "0"
        new_e = map(lambda x: F_p(x, self.K.char), [0]*self.K.deg)
        return F_c_d(self.K, new_e)

    def one(self): # we call the multiplicative identity "1"
        new_e = map(lambda x: F_p(x, self.K.char), [0]*(self.K.deg-1) \
                    + [1])
        return F_c_d(self.K, new_e)

    # addition done by adding polynomials (no reduction needed)
    def __add__(self, rhs):
        new_e = self.e + rhs.e
        return F_c_d(self.K, new_e)

    # negation done by subtracting polynomials (no reduction needed)
    def __neg__(self):
        new_e = (self.K.poly - self.e)
        return F_c_d(self.K, new_e)

    # multiplication done by K[x] % primitive
    def __mul__(self, rhs):
        if type(rhs) == type(0):
            # allow multiplication by an int -> repeated adding
            return MultiplicationByDoubling(self, rhs)
            
        # true field multiplication by another element
        new_e = (self.e * rhs.e) % self.K.poly
        return F_c_d(self.K, new_e)

    # operations that are just composed of others
    def __sub__(self, rhs):
        return self + (-rhs)

    def __div__(self, rhs):
        return self * rhs**-1

    def __pow__(self, e):
        result = None
        # b^(-e) = (b^(-1))^e
        if e < 0:
            xgcd = ExtendedEuclidean(self.e, self.K.poly)
            if xgcd[2] != 1:
                raise ValueError("gcd(%d,%d) != 1" % (self.e, self.K.char))
            new_e = xgcd[0]
            if new_e < 0:
                new_e += self.K.char
            result = F_c_d(self.K, new_e)
            e = -1*e
        else:
            result = self

        return ExponentiationBySquaring(result, e)

    def __eq__(self, rhs):
        if rhs == None:
            return False

        if (self.e == rhs.e) and (self.K == rhs.K):
            return True
        else:
            return False

    def __ne__(self, rhs):
        return not (self == rhs)

    def __str__(self):
        return '%d' % self.e

    def __repr__(self):
        return 'F_c_d(%s, %d)' % (repr(self.K), self.e)

    def __nonzero__(self):
        return self.e != 0

    def characteristic(self):
        return self.K.char

