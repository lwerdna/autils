#!/usr/bin/python

from hashlib import sha1
from bitops import strToHex
import hmac

def HmacSha1(key, message):
    i_pad = map(ord, list(key))
    o_pad = map(ord, list(key))

    while(len(i_pad) < 64):
        i_pad += [0]
        o_pad += [0]

    for i in range(64):
        i_pad[i] ^= 0x36
        o_pad[i] ^= 0x5c

    i_pad = ''.join(map(chr, i_pad))
    o_pad = ''.join(map(chr, o_pad))

    #print 'i_pad: ' + strToHex(i_pad)
    #print 'o_pad: ' + strToHex(o_pad)

    #print "input to first hash: " + strToHex(i_pad + message)
    first = sha1(i_pad + message).digest()
    #print "first hash: " + strToHex(first)
    
    #print "input to second hash: " + strToHex(o_pad + first)
    second = sha1(o_pad + first).digest()
    #print "second hash: " + strToHex(second)

    return second

#------------------------------------------------------------------------------
# MAIN 
#------------------------------------------------------------------------------
if __name__ == "__main__":
    key = 'key'
    msg = 'The quick brown fox jumps over the lazy dog'

    our_answer = strToHex(HmacSha1(key, msg)).lower()
    right_answer = hmac.new(key, msg, sha1).hexdigest().lower()
    print our_answer
    print right_answer
    if our_answer == right_answer:
        print "PASS"
    else:
        print "FAIL"
