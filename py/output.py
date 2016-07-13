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

from struct import unpack

# client probably wants something like this:
# 
# import termcolors
# 
# def ColorDebug():
#     termcolors.ColorOrange()
# def ColorWarn():
#     termcolors.ColorYellow()
# def ColorError():
#     termcolors.ColorRed()
# def ColorInfo():
#     termcolors.ColorGrey()
# def ColorData():
#     termcolors.ColorBlue()
# def ColorNormal():
#     termcolors.ColorNormal()
# 
# def printInfo(msg):
#     ColorInfo()
#     print msg
#     termcolors.ColorPop()
# 
# def printError(msg):
#     ColorError()
#     print msg
#     termcolors.ColorPop()
# 
# def printWarn(msg):
#     ColorWarn()
#     print msg
#     termcolors.ColorPop()
# 
# def printDebug(msg):
#     ColorDebug()
#     print msg
#     termcolors.ColorPop()

#experiment with: echo -e "\033[31m ROUGE \033[0m"
FOREGROUND_BLACK = '\033[30m'
FOREGROUND_RED = '\033[31m'
FOREGROUND_GREEN = '\033[32m'
FOREGROUND_YELLOW = '\033[33m'
FOREGROUND_BLUE_DARK = '\033[34m'
FOREGROUND_ORANGE = '\033[35m'
FOREGROUND_BLUE_LIGHT = '\033[36m'
FOREGROUND_WHITE = '\033[37m'
FOREGROUND_ORIG = '\033[0m'

FOREGROUND_DISAS = FOREGROUND_BLUE_LIGHT
FOREGROUND_DISAS_SYM = FOREGROUND_ORANGE

original_color_saved = 0
original_color = 0
color_stack = [FOREGROUND_ORIG]

def ColorPush(color):
    color_stack.append(color)
    print color_stack[-1],

def ColorPop():
    color_stack.pop()
    print color_stack[-1],

# only change color if its not already changed
def ColorNudge(color):
    if len(color_stack) > 1:
        ColorPush(color)

def ColorReset():
    color_stack = [FOREGROUND_ORIG]
    print color_stack[-1],

def ColorDebug():
    ColorPush(FOREGROUND_ORANGE)
def ColorWarn():
    ColorPush(FOREGROUND_YELLOW)
def ColorError():
    ColorPush(FOREGROUND_RED)
def ColorInfo():
    ColorPush(FOREGROUND_GREEN)
def ColorData():
    ColorPush(FOREGROUND_BLUE_LIGHT)
def ColorNormal():
    ColorPush(FOREGROUND_ORIG)

def Info(msg):
    ColorInfo()
    print msg
    ColorPop()

def Error(msg):
    ColorError()
    print msg
    ColorPop()

def Warn(msg):
    ColorWarn()
    print msg
    ColorPop()

def Debug(msg):
    ColorDebug()
    print msg
    ColorPop()

def print_hex(addr, data):
    while(data):
        ascii = ''
        buff16 = data[0:16]
        data = data[16:]

        print "%08X:" % addr,

        for i in xrange(16):
            if(i < len(buff16)):
                print "%02X" % ord(buff16[i]),
                if(buff16[i] >= ' ' and buff16[i] <= '~'):
                    ascii += buff16[i]
                else:
                    ascii += '.'
            else:
                print "  ",;

        print ascii

        addr += 16;

def print_gdb_writes(addr, data):
    while(data):
        if(len(data) >= 4):
            print 'set *(unsigned int *)0x%X = 0x%X' % \
                    (addr, unpack('I',data[0:4])[0])
            data = data[4:]
            addr += 4
        elif(len(data) >= 2):
            print 'set *(unsigned short *)0x%X = 0x%X' % \
                    (addr, unpack('H',data[0:2])[0])
            data = data[2:]
            addr += 2
        elif(len(data) == 1):
            print 'set *(unsigned char *)0x%X = 0x%X' % \
                    (addr, unpack('B',data[0:1])[0])
            data = data[1:]
            addr += 1
        else:
            print 'IMPOSSIBLE!'

def print_ida_patches(addr, data):
    while(data):
        if(len(data) >= 4):
            print 'PatchDword(0x%X, 0x%X);' % \
                    (addr, unpack('I',data[0:4])[0])
            data = data[4:]
            addr += 4
        elif(len(data) >= 2):
            print 'PatchWord(0x%X, 0x%X);' % \
                    (addr, unpack('H',data[0:2])[0])
            data = data[2:]
            addr += 2
        elif(len(data) == 1):
            print 'PatchByte(0x%X, 0x%X);' % \
                    (addr, unpack('B',data[0:1])[0])
            data = data[1:]
            addr += 1
        else:
            print 'IMPOSSIBLE!'

