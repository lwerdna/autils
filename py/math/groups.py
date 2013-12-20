#!/usr/bin/python
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

# abstract Group type
class Group(object):
    def __init__(self, order):
        self.m_order = order

        # delay calculating this
        self.m_order_factors = []

    def order(self):
        return self.m_order

    def order_factors(self):
        # requested! put in the work to calculate this!
        if not self.m_order_factors:
            self.m_order_factors = Factor(self.m_order)

        return self.m_order_factors

class GroupElem(object):
    def __init__(self, G):
        self.G = G
    # identity
    def one(self):
        raise NotImplemented()
    # concrete groups can choose to represent their group operation with 
    # add/sub or with mul/div
    def __add__(self, rhs):
        raise NotImplemented()
    def __sub__(self, rhs):
        raise NotImplemented()
    def __mul__(self, rhs):
        raise NotImplemented()
    def __div__(self, rhs):
        raise NotImplemented()
    # whatever is chosen, best to reference here for generic algorithms
    def groupAction(self, rhs):
        raise NotImplemented()
    # negation of the 
    def __neg__(self):          # eg: -a s.t. a + (-a) = 0
        raise NotImplemented()
    def __eq__(self, rhs):
        raise NotImplemented()
    def __ne__(self, rhs):
        raise NotImplemented()
    def __nonzero__(self):
        raise NotImplemented()
    # return containing group
    def group(self):
        raise NotImplemented()
    #
    def order(self):
        raise NotImplemented()
    # some algos (pollard rho for example) need group elements randomly assigned to n buckets,
    # return [0, n-1] the index to which bucket this element is in
    def bucketize(self, n):
        raise NotImplemented()

