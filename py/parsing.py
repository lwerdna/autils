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

import re
import string
from struct import pack, unpack

#------------------------------------------------------------------------------
# binary/byte parsing 
#------------------------------------------------------------------------------

# eg: "0xDEADBEEF" returns 0xDEADBEEF
# will pick out first instance of hex value
# eg: "8000 8FFF DE AD BE EF" returns 0x8000 
def parseHexValue(line):
	toks = re.split('\s', line)

	for t in toks:
		if re.match('^(0x)?[0-9A-Fa-f]+$', t):
			return int(t,16)

	raise Exception('couldn\'t parse %s' % line)

# eg: "DE AD BE EF" returns [0xDE, 0xAD, 0xBE, 0xEF]
def parseBytes(text):
	rv = '' 
	toks = re.split('\s', text)
	for t in toks:
		if re.match('^[0-9A-Fa-f][0-9A-Fa-f]$', t):
			rv += chr(int(t, 16))

	return rv 

# this is useful for parsing output from objdump, which can come
# as a list of bytes, list of words, etc.
#
# bytes example (x86_64):
# 40051c:	55					  	push   %rbp
# 40051d:	48 89 e5					mov	%rsp,%rbp
# 400520:	bf d4 05 40 00		  	mov	$0x4005d4,%edi
#
# words example (arm thumb):
# 1928: 2a00	  	cmp	r2, #0
# 192a: d031	  	beq.n	1990 <.text+0x150>
# 192c: f8d8 300c 	ldr.w	r3, [r8, #12]
#
def parseDwordsWordsBytes(text, endian='little'):
	bytes = ''

	iFmt = '<I'
	hFmt = '<H'
	bFmt = '<B'
	if endian == 'big':
		iFmt = '>I'
		hFmt = '>H'
		bFmt = '>B'

	while text:
		# eat whitespace
		if re.match(r'^\s', text):
			text = text[1:]
		# eat dwords
		elif re.match(r'^[0-9A-Fa-f]{8}', text):
			#print "packing dword"
			bytes += pack(iFmt, int(text[0:8], 16))
			text = text[8:]
		# eat words
		elif re.match(r'^[0-9A-Fa-f]{4}', text):
			#print "packing word"
			bytes += pack(hFmt, int(text[0:4], 16))
			text = text[4:]
		# eat bytes
		elif re.match(r'^[0-9A-Fa-f]{2}', text):
			#print "packing byte"
			bytes += pack(bFmt, int(text[0:2], 16))
			text = text[2:]

	#print "returning bytes: ", repr(bytes)
	return bytes

# parse all the bytes from a hex dump
def parseBytesFromHexDump(text, doubleSpace=None):
	bytes = ''

	lines = text.split('\n')

	# expects format <address><optional space>: AA BB CC <ascii>
	regex = r'^[0-9a-fA-F]{1,16}\s?: (.*)  '
	if doubleSpace:
		# expects format <address><optional space>: AA BB CC<two spaces><ascii>
		regex = r'^[0-9a-fA-F]{1,16}\s?: (.*) '

	for i,l in enumerate(lines):
		m = re.match(regex, l)
		if m:
			bytes += parseBytes(m.group(1))

	#print "returning bytes: ", bytes
	return bytes

#------------------------------------------------------------------------------
# utilities for argument/command 
#------------------------------------------------------------------------------

# eg: consumeTokens("one two three") -> "two three"
def consumeTokens(line, deliminator=' ', n=1):
	tokens = line.split(deliminator)
	return deliminator.join(tokens[n:])

def consumeToken(line, deliminator=' ', n=1):
	return consumeTokens(line, deliminator, n)

#------------------------------------------------------------------------------
# argument/command type parsing
#------------------------------------------------------------------------------

# from windbg "db" syntax...
# eg: "8000 L1000" returns [0x8000, 0x1000]
def parseAddressRange(line_in, default_size=256):
	line = line_in
	toks = line.split(' ')

	# no params? 0 0
	if(not toks):
		return [0, 0]

	# at least one param? parse start address
	start = int(toks[0], 16);

	size = default_size
	if(len(toks) > 1):
		if(toks[1][0] == 'l' or toks[1][0] == 'L'):
			size = int(toks[1][1:], 16)
		else:
			end = int(toks[1], 16)
			size = end-start;

	return [start, size]

#------------------------------------------------------------------------------
# tests 
#------------------------------------------------------------------------------

# main
if __name__ == '__main__':
	text = "" + \
		"blah blah blah\n" + \
		"blah blah DEADBEEF blah\n" + \
		"blah blah\n" + \
		"0xCAFEBABEEE\n" + \
		"derp werp\n" + \
		"ree dee\n"

	temp = parseHexValue(text)
	if(temp == 0xDEADBEEF):
		print "PASS!"
	else:
		print "FAIL! (is instead: 0x%08X)" % temp

	text = "" + \
		"[R]ead [M]emory via [S]DIO\n" + \
		"parsed address: 0x00000500\n" + \
		"parsed len: 0x00000100\n" + \
		"len = 0x100\n" + \
		"addr = 0x500\n" + \
		"partition = 0x0\n" + \
		"00000500: DE AD BE EF 12 13 14 15 16 17 18 19 20 21 22 23 .`.h..G..'......\n"

	if parseBytes(text) == '\xDE\xAD\xBE\xEF\x12\x13\x14\x15\x16\x17\x18\x19\x20\x21\x22\x23':
		print "PASS!"
	else:
		print "FAIL!"
		print binascii.hexlify(parseBytes(text))

	input = "one time I had a"
	output = consumeTokens(input, " ", 0)
	if output == "one time I had a":
		print "PASS!"
	else:
		print "FAIL!"

	input = "one time I had a"
	output = consumeTokens(input, " ", 1)
	if output == "time I had a":
		print "PASS!"
	else:
		print "FAIL!"

	input = "one time I had a"
	output = consumeTokens(input, " ", 2)
	if output == "I had a":
		print "PASS!"
	else:
		print "FAIL!"

	input = "one time I had a"
	output = consumeTokens(input, " ", 5)
	if output == "":
		print "PASS!"
	else:
		print "FAIL!"

	input = "one time I had a"
	output = consumeTokens(input, " ", 100)
	if output == "":
		print "PASS!"
	else:
		print "FAIL!"

	if '' == consumeTokens("test", " ", 1):
		print "PASS!"
	else:
		print "FAIL!"
