#!/usr/bin/python
#------------------------------------------------------------------------------
#
#    This file is a part of alib. 
#
#    Copyright 2011-2013 Andrew Lamoureux
#
#    This program is free software: you can redistribute it and/or modify
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

import sys
import random
from struct import pack, unpack

from bitops import *

def xtea_encrypt_block(v, key, num_rounds=32):
    sum=0
    delta=0x9E3779B9

    [v0,v1] = unpack('>II', v) 
    subkeys = unpack('>IIII', key)

    #print "subkeys: %08X %08X %08X %08X" % subkeys

    for i in range(num_rounds):
        #print "entering encrypt round=%d" % i,
        #print "v=(%08X,%08X)" % (v0, v1),
        #print "sum=%08X" % sum

        v0 = bitadd(v0, bitadd(( bitshl(v1, 4) ^ (v1 >> 5)), v1) ^ bitadd(sum, subkeys[sum & 3]))
        sum = bitadd(sum, delta)
        v1 = bitadd(v1, bitadd(( bitshl(v0, 4) ^ (v0 >> 5)), v0) ^ bitadd(sum, subkeys[(sum>>11) & 3]))

    return pack('>II', v0, v1)
 
def xtea_decrypt_block(v, key, num_rounds=32):
    delta=0x9E3779B9
    sum=delta*num_rounds;
    [v0,v1] = unpack('>II', v) 
    subkeys = unpack('>IIII', key)

    for i in range(num_rounds):
        v1 -= (( bitshl(v0, 4) ^ (v0 >> 5)) + v0) ^ (sum + subkeys[(sum>>11) & 3])
        v1 &= 0xFFFFFFFF
        sum -= delta
        v0 -= (( bitshl(v1, 4) ^ (v1 >> 5)) + v1) ^ (sum + subkeys[sum & 3])
        v0 &= 0xFFFFFFFF

    return pack('>II', v0, v1)

def xtea_encrypt_ofb(plaintext, key, iv="\x41\x42\x43\x44\x45\x46\x47\x48"):
    length = len(plaintext)

    # build stream at least as long as the plaintext
    ct = iv
    stream = []
    for i in range((length + 7) / 8):
        ct = xtea_encrypt_block(ct, key)
        stream += unpack("8B", ct)
  
    #print stream
    #print "stream: " + str(stream)

    # xor each byte
    ciphertext = ''
    for i in range(length):
        ciphertext += pack('B', ord(plaintext[i]) ^ stream[i])

    return ciphertext 

if __name__ == '__main__':
    random.seed()
    
    print "Running some tests..."
   
    arg = None
    if len(sys.argv) >= 2:
        arg = sys.argv[1]

    # these test vectors come from http://www.freemedialibrary.com/index.php/XTEA_test_vectors
    
    print "XTEA test..."

    keys = [
        "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f",
        "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f",
        "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f",
        "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    ]

    plaintexts = [
        "\x41\x42\x43\x44\x45\x46\x47\x48",
        "\x41\x41\x41\x41\x41\x41\x41\x41",
        "\x5a\x5b\x6e\x27\x89\x48\xd7\x7f",
        "\x41\x42\x43\x44\x45\x46\x47\x48",
        "\x41\x41\x41\x41\x41\x41\x41\x41",
        "\x70\xe1\x22\x5d\x6e\x4e\x76\x55"
    ]

    ciphertexts = [
        "\x49\x7d\xf3\xd0\x72\x61\x2c\xb5",
        "\xe7\x8f\x2d\x13\x74\x43\x41\xd8",
        "\x41\x41\x41\x41\x41\x41\x41\x41",
        "\xa0\x39\x05\x89\xf8\xb8\xef\xa5",
        "\xed\x23\x37\x5a\x82\x1a\x8c\x2d",
        "\x41\x41\x41\x41\x41\x41\x41\x41"
    ]

    for i in range(len(keys)):
        key = keys[i]
        plain = plaintexts[i]

        cipher = xtea_encrypt_block(plain, key)

        if cipher == ciphertexts[i]:
            print "PASS"
        else:
            print "FAIL"

        if xtea_decrypt_block(cipher, key) == plain:
            print "PASS"
        else:
            print "FAIL"

    input = "\x49\x7d\xf3\xd0\x72\x61\x2c\xb5And in front of my desk I see a little blue pencil and a whiteboard, what do I write?"
    ct = xtea_encrypt_ofb(input, keys[0]) 
    if ct == input:
        print "FAIL"
    #print repr(ct)
    if input == xtea_encrypt_ofb(ct, keys[0]):
        print "PASS"
    else:
        print "FAIL"

