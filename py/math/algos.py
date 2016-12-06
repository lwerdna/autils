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

# digit-by-digit (base 2) integer square root algorithm
# (since python math.sqrt() converts to float)
# returns y = f(x) s.t. y^2 < x and no z>y exists with the same property
def LongSqrt(x):
	root = 0
	res = 0	

	# position '11' mask
	mask = 3
	shift = 0
	while mask < x:
		mask <<= 2
		shift += 2 

	while shift >= 0:
		# get pair of bits
		c = (x & mask) >> shift
		# update remainder
		res = (res << 2) | c

		# append root
		prod = (root<<2) + 1

		root <<= 1
		if prod <= res:
			root |= 1
			res -= prod

		# continue
		mask >>= 2
		shift -= 2

	return root

# Pollard's rho algorithm for discrete logarithms
# calculate x in g^x = y within group G = <g>
#
# [notes]
#  - cycle detection: Floyd (one walks 2x speed as the other)
#  - random walk: the original 3-partition one

# given e = g^a * y^b, return a stepped e and calculate
# adjusted a, b to keep track of the expression
def DilogPollardRhoStep(e, g, y, a, b, order):
	bucket = e.bucketize(3)

	# elements in bucket 0 are multiplied by y
	if bucket == 0:   
		return [y.groupAction(e), a, ZZn(b+1, order).lift()]
	# elements in bucket 1 are squared
	if bucket == 1:
		return [e.groupAction(e), ZZn(2*a, order).lift(), ZZn(2*b, order).lift()]
	# elements in bucket 2 are multiplied by g
	return [g.groupAction(e), ZZn(a+1, order).lift(), b] 
 
def DilogPollardRho(g, y, init_a=1, init_b=1):
	order = g.order()
	#print "g's order is: ", order
	
	# we keep track of search
	# the tortoise = g^a * y^b
	(tortoise, tortoise_a, tortoise_b) = (g**init_a * y**init_b, init_a, init_b)
	# the hare
	(hare, hare_a, hare_b) = (tortoise, init_a, init_b)

	itera = 0

	while 1:
		# tortoise takes one step
		(tortoise, tortoise_a, tortoise_b) = \
			DilogPollardRhoStep(tortoise, g, y, tortoise_a, tortoise_b, order)

		# hare takes two steps
		(hare, hare_a, hare_b) = \
			DilogPollardRhoStep(hare, g, y, hare_a, hare_b, order)
		(hare, hare_a, hare_b) = \
			DilogPollardRhoStep(hare, g, y, hare_a, hare_b, order)

		print "iter:%d (a,b,A,B)=(%d,%d,%d,%d)" % (itera, tortoise_a, tortoise_b, hare_a, hare_b)
		itera += 1

		# they match! we looped at some point!	  
		if tortoise == hare:
			# tortoise = g^a * y^b
			# hare = g^A * y^B
			# equating, we have:
			# g^a * y^b = g^A * y^B
			# if the dilog exists, then y = g^x, so we substitute:
			# g^a * (g^x)^b = g^A * (g^x)^B
			# g^a * g^(bx) = g^A * g^(Bx)
			# g^(a+bx) = g^(A+Bx)
			# a+bx = A+Bx (mod ord(G))  
			# (b-B)x = A-a
			# x = (b-B)/(A-a)

			if tortoise_b == hare_b:
				raise ValueError("invalid b, B found")
			if tortoise_a == hare_a:
				raise ValueError("invalid a, A found")

			# danger, danger
			if hare_a / (1.0 * tortoise_a) == hare_b / (1.0 * tortoise_b):
				print "trival solution found - elements along walk are just multiples of one another"
				(init_a, init_b) = (random.randrange(1, order), random.randrange(1, order))
				(tortoise, tortoise_a, tortoise_b) = (g**init_a * y**init_b, init_a, init_b)
				(hare, hare_a, hare_b) = (g**init_a * y**init_b, init_a, init_b)
				continue 

			factors = Factor(order)
			print "solving equations over factors: ", factors

			# collect the equations
			mods = []
			for f in factors:
				numerator = ZZn(tortoise_b - hare_b, f)
				denominator = ZZn(hare_a - tortoise_a, f)
				print "adding to equations: %d/%d (mod %d)" % (numerator.elem, denominator.elem, f) 
				mods.append(numerator / denominator)

			# combine equations
			print "sending ", mods
			result = ChineseRemainderTheorem(mods)
			print result

#
# [input]
#  - two ZZn
# [notes]
#  - modulii are expected coprime
def ChineseRemainderTheoremPair(a1, a2):
	n1 = a1.modulus
	n2 = a2.modulus
	n1_inv_n2 = InverseMod(n1, n2)
	n2_inv_n1 = InverseMod(n2, n1)
	#print "returning ZZn(%d*%d + %d*%d, %d)" % (a1.elem, n2_inv_n1, a2.elem, n1_inv_n2, n1*n2)
	return ZZn(a1.elem * n2 * n2_inv_n1 + a2.elem * n1 * n1_inv_n2, n1*n2)

#
# [input]
#  - list of ZZn's to combine
def ChineseRemainderTheorem(l):
	answer = l.pop(0)
	while l:
		answer = ChineseRemainderTheoremPair(answer, l.pop(0))
	return answer

# Exponentiation by Squaring
# calculating b^e
# suppose e=1+2^3+2^8
# -> b^e = b^1 * b^(2^3) * b^(2^8)
# other bases would work, but e is already represented internally as base 2
#
# b can be a normal python integer, or a FieldE (field element)
# e is a normal python integer (required! else integer divison won't work)
def ExponentiationBySquaring(b, e):
	result = 1 if type(b)==type(0) else b.one()
	runner = b

	while e:
		if e & 1:
			#print "result: ", result
			#print "runner: ", runner
			result = result * runner

		# track b^(next power)
		runner = runner * runner
			
		# consider next set bit
		e = e/2

	return result

# same, but for repeated "add" operator, calculate b*e, e \in Z
def MultiplicationByDoubling(b, e):
	result = b.zero()  
	runner = b

	while e:
		if e & 1:
			result = result + runner

		# track (next double)*b
		runner = runner + runner

		# next bit
		e = e/2

	return result

# eXtended Euclidean algorithm
# given x,y yields (a,b,gcd(x,y)) s.t. ax + by = gcd(x,y)
#
# obviously gcd(x,y)|x and gcd(x,y)|y
# it's easy to see that gcd(x-y) must also divide the gap |x-y|
# algorithm essentially reduces and reduces self gap, tracking also how much
# each of x and y are used to form the smallest gap
#
def ExtendedEuclidean(x, y):
	if x-y == x:
		return [1, 0, 1]
	if y-x == y:
		return [0, 1, 1]

	# initially x = (1)x + (0)y
	ax,bx = 1, 0
	# initially y = (0)x + (1)y
	ay,by = 0, 1

	# position largest elem in x
	if x<y:
		x,ax,bx,y,ay,by = y,ay,by,x,ax,bx

	while 1:
		times = x/y

		x = x - times*y
		ax = ax - times*ay
		bx = bx - times*by

		if x==0:
			break;

		# position largest elem in x
		x,ax,bx,y,ay,by = y,ay,by,x,ax,bx
   
	return [ay, by, y]	 

def InverseMod(x, p):
	xgcd = ExtendedEuclidean(x, p)
	if xgcd[2] != 1:
		raise ValueError("x is not in Z_p (%d is not in Z_%d)" % (x, p))
	if(xgcd[0] > 0):
		return xgcd[0]
	return xgcd[0] + p

