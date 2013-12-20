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

def BoolParserRdDisj(s):
    #print "BoolParserRdDisj entered with s: ", s
    subexprs = []
    subexprs.append(BoolParserRdConj(s))
    if s and s[0] == '+':
        while s and s[0] == '+':
            s.pop(0)
            subexprs.append(BoolParserRdDisj(s))
        return BoolDisj(subexprs)
    else:
        return subexprs[0]

def BoolParserRdConj(s):
    #print "BoolParserRdConj entered with s: ", s
    subexprs = []
    subexprs.append(BoolParserRdXor(s))
    if s and s[0] == '*':
        while s and s[0] == '*':
            s.pop(0)
            subexprs.append(BoolParserRdConj(s))
        return BoolConj(subexprs) 
    else:
        return subexprs[0]

def BoolParserRdXor(s):
    #print "BoolParserRdXor entered with s: ", s
    subexprs = []
    subexprs.append(BoolParserRdNot(s))
    if s and s[0] == '^':
        while s and s[0] == '^':
            s.pop(0)
            subexprs.append(BoolParserRdXor(s))
        return BoolXor(subexprs) 
    else:
        return subexprs[0]

# not -> lit
#     -> '/'<disj>
def BoolParserRdNot(s):
    if s[0] == '/':
        s.pop(0)
        return BoolNot(BoolParserRdLit(s))
    else:
        return BoolParserRdLit(s)

# lit -> <identifier>
#     -> '('<disj>')'
def BoolParserRdLit(tokens):
    #print "BoolParserRdLit entered with tokens: ", tokens
    (compl, name) = (0, '')
  
    # case {'(', <expr>, ')'}
    if tokens[0] == '(':
        tokens.pop(0)
        t = BoolParserRdDisj(tokens)
        if tokens[0] != ')':
            print "missing right hand parenthesis"
            return None
        tokens.pop(0)
        return t 

    # case 0 or 1 (an assigned literal)
    m = re.match(r'^([01])$', tokens[0])
    if m:
        tokens.pop(0)
        return BoolConst(int(m.group(1)))

    name = tokens[0]
    if not re.match(r'^[0-9a-zA-Z]+$', name):
        print "invalid literal name: %s" % name
        return None

    tokens.pop(0)
    return BoolLit(name)

def BoolParser(s):
    error = 0

    # tokenize the input
    tokens = []

    # remove whitespace
    s = re.sub(r'\s', '', s)

    # go
    while s:
        # get all operators (and, or, xor, not) and parenthesis
        m = re.match(r'^[\*\+\^\/)(]', s)
        if m:
            tokens.append(m.group(0))
            s = s[1:]
            continue

        # get literal names
        m = re.match(r'^[a-zA-Z0-9]+', s)
        if m:
            tokens.append(m.group(0))
            s = s[len(m.group(0)):]
            continue

        # else wtf did we encounter?
        print "tokenizer error at \"...%s\"" % s
        error = 1
        break;

    #
    if error:
        return
        
    #print "tokens: ", tokens

    # now recursively descend over the tokens
    topnode = BoolParserRdDisj(tokens) 
    return topnode

