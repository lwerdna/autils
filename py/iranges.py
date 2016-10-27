#!/usr/bin/env python

# manage integer ranges

import random

# class used internally by the IrangeManager
class Irange:
	# by convention Iranges are [left,right)
	def __init__(self, left, right, hexFmt=False):
		assert(right>left)
		self.left = left
		self.right = right
		self.hexFmt = hexFmt

	def length(self):
		return right-left

	def __contains__(self, other):
		# see if a range is within our range
		if isinstance(other, Irange):
			return other.left >= self.left and other.right <= self.right
		# see if an integer is within our range
		else:
			return other >= self.left and other < self.right

	def __eq__(self, other):
		return self.left==other.left and self.right==other.right

	def __str__(self):
		if self.hexFmt:
			return "[0x%x,0x%x)" % (self.left, self.right)
		else:
			return "[%d,%d)" % (self.left, self.right)

class IrangeManager:
	def __init__(self, capacity):
		assert(capacity>0)
		self.Iranges = []
		self.capacity = capacity;

	def normalize(self):
		# if exceeded capacity, keep largest ranges
		if len(self.Iranges) > self.capacity:
			self.Iranges = sorted(self.Iranges, key=lambda r:r.length())
			self.Iranges = self.Iranges[0:self.capacity]

		# sort ascending order
		self.Iranges = sorted(self.Iranges, key=lambda r:r.left)

	def add(self, left, right):
		newRange = Irange(left, right)

		# remove current ranges enveloped by this one
		# important! rest of functionality depends on this post condition
		self.Iranges = filter(lambda x: x not in newRange, self.Iranges)


		# find interval(s) that the endpoints are in
		a = filter(lambda ir: left in ir, self.Iranges)
		b = filter(lambda ir: right in ir, self.Iranges)

		# convert filter returns to intervals
		assert(not a or len(a)==1)
		assert(not b or len(b)==1)
		if(a): a = a[0]
		if(b): b = b[0]

		# sanity checks
		assert((not a or not b) or (a.left < b.left))

		# handle cases
		if not a and not b:
			self.Iranges.append(newRange)
		elif a and not b:
			self.Iranges.remove(a)
			self.Iranges.append(Irange(a.left, right))
		elif not a and b:
			self.Iranges.remove(b)
			self.Iranges.append(Irange(left, b.right))
		elif a and b:
			self.Iranges.remove(a)
			self.Iranges.remove(b)
			self.Iranges.append(Irange(a.left, b.right))
		
		self.normalize()

	def asList(self):
		result = []
		for ir in self.Iranges:
			result += list(range(ir.left, ir.right))
		return result

	def __str__(self):
		substrs = []
		for ir in self.Iranges:
			substrs.append(str(ir))
		return '\n'.join(substrs)

if __name__ == '__main__':
	irm = IrangeManager(10)
	irm.add(10, 20)
	irm.add(30, 40)
	irm.add(50, 60)
	irm.add(70, 80)
	irm.add(90, 100)
	print irm
	print '--------------'
	irm.add(15,35)
	irm.add(75,95)
	print irm
	print irm.asList()

	for 
