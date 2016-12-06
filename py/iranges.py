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

	def __len__(self):
		return self.right-self.left

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
	def __init__(self, capacity=None, hexFmt=False):
		assert(not capacity or capacity>0)
		self.Iranges = []
		self.capacity = capacity;
		self.hexFmt = hexFmt

	def normalize(self):
		# if exceeded capacity, keep largest ranges
		if self.capacity and len(self.Iranges) > self.capacity:
			self.Iranges = sorted(self.Iranges, key=lambda r:len(r))
			self.Iranges = self.Iranges[0:self.capacity]

		# sort ascending order
		self.Iranges = sorted(self.Iranges, key=lambda r:r.left)

	def add(self, left, right):
		# nonsense or 0 length ranges
		if right <= left: return

		newRange = Irange(left, right, self.hexFmt)

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
		assert((not a or not b) or (a.left <= b.left))

		# handle cases
		if not a and not b:
			self.Iranges.append(newRange)
		elif a and not b:
			self.Iranges.remove(a)
			self.Iranges.append(Irange(a.left, right, self.hexFmt))
		elif not a and b:
			self.Iranges.remove(b)
			self.Iranges.append(Irange(left, b.right, self.hexFmt))
		elif a and b:
			self.Iranges.remove(a)
			if a != b:
				self.Iranges.remove(b)
			self.Iranges.append(Irange(a.left, b.right, self.hexFmt))
		
		self.normalize()

	def remove(self, left, right):
		if right <= left: return

		newRange = Irange(left, right, self.hexFmt)

		self.Iranges = filter(lambda x: x not in newRange, self.Iranges)

		a = filter(lambda ir: left in ir, self.Iranges)
		b = filter(lambda ir: right in ir, self.Iranges)
		assert(not a or len(a)==1)
		assert(not b or len(b)==1)
		if(a): a = a[0]
		if(b): b = b[0]

		if a: 
			self.Iranges.remove(a)
			assert(a.left <= left)
			if a.left != left:
				self.Iranges.append(Irange(a.left, left, self.hexFmt))

		if b:
			if b != a:
				self.Iranges.remove(b)
			assert(right <= b.right)
			if right != b.right:
				self.Iranges.append(Irange(right, b.right, self.hexFmt))

		self.normalize()

	def asList(self):
		result = []
		for ir in self.Iranges:
			result += list(range(ir.left, ir.right))
		return result

	def __len__(self):
		return len(self.Iranges)

	def __str__(self):
		substrs = []
		for ir in self.Iranges:
			substrs.append(str(ir))
		return ' '.join(substrs)

if __name__ == '__main__':
	for testIdx in range(1000000):
		print "generating random list"
		myMgr = IrangeManager()
		mySet = set()
		for rIdx in range(10):
			(a,b) = (None,None)
			a = random.randint(1,99)
			b = -1
			while b<1 or b>99:	
				b = a + random.randint(-12,12)

			if random.randint(0,1):
				print "adding [%d,%d)" % (a,b)
				myMgr.add(a,b)
				mySet = mySet.union(set(range(a,b)))
			else:
				print "removing [%d,%d)" % (a,b)
				myMgr.remove(a,b)
				mySet = mySet.difference(set(range(a,b)))

		myMgr = myMgr.asList()
		mySet = sorted(list(mySet))
		
		print "myMgr: ", myMgr
		print "mySet: ", mySet

		if myMgr == mySet:
			print "PASS %d" % testIdx
		else:
			print "FAIL"
			assert(False)
				
