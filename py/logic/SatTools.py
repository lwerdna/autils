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

import re
import itertools
import subprocess

import QuineMcCluskey

# expects a CNF input formula
# returns (dimacs, listOfVariables)
# eg:
#   INPUT: (A+B+C)(/A+/B+C)(A+/B+/C)
#   OUTPUT:
#     p cnf 3 3
#     1 3 2 0
#     -1 -3 2 0
#     1 -3 -2 0
#
#   and ['A', 'C', 'B']
def cnfToDimacs(formulaCnf):
    result = ''

    varNames = re.findall(r'[\w\d]+', formulaCnf)
    varNames = list(set(varNames))
    clauses = re.findall(r'\(.*?\)', formulaCnf)
    
    result += 'p cnf %d %d\n' % (len(varNames), len(clauses))

    for clause in clauses:
        terms = re.findall(r'/?[\w\d]+', clause)
        for term in terms:
            if term[0]=='/':
                result += '-'
                term = term[1:]
            # note that dimacs indexes variables based at 1
            result += str(varNames.index(term)+1) + ' '
        result += '0\n'

    return (result, varNames)

# attempts to remove unnecessary parenthesis via passes of regex
#
def filterParenthesis(formula):
    # remove unnecessary whitespace (needed to detect factors)
    formula = re.sub(r'\s', '', formula)

    # loop over simplifications
    while 1:
        #print "input formula: %s" % formula

        oldlen = len(formula)

        # rid parenthesized single-terms
        formula = re.sub(r'\(([/\w\d]+)\)', r'\1', formula)
        # rid parenthesis on product-only clauses
        formula = re.sub(r'\(((?:[/\w\d]+\*)+[/\w\d]+)\)', r'\1', formula)
        
        # release parenthesis around factors
        formula = re.sub(r'\*\(((?:[/\w\d]+\*)+[/\w\d]+)\)',   r'*\1', formula)
        formula = re.sub(  r'\(((?:[/\w\d]+\*)+[/\w\d]+)\*\)', r'\1*', formula)
        
        # release sum parenthesis of subexpression only if not a factor
        # ...+(A+B)X... to ...+A+BX... where X is not '*'
        formula = re.sub(r'\+\(((?:[/\w\d]+\+)+[/\w\d]+)\)([^\*]|$)',   r'+\1\2', formula)
        # ...X(A+B)+...  to ...X(Awhere X is not '*'
        formula = re.sub(r'([^\*]|^)\(((?:[/\w\d]+\+)+[/\w\d]+)\+\)', r'\1\2+', formula)

        # if not change anything, break
        if oldlen == len(formula):
            break
         
    return formula

def parseQmFormula(formula):
    formula = formula.replace(' AND ','*')
    formula = formula.replace(' OR ','+')
    formula = formula.replace('NOT ','/')
    #print "before filtering parenthesis: " + formula
    formula = filterParenthesis(formula)
    return formula

def formulaFromTruthTable(varNames, trueRows):
    ones = []

    for row in trueRows:
        mintermId = int(''.join(map(lambda x:str(x), row)), 2)
        ones.append(mintermId)

    #print varNames
    #print trueRows
    #print ones

    qm = QuineMcCluskey.QM(varNames)
    (complexity, minterms) = qm.solve(ones, [])
    return parseQmFormula(qm.get_function(minterms))

#------------------------------------------------------------------------------
# PROBLEM INSTANCES
#------------------------------------------------------------------------------

# try to put nPigeons into nHoles
#
# pigeonHole(n, m) is unresolvable when n > m
# pigeonHole(n+1, n) is a hard unresolvable problem, good for testing
# how quickly a solver gives up
#
# you can experiment easily with different ways to enforce that no hole
# has more than one pigeons
# 
#
def pigeonHole(nPigeons, nHoles):
    result = ''

    # we make a variable v_{i,j} to indicate pigeon i goes in hole j

    # enforce that pigeon 1 goes into AT LEAST one hole:
    # (x_{1,1} + x_{1,2} + x_{1,3} + ...)
    # enforce that pigeon 2 goes into AT LEAST one hole:
    # (x_{2,1} + x_{2,2} + x_{2,3} + ...)
    # ...etc
    for p in range(nPigeons):
        vars = map(lambda x: "v_%d_%d" % (p, x), range(nHoles))
        result += '(' + '+'.join(vars) + ')'

    # enforce that no hole has more than one pigeon
    # for every pair of pigeons i,k and each hole j
    # "if pigeon i in hole j -> pigeon k cannot be in hole j"
    # (/x_{i,j} + /x_{k,j})
    for pigeonPair in itertools.combinations(range(nPigeons), 2):
        for hole in range(nHoles):
            result += '(/v_%d_%d+/v_%d_%d)' % \
                (pigeonPair[0], hole, pigeonPair[1], hole)

    # this was essentially =_1(all pigeons, hole 0)
    #                  and =_1(all pigeons, hole 1)
    #                                          ...

    # see also:
    # Frisch, Giannoros - SAT Encodings of the At-Most-k Constraint
    # Sabharwal - Symmetry in Satisfiability Solvers
    # 

    # done
    return result

#------------------------------------------------------------------------------
# VARIOUS CONSTRAINT ENCODINGS
#------------------------------------------------------------------------------

# return the "binomial" encoding of the
# "at-most-k" <=_k(X_1, X_2, ..., X_n) constraint
#
# example for <=_1(A,B,C,D):
# "if A is true, B cannot be true" (A -> /B)
# "if A is true, C cannot be true" (A -> /C)
# "if A is true, D cannot be true" (A -> /D)
# "if B is true, C cannot be true" (B -> /C)
# "if B is true, C cannot be true" (B -> /C)
# "if C is true, D cannot be true" (C -> /D)
# resulting in (/A+/B)(/A+/C)(/A+/D)(/B+/C)(/B+/D)(/C+/D)
#
# example for <=_2(A,B,C,D): 
# "if A is true and B is true, (C or D) is not true" (A*B -> /(C+D))
# etc...
# this expands to clause (/A + /B + /(C*D))
# we can just make two clauses to get this in CNF form:
# (/A + /B + /C)(/A + /B + /D)
# etc...
# resulting in (/A+/B+/C)(/A+/B+/D)(/A+/C+/D)(/B+/C+/D)
#
def atMostK_Binomial(varlist, k):
    result = ''
    # "for every k+1 sized subset of variables, 
    for subset in itertools.combinations(varlist, k+1):
        # make a clause that is the disjuction of those inverted variables in the subset"
        inverted = map(lambda x: '/%s' % x, subset)
        result += '(' + '+'.join(inverted) + ')'
    return result

#------------------------------------------------------------------------------
# PIPING TO VARIOUS SOLVERS
#------------------------------------------------------------------------------

#  in:   formula
# out:   map from variables' name to value
def PicosatPipeSolve(formula):
    (dimacs, varNames) = cnfToDimacs(formula)

    print dimacs

    p = subprocess.Popen('picosat', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(dimacs)
    p.stdin.close()

    output = p.stdout.read()
    p.stdout.close()

    print output

    if not re.match(r'^s SATISFIABLE', output):
        return None
   
    # parse out all the variables from here... 
    result = {}

    ints = re.findall(r'(-?\d+)', output)
    ints = map(lambda x: int(x), ints)
    for i in ints:
        result[ varNames[abs(i)-1] ] = int(i>0)
    
    return result

#------------------------------------------------------------------------------ 
# MAIN
#------------------------------------------------------------------------------

if __name__ == "__main__":
    formula = '(A+B+C)(/A+/B+C)(A+/B+/C)'
    (dimacs, varlist) = cnfToDimacs(formula)
    print dimacs
    for idx, vname in enumerate(varlist):
        print "dimacs %d is variable \"%s\"" % (idx+1, vname)
    print varlist

    # xor truth table
    table = [ \
        [1, 0], \
        [0, 1], \
    ]
    formula = formulaFromTruthTable(['A', 'B'], table)
    print formula

    # xor truth table
    # true when only one of the input variables are true
    # should produce:
    # (/A*/B*/C*/D*E*/F*/G*/H+/A*/B*/C*/D*/E*/F*G*/H+/A*/B*/C*D*/E*/F*/G*/H+/A*B*/C*/D*/E*/F*/G*/H+/A*/B*/C*/D*/E*/F*/G*H+/A*/B*/C*/D*/E*F*/G*/H+A*/B*/C*/D*/E*/F*/G*/H+/A*/B*C*/D*/E*/F*/G*/H)
    size = 8
    table = []
    for i in range(size):
        row = [0]*size
        row[i] = 1
        table.append(row)
    print table
    formula = formulaFromTruthTable(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[0:size]), table)
    print formula

    # at-most-k
    print atMostK_Binomial(list('ABCD'), 2)

    # pigeonhole
    print "PIGEONHOLE PROBLEM:"
    ph = pigeonHole(5,4)
    print ph
    (dimacs, varlist) = cnfToDimacs(ph)
    print dimacs

    #print PicosatPipeSolve(ph)
