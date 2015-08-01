#!/usr/bin/python3
#------------------------------------------------------------------------------
#
#    Copyright 2011-2015 Andrew Lamoureux
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
#------------------------------------------------------------------------------

from struct import pack, unpack

# rotates 
def bitrol(r, n, regsize=32):
    n = n % regsize
    return ((r<<n) | (r>>(regsize-n))) & (2**regsize - 1)

def bitror(r, n, regsize=32):
    n = n % regsize
    return ((r>>n) | (r<<(regsize-n))) & (2**regsize - 1)

# unsigned add/sub within a register
def bitadd(a, b, regsize=32):
    return (a+b) & (2**regsize - 1)

def bitsub(a, b, regsize=32):
    return (a + (2**regsize - b)) & (2**regsize -1)

# shifts
def bitshl(a, n, regsize=32):
    return (a<<n) & (2**regsize - 1)

def bitshr(a, n, regsize=32):
    return (a>>n) & (2**regsize - 1)

# other
# convention: bytes[0] becomes least significant
def bytes2reg(*bytes):
    reg = 0
    for b in reversed(bytes):
        reg = (reg << 8) | b
    return reg

# convention: bytes[0] becomes least significant of reg
def reg2bytes(reg, size=32):
    minBytes = size/8
    bytes = []

    while reg:
        bytes.append(reg & 0xFF)
        reg >>= 8

    while len(bytes) < minBytes:
        bytes.append(0)

    return bytes

def strToHex(s):
    return ''.join(map(lambda x: '%02X'%ord(x), list(s)))

if __name__ == '__main__':
    print("testing...")

    if reg2bytes(0xDEADBEEF) == [0xEF, 0xBE, 0xAD, 0xDE]:
        print("PASS")
    else:
        print("FAIL")

    if bitshl(0xDEADBEEF, 8) == 0xADBEEF00:
        print("PASS")
    else:
        print("FAIL")

    if bitshr(0xDEADBEEF, 8) == 0x00DEADBE:
        print("PASS")
    else:
        print("FAIL")

    if bitrol(0xDEADBEEF, 4) == 0xEADBEEFD:
        print("PASS")
    else:
        print("FAIL")

    if bitror(0xDEADBEEF, 4) == 0xFDEADBEE:
        print("PASS")
    else:
        print("FAIL")

    if bytes2reg(0xDE, 0xAD, 0xBE, 0xEF) == 0xEFBEADDE:
        print("PASS")
    else:
        print("FAIL")

    if bytes2reg(0xEF, 0xBE, 0xAD, 0xDE) == 0xDEADBEEF:
        print("PASS")
    else:
        print("FAIL")

