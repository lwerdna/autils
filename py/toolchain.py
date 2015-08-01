#!/usr/bin/python
#------------------------------------------------------------------------------
#
#    This file is a part of alib.
#
#    Copyright 2011-2014 Andrew Lamoureux
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

G_TOOLCHAIN_DEBUG = True

import re
import os
import sys
import string
import struct
import tempfile
import parsing
import binascii
import readline

import elf
import bytes
import utils

def assemble(source, toolchainSettings):
    (asm_handle, asm_name) = tempfile.mkstemp(suffix='.s')
    (obj0_handle, obj0_name) = tempfile.mkstemp(suffix='.o')

    if G_TOOLCHAIN_DEBUG: 
        print "asm_name: %s" % asm_name
        print "obj0_name: %s" % obj0_name

    # create asm input file
    asm_obj = os.fdopen(asm_handle, 'w')
    asm_obj.write(source + "\n")
    asm_obj.close()

    # assemble to object file
    cmd = '%s %s %s -o %s' % \
            (toolchainSettings['as'], toolchainSettings['as_flags'], asm_name, obj0_name)
    output = utils.runGetOutput(cmd, G_TOOLCHAIN_DEBUG) 

    # disassemble output file
    cmd = '%s -d %s %s' % (toolchainSettings['objdump'], toolchainSettings['objdump_flags'], obj0_name) 
    output = utils.runGetOutput(cmd, G_TOOLCHAIN_DEBUG)

    # parse disassembly output
    blob = ''
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
            blob += parsing.parseDwordsWordsBytes(m.group(1))
            #print "got blob: ", bytes.getStrAsHex(blob)

    # parse symbol table
    cmd = '%s -t %s %s' % (toolchainSettings['objdump'], toolchainSettings['objdump_flags'], obj0_name) 
    output = utils.runGetOutput(cmd, G_TOOLCHAIN_DEBUG)

    syms = {}
    lines = output.split("\n")
    for l in lines:
        # eg:
        # 00000000 l    d  .text	00000000 .text
        # 00000000 l    d  .data	00000000 .data
        # 00000000 l    d  .bss	00000000 .bss
        # deadbef0 l       *ABS*	00000000 MARKER_ORIG_BYTES0
        # deadbef1 l       *ABS*	00000000 MARKER_ORIG_BYTES1
        # deadbef2 l       *ABS*	00000000 MARKER_ADDR_RETURN
        # 00000060 l       .text	00000000 context
        reStr = r'^' + \
                r'(?P<val_addr>[a-f0-9]{8})\s+' + \
                r'(?P<flags>[lgu\!wCWIidDFfo ]+)\s+' + \
                r'(?P<section>\S+)\s+' + \
                r'(?P<align_size>[a-f0-9]{8})\s+' + \
                r'(?P<name>\S+)\s*' + \
                r'$'

        m = re.match(reStr, l)
        if m:
            #if G_TOOLCHAIN_DEBUG:
            #    print "DID MATCH ON SYMBOL INFO LINE:\n%s" % l

            #syms.append( \
            #    {   'val_addr' : int(m.group('val_addr'), 16), \
            #        'flags' : m.group('flags'), \
            #        'section' : m.group('section'), \
            #        'align_size' : int(m.group('align_size'), 16), \
            #        'name' : m.group('name')
            #    }
            #)
            syms[m.group('name')] = int(m.group('val_addr'), 16)
            
        else:
            #if G_TOOLCHAIN_DEBUG:
            #    print "COULDN'T MATCH SYMBOL INFO ON LINE:\n%s" % l
            pass

    # delete temp files
    if not G_TOOLCHAIN_DEBUG:
        os.unlink(asm_name)
        os.unlink(obj0_name)

    return [blob, syms]

def disasmToString(addr, data, toolchainSettings):

    result = ''

    # objdump doesn't like unaligned sections
    prepad = 0
    postpad = 0

    if 'DONT_ALIGN' in toolchainSettings:
        pass
    else:
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
    output = utils.runGetOutput(cmd, G_TOOLCHAIN_DEBUG) 

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
    output = utils.runGetOutput(cmd, G_TOOLCHAIN_DEBUG)

    # replace all symbols '$d' with '$a' so that objdump won't distinguish between
    # code and data within .text (see "mapping symbols" in arm eabi pdf)
    # note some elf's don't have a string table (eg: HC12)
    try:
        elf.replaceStrtabString(obj1_name, '$d', '$a')
    except Exception as e:
        pass
        #print e
        #print "possibly strtab doesn't exist, skipping this step..."
 
    # disassemble output file
    cmd = '%s -d %s %s' % (toolchainSettings['objdump'], toolchainSettings['objdump_flags'], obj1_name) 
    output = utils.runGetOutput(cmd, G_TOOLCHAIN_DEBUG)

    # delete temp files
    if G_TOOLCHAIN_DEBUG:
        print "file input: " + asm_name
        print "file obj0: " + obj0_name
        print "file obj1: " + obj1_name
        print "file linker: " + ld_name
    else:
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

# eg: 
# ndk_eabi
# ./toolchain.py ARM assemble
if __name__ == "__main__":
    G_TOOLCHAIN_DEBUG = 1

    arch = 'AMD64'
    if sys.argv[1:]:
        arch = sys.argv[1]
    print "using ARCH: " + arch 

    oper = ''
    if sys.argv[2:]:
        oper = sys.argv[2]

    print "operation \"%s\" on architecture %s" % (oper, arch)

    # detect specified cross compiler
    # ARM example: 
    cross_compile = ''
    if 'CCOMPILER' in os.environ:
        cross_compile = os.environ['CCOMPILER']
    else:
        print "no CCOMPILER in environment, defaulting to AMD64"
        cross_compile = ''
        arch = 'AMD64'

    settings = {'as': cross_compile + 'as', \
                'as_flags':'', \
                'ld': cross_compile + 'ld', \
                'ld_flags':'', \
                'objdump': cross_compile + 'objdump', \
                'objdump_flags':'' \
            }

    ###########################################################################
    # do an example disassembly
    ###########################################################################
    if arch == 'AMD64':
        settings['DONT_ALIGN'] = 1
        settings['objdump_flags'] = ' -M intel'
        settings ['as_flags'] = ' -mmnemonic=intel -msyntax=intel'
        # from UPX's inserted code:
        #  40349d: 5b                   	pop    rbx
        #  40349e: 6a 01                	push   0x1
        #  4034a0: 68 0c 00 40 00       	push   0x40000c
        #  4034a5: 50                   	push   rax
        #  4034a6: 68 ac 6b 21 00       	push   0x216bac
        #  4034ab: 51                   	push   rcx
        #  4034ac: 41 57                	push   r15
        #  4034ae: bf 00 00 80 00       	mov    edi,0x800000
        #  4034b3: 6a 07                	push   0x7
        #  ...
        testInput = [ \
            0x5B, 0x6A, 0x01, 0x68, 0x0C, 0x00, 0x40, 0x00, 0x50, 0x68, 0xAC, 0x6B, 0x21, 0x00, 0x51, 0x41,
            0x57, 0xBF, 0x00, 0x00, 0x80, 0x00, 0x6A, 0x07, 0x5A, 0xBE, 0xAC, 0x6B, 0x21, 0x00, 0x6A, 0x32,
            0x41, 0x5A, 0x45, 0x29, 0xC0, 0x6A, 0x09, 0x58, 0x0F, 0x05, 0x39, 0xC7, 0x0F, 0x85, 0xF5, 0xFE,
            0xFF, 0xFF, 0xBE, 0x00, 0x00, 0x40, 0x00, 0x89, 0xFA, 0x29, 0xF2, 0x74, 0x15, 0x01, 0xD5, 0x01,
            0x54, 0x24, 0x08, 0x01, 0x54, 0x24, 0x18, 0x89, 0xD9, 0x29, 0xF1, 0xC1, 0xE9, 0x03, 0xFC, 0xF3,
            0x48, 0xA5, 0x97, 0x48, 0x89, 0xDE, 0x50, 0x92, 0xAD, 0x50, 0x48, 0x89, 0xE1, 0xAD, 0x97, 0xAD,
            0x44, 0x0F, 0xB6, 0xC0, 0x48, 0x87, 0xFE, 0xFF, 0xD5, 0x59, 0xC3
        ]

        testInput = ''.join(map(lambda x: struct.pack('B', x), testInput))
        print repr(testInput)
        print disasmToString(0x40349D, testInput, settings)

    elif arch == 'ARM': 
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

    elif arch == 'HC12':
        # eg:
        # sudo apt-get install gcc-m68hc1x
        # $ CCOMPILER=m68hc11- ~/code/alib/py/toolchain.py HC12
        settings['DONT_ALIGN'] = 1

        testInput = '\x3B\x1B\x9c\x6c\x80\xec\x88\x6c\x82\x20\x16'

        print disasmToString(0xF873, testInput, settings)

    elif arch == 'THUMB':
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

    elif arch == 'POWERPC':
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

        # TODO: get this to work
        #print disasmToString(0x1000154c, testInput, settings)
        pass

    ###########################################################################
    # do an example disassembly
    ###########################################################################

    # now go into shell mode
    if oper and oper in ('assemble', 'disassemble'):

        while(1):
            line = raw_input('%s> ' % oper)
    
            if not line:
                break
   
            if(oper == 'disassemble'):
                bs = parsing.parseBytes(line)
                print "got bytes: ", binascii.hexlify(bs)
                print disasmToString(0, bs, settings)
            else:
                (bytes_, syms) = assemble(line, settings)
                print binascii.hexlify(bytes_)
                #print syms

