#!/usr/bin/python
#------------------------------------------------------------------------------
#
#    This file is a part of alib.
#
#    Copyright 2011-2013 Andrew Lamoureux
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

import re
import os
import sys
import string
import struct
import tempfile

import elf
import bytes
import utils

def assembleToString(source, toolchainSettings):
    result = ''
    (asm_handle, asm_name) = tempfile.mkstemp(suffix='.s')
    (obj0_handle, obj0_name) = tempfile.mkstemp(suffix='.o')

    # create asm input file
    asm_obj = os.fdopen(asm_handle, 'w')
    asm_obj.write(source + "\n")
    asm_obj.close()

    # assemble to object file
    cmd = '%s %s %s -o %s' % \
            (toolchainSettings['as'], toolchainSettings['as_flags'], asm_name, obj0_name)
    output = utils.runGetOutput(cmd) 
    print cmd

    # disassemble output file
    cmd = '%s -d %s %s' % (toolchainSettings['objdump'], toolchainSettings['objdump_flags'], obj0_name) 
    output = utils.runGetOutput(cmd)

    # delete temp files
    if 1:
        os.unlink(asm_name)
        os.unlink(obj0_name)

    # output into list of lines
    lines = output.split("\n")

    for l in lines:
        # is it a disassembly line, for example;
        # (arm example)    
        # 192c: f8d8 300c 	ldr.w	r3, [r8, #12]
        # (x86_64 example)   
        # 400520:	bf d4 05 40 00          	mov    $0x4005d4,%edi
        reStr = r'^\s*(?:0x)?[a-f0-9]{1,16}:\s+' + \
                r'(.*?)\t' + \
                r'.*'

        m = re.match(reStr, l)
        if m:
            #print "parsing: " + m.group(1)
            result += bytes.parseDwordsWordsBytes(m.group(1))
            #print "got result: ", bytes.getStrAsHex(result)

    return result

def disasmToString(addr, data, toolchainSettings):

    result = ''

    # objdump doesn't like unaligned sections
    prepad = 0
    postpad = 0
    while addr % 4:
        #print "data was: ", data
        data = '\x00' + data
        #print "data is: ", data
        addr -= 1
        prepad += 1

    while len(data) % 4:
        #print "data was: ", data
        data = data + '\x00'
        #print "data is: ", data
        postpad += 1
   
    #print "prepad: ", prepad
    #print "postpad: ", postpad
 
    (asm_handle, asm_name) = tempfile.mkstemp(suffix='.s')
    (obj0_handle, obj0_name) = tempfile.mkstemp(suffix='.o')
    (obj1_handle, obj1_name) = tempfile.mkstemp(suffix='.o')
    (ld_handle, ld_name) = tempfile.mkstemp(suffix='.ld')

    #print "file obj0: " + obj0_name
    #print "file obj1: " + obj1_name
    #print "file input: " + asm_name
    #print "file linker: " + ld_name

    # create asm input file
    asm_obj = os.fdopen(asm_handle, 'w')
    input_text = ''
    #input_text = '.org 0x%X\n' % addr
    input_text += '.byte'
    while data:
        input_text += ' 0x%02X' % struct.unpack('B', data[0])
        #print "input_text is: ", input_text
        data = data[1:]
        if data:
            input_text += ','
    input_text += "\n"
    asm_obj.write(input_text)
    asm_obj.close()

    # create asm output file 
    obj0_obj = os.fdopen(obj0_handle)
    obj0_obj.close()

    # assemble to object file
    cmd = '%s %s %s -o %s' % \
            (toolchainSettings['as'], toolchainSettings['as_flags'], asm_name, obj0_name)
    output = utils.runGetOutput(cmd) 

    # create linker file
    ld_obj = os.fdopen(ld_handle, 'w')
    ld_obj.write("SECTIONS\n")
    ld_obj.write("{\n")
    ld_obj.write("  . = 0x%X;\n" % addr)
    ld_obj.write("  .text . : { %s(.text) }\n" % obj0_name)
    ld_obj.write("}\n");
    ld_obj.close()

    # link object file to new object file with the relocation of .text
    cmd = '%s %s --script %s -o %s' % (toolchainSettings['ld'], obj0_name, ld_name, obj1_name)
    output = utils.runGetOutput(cmd)

    # replace all symbols '$d' with '$a' so that objdump won't distinguish between
    # code and data within .text (see "mapping symbols" in arm eabi pdf)
    elf.replaceStrtabString(obj1_name, '$d', '$a')
    #try:
    #    elf.replaceStrtabString(obj1_name, '$d', '$a')
    #except Exception as e:
    #    print e
        #print "possibly strtab doesn't exist, skipping this step..."
 
    # disassemble output file
    cmd = '%s -d %s %s' % (toolchainSettings['objdump'], toolchainSettings['objdump_flags'], obj1_name) 
    output = utils.runGetOutput(cmd)

    # delete temp files
    if 1:
        os.unlink(asm_name)
        os.unlink(obj0_name)
        os.unlink(obj1_name)
        os.unlink(ld_name)

    # output into list of lines
    lines = output.split("\n")
    # filter only disassembly lines
    lines = [l for l in lines if re.match(r'^\s*(?:0x)?[a-fA-F0-9]{1,16}:.*', l)]
    # get rid of prepad and post pad
    #print "prepad: ", prepad
    #print "postpad: ", postpad
    #lines = lines[prepad: len(lines)-postpad]
    # reduce the the space between address ':' and instruction
    lines = [re.sub(r':\s', ': ', x) for x in lines]
    # return
    return "\n".join(lines)

if __name__ == "__main__":
    TEST_ARM = 0
    TEST_THUMB = 0
    TEST_POWERPC = 1

    cross_compile = os.environ['CCOMPILER']

    settings = {'as': cross_compile + 'as', \
                'as_flags':'', \
                'ld': cross_compile + 'ld', \
                'ld_flags':'', \
                'objdump': cross_compile + 'objdump', \
                'objdump_flags':'' \
            }

    if TEST_ARM:
        # from http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0040d/BCECABDF.html
        #0xf0000000:                 0xe3a08000 ....     :mov                     r8,#0
        #0xf0000004:                 0xe28f900c ....     :add                     r9,pc,#0xc
        #0xf0000008:                 0xe8b900ff ....     :ldmia                   r9!,{r0-r7}
        #0xf000000c:                 0xe8a800ff ....     :stmia                   r8!,{r0-r7}
        #0xf0000010:                 0xe8b900ff ....     :ldmia                   r9!,{r0-r7}
        #0xf0000014:                 0xe8a800ff ....     :stmia                   r8!,{r0-r7}
        #0xf0000018:                 0xe59ff018 ....     :ldr                     pc,0xf0000038                     ; = #0xf0000070
        #0xf000001c:                 0xe59ff018 ....     :ldr                     pc,0xf000003c                     ; = #0xf0000058
        #0xf0000020:                 0xe59ff018 ....     :ldr                     pc,0xf0000040                     ; = #0xf000005c
        #0xf0000024:                 0xe59ff018 ....     :ldr                     pc,0xf0000044                     ; = #0xf0000060
        #0xf0000028:                 0xe59ff018 ....     :ldr                     pc,0xf0000048                     ; = #0xf0000064
        #0xf000002c:                 0xe1a00000 ....     :nop     
        #0xf0000030:                 0xe59ff018 ....     :ldr                     pc,0xf0000050                     ; = #0xf0000068
        #0xf0000034:                 0xe59ff018 ....     :ldr                     pc,0xf0000054                     ; = #0xf000006c
        #0xf0000038:                 0xf0000070 ...p     :andnv                   r0,r0,r0,ror r0
        #0xf000003c:                 0xf0000058 ...X     :andnv                   r0,r0,r8,asr r0
        testInput = '' + \
            "\x00\x80\xa0\xe3" + \
            "\x0c\x90\x8f\xe2" + \
            "\xff\x00\xb9\xe8" + \
            "\xff\x00\xa8\xe8" + \
            "\xff\x00\xb9\xe8" + \
            "\xff\x00\xa8\xe8" + \
            "\x18\xf0\x9f\xe5" + \
            "\x18\xf0\x9f\xe5" + \
            "\x18\xf0\x9f\xe5" + \
            "\x18\xf0\x9f\xe5" + \
            "\x18\xf0\x9f\xe5" + \
            "\x00\x00\xa0\xe1" + \
            "\x18\xf0\x9f\xe5" + \
            "\x18\xf0\x9f\xe5" + \
            "\x70\x00\x00\xf0" + \
            "\x58\x00\x00\xf0"
    
        print disasmToString(0xf0000000, testInput, settings)

    if TEST_THUMB:
        cross_compile = os.environ['CCOMPILER']

        # for thumb, add in switches
        settings['as_flags'] = ' -mcpu=cortex-m3 -mthumb'
        settings['objdump_flags'] = ' -M force-thumb'

        # from http://johannes-bauer.com/mcus/cortex/
        #    8000:       b410            push    {r4}
        #    8002:       f64f 7cee       movw    ip, #65518      ; 0xffee
        #    8006:       f243 3444       movw    r4, #13124      ; 0x3344
        #    800a:       2300            movs    r3, #0
        #    800c:       f2c1 1422       movt    r4, #4386       ; 0x1122
        #    8010:       f2c0 0cc0       movt    ip, #192        ; 0xc0
        #    8014:       43d8            mvns    r0, r3
        #    8016:       6023            str     r3, [r4, #0]
        #    8018:       3301            adds    r3, #1
        #    801a:       f243 3144       movw    r1, #13124      ; 0x3344
        #    801e:       f000 00c3       and.w   r0, r0, #195    ; 0xc3
        #    8022:       f64f 72ee       movw    r2, #65518      ; 0xffee
        #    8026:       2b80            cmp     r3, #128        ; 0x80
        #    8028:       f2c1 1122       movt    r1, #4386       ; 0x1122
        #    802c:       f2c0 02c0       movt    r2, #192        ; 0xc0
        #    8030:       f8cc 0000       str.w   r0, [ip]
        #    8034:       d1ee            bne.n   8014 
        #    8036:       680b            ldr     r3, [r1, #0]
        #    8038:       6810            ldr     r0, [r2, #0]
        #    803a:       4218            tst     r0, r3
        #    803c:       d104            bne.n   8048 
        #    803e:       2399            movs    r3, #153        ; 0x99
        #    8040:       6013            str     r3, [r2, #0]
        #    8042:       2000            movs    r0, #0
        #    8044:       bc10            pop     {r4}
        #    8046:       4770            bx      lr
        #    8048:       2377            movs    r3, #119        ; 0x77
        #    804a:       600b            str     r3, [r1, #0]
        #    804c:       e7f9            b.n     8042 
        #    804e:       bf00            nop
    
        testInput = '' + \
            "\x10\xb4\x4f\xf6\xee\x7c\x43\xf2\x44\x34\x00\x23\xc1\xf2\x22\x14\xc0\xf2" + \
            "\xc0\x0c\xd8\x43\x23\x60\x01\x33\x43\xf2\x44\x31\x00\xf0\xc3\x00\x4f\xf6" + \
            "\xee\x72\x80\x2b\xc1\xf2\x22\x11\xc0\xf2\xc0\x02\xcc\xf8\x00\x00\xee\xd1" + \
            "\x0b\x68\x10\x68\x18\x42\x04\xd1\x99\x23\x13\x60\x00\x20\x10\xbc\x70\x47" + \
            "\x77\x23\x0b\x60\xf9\xe7\x00\xbf"

        print disasmToString(0x8000, testInput, settings)

    if TEST_POWERPC:
        # from: http://devpit.org/wiki/Debugging_PowerPC_ELF_Binaries
        # 1000154c:       94 21 ff e0     stwu    r1,-32(r1)
        # 10001550:       93 e1 00 18     stw     r31,24(r1)
        # 10001554:       7c 3f 0b 78     mr      r31,r1
        # 10001558:       90 7f 00 08     stw     r3,8(r31)
        # 1000155c:       81 3f 00 08     lwz     r9,8(r31)
        # 10001560:       38 09 00 01     addi    r0,r9,1
        # 10001564:       90 1f 00 08     stw     r0,8(r31)
        # 10001568:       80 1f 00 08     lwz     r0,8(r31)
        # 1000156c:       7c 03 03 78     mr      r3,r0
        # 10001570:       81 61 00 00     lwz     r11,0(r1)
        # 10001574:       83 eb ff f8     lwz     r31,-8(r11)
        # 10001578:       7d 61 5b 78     mr      r1,r11
        # 1000157c:       4e 80 00 20     blr

#        testInput = '' + \
#94 21 ff e0
#93 e1 00 18
#7c 3f 0b 78
#90 7f 00 08
#81 3f 00 08
#38 09 00 01
#90 1f 00 08
#80 1f 00 08
#7c 03 03 78
#81 61 00 00
#83 eb ff f8
#7d 61 5b 78
#4e 80 00 20

        # TODO: get this to work
        #print disasmToString(0x1000154c, testInput, settings)
        pass

    # now go into shell mode
    if (len(sys.argv) > 1) and \
        (sys.argv[1] == 'assemble' or sys.argv[1] == 'disassemble'):

        while(1):
            line = sys.stdin.readline()
    
            if not line:
                break
   
            if(sys.argv[1] == 'disassemble'):
                bs = bytes.getBytes(line)
                print "got bytes: ", bytes.getStrAsHex(bs)
                print disasmToString(0, bs, settings)
            else:
                bytes = assembleToString(line, settings)
                print bytes.getStrAsHex(bytes, True)

