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

import os
import sys

import re
from struct import pack, unpack
import string

sys.path.append(os.environ['PATH_AUTILS'])
from parsing import *

regex_hex_int = r'^(?:0x)?[a-fA-F0-9]{1,16}$'

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

#------------------------------------------------------------------------------
# binary data to various string representations 
#------------------------------------------------------------------------------
def getHexDump(data, addr=0, grouping=1, endian='little'):
	result = ''

	while(data):
		ascii = ''
		buff16 = data[0:16]
		data = data[16:]

		result += "%08X: " % addr

		i = 0
		while i < 16:
			if(i < len(buff16)):
				f0 = { \
					'big':	{1:'>B', 2:'>H', 4:'>I', 8:'>Q'}, \
					'little': {1:'<B', 2:'<H', 4:'<I', 8:'<Q'} \
				}

				f1 = { \
					1:'%02X ', 2:'%04X ', 4:'%08X ', 8:'%016X ' \
				}

				temp = unpack(f0[endian][grouping], buff16[i:i+grouping])[0]

				result += f1[grouping] % temp

				for j in range(grouping):
					if(buff16[i+j] >= ' ' and buff16[i+j] <= '~'):
						ascii += buff16[i+j]
					else:
						ascii += '.'
			else:
				if grouping == 1:
					result += ' '*len('DE ')
				elif grouping == 2:
					result += ' '*len('DEAD ')
				elif grouping == 4:
					result += ' '*len('DEADBEEF ')
				elif grouping == 8:
					result += ' '*len('DEADBEEFCAFEBABE ')

			i += grouping

		result += ' %s\n' % ascii

		addr += 16;

	return result

def getGdbWrites(addr, data):
	result = ''

	while(data):
		if(len(data) >= 4):
			result += 'set *(unsigned int *)0x%X = 0x%X\n' % \
					(addr, unpack('I',data[0:4])[0])
			data = data[4:]
			addr += 4
		elif(len(data) >= 2):
			result += 'set *(unsigned short *)0x%X = 0x%X\n' % \
					(addr, unpack('H',data[0:2])[0])
			data = data[2:]
			addr += 2
		elif(len(data) == 1):
			result += 'set *(unsigned char *)0x%X = 0x%X\n' % \
					(addr, unpack('B',data[0:1])[0])
			data = data[1:]
			addr += 1
		else:
			print 'IMPOSSIBLE!'

	return result;

def getIdaPatchIdc(addr, data):
	result = ''

	while(data):
		if(len(data) >= 4):
			result += 'PatchDword(0x%X, 0x%X);\n' % \
					(addr, unpack('I',data[0:4])[0])
			data = data[4:]
			addr += 4
		elif(len(data) >= 2):
			result += 'PatchWord(0x%X, 0x%X);\n' % \
					(addr, unpack('H',data[0:2])[0])
			data = data[2:]
			addr += 2
		elif(len(data) == 1):
			result += 'PatchByte(0x%X, 0x%X);\n' % \
					(addr, unpack('B',data[0:1])[0])
			data = data[1:]
			addr += 1
		else:
			result += 'IMPOSSIBLE!'

	return result

def getCString(data):
	result = ''
	count = 0

	group16 = ''

	while(data):
		group16 += "\\x%02X" % unpack('B', data[0])[0]
		data = data[1:]
		count += 1

		if count == 16:
			result += '"%s"\n' % group16
			group16 = ''
			count = 0

	if group16:
		result += '"%s"' % group16

	return result

def getPythonString(data):
	temp = getCString(data)
	temp = re.sub("\n", " + \\\n", temp)
	return temp

def getStrAsHex(s, spaced=False):
	raise Exception("use binascii.hexlify() or foo.encode('hex') instead")

#------------------------------------------------------------------------------
# bit access
#------------------------------------------------------------------------------

def getBits(val, hi, lo):
	mask = (2**(hi+1) - 1) - (2**lo-1)
	return (val & mask) >> lo

#------------------------------------------------------------------------------
# endian conversions 
#------------------------------------------------------------------------------

def bswap32(val):
	return unpack('>I', pack('<I', val))[0]

def bswap16(val):
	return unpack('>H', pack('<H', val))[0]

#------------------------------------------------------------------------------
# bit byte calculations
#------------------------------------------------------------------------------

def dataXor(a, b):
	assert(len(a)==len(b))
	length = len(a)
	result = ''
	for i in range(length):
		result += pack('B', ord(a[i]) ^ ord(b[i]))
	return result

#------------------------------------------------------------------------------
# tests 
#------------------------------------------------------------------------------

if __name__ == '__main__':
	# test getFirstHexInt()
	text = "" + \
		"blah blah blah\n" + \
		"blah blah 0xDEADBEEF blah\n" + \
		"blah blah\n" + \
		"0xCAFEBABEEE\n" + \
		"derp werp\n" + \
		"ree dee\n"

	if(parseHexValue(text) == 0xDEADBEEF):
		print "PASS!"
	else:
		print "FAIL!"

	text = "" + \
		"[R]ead [M]emory via [S]DIO\n" + \
		"parsed address: 0x00000500\n" + \
		"parsed len: 0x00000100\n" + \
		"len = 0x100\n" + \
		"addr = 0x500\n" + \
		"partition = 0x0\n" + \
		"00000500: A0 60 00 68 08 B1 47 F4 00 27 B8 F1 05 0F 18 BF .`.h..G..'......\n" + \
		"00000510: 47 F0 80 77 00 2F 4F F0 01 07 0B D1 28 68 28 B1 G..w./O.....(h(.\n" + \
		"00000520: 28 68 38 B1 30 46 1C F0 21 FC 18 B1 17 B1 0A F0 (h8.0F..!.......\n" + \
		"00000530: B1 FC 1E E0 01 20 29 F0 59 FB 21 F0 FD FF 16 E0 ..... ).Y.!.....\n"

	if(parseBytes(text) == "" + \
		"\xA0\x60\x00\x68\x08\xB1\x47\xF4\x00\x27\xB8\xF1\x05\x0F\x18\xBF" + \
		"\x47\xF0\x80\x77\x00\x2F\x4F\xF0\x01\x07\x0B\xD1\x28\x68\x28\xB1" + \
		"\x28\x68\x38\xB1\x30\x46\x1C\xF0\x21\xFC\x18\xB1\x17\xB1\x0A\xF0" + \
		"\xB1\xFC\x1E\xE0\x01\x20\x29\xF0\x59\xFB\x21\xF0\xFD\xFF\x16\xE0"):
		print "PASS!"
	else:
		print "FAIL!"
		print parseBytes(text)

	data = \
		"\x23\x21\x2f\x75\x73\x72\x2f\x62\x69\x6e\x2f\x70\x79\x74\x68\x6f" + \
		"\x6e\x0a\x23\x20\x32\x30\x31\x32\x20\x61\x6e\x64\x72\x65\x77\x6c" + \
		"\x0a\x0a\x23\x20\x72\x6f\x75\x74\x69\x6e\x65\x73\x20\x66\x6f\x72" + \
		"\x20\x70\x61\x72\x73\x69\x6e\x67\x2f\x70\x72\x6f\x63\x65\x73\x73" + \
		"\x69\x6e\x67\x20\x62\x69\x74\x73\x2f\x62\x79\x74\x65\x73\x0a\x0a" + \
		"\x69\x6d\x70\x6f\x72\x74\x20\x72\x65\x0a\x66\x72\x6f\x6d\x20\x73" + \
		"\x74\x72\x75\x63\x74\x20\x69\x6d\x70\x6f\x72\x74\x20\x70\x61\x63" + \
		"\x6b\x2c\x20\x75\x6e\x70\x61\x63\x6b\x0a\x69\x6d\x70\x6f\x72\x74" + \
		"\x20\x73\x74\x72\x69\x6e\x67\x0a\x0a\x72\x65\x67\x65\x78\x5f\x68" + \
		"\x65\x78\x5f\x69\x6e\x74\x20\x3d\x20\x72\x27\x5e\x28\x3f\x3a\x30" + \
		"\x78\x29\x3f\x5b\x61\x2d\x66\x41\x2d\x46\x30\x2d\x39\x5d\x7b\x31" + \
		"\x2c\x31\x36\x7d\x24\x27\x0a\x0a\x23\x20\x67\x72\x61\x62\x73\x20" + \
		"\x66\x69\x72\x73\x74\x20\x70\x61\x72\x73\x65\x61\x62\x6c\x65\x20" + \
		"\x68\x65\x78\x61\x64\x65\x63\x69\x6d\x61\x6c\x20\x69\x6e\x74\x65" + \
		"\x67\x65\x72\x20\x66\x72\x6f\x6d\x20\x61\x20\x6c\x69\x6e\x65\x0a" + \
		"\x23\x0a\x64\x65\x66\x20\x67\x65\x74\x46\x69\x72\x73\x74\x4c\x69"

	print getHexDump(data, 0, grouping=1, endian='big') 
	print getHexDump(data, 0, grouping=2, endian='big') 
	print getHexDump(data, 0, grouping=4, endian='big') 
	print getHexDump(data, 0, grouping=8, endian='big') 
	print getHexDump(data, 0, grouping=1, endian='little') 
	print getHexDump(data, 0, grouping=2, endian='little') 
	print getHexDump(data, 0, grouping=4, endian='little') 
	print getHexDump(data, 0, grouping=8, endian='little') 

	print getGdbWrites(0, data)
	print getIdaPatchIdc(0, data)
	print getCString(data)
	print getPythonString(data)

