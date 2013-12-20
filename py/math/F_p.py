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

from factoring import IsPrime
from fields import Field, FieldElem
from algos import ExponentiationBySquaring, MultiplicationByDoubling, ExtendedEuclidean

class PrimeField(Field):
    # prime field has degree 1, just a prime characteristic
    def __init__(self, char):
        if not IsPrime(char):
            raise ValueError("%d is not prime" % char)

        super(PrimeField, self).__init__(char, 1)

    def zero(self):
        return F_p(self, 0); 

    def one(self):
        return F_p(self, 1); 

    def __str__(self):
        return 'F_%d' % (self.characteristic)

    def __repr__(self):
        return 'PrimeField(%d)' % (self.characteristic)

# prime fields elements 
class F_p(FieldElem):
    def __init__(self, K, e):
        # K is the field that this element is a member of
        self.K = K
        # prime field represents its element as an integer
        if e >= self.K.characteristic:
            e = e % self.K.characteristic

        if type(e) != type(0) and type(e) != type(0L):
            raise ValueError('expected integer type for field element initializer')
        
        self.e = e

    def __add__(self, rhs):
        new_e = (self.e + rhs.e) % self.K.characteristic
        return F_p(self.K, new_e)

    def __neg__(self):
        new_e = (self.K.characteristic - self.e)
        return F_p(self.K, new_e)

    def __sub__(self, rhs):
        return self + (-rhs)

    def __mul__(self, rhs):
        if type(rhs) == type(0):
            # allow multiplication by an int -> repeated adding
            return MultiplicationByDoubling(self, rhs)
            
        # true field multiplication by another element
        new_e = (self.e * rhs.e) % self.K.characteristic
        return F_p(self.K, new_e)

    def __div__(self, rhs):
        return self * rhs**-1

    def __pow__(self, e):
        #print "pow performing %s raised %d" % (self, e)
        result = None
        # b^(-e) = (b^(-1))^e
        if e < 0:
            xgcd = ExtendedEuclidean(self.e, self.K.characteristic)
            if xgcd[2] != 1:
                raise ValueError("gcd(%d,%d) != 1" % (self.e, self.K.characteristic))
            new_e = xgcd[0]
            if new_e < 0:
                new_e += self.K.characteristic
            result = F_p(self.K, new_e)
            e = -1*e
        else:
            result = self

        return ExponentiationBySquaring(result, e)

    def __eq__(self, rhs):
        if rhs == None:
            return False

        # convert integers to allow for comparison
        if type(rhs) == type(0):
            if rhs >= self.K.characteristic:
                raise ValueException("comparing against a non field element")

            rhs = F_p(self.K.characteristic, rhs) 

        if (self.e == rhs.e) and (self.K == rhs.K):
            return True
        else:
            return False

    def __ne__(self, rhs):
        return not (self == rhs)

    def __str__(self):
        return '%d' % self.e

    def __repr__(self):
        return 'F_p(%s, %d)' % (repr(self.K), self.e)

    def __nonzero__(self):
        return self.e != 0

###############################################################################
# main()
###############################################################################
if __name__ == '__main__':

    print "field tests"
    
    # work over F_23
    F = PrimeField(23)
    x = F_p(F, 9)
    y = F_p(F, 5)

    print "%s*%s = %s" % (y, y, y*y)
    print "%s**2 = %s" % (y, y**2)
    

