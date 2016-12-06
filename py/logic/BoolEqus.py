#!/usr/bin/python
#------------------------------------------------------------------------------
#
#	This file is a part of autils.
#
#	Copyright 2011-2016 Andrew Lamoureux
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

###############################################################################
# Boolean Formulas
###############################################################################

def PicosatPipeSolve(expr):
	p = subprocess.Popen('picosat', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	
	# p cnf <NUMBER OF VARIABLES> <NUMBER OF CLAUSES>
	print "collecting var names on: ", expr
	mapVarInd = expr.collectVarNames()
	mapIndVar = {}

	varsN = len(mapVarInd)
	clausesN = len(expr.subexprs)  
 
	# create a mapping from varname -> index
	for i,v in enumerate(sorted(mapVarInd.keys())):
		# the format is 1-indexed
		mapVarInd[v] = i+1
		mapIndVar[i+1] = v
	print mapVarInd
	print mapIndVar
	
	t = 'p cnf %d %d\n' % (varsN, clausesN)
	print t,
	p.stdin.write(t)

	# enter each clause
	for se in expr.subexprs:
		# enter each [not]literal
		if isinstance(se, BoolDisj):
			for sse in se.subexprs:
				neg = ''
				name = ''
				if isinstance(sse, BoolNot):
					neg = '-'
					name = sse.subexprs[0].name
				else:
					name = sse.name
	
				t = '%s%s ' % (neg, mapVarInd[name])
				print t,
				p.stdin.write(t)
		elif isinstance(se, BoolNot):
			t = '-%s ' % mapVarInd[se.subexprs[0].name]
			print t,
			p.stdin.write(t)
		elif isinstance(se, BoolLit):
			t = '%s ' % mapVarInd[se.name]
			print t,
			p.stdin.write(t)
		else:
			raise ValueError("wtf? in pipe solver")

		t = '0\n'
		print t,
		p.stdin.write(t)

	# close the pipe, ending input
	p.stdin.close()

	print "output:"

	# read from input now
	line1 = p.stdout.readline()
	print line1,
	if not re.match(r'^s SATISFIABLE', line1):
		return {}
   
	# parse out all the variables from here... 
	result = {}

	while 1:
		line2 = p.stdout.readline()
		print line2,

		if not line2:
			break

		# get rid of the 'v '
		m = re.match(r'^(v +)', line2)
		if not m:
			return {}

		line2 = string.replace(line2, m.group(1), '', 1)
		print "line (r'^v ' removed): %s" % line2

		# parse every int in this line
		while 1:
			m = re.match('^( *[+-]?\d+ *)', line2)
			if not m:
				break;

			index = int(m.group(1))
			if index == 0:
				print "got end-of-list index"
				break

			value = 1
			if index<0:
				value = 0
				index *= -1

			result[mapIndVar[index]] = value
	   
			line2 = string.replace(line2, m.group(1), '', 1)

	# close
	p.stdout.close()

	#
	return result

# boolean system is a collection of boolean equations
class BoolSystem:
	def __init__(self, n):
		self.equs = [BoolEquation() for i in range(n)]

	def copy(self):
		bs = BoolSystem(len(self.equs))
		bs.equs = map(lambda x: x.copy(), self.equs)
		return bs

	def fromExprs(self, exprs):
		self.equs = [BoolEquation() for i in range(len(exprs))]
		for i in range(len(exprs)):
			self.equs.expr = exprs[i].copy()

	def loadTargetsFromArray(self, arr):
		if len(arr) > len(self.equs):
			raise ValueError("setting target of more equations than exist")

		for i,t in enumerate(arr):
			# some array slots can be "None" to mean no effect
			if t:
				self.equs[i].target = t

	def loadTargetsFromBits(self, n, mask):
		arr = []
		for i in range(n):
			arr.append(mask & 1)
			mask >>= 1

		self.loadTargetsFromArray(arr)		

	def loadEqus(self, arr):
		if len(arr) > len(self.equs):
			raise ValueError("setting equations for more equations than exist")

		for i,t in enumerate(arr):
			# some array slots can be "None" to mean no effect
			if t:
				self.equs[i].target = t

	def satSolve(self):
		# collect all Tseitin versions of equations
		cnf = BoolConst(1)

		lastName = ['gate0']

		# then collect all the per-equation cnf forms together into one cnf
		for i,equ in enumerate(self.equs):
			temp = equ.expr.TseitinTransformTargetting(equ.target, lastName).simplify()
			print "in equation %d, got: %s" % (i, temp)
			cnf = (cnf * temp).simplify()

		print "combined: ", cnf
		result = PicosatPipeSolve(cnf)

		print result

		# filter out the gate entires
		result = dict((k,v) for k,v in result.iteritems() if not re.match(r'^gate', k))

		print result

		for k in sorted(result):
			print "%s: %d" % (k, result[k])

		# print it as a hex 
		# collect all varnames
		varnames = {}
		for x in result:
			m = re.match(r'^(.*?)\d+$', x)
			if m:
				varnames[m.group(1)] = 1

		print "found varnames", varnames

		# for each varname, try to get the bits
		for vn in varnames:
			val = 0
			for i in range(len(result)):
				vnb = "%s%d" % (vn, i)
				if vnb in result:
					val = val | (result[vnb] << i)
				else:
					break

			print "%s: 0x%X" % (vn, val)

	def toCNF(self):
		for i,equ in enumerate(self.equs):
			self.equs[i] = equ.toCNF()

		return self

	def simplify(self):
		for i,equ in enumerate(self.equs):
			self.equs[i] = equ.simplify()

	def assign(self, varname, varvalue):
		for i,equ in enumerate(self.equs):
			self.equs[i] = equ.assign(varname, varvalue)

	# assign
	def assignBits(self, n, varname, bits):
		for i in range(n):
			self.assign("%s%d" % (varname, i), bits & 1)
			bits >>= 1

	# add stuff
	#
	def adder(self, exprs, cin=0):
		if not cin:
			cin = BoolConst(0)
		else:
			cin = BoolConst(1)

		for i,ex in enumerate(exprs): 
			a = self.equs[i].expr
			b = ex

			s = a ^ b ^ cin
			s = s.simplify()
			# lol,
			s = s.simplify()

			cin = (cin * (a^b)) + (a * b)
			cin = cin.simplify()

			self.equs[i].expr = s

	# given 8, 'a' adds to system a7,a6,...,a0 to 
	def bitAddVar(self, n, varname, where=0):
		self.adder(map(lambda x:BoolParser("%s%d" % (varname, x)), range(n)))

	# given 8, 0xA5 adds to system 10100101
	def bitAddVal(self, n, val):
		exprs = []
		for i in range(n):
			exprs.append(BoolParser("%d" % (val&1)))
			val >>= 1
		self.adder(exprs)

	# sub stuff
	#
	def subtracter(self, exprs):
		# complement all the expressions of the bits
		for i,ex in enumerate(exprs):
			exprs[i] = ex.complement()

		# attach adder with initial carry input = 1 (so 2's complemented it)
		self.adder(exprs, 1)

	# given 8, 'a' adds to system a7,a6,...,a0
	def bitSubVar(self, n, varname):
		self.subtracter(map(lambda x:BoolParser("%s%d" % (varname, x)), range(n)))

	# given 8, 0xA5 adds to system 10100101
	def bitSubVal(self, n, val):
		exprs = []
		for i in range(n):
			exprs.append(BoolParser("%d" % (val&1)))
			val >>= 1
		self.subtracter(exprs)

	# xor stuff
	#
	def xorer(self, exprs):
		print "incoming exprs: ", exprs
		for i,ex in enumerate(exprs):
			self.equs[i].expr = BoolXor([self.equs[i].expr, ex])

	def bitXorVar(self, n, varname):
		self.xorer(map(lambda x:BoolParser("%s%d" % (varname, x)), range(n)))

	def bitXorVal(self, n, val):
		exprs = []
		for i in range(n):
			exprs.append(BoolParser("%d" % (val&1)))
			val >>= 1
		print exprs
		self.xorer(exprs)
   
	# rotate stuff
	#
 
	# set each bit equal to a variable
	def bitEquVar(self, n, varname):
		for i in range(n):
			self.equs[i].expr = BoolParser("%s%d" % (varname, i))	

	def bitEquVal(self, n, v):
		for i in range(n):
			self.equs[i].expr = BoolParser("%d" % (v & 1))
			v = v >> 1

	# complement the first n equations
	def complement(self, n=0):
		if not n:
			n = len(self.equs)

		for i,equ in enumerate(self.equs[0:n]):
			self.equs[i] = equ.complement()

	def __add__(self, bs):
		a = self.copy()
		b = bs.copy()
		a.equs = a.equs + bs.equs
		return a

	def __getitem__(self, i):
		return self.equs[i]

	def __str__(self):
		rv = ''
		for equ in self.equs:
			rv += str(equ)
			rv += "\n"
		return rv

# boolean equation is an <expr> = <target>
class BoolEquation:
	# you can send it shit like "1=(a+/b) + (c*d*e*f)"
	def __init__(self, string=None):
		self.target = 0
		self.expr = None
		if string:
			m = re.match(r'^([01])=(.*)$', string)
			if not m:
				raise ValueError("invalid boolean equation: %s" % string)
			self.target = int(m.group(1))
			self.expr = BoolParser(m.group(2))
 
#	def __init__(self, expr, target):
#		self.expr = expr
#		self.target = target

	def copy(self):
		rv = BoolEquation()
		rv.target = self.target
		rv.expr = self.expr.copy()
		return rv

	def flatten(self):
		rv = self.copy()
		rv.expr =  rv.expr.flatten() 
		return rv

	def simplify(self):
		self.expr = self.expr.simplify()
		return self

	def isCNF(self):
		if isinstance(self.expr, BoolConj) and self.expr.isCNF():
			return True
		return False

	def complement(self):
		rv = BoolEquation()
		rv.target = self.target ^ 1
		rv.expr = self.expr.complement()
		return rv

	def distribute(self):
		rv = self.copy()
		rv.expr = rv.expr.distribute()
		return rv

	def assign(self, varname, varvalue):
		rv = self.copy()
		rv.expr = rv.expr.assign(varname, varvalue)
		return rv

	def countOps(self):
		return self.expr.countOps()

	# convert to conjunctive normal form
	# usual action is to flatten then complement
	def toCNF(self):
		temp = self.copy()

		if temp.target == 0:
			print "target is 0, going for the single shot..."
			temp = temp.flatten()
			temp = temp.complement()

		print "testing if in CNF..."
		if not temp.isCNF():
			print "nope, doing double flatten/complement..."
			temp = temp.flatten()
			temp = temp.complement()
			temp = temp.flatten()
			temp = temp.complement()

		if temp.isCNF():
			print "succeeded!"
		else:
			print "failed! :("
		
		return temp

	def dimacs(self):
		toCNF()

		#print "p cnf %d %d" % (

	def __str__(self):
		return '%d=%s' % (self.target, str(self.expr))



#------------------------------------------------------------------------------
# boolean expression class
#------------------------------------------------------------------------------

class BoolExpr:
	def __init__(self):
		self.subexprs = []

	def __mul__(self, rhs):
		if not rhs:
			return self
		if type(rhs) == type("string"):
			rhs = BoolParser(rhs)
		elif isinstance(rhs, BoolLit):
			rhs = rhs.copy()
		return BoolConj([rhs, self])

	def __add__(self, rhs):
		if not rhs:
			return self
		if type(rhs) == type("string"):
			rhs = BoolParser(rhs)
		elif isinstance(rhs, BoolLit):
			rhs = rhs.copy()
		return BoolDisj([self, rhs])

	def __xor__(self, rhs):
		if not rhs:
			return self
		if type(rhs) == type("string"):
			rhs = BoolParser(rhs)
		elif isinstance(rhs, BoolLit):
			rhs = rhs.copy()
		return BoolXor([self.copy(), rhs.copy()])
		#return BoolDisj([ \
		#		BoolConj([self, rhs.complement()]), \
		#		BoolConj([self.complement(), rhs]) \
		#	])

	def complement(self):
		return BoolNot(self.copy())

	def __invert__(self):
		return self.complement() 

	def isLeafOp(self):
		for se in self.subexprs:
			if not isinstance(se, BoolLit):
				return False

		return True

	def collectVarNames(self):
		answer = {}
		# terminal case is for BoolLits who override this method
		for se in self.subexprs:
			answer.update(se.collectVarNames())
		return answer

	def flatten(self):
		temp = self.copy()
		currops = temp.countOps()
		while 1:
			print "currops: ", currops
			temp = temp.distribute()
			temp = temp.simplify()
			c = temp.countOps()
			print " newops: ", c
			if c == currops:
				break
			else:
				currops = c
		return temp
 
	def distribute(self):
		return self
	def simplify(self, recur=0):
		return self

	# count the number of operator nodes		
	# bool lit must override this to always return 0
	def countOps(self):
		rv = 1

		for se in self.subexprs:
			rv += se.countOps()

		return rv

	def TseitinTransformGenName(self, lastName):
		m = re.match('^gate([a-fA-F0-9]+)$', lastName[0])
		ind = int(m.group(1),16)
		newName = "gate%X" % (ind+1)
		lastName[0] = newName

		#print "%s generated inside a %s" % (newName, self.__class__)
		return newName 

	# compute the Tseitin transformation of this gate
	# returns a 2-tuple [gateName, subExpr]
	def TseitinTransform(self, lastName=['gate0']):
		temp = self.copy().simplify()

		c_name = ''
		gates = []

		# each of the subgates must operate correctly
		#
		cnf = BoolConst(1)

		tcnfs = map(lambda x: x.TseitinTransform(lastName), temp.subexprs)
		for tcnf in tcnfs:
			[name, x] = tcnf
			gates.append(name)
			cnf = (cnf * x).simplify()	

		# now operate on this gate using output of subgates
		# 
		print gates
		while len(gates) >= 2:
			a = BoolLit(gates.pop(0))
			b = BoolLit(gates.pop(0))
			cName = self.TseitinTransformGenName(lastName)
			c = BoolLit(cName)

			if isinstance(self, BoolDisj):
				# c=a+b is true when (/c+b+a) * (c+/b) * (c*/a) is true
				cnf = (cnf * (c.complement()+b+a) * (c+b.complement()) * (c+a.complement())).simplify()
			elif isinstance(self, BoolConj):
				# c=(a*b) is true when (c+/b+/a)(/c+b)(/c+a) is true
				cnf = (cnf * (c + a.complement() + b.complement()) * (c.complement()+b) * (c.complement()+a)).simplify()
			elif isinstance(self, BoolXor):
				# c=(a*b) is true when (/b+/c+/a)*(a+/c+b)*(a+c+/b)*(b+c+/a) is true
				cnf = (cnf * (b.complement() + c.complement() + a.complement()) * (a + c.complement() + b) * \
						(a + c + b.complement()) * (b + c + a.complement())).simplify()
			else:
				raise Exception("unknown gate!")

			gates.append(cName)

		# now the final guy
		return [gates[0], cnf.simplify()]

	def TseitinTransformTargetting(self, target, lastName=['gate0']):
		[tName, tExpr] = self.TseitinTransform(lastName)

		if target == 0:
			return (tExpr * BoolNot(BoolLit(tName))).simplify()
		else:
			return (tExpr * BoolLit(tName)).simplify()
			
	# this is overridden by BoolLit 
	def evaluate(self):
		return None

	# this is overridden by BoolLit to actually assign the value when name matches
	def assign(self, name, value):
		temp = self.copy()
		for i,se in enumerate(temp.subexprs):
			temp.subexprs[i] = se.assign(name, value)
		return temp

	# to valuate - assign all variables and see what comes out
	def valuate(self, values):
		temp = self.copy()
		for varname in values.keys():
			temp = temp.assign(varname, values[varname])
		temp = temp.simplify()
		return temp

	def __repr__(self):
		return str(self)

class BoolDisj(BoolExpr):
	def __init__(self, subexprs):
		self.subexprs = list(subexprs)

	def copy(self):
		temp = list(self.subexprs)
		for i,se in enumerate(temp):
			temp[i] = se.copy()
		return BoolDisj(temp)

	def distribute(self):
		copy = self.copy()

		temp = list(copy.subexprs)
		for i,se in enumerate(copy.subexprs):
			copy.subexprs[i] = se.distribute()

		if len(copy.subexprs)==1:
			return copy.subexprs[0]

		return copy

	def simplify(self, recur=1):
		copy = self.copy()

		if recur:
			for i,se in enumerate(copy.subexprs):
				copy.subexprs[i] = se.simplify(recur)

		# lift any or subexpressions into this one
		temp = list(copy.subexprs)
		for se in temp:
			#print "considering: ", se
			if isinstance(se, BoolDisj):
				#print "bringing junk up from: ", se

				for sse in se.subexprs:
					copy.subexprs.append(sse)
				copy.subexprs.remove(se)

		# if any subexpression evaluate to 1, this whole expression is true
		if filter(lambda x: isinstance(x, BoolConst) and x.value == 1, copy.subexprs):
			return BoolConst(1)

		# remove any subexpressions that equate to 0
		for x in filter(lambda x: x.evaluate() == 0, copy.subexprs):
			copy.subexprs.remove(x)

			# if, during this process, all expressions were removed, then this disjunction is false
			if not copy.subexprs:
				return BoolConst(0)

		# do some simple simplifications
		if self.isLeafOp():
			# if any two literals are complements of one another, this whole expression is true
			for i in range(len(copy.subexprs)):
				for j in range(len(copy.subexprs)):
					if j!=i and copy.subexprs[i] == ~(copy.subexprs[j]):
						return BoolConst(1)
			
			# if any boolit appears twice, remove the redundent one
			while 1:
				restart = 0
				for i in range(len(copy.subexprs)):
					for j in range(len(copy.subexprs)):
						if j!=i and copy.subexprs[i] == copy.subexprs[j]:
							copy.subexprs.pop(j)
							restart = 1
							break

					if restart:
						break
				if not restart:
					break
  
		# if only one subexpr, return us up
		if len(copy.subexprs) == 1:
			return copy.subexprs[0]

		return copy

	def isCNF(self):
		# or subexpressions are in CNF if they're at the bottom of the tree
		return self.isLeafOp()		

	# operator overloading
	#
	def __str__(self):
		result = '('

		for se in self.subexprs:
			if result != '(':
				result += ('+')
			result += str(se)

		return result + ')'

	def __eq__(self, rhs):
		if not isinstance(rhs, BoolDisj):
			return False
		if not len(self.subexprs) == len(rhs.subexprs):
			return False
		temp1 = list(self.subexprs)
		temp2 = list(rhs.subexprs)
		for se in temp1:
			if se not in temp2:
				print "%s was not in %s" % (se, temp2)
				return False
			temp1.remove(se)
			temp2.remove(se)
		return True

class BoolConj(BoolExpr):
	def __init__(self, subexprs):
		self.subexprs = list(subexprs)

	def copy(self):
		temp = list(self.subexprs)
		for i,se in enumerate(temp):
			temp[i] = se.copy()
		return BoolConj(temp)

	def simplify(self, recur=1):
		copy = self.copy()

		if recur:
			for i,se in enumerate(copy.subexprs):
				copy.subexprs[i] = se.simplify(recur)

		# "lift" any and subexpressions into this one
		temp = list(copy.subexprs)
		for se in temp:
			if isinstance(se, BoolConj):
				for sse in se.subexprs:
					copy.subexprs.append(sse)
				copy.subexprs.remove(se)

		# if any subexpression evaluate to 0, this whole expression is false
		if filter(lambda x: x.evaluate() == 0, copy.subexprs):
			return BoolConst(0)

		# remove any subexpressions that equate to 1
		for x in filter(lambda x: x.evaluate() == 1, copy.subexprs):
			copy.subexprs.remove(x)

			# if during this process, all expressions were removed, then result is true
			if not copy.subexprs:
				return BoolConst(1)

		# do some simple simplifications
		if self.isLeafOp():
			# if any two literals are complements of one another, this whole expression is false
			for i in range(len(copy.subexprs)):
				for j in range(len(copy.subexprs)):
					if j!=i and copy.subexprs[i] == (~(copy.subexprs[j])).simplify(0):
						return BoolConst(0)
			
			# if any boolit appears twice, remove the redundent one
			while 1:
				restart = 0
				for i in range(len(copy.subexprs)):
					for j in range(len(copy.subexprs)):
						if j!=i and copy.subexprs[i] == copy.subexprs[j]:
							copy.subexprs.pop(j)
							restart = 1
							break

					if restart:
						break
				if not restart:
					break

		# if only one subexpression remains, move it up
		if len(copy.subexprs) == 1:
			return copy.subexprs[0]

		return copy

	def distribute(self):
		copy = self.copy()

		temp = list(copy.subexprs)
		for i,se in enumerate(copy.subexprs):
			copy.subexprs[i] = se.distribute()

		# only work hard if there are disjunctions
		while 1:
			if not filter(lambda x: isinstance(x, BoolDisj), copy.subexprs):
				break

			if len(copy.subexprs) == 1:
				copy = copy.subexprs[0]
				break

			# we do 2-op cartesian products at a time
			disj = None
			other = None
			for se in copy.subexprs:
				if isinstance(se, BoolDisj):
					if disj == None:
						disj = se

				if se != disj and other==None:
					other = se

				if disj and other:
					break

			#print copy.subexprs

			# remove them
			copy.subexprs.remove(disj)
			copy.subexprs.remove(other)
		  
			pargs = [[other], disj.subexprs]
			products = map(lambda x:list(x), list(itertools.product(*pargs)))
			newse = map(lambda x:BoolConj(x), products)

			# and of or's
			newguy = BoolDisj(newse)
			copy.subexprs.append(newguy)

			#print "converted: ", disj
			#print "	  and: ", other
			#print "	   to: ", newguy
			#print "   result: ", copy
			#print "----------"
		#print result
		return copy

	def isCNF(self):
		# and subexpressions are cnf if all children are disjunctions that are cnf
		for se in self.subexprs:
			if isinstance(se, BoolDisj):
				if not se.isLeafOp():
					return False
			else:
				if not isinstance(se, BoolLit):
					return False

		return True

	def __eq__(self, rhs):
		if not isinstance(rhs, BoolConj):
			return False
		if len(self.subexprs) != len(rhs.subexprs):
			return False
		temp1 = list(self.subexprs)
		temp2 = list(rhs.subexprs)
		for se in temp1:
			if se not in temp2:
				return False
			temp1.remove(se)
			temp2.remove(se)
		return True

	def __str__(self):
		result = '('

		for se in self.subexprs:
			if result != '(':
				result += '*'
			result += str(se)

		return result + ')'

class BoolXor(BoolExpr):
	def __init__(self, subexprs):
		self.subexprs = list(subexprs)

	def copy(self):
		temp = list(self.subexprs)
		for i,se in enumerate(temp):
			temp[i] = se.copy()
		return BoolXor(temp)

	def simplify(self, recur=1):
		copy = self.copy()

		if recur:
			for i,se in enumerate(copy.subexprs):
				copy.subexprs[i] = se.simplify(recur)

		# add all literals % 2, then complement one remaining subexpr if necessary
		constants = filter(lambda x: isinstance(x, BoolConst), copy.subexprs)

		if not constants:
			return copy

		val = 0
		for c in constants:
			copy.subexprs.remove(c)
			val = (val + c.value) % 2

		# if everything was a constant, return the result
		if not copy.subexprs:
			return BoolConst(val)

		# else, if the constants effectively complement a subexpression, do that
		if val:
			copy.subexprs[0] = copy.subexprs[0].complement()

		# finally, if one subexpression is remaining, return it
		if len(copy.subexprs) == 1:
			return copy.subexprs[0]

		# otherwise, return a reduced xor gate
		return copy

	def distribute(self):
		return self.copy()

	def isCNF(self):
		# xor's not allowed in CNF
		return False

	def __eq__(self, rhs):
		if not isinstance(rhs, BoolXor):
			return False
		if len(self.subexprs) != len(rhs.subexprs):
			return False
		temp1 = list(self.subexprs)
		temp2 = list(rhs.subexprs)
		for se in temp1:
			if se not in temp2:
				return False
			temp1.remove(se)
			temp2.remove(se)
		return True

	def __str__(self):
		result = '('

		for se in self.subexprs:
			if result != '(':
				result += '^'
			result += str(se)

		return result + ')'

class BoolNot(BoolExpr):
	def __init__(self, subexpr):
		self.subexprs = [subexpr]

	def copy(self):
		return BoolNot(self.subexprs[0].copy())

	def simplify(self, recur=1):
		temp = self.copy()

		if recur:
			temp.subexprs[0] = temp.subexprs[0].simplify()

		if isinstance(temp.subexprs[0], BoolNot):
			return temp.subexprs[0].subexprs[0]

		if isinstance(temp.subexprs[0], BoolConst):
			return temp.subexprs[0].complement()
	
		return temp

	def TseitinTransform(self, lastName=['gate0']):
		temp = self.copy()

		[aName, aCnf] = temp.subexprs[0].TseitinTransform(lastName)
		cName = self.TseitinTransformGenName(lastName)

		a = BoolLit(aName)
		c = BoolLit(cName)

		# c=/a is true when (/c+/a)*(a+c) is true
		cCnf = (c.complement() + a.complement()) * (c + a)

		return [cName, (cCnf * aCnf).simplify()]

	def __eq__ (self, rhs):
		return isinstance(rhs, BoolNot) and \
			self.subexprs[0] == rhs.subexprs[0]

	def __str__(self):
		return '/' + str(self.subexprs[0])

class BoolLit(BoolExpr):
	def __init__(self, name):
		self.name = name
		self.subexprs = [self]

	def copy(self):
		return BoolLit(self.name)

	def assign(self, name, value):
		if name == self.name:
			return BoolConst(value)
		else:
			return self

	def TseitinTransform(self, lastName=['gate0']):
		# we consider a literal's gate as a "buffer" which is always true
		return [self.name, BoolConst(1)]

	# these are some bottom-of-tree special overrides of BoolExpr
	#
	def countOps(self):
		return 0

	def collectVarNames(self):
		return {self.name:1}

	# operator overloading
	#
	def __eq__(self, rhs):
		return isinstance(rhs, BoolLit) and \
			self.name == rhs.name and self.value == rhs.value

	def __str__(self):
		return self.name

class BoolConst(BoolExpr):
	def __init__(self, value):
		self.value = value

	def copy(self):
		return BoolConst(self.value)

	def evaluate(self):
		return self.value

	def complement(self):
		return BoolConst(self.value ^ 1)

	def TseitinTransform(self, lastName):
		raise NotImplemented("simplify away this constant, first")

	def __eq__(self, rhs):
		return isinstance(rhs, BoolConst) and self.value == rhs.value

	def __str__(self):
		return '%d' % self.value

