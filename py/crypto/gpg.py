#!/usr/bin/python
#------------------------------------------------------------------------------
#
#    Copyright 2011-2013 Andrew Lamoureux
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
# trying to use RFC4880 "OpenPGP Message Format" to read
# "ASCII Armor" (Base64 encoding) OpenPGP message data (packet type 3)
#------------------------------------------------------------------------------
# 

import os
import sys
import zlib
import base64
import hashlib
from cast128 import cast128_encrypt_block

from struct import pack, unpack

from bitops import *
from utils import *

# #define's
#

# TODO: 9.1 public key ones

# 9.2.  Symmetric-Key Algorithms
SYMM_ID_PLAINTEXT = 0
SYMM_ID_IDEA = 1
SYMM_ID_3DES = 2
SYMM_ID_CAST5 = 3
SYMM_ID_BLOWFISH = 4
SYMM_ID_AES128 = 7
SYMM_ID_AES192 = 8
SYMM_ID_AES256 = 9
SYMM_ID_TWOFISH256 = 10

# 9.3.  Compression Algorithms
COMPRESS_ID_UNCOMPRESSED = 0
COMPRESS_ID_ZIP = 1
COMPRESS_ID_ZLIB = 0
COMPRESS_ID_BZIP2 = 0

# 9.4.  Hash Algorithms
HASH_ID_MD5 = 1
HASH_ID_SHA1 = 2
HASH_ID_RIPEMD160 = 3
HASH_ID_SHA256 = 8
HASH_ID_SHA384 = 9
HASH_ID_SHA512 = 10
HASH_ID_SHA224 = 11

# 3.7.1.  String-to-Key (S2K) Specifier Types
S2K_TYPE_SIMPLE = 0
S2K_TYPE_SALTED = 1
S2K_TYPE_ITERATED_SALTED = 3

# from 9.1
def lookupPublicAlgoName(id_):
    lookup = {
      1: 'RSA (Encrypt or Sign) [HAC]',
      2: 'RSA Encrypt-Only [HAC]',
      3: 'RSA Sign-Only [HAC]',
      16: 'Elgamal (Encrypt-Only) [ELGAMAL] [HAC]',
      17: 'DSA (Digital Signature Algorithm) [FIPS186] [HAC]',
      18: 'Reserved for Elliptic Curve',
      19: 'Reserved for ECDSA',
      20: 'Reserved (formerly Elgamal Encrypt or Sign)',
      21: 'Reserved for Diffie-Hellman (X9.42, as defined for IETF-S/MIME)'
    }

    if id_ >= 100 and id_ <= 110:
        return 'Private/Experimental algorithm'

    if id_ in lookup:
        return lookup[id_]

    return 'unknown'

# from 9.2
def lookupSymmetricAlgoName(id_):
    lookup = [ \
        'Plaintext or unencrypted data', \
        'IDEA [IDEA]', \
        'TripleDES (DES-EDE, [SCHNEIER] [HAC] - 168 bit key derived from 192)', \
        'CAST5 (128 bit key, as per [RFC2144])', \
        'Blowfish (128 bit key, 16 rounds) [BLOWFISH]', \
        'Reserved', \
        'Reserved', \
        'AES with 128-bit key [AES]', \
        'AES with 192-bit key', \
        'AES with 256-bit key', \
        'Twofish with 256-bit key [TWOFISH]'
    ]

    if id_ >= 100 and id_ <= 110:
        return 'Private/Experimental algorithm'

    if id_ < len(lookup):
        return lookup[id_]

    return 'unknown'

symmToKeySize = {
    SYMM_ID_PLAINTEXT: None,
    SYMM_ID_IDEA: 128,
    SYMM_ID_3DES: 168,
    SYMM_ID_CAST5: 128,
    SYMM_ID_BLOWFISH: 128,
    SYMM_ID_AES128: 128,
    SYMM_ID_AES192: 192,
    SYMM_ID_AES256: 256,
    SYMM_ID_TWOFISH256: 256
}

# from 9.3
compressIdToString = {
    COMPRESS_ID_UNCOMPRESSED: 'Uncompressed',
    COMPRESS_ID_ZIP: 'ZIP [RFC1951]',
    COMPRESS_ID_ZLIB: 'ZLIB [RFC1950]',
    COMPRESS_ID_BZIP2: 'BZip2 [BZ2]'
}

# from 9.4
def lookupHashAlgoName(id_):
    lookup = {
        1: 'MD5 [HAC]',
        2: 'SHA-1 [FIPS180]',
        3: 'RIPE-MD/160 [HAC]',
        4: 'Reserved',
        5: 'Reserved',
        6: 'Reserved',
        7: 'Reserved',
        8: 'SHA256 [FIPS180]',
        9: 'SHA384 [FIPS180]',
        10: 'SHA512 [FIPS180]',
        11: 'SHA224 [FIPS180]'
    }

    if id_ >= 100 and id_ <= 110:
        return 'Private/Experimental algorithm'

    if id_ in lookup:
        return lookup[id_]

    return 'unknown'

# eg: s2k_sha1("\x17\xab\x99\x73\x32\x89\xf5\x72", "passphrase", 65536)
def s2k_sha1(salt, phrase, count):
    salt = "\x17\xab\x99\x73\x32\x89\xf5\x72"
    phrase = "passphrase"

    x = ''
    while len(x) < 65536:
        x += salt
        x += phrase
    
    x = x[0:65536]
    
    m = hashlib.sha1()
    m.update(x)
    print m.hexdigest()

class S2KSpecifier:
    def __init__(self, stream):
        self.salt = None
        self.count = None
        self.id_s2k = unpack('B', stream[0])[0]
        self.length = 1

        if not self.id_s2k in [0, 1, 3]:
            raise Exception("unsupported S2K id:%d" % self.id_s2k)

        # this is true for all S2K's
        self.id_hash = unpack('B', stream[1])[0]
        self.length += 1

        # everything but simple S2K has salt
        if self.id_s2k != 0:
            #self.salt = map(lambda x: unpack('B', x)[0], list(stream[2:10]))
            self.salt = stream[2:10]
            self.length += 8

        # and iterated+salted S2K also has a count
        if self.id_s2k == 3:
            c = unpack('B', stream[10])[0]
            self.length += 1
            #   The count is coded into a one-octet number using the following
            #   formula:
            #       #define EXPBIAS 6
            #           count = ((Int32)16 + (c & 15)) << ((c >> 4) + EXPBIAS);
            self.count = (16 + (c & 15)) << ((c >> 4) + 6)

    def derive(self, phrase, keybits):
        if keybits % 8:
            raise Exception('keysize (in bits) not divisible by 8')

        # >>> hashlib.algorithms
        #('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512') 
        m = None
        if self.id_hash == HASH_ID_MD5:
            m = hashlib.md5()
        elif self.id_hash == HASH_ID_SHA1:
            m = hashlib.sha1()
        elif self.id_hash == HASH_ID_SHA224:
            m = hashlib.sha224()
        elif self.id_hash == HASH_ID_SHA256:
            m = hashlib.sha256()
        elif self.id_hash == HASH_ID_SHA384:
            m = hashlib.sha384()
        elif self.id_hash == HASH_ID_SHA512:
            m = hashlib.sha512()
        else:
            raise Exception("unsupported hash id: %d" % self.id_hash)

        if self.id_s2k == S2K_TYPE_ITERATED_SALTED:
            # TODO: make this where it doesn't require a precomputed hash input
            msg = ''
            while len(msg) < self.count:
                msg = msg + self.salt + phrase
            msg = msg[0:self.count]

            m.update(msg)

            digest = m.digest()
        
            keybytes = keybits/8

            # TODO: what if keysize is larger than the hash output?
            if len(digest) < keybytes:
                raise Exception('currently cipher key sizes that exceed s2k hash sizes are unsupported')

            return digest[0:keybytes]

        else:
            raise Exception("unsupported S2K type: %d" % self.id_s2k)

    def __len__(self):
        return self.length

    def __str__(self):
        lookup = [ \
            'Simple S2K', \
            'Salted S2K', \
            'Reserved Value', \
            'Iterated and Salted S2K' \
        ]

        answer = lookup[self.id_s2k] + "\n"

        answer += "hash: %d (%s)\n" % \
            (self.id_hash, lookupHashAlgoName(self.id_hash))

        if self.salt:
            answer += 'salt: %s\n' % str2hex(self.salt)

        if self.count:
            answer += 'count: %d (number of octets!)\n' % self.count

        return answer

class PgpPacket:
    def __init__(self, stream):
        self.body = None
        self.tagValue = None
        self.lenType = None
        self.bodyLen = None
        self.pktLen = None

        tag = unpack('B', stream[0])[0]
    
        if not (tag & 0x80):
            raise Exception("ERROR: expected b7 of tag set (always one)")
    
        # new stream format?
        if tag & 0x40:
            # 4.2.1
            #print "NEW stream format detected"
        
            # New format streams contain:
            # Bits 5-0 -- stream tag
            self.tagValue = tag & 0x3F
    
            octet1 = unpack('B', stream[1])[0]
    
            # 1. A one-octet Body Length header encodes stream lengths of up to 191 octets.
            if octet1 < 192:
                self.bodyLen = octet1
                self.pktLen = 2 + self.bodyLen
            # 2. A two-octet Body Length header encodes stream lengths of 192 to 8383 octets.
            elif (octet1 >= 192) and (octet1 <= 223):
                octet2 = unpack('B', stream[2])[0]
                self.bodyLen =  ((octet1 - 192) << 8) + octet2 + 192
                self.pktLen = 3 + self.bodyLen
            # 3. A five-octet Body Length header encodes stream lengths of up to 4,294,967,295 (0xFFFFFFFF) octets in length.  (This actually encodes a four-octet scalar number.)
            elif octet1 == 255:
                (octet2, octet3, octet4, octect5) = unpack('BBBB', stream[2:6])
                self.bodyLen = (octet2 << 24) | (octet3 << 16) | (octet4 << 8) | octet5
                self.pktLen = 6 + self.bodyLen
            # 4. When the length of the stream body is not known in advance by the issuer, Partial Body Length headers encode a stream of indeterminate length, effectively making it a stream.
            elif (octet1 >= 224) and (octet1 < 255):
                raise Exception("ERROR: partial body lengths not supported")
            else:
                raise Exception("ERROR: decoding stream length")
        # old stream format
        else:
            # 4.2.2
            #print "OLD stream format detected"
    
            # Old format streams contain:
            # Bits 5-2 -- stream tag
            # Bits 1-0 -- length-type
            self.tagValue = (tag & 0x2C) >> 2
            self.lenType = tag & 0x3
            #print "length type: %d" % self.lenType
    
            if self.lenType == 0:
                # 0 - The stream has a one-octet length.  The header is 2 octets long.
                self.bodyLen = unpack('B', stream[1])[0]
                self.pktLen = 2 + self.bodyLen
            elif self.lenType == 1:
                # 1 = The stream has a two-octet length.  The header is 3 octets long.
                self.bodyLen = unpack('H', stream[1:3])[0]
                self.pktLen = 3 + self.bodyLen
            elif self.lenType == 2:
                # 2 = The stream has a four-octet length.  The header is 5 octets long.
                self.bodyLen = unpack('H', stream[1:5])[0]
                self.pktLen = 5 + self.bodylen
            elif self.lenType == 3:
                # 3 - The stream is of indeterminate length. (Eg: zlib)
                #raise Exception("ERROR: indetermined length streams are unsupported")
                self.pktLen = len(stream)
                self.bodyLen = len(stream) - 1
            else:
                raise Exception("ERROR: decoding stream length")
        
        self.hdrLen = self.pktLen - self.bodyLen
        self.body = stream[self.hdrLen:]

    def __len__(self):
        return self.pktLen

    def __str__(self):
        answer = ''
        answer += "pktType:%d\n" % self.tagValue
        answer += "hdrLen:%d + bodyLen:%d = totalLen:%d\n" % \
            (self.hdrLen, self.bodyLen, self.pktLen)
        answer += repr(self.body)
        return answer

# 
class PgpPacket3(PgpPacket):
    def __init__(self, stream):
        PgpPacket.__init__(self, stream)

        # 5.3

        # - A one-octet version number.  The only currently defined version is 4.
        self.version = unpack('B', self.body[0])[0]
        if self.version != 4:
            raise Exception("the only currently defined version is 4")

        # - A one-octet number describing the symmetric algorithm used.
        self.symAlgoId = unpack('B', self.body[1])[0]

        # - A string-to-key (S2K) specifier, length as defined above.
        #print "sending S2KSpecifier: " + repr(self.body[2:])
        self.s2k = S2KSpecifier(self.body[2:])

        # - Optionally, the encrypted session key itself, which is decrypted with the string-to-key object.
        if 2 + len(self.s2k) == self.bodyLen:
            # encrypted session key not present! S2K applied to passphrase produces the session key
            self.sessKey = None
        else:
            self.sessKey = self.body[2 + len(self.s2k) : self.bodyLen]

    def __str__(self):
        answer = "Packet (Tag 3): Symmetric-Key Encrypted Session Key\n"
        answer += "Algorithm ID: %d (%s)\n" % \
            (self.symAlgoId, lookupSymmetricAlgoName(self.symAlgoId))
        answer += "S2K: " + str(self.s2k)
        answer += "Session Key: "
        if(self.sessKey):
            answer += repr(self.sessKey)
        else:
            answer += 'empty (derived from S2K(passphrase))'
        return answer

class PgpPacket8(PgpPacket):
    def __init__(self, stream):
        PgpPacket.__init__(self, stream)

        # 5.6 Compressed Data Packet (Tag 8)
        
        # first octet is the algo
        self.compression_id = ord(self.body[0])
        self.body = self.body[1:]

    def __str__(self):
        answer = "Packet (Tag 8): Compressed Data Packet\n"
        answer += 'algorithm: %d (%s)\n' % (self.compression_id, compressIdToString[self.compression_id])
        answer += str2hexdump(0, self.body)
        
        return answer

class PgpPacket9(PgpPacket):
    def __init__(self, stream):
        PgpPacket.__init__(self, stream)

        # 5.7

        # the body is the encrypted data, simple

    def __str__(self):
        answer = "Packet (Tag 9): Symmetrically Encrypted Data\n"
        answer += str2hexdump(0, self.body)
        
        return answer

class PgpPacket11(PgpPacket):
    def __init__(self, stream):
        PgpPacket.__init__(self, stream)

        if self.body[0] == 'b':
            self.dtype = 'binary'
        elif self.body[0] == 't':
            self.dtype = 'text'
        elif self.body[0] == 'u':
            self.dtype = 'text (UTF-8)'
        elif self.body[0] == 'l':
            self.dtype = 'local'
        else:
            self.dtype = 'unknown'

        fnameLen = ord(self.body[1])

        self.fname = self.body[2:2+fnameLen]

        self.date = unpack('<I', self.body[2+fnameLen:2+fnameLen+4])

        self.data = self.body[2+fnameLen+4:]

    def __str__(self):
        answer = "Packet (Tag 11): Literal Data Packet\n"
        answer += 'data type: %s\n' % self.dtype
        answer += 'filename: %s\n' % self.fname
        answer += 'date: %d\n' % self.date
        answer += str2hexdump(0, self.data)
        
        return answer


# 'cause OOP confuses me, use helper method to instantiate appropriate object
def packetBroker(stream):
    tag = unpack('B', stream[0])[0]
    if not (tag & 0x80):
        raise Exception("ERROR: expected b7 of tag set (always one)")

    # new stream format
    if tag & 0x40:
        tagValue = tag & 0x3F
    # old stream format
    else:
        tagValue = (tag & 0x2C) >> 2

    if tagValue == 3:
        return PgpPacket3(stream)
    elif tagValue == 8:
        return PgpPacket8(stream)
    elif tagValue == 9:
        return PgpPacket9(stream)
    elif tagValue == 11:
        return PgpPacket11(stream)
    else:
        return PgpPacket(stream)

# 13.9.  OpenPGP CFB Mode
def decrypt_cfb(ctext, key):
    print "ctext: " + ctext.encode('hex')

    FR = '\x00\x00\x00\x00\x00\x00\x00\x00'
    FRE = cast128_encrypt_block(FR, key)
    random = strXor(ctext[0:0+8], FRE)
    print "random: " + random.encode('hex')

    FR = ctext[0:0+8]
    FRE = cast128_encrypt_block(FR, key)
    check = strXor(ctext[8:8+2], FRE[0:0+2])
    print "check: " + check.encode('hex')

    if check[0] != random[6] or check[1] != random[7]:
        raise Exception('key check failed')

    # encryptor was now re-initialized with IV = c_3 ... c_10 (1-indexed)
    FR = ctext[2:2+8]
    ctext = ctext[10:]

    ptext = ''
    while ctext:
        FRE = cast128_encrypt_block(FR, key)

        x = ctext[0:0+8]
        if len(x) < 8:
            FRE = FRE[0:0+len(x)]
        
        y = strXor(x, FRE)
        print "decrypted block: %s -> %s" % (x.encode('hex'), y.encode('hex'))

        ptext += y
        FR = ctext[0:8]
        ctext = ctext[8:]

    print "returning ptext: " + ptext.encode('hex')
    return ptext

if __name__ == "__main__":
    if not sys.argv[1:]:
        print "file argument required"
        sys.exit(-1)

    #
    # read file, scrub lines
    #
    fobj = open(sys.argv[1])
    lines = fobj.readlines()
    fobj.close()

    for i in range(len(lines)):
        #print "line %d: %s" % (i, lines[i])
        # inefficient, but convenient
        lines[i] = lines[i].lstrip().rstrip()

    #
    # read and sanity check the basic file bits
    #
    lineno = 1

    # see 6.2. Forming ASCII Armor
    # Concatenating the following data creates ASCII Armor:
    # - An Armor Header Line, appropriate for the type of data
    # - Armor Headers
    # - A blank (zero-length, or containing only whitespace) line
    # - The ASCII-Armored data
    # - An Armor Checksum
    # - The Armor Tail, which depends on the Armor Header Line

    print "state: seeking armor header"
    ahl_supported = "-----BEGIN PGP MESSAGE-----"
    ahl = lines[lineno-1]
    if ahl != ahl_supported:
        print "ERROR: only the \"%s\" armor header is supported" % ahl_supported
        print "LINE %d: %s" % (lineno, lines[lineno-1])
        sys.exit(-1)
    print "LINE %d: %s" % (lineno, lines[lineno-1])
    lineno += 1

    print "state: consuming armor headers"
    while 1:
        if lineno-1 >= len(lines):
            print "ERROR: encountered end-of-file early!"
            sys.exit(-1)

        if lines[lineno-1] == '':
            print "LINE %d: %s" % (lineno, lines[lineno-1])
            lineno += 1
            break

        # eg: "Version:", "Comment:", "MessageID:", etc. etc...
        print "consumed armor header"
        print "LINE %d: %s" % (lineno, lines[lineno-1])
        lineno += 1

    print "state: reading ascii-armored (base64 encoded) data"
    b64data = ''
    while 1:
        # we know when to quit by finding the Armor Checksum
        if lines[lineno-1][0] == '=':
            break

        print "LINE %d: %s" % (lineno, lines[lineno-1])
        b64data += lines[lineno-1]
        lineno += 1

    print "state: reading armor checksum"
    b64checksum = lines[lineno-1]
    print "LINE %d: %s" % (lineno, lines[lineno-1])
    lineno += 1

    print "state: seeking armor tail"
    aht_supported = "-----END PGP MESSAGE-----"
    aht = lines[lineno-1]
    if aht != aht_supported:
        print "ERROR: only the \"%s\" armor tail is supported" % aht_supported
        print "LINE %d: %s" % (lineno, aht)
        sys.exit(-1)
    print "LINE %d: %s" % (lineno, lines[lineno-1])
    lineno += 1

    print ''

    #
    # decode, parse the data (tags, etc.)
    #
    data = base64.b64decode(b64data)

    print "state: parsing packets from data"

    packets = []

    packet9 = None
    packet3 = None

    while data:
        #print "current data:"
        #print repr(data)

        packet = packetBroker(data)
        if isinstance(packet, PgpPacket3):
            packet3 = packet
        if isinstance(packet, PgpPacket9):
            packet9 = packet

        print packet
        print ''

        data = data[len(packet):]

    # ask for passphrase 
    print "Enter passphrase:",
    #passphrase = raw_input()
    passphrase = "passphrase"

    key = None

    if packet3:
        print "packet3 detected!"

        if not packet3.s2k:
            raise Exception("expected S2K specifier in packet3!")

        keySize = symmToKeySize[packet3.symAlgoId]

        print "deriving key for %s (%d bit key)" % \
            (lookupSymmetricAlgoName(packet3.symAlgoId), keySize)

        key = packet3.s2k.derive(passphrase, keySize)

        print str2hex(key)

    if packet9:
        print "packet9 detected!"

        print "attempting to decrypt: %s" % str2hex(packet9.body)

        ptext = decrypt_cfb(packet9.body, key)

        print "ptext: " + ptext.encode('hex')
        p9sub = packetBroker(ptext)
        print p9sub
        if isinstance(p9sub, PgpPacket8):
            print p9sub
