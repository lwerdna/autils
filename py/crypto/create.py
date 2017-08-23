#!/usr/bin/env python

# echo RELOADAGENT | gpg-connect-agent
# gpg --decrypt created.gpg

import os
import sys
from binascii import hexlify
from base64 import b64encode
from cast128 import cast128_encrypt_block
from struct import pack
import hashlib

g_outfile = 'created.gpg'
g_ascii_armor = True
g_fname = 'ptext.txt'
g_message = 'Hello, world!'
g_passphrase = 'pw'

def crc24(data):									# per RFC4880 6.1
	crc = 0xB704CE
	for c in data:
		crc ^= (ord(c) << 16)
		for i in range(8):
			crc <<= 1
			if crc & 0x1000000:
				crc ^= 0x1864CFB
	return crc & 0xFFFFFF

def strxor(a, b):
	chunk = min(len(a), len(b))
	result = ''
	for i in range(chunk):
		result += pack('B', ord(a[i]) ^ ord(b[i]))
	return result

def create_pkt(body, tagid):
	tag_byte = 0x80									# b7=1 (always) b6=0 (old fmt)
	tag_byte |= (tagid << 2)						# b5..b2

	length_bytes = ''
	if len(body) < 256:
		tag_byte |= 0								# length type = 0 (1 byte length)
		length_bytes = pack('>B', len(body))		#
	elif len(body) < 65536:
		tag_byte |= 1
		length_bytes = pack('>H', len(body))
	elif len(body) < 1048576:
		tag_byte |= 2
		length_bytes = pack('>I', len(body))
	else:
		raise Exception('too large')

	pkt_hdr = pack('B', tag_byte) + length_bytes	# hdr = tag byte + length bytes

	return pkt_hdr + body							# add hdr

def create_pkt3(salt):
	body = '\x04'									# version
	body += '\x03'									# block algo: CAST5
	body += '\x03'									# s2k id: Iterated+Salted
	body += '\x02'									# hash id: sha1
	body += salt
	body += '\x60'									# count (decodes to 65536)
	return create_pkt(body, 3)

def create_pkt9(ptext, passphrase, salt):
	msg = ''										# create hash input
	while len(msg) < 65536:
		msg = msg + salt + passphrase
	msg = msg[0:65536]
	print 'msg into hash: ', (msg[0:16]).encode('hex'), '...'

	m = hashlib.sha1()								# hash it
	m.update(msg)
	digest = m.digest()

	key = digest[0:16]								# CAST5 key is 16 bytes of hash
	print 'CAST5 key: ', key.encode('hex')

	# encrypt with OpenPGP CFB Mode (see 13.9)
	prefix = os.urandom(8)
	prefix = '\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8'

	FR = '\x00'*8
	FRE = cast128_encrypt_block(FR, key)
	print 'CAST5 first output: ', FRE.encode('hex')
	ctext = strxor(prefix, FRE)
	print 'CAST5 first ctext: ', ctext.encode('hex')

	FR = ctext
	FRE = cast128_encrypt_block(FR, key)
	ctext += strxor(prefix[6:8], FRE[0:2])

	FR = ctext[2:10]
	while ptext:
		FRE = cast128_encrypt_block(FR, key)
		FR = strxor(ptext[0:8], FRE)
		ctext += FR
		ptext = ptext[8:]

	return create_pkt(ctext, 9)

def create_pkt11(msg):
	body = '\x62'									# 'b' format (binary)
	body += pack('B', len(g_fname))					# filename len
	body += g_fname									# filename
	body += '\x00'*4								# date
	body += msg
	return create_pkt(body, 11)

if __name__ == '__main__':
	pkt11 = create_pkt11(g_message)
	print 'pkt11: ', pkt11.encode('hex')

	salt = os.urandom(8)
	salt = '\x11\x22\x33\x44\x55\x66\x77\x88'
	pkt9 = create_pkt9(pkt11, g_passphrase, salt)
	print 'pkt9: ', pkt9.encode('hex')

	pkt3 = create_pkt3(salt)
	print 'pkt3: ', pkt3.encode('hex')

	if g_ascii_armor:
		data = pkt3 + pkt9
		csum = crc24(data)
		print 'csum: %08X' % csum
		csum_bytes = pack('>I', csum)[1:]
		print 'csum_bytes: ' + hexlify(csum_bytes)
		csum_b64 = b64encode(csum_bytes)

		fp = open(g_outfile, 'w')
		fp.write('-----BEGIN PGP MESSAGE-----\n\n')
		fp.write(b64encode(data) + '\n')
		fp.write('=%s\n' % csum_b64)
		fp.write('-----END PGP MESSAGE-----\n')
		fp.close()

	else:
		fp = open(g_outfile, 'wb')
		fp.write(pkt3)
		fp.write(pkt9)
		fp.close()

