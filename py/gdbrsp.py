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

#------------------------------------------------------------------------------
# GDB STUB STUFF
#------------------------------------------------------------------------------

def send_packet_data(data):
	checksum = 0;
	for i in data:
		checksum += ord(i)
	packet = '$' + data + '#' + ("%02x" % (checksum % 256))

	s.send(packet)
	if(g_debug):
		ColorDebug()
		print '->'
		print_hex(0,packet)
		ColorOff()

	data = s.recv(1)
	if(g_debug):
		ColorDebug()
		print '<-'
		print_hex(0,data)
		ColorOff()

	if(data != '+'):
		ColorError()
		print "no ack for last packet"
		ColorOff()

packet_buff = ''

def extract_packet_data():
	global packet_buff

	# consume ack's
	while True:
		if(len(packet_buff)>0 and packet_buff[0] == '+'):
			packet_buff = packet_buff[1:]
		else:
			break;

	if(len(packet_buff)>0 and packet_buff[0] == '$'):
		hash = string.find(packet_buff, '#')
		if(hash):
			data = packet_buff[1:hash]
			packet_buff = packet_buff[hash+3:]
			return data

def get_packet_data():
	global packet_buff

	while True:
		data = extract_packet_data()
		if(data):
			send_ack();
			return data;

		data = s.recv(4096)
		if(g_debug):
			ColorDebug()
			print 'z<-'
			print_hex(0,data)
			ColorOff()
		packet_buff += data

	return data;

def get_packet_data_noblock():
	global packet_buff

	s.setblocking(0)

	while True:
		data = extract_packet_data()
		if(data):
			send_ack()
			return data

		try:
			data = s.recv(4096)
			if(g_debug):
				ColorDebug()
				print '<-'
				print_hex(0,data)
				ColorOff()
		except socket.error:
			if(g_debug):
				ColorDebug()
				print '<- (no data, did not block)'
				ColorOff()
			return

		packet_buff += data

	return data;

def send_ack():
	packet = '+'
	s.send(packet)
	if(g_debug):
		ColorDebug()
		print '->'
		print_hex(0,packet)

