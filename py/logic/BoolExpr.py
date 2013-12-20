#!/usr/bin/python
#------------------------------------------------------------------------------
#
#    This file is a part of alib.
#
#    Copyright 2011-2013 Andrew Lamoureux
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

# idea is to represent a boolean expression as a hierarchy, a tree
#
# contains abstract BoolExpr
#
# and implementing:
# BoolDisj
# BoolConj 
# BoolXor 
# BoolNot 
# BoolVar 
# BoolConst
#
# operations like evaluation, or performing the Tseitin transformation are to be
# in a tree like fashion (perhaps descending to find values, etc.)

class BoolExpr:
    def __init__(self):
        self.subexprs = []

    # can multiply (and) this expression with another (return parent and gate)
    def __mul__(self, rhs):
        if not rhs:
            return self
        if type(rhs) == type("string"):
            rhs = BoolParser(rhs)
        elif isinstance(rhs, BoolVar):
            rhs = rhs.copy()
        return BoolConj([rhs, self])

    # can add (or) the expression with another (return parent or gate)
    def __add__(self, rhs):
        if not rhs:
            return self
        if type(rhs) == type("string"):
            rhs = BoolParser(rhs)
        elif isinstance(rhs, BoolVar):
            rhs = rhs.copy()
        return BoolDisj([self, rhs])

    #
    def __xor__(self, rhs):
        if not rhs:
            return self
        if type(rhs) == type("string"):
            rhs = BoolParser(rhs)
        elif isinstance(rhs, BoolVar):
            rhs = rhs.copy()
        return BoolXor([self.copy(), rhs.copy()])
        #return BoolDisj([ \
        #        BoolConj([self, rhs.complement()]), \
        #        BoolConj([self.complement(), rhs]) \
        #    ])

    def complement(self):
        return BoolNot(self.copy())

    def __invert__(self):
        return self.complement() 

    def isLeafOp(self):
        for se in self.subexprs:
            if not isinstance(se, BoolVar):
                return False

        return True

    def collectVarNames(self):
        answer = {}
        # terminal case is for BoolVars who override this method
        for se in self.subexprs:
            answer.update(se.collectVarNames())
        return answer

    def flatten(self):
        temp = self.copy()
        currops = temp.countOps()
        while 1:
            #print "currops: ", currops
            temp = temp.distribute()
            temp = temp.simplify()
            c = temp.countOps()
            #print " newops: ", c
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
            a = BoolVar(gates.pop(0))
            b = BoolVar(gates.pop(0))
            cName = self.TseitinTransformGenName(lastName)
            c = BoolVar(cName)

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
            return (tExpr * BoolNot(BoolVar(tName))).simplify()
        else:
            return (tExpr * BoolVar(tName)).simplify()
            
    # this is overridden by all
    # first call assign()
    def evaluate(self):
        return NotImplementedError("evaluate");

    # this descends out to all branches
    # and is overridden by BoolVar at the leaves to actually assign the value when name matches
    def assign(self, name, value):
        temp = self.copy()
        for i,se in enumerate(temp.subexprs):
            temp.subexprs[i] = se.assign(name, value)
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

    def evaluate(self):
        # as an OR gate, return true when ANY subexpression is true
        for se in self.subexprs:
            if se.evaluate():
                return True

        return False

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
            #print "      and: ", other
            #print "       to: ", newguy
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
                if not isinstance(se, BoolVar):
                    return False

        return True

    def evaluate(self):
        # as an AND gate, return true only when EVERY subexpr is true
        for se in self.subexprs:
            if not se.evaluate():
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

    def evaluate(self):
        # as an XOR gate, turn true when only one subexpr is true
        total = 0;

        for se in self.subexprs:
            if se.evaluate():
                total += 1

                if total > 1:
                    return False

            if total == 1:
                return True

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
        if len(subexprs) != 1:
            raise ValueError("BoolNot is a single-input gate")

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

        a = BoolVar(aName)
        c = BoolVar(cName)

        # c=/a is true when (/c+/a)*(a+c) is true
        cCnf = (c.complement() + a.complement()) * (c + a)

        return [cName, (cCnf * aCnf).simplify()]

    def evaluate(self):
        return not self.subexpr.evaluate()

    def __eq__ (self, rhs):
        return isinstance(rhs, BoolNot) and \
            self.subexprs[0] == rhs.subexprs[0]

    def __str__(self):
        return '/' + str(self.subexprs[0])

class BoolVar(BoolExpr):
    def __init__(self, name):
        self.name = name
        self.subexprs = [self]
        self.value = None

    def copy(self):
        return BoolVar(self.name)

    def assign(self, name, value):
        if name == self.name:
            self.value = value

    def TseitinTransform(self, lastName=['gate0']):
        # we consider a variables gate as a "buffer" which is always true
        return [self.name, BoolConst(1)]

    # these are some bottom-of-tree special overrides of BoolExpr
    #
    def countOps(self):
        return 0

    def collectVarNames(self):
        return {self.name:1}

    def evaluate(self):
        if self.value == None
        return self.value

    # operator overloading
    #
    def __eq__(self, rhs):
        return isinstance(rhs, BoolVar) and \
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

