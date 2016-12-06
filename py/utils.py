#!/usr/bin/python
#------------------------------------------------------------------------------
#
#	Copyright 2011-2015 Andrew Lamoureux
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
import random
import subprocess

def runGetOutput(cmdAndArgs, verbose=False):
	if verbose:
		print cmdAndArgs

	pipe = subprocess.Popen(cmdAndArgs, stdout=subprocess.PIPE, shell=True);
	text = pipe.communicate()[0]

	return text

	# pipe is destroyed upon scope exit??

def genRandomData(length=8):
	random.seed()
	res = ''
	for i in range(length):
		res += chr(random.randint(0,255))
	return res

def genFileName(ext='', nChars=8):
	random.seed()
	lookup = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
	fname = ''
	for i in range(nChars):
		fname += lookup[random.randint(0,len(lookup)-1)]
	fname += ext
	return fname

def genTempFileName(path='./', ext='', nChars=8):
	temp = ''
	while 1:
		temp = path + genFileName(ext, nChars)
		if not os.path.exists(temp):
			break
	return temp
