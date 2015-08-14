#!/usr/bin/python
#------------------------------------------------------------------------------
#
#    This file is a part of alib. 
#
#    Copyright 2011-2015 Andrew Lamoureux
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


import os
import sys
import time
import shutil
from struct import pack, unpack
import string


#------------------------------------------------------------------------------
# ELF defines
#------------------------------------------------------------------------------
EI_NIDENT = 16

I_NIDENT = (16)
EI_MAG0 = 0
ELFMAG0 = 0x7f
EI_MAG1 = 1
ELFMAG1 = 'E'
EI_MAG2 = 2
ELFMAG2 = 'L'
EI_MAG3 = 3
ELFMAG3 = 'F'
ELFMAG = "\177ELF"
SELFMAG = 4
EI_CLASS = 4
ELFCLASSNONE = 0
ELFCLASS32 = 1
ELFCLASS64 = 2
ELFCLASSNUM = 3
EI_DATA = 5
ELFDATANONE = 0
ELFDATA2LSB = 1
ELFDATA2MSB = 2
ELFDATANUM = 3
EI_VERSION = 6
EI_OSABI = 7

ELFOSABI_NONE = 0
ELFOSABI_SYSV = 0
ELFOSABI_HPUX = 1
ELFOSABI_NETBSD = 2
ELFOSABI_GNU = 3
ELFOSABI_LINUX = ELFOSABI_GNU
ELFOSABI_SOLARIS = 6
ELFOSABI_AIX = 7
ELFOSABI_IRIX = 8
ELFOSABI_FREEBSD = 9
ELFOSABI_TRU64 = 10
ELFOSABI_MODESTO = 11
ELFOSABI_OPENBSD = 12
ELFOSABI_ARM_AEABI = 64
ELFOSABI_ARM = 97
ELFOSABI_STANDALONE = 255

EI_ABIVERSION = 8
EI_PAD = 9
ET_NONE = 0
ET_REL = 1
ET_EXEC = 2
ET_DYN = 3
ET_CORE = 4
ET_NUM = 5
ET_LOOS = 0xfe00
ET_HIOS = 0xfeff
ET_LOPROC = 0xff00
ET_HIPROC = 0xffff
EM_NONE = 0
EM_M32 = 1
EM_SPARC = 2
EM_386 = 3
EM_68K = 4
EM_88K = 5
EM_860 = 7
EM_MIPS = 8
EM_S370 = 9
EM_MIPS_RS3_LE = 10
EM_PARISC = 15
EM_VPP500 = 17
EM_SPARC32PLUS = 18
EM_960 = 19
EM_PPC = 20
EM_PPC64 = 21
EM_S390 = 22
EM_V800 = 36
EM_FR20 = 37
EM_RH32 = 38
EM_RCE = 39
EM_ARM = 40
EM_FAKE_ALPHA = 41
EM_SH = 42
EM_SPARCV9 = 43
EM_TRICORE = 44
EM_ARC = 45
EM_H8_300 = 46
EM_H8_300H = 47
EM_H8S = 48
EM_H8_500 = 49
EM_IA_64 = 50
EM_MIPS_X = 51
EM_COLDFIRE = 52
EM_68HC12 = 53
EM_MMA = 54
EM_PCP = 55
EM_NCPU = 56
EM_NDR1 = 57
EM_STARCORE = 58
EM_ME16 = 59
EM_ST100 = 60
EM_TINYJ = 61
EM_X86_64 = 62
EM_PDSP = 63
EM_FX66 = 66
EM_ST9PLUS = 67
EM_ST7 = 68
EM_68HC16 = 69
EM_68HC11 = 70
EM_68HC08 = 71
EM_68HC05 = 72
EM_SVX = 73
EM_ST19 = 74
EM_VAX = 75
EM_CRIS = 76
EM_JAVELIN = 77
EM_FIREPATH = 78
EM_ZSP = 79
EM_MMIX = 80
EM_HUANY = 81
EM_PRISM = 82
EM_AVR = 83
EM_FR30 = 84
EM_D10V = 85
EM_D30V = 86
EM_V850 = 87
EM_M32R = 88
EM_MN10300 = 89
EM_MN10200 = 90
EM_PJ = 91
EM_OPENRISC = 92
EM_ARC_A5 = 93
EM_XTENSA = 94
EM_AARCH64 = 183
EM_TILEPRO = 188
EM_TILEGX = 191
EM_NUM = 192
EM_ALPHA = 0x9026

EV_NONE = 0
EV_CURRENT = 1
EV_NUM = 2

DT_NULL      = 0       # Marks end of dynamic section
DT_NEEDED    = 1       # Name of needed library
DT_PLTRELSZ  = 2       # Size in bytes of PLT relocs
DT_PLTGOT    = 3       # Processor defined value
DT_HASH      = 4       # Address of symbol hash table
DT_STRTAB    = 5       # Address of string table
DT_SYMTAB    = 6       # Address of symbol table
DT_RELA      = 7       # Address of Rela relocs
DT_RELASZ    = 8       # Total size of Rela relocs
DT_RELAENT   = 9       # Size of one Rela reloc
DT_STRSZ     = 10      # Size of string table
DT_SYMENT    = 11      # Size of one symbol table entry
DT_INIT      = 12      # Address of init function
DT_FINI      = 13      # Address of termination function
DT_SONAME    = 14      # Name of shared object
DT_RPATH     = 15      # Library search path (deprecated)
DT_SYMBOLIC  = 16      # Start symbol search here
DT_REL       = 17      # Address of Rel relocs
DT_RELSZ     = 18      # Total size of Rel relocs
DT_RELENT    = 19      # Size of one Rel reloc
DT_PLTREL    = 20      # Type of reloc in PLT
DT_DEBUG     = 21      # For debugging; unspecified
DT_TEXTREL   = 22      # Reloc might modify .text
DT_JMPREL    = 23      # Address of PLT relocs
DT_BIND_NOW  = 24      # Process relocations of object
DT_INIT_ARRAY    = 25      # Array with addresses of init fct
DT_FINI_ARRAY    = 26      # Array with addresses of fini fct
DT_INIT_ARRAYSZ  = 27      # Size in bytes of DT_INIT_ARRAY
DT_FINI_ARRAYSZ  = 28      # Size in bytes of DT_FINI_ARRAY
DT_RUNPATH   = 29      # Library search path
DT_FLAGS     = 30      # Flags for the object being loaded
DT_ENCODING  = 32      # Start of encoded range
DT_PREINIT_ARRAY  = 32     # Array with addresses of preinit fct
DT_PREINIT_ARRAYSZ  = 33       # size in bytes of DT_PREINIT_ARRAY
DT_NUM       = 34      # Number used

PF_R = 4 # [p]rogram header [f]lag [r]ead
PF_W = 2
PF_X = 1
PF_FLAG_VALUES = [4, 2, 1]
PF_FLAG_STRINGS = ['PF_R', 'PF_W', 'PF_X']

PT_NULL = 0 # [p]rogram header [t]ype
PT_LOAD = 1
PT_DYNAMIC = 2
PT_INTERP = 3
PT_NOTE = 4
PT_SHLIB = 5
PT_PHDR = 6
PT_TLS = 7
PT_LOOS = 0x60000000 # OS-specific
PT_HIOS = 0x6fffffff # OS-specific
PT_LOPROC = 0x70000000
PT_HIPROC = 0x7fffffff
PT_GNU_EH_FRAME = 0x6474e550
PT_GNU_STACK = (PT_LOOS + 0x474e551)

SHT_NULL = 0
SHT_PROGBITS = 1
SHT_SYMTAB = 2
SHT_STRTAB = 3
SHT_RELA = 4
SHT_HASH = 5
SHT_DYNAMIC = 6
SHT_NOTE = 7
SHT_NOBITS = 8
SHT_REL	 = 9
SHT_SHLIB = 10
SHT_DYNSYM = 11
SHT_NUM	 = 12
SHT_LOPROC = 0x70000000
SHT_HIPROC = 0x7fffffff
SHT_LOUSER = 0x80000000
SHT_HIUSER = 0xffffffff


SHF_WRITE = 0x1
SHF_ALLOC = 0x2
SHF_EXECINSTR = 0x4
SHF_MASKPROC = 0xf0000000

#------------------------------------------------------------------------------
# UTILITIES
#------------------------------------------------------------------------------
def strFlags(value, flagValues, flagStrs):
    result = []

    for i in range(len(flagValues)):
        if value & flagValues[i]:
            result.append(flagStrs[i])

    return '|'.join(result)

def strValueLookup(value, lookup):
    if value in lookup:
        return lookup[value]

    return '<unknown>'

def programHeaderTypeToString(t):
    lookup = { \
            PT_NULL:'PT_NULL', PT_LOAD:'PT_LOAD', PT_DYNAMIC:'PT_DYNAMIC',
            PT_INTERP:'PT_INTERP', PT_NOTE:'PT_NOTE', PT_SHLIB:'PT_SHLIB', 
            PT_PHDR:'PT_PHDR', PT_TLS:'PT_TLS', PT_GNU_EH_FRAME:'PT_GNU_EH_FRAME',
            PT_GNU_STACK:'PT_GNU_STACK'
        }

    if t in lookup:
        return lookup[t]

    if (t >= PT_LOPROC) and (t <= PT_HIPROC):
        return 'PROC'

    if (t >= PT_LOOS) and (t <= PT_HIOS):
        return 'OS'

    return '<unknown>'

def sectionTypeToString(t):
    if t==SHT_NULL: return 'SHT_NULL'
    if t==SHT_PROGBITS: return 'SHT_PROGBITS'
    if t==SHT_SYMTAB: return 'SHT_SYMTAB'
    if t==SHT_STRTAB: return 'SHT_STRTAB'
    if t==SHT_RELA: return 'SHT_RELA'
    if t==SHT_HASH: return 'SHT_HASH'
    if t==SHT_DYNAMIC: return 'SHT_DYNAMIC'
    if t==SHT_NOTE: return 'SHT_NOTE'
    if t==SHT_NOBITS: return 'SHT_NOBITS'
    if t==SHT_REL	: return 'SHT_REL	'
    if t==SHT_SHLIB: return 'SHT_SHLIB'
    if t==SHT_DYNSYM: return 'SHT_DYNSYM'
    if t==SHT_NUM	: return 'SHT_NUM	'
    if t==SHT_LOPROC: return 'SHT_LOPROC'
    if t==SHT_HIPROC: return 'SHT_HIPROC'
    if t==SHT_LOUSER: return 'SHT_LOUSER'
    if t==SHT_HIUSER: return 'SHT_HIUSER'

    if t >= SHT_LOPROC and t <= SHT_HIPROC:
        return 'PROC'
    if t >= SHT_LOUSER and t <= SHT_HIUSER:
        return 'USER'

    return 'UNKOWN'

def sectionFlagsToString(f):
    answer = []
    if f & SHF_WRITE:
        answer.append('WRITE')
    if f & SHF_ALLOC:
        answer.append('ALLOC')
    if f & SHF_EXECINSTR:
        answer.append('EXEC')

    return '|'.join(answer)

def dynamicTypeToString(t):
    if t==DT_NULL: return 'DT_NULL'
    if t==DT_NEEDED: return 'DT_NEEDED'
    if t==DT_PLTRELSZ: return 'DT_PLTRELSZ'
    if t==DT_PLTGOT: return 'DT_PLTGOT'
    if t==DT_HASH: return 'DT_HASH'
    if t==DT_STRTAB: return 'DT_STRTAB'
    if t==DT_SYMTAB: return 'DT_SYMTAB'
    if t==DT_RELA: return 'DT_RELA'
    if t==DT_RELASZ: return 'DT_RELASZ'
    if t==DT_RELAENT: return 'DT_RELAENT'
    if t==DT_STRSZ: return 'DT_STRSZ'
    if t==DT_SYMENT: return 'DT_SYMENT'
    if t==DT_INIT: return 'DT_INIT'
    if t==DT_FINI: return 'DT_FINI'
    if t==DT_SONAME: return 'DT_SONAME'
    if t==DT_RPATH: return 'DT_RPATH'
    if t==DT_SYMBOLIC: return 'DT_SYMBOLIC'
    if t==DT_REL: return 'DT_REL'
    if t==DT_RELSZ: return 'DT_RELSZ'
    if t==DT_RELENT: return 'DT_RELENT'
    if t==DT_PLTREL: return 'DT_PLTREL'
    if t==DT_DEBUG: return 'DT_DEBUG'
    if t==DT_TEXTREL: return 'DT_TEXTREL'
    if t==DT_JMPREL: return 'DT_JMPREL'
    if t==DT_BIND_NOW: return 'DT_BIND_NOW'
    if t==DT_INIT_ARRAY: return 'DT_INIT_ARRAY'
    if t==DT_FINI_ARRAY: return 'DT_FINI_ARRAY'
    if t==DT_INIT_ARRAYSZ: return 'DT_INIT_ARRAYSZ'
    if t==DT_FINI_ARRAYSZ: return 'DT_FINI_ARRAYSZ'
    if t==DT_RUNPATH: return 'DT_RUNPATH'
    if t==DT_FLAGS: return 'DT_FLAGS'
    if t==DT_ENCODING: return 'DT_ENCODING'
    if t==DT_PREINIT_ARRAY: return 'DT_PREINIT_ARRAY'
    if t==DT_PREINIT_ARRAYSZ: return 'DT_PREINIT_ARRAYSZ'
    if t==DT_NUM: return 'DT_NUM'
    return '<unknown>'
 
#------------------------------------------------------------------------------
# CLASSES REPRESENTING ELF STRUCTS
#------------------------------------------------------------------------------

class ElfElem:
    def __init__(self, offset, length, label):
        self.offset = offset
        self.length = length
        self.label = label

    def __len__(self):
        return self.length

    def __str_short__(self):
        return "[%08Xh,%08Xh) (%Xh) %s" % (self.offset, self.offset + len(self), len(self), self.label)

    def __str__(self):
        return self.__str_short__()

#------------------------------------------------------------------------------
# CLASSES REPRESENTING ELF STRUCTS
#------------------------------------------------------------------------------

# convention:
# class Elf_XXX (parent class)
# class Elf32_XXX
# class Elf64_XXX

# generic program header (32 bit and 64 bit versions derive from here)
class Elf_Phdr:
    def __init__(self, FP):
        if type(FP).__name__ == 'file':
            self.from_FP(FP)

    def from_FP(self, FP):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

    def __str_short__(self):
        return "[%08X,%08Xh) (%Xh) %s" % \
            (self.offset, self.offset + len(self), len(self), self.__class__.__name__)

    def __str__(self):
        buf = self.__str_short__() + ":\n"
        buf += '  p_type: %Xh (%s)\n' % (self.p_type, programHeaderTypeToString(self.p_type))
        buf += '  p_flags: %Xh (%s)\n' % (self.p_flags, strFlags(self.p_flags, PF_FLAG_VALUES, PF_FLAG_STRINGS))
        buf += '  p_offset: %Xh\n' % (self.p_offset)
        buf += '  p_vaddr: %Xh\n' % (self.p_vaddr)
        buf += '  p_paddr: %Xh\n' % (self.p_paddr)
        buf += '  p_filesz: %Xh\n' % (self.p_filesz)
        buf += '  p_memsz: %Xh\n' % (self.p_memsz)
        buf += '  p_align: %Xh\n' % (self.p_align)
        return buf

class Elf32_Phdr(Elf_Phdr):
    def from_FP(self, FP):
        self.offset = FP.tell()

        data = FP.read(len(self))
        (self.p_type, self.p_flags, self.p_offset, self.p_vaddr, self.p_paddr, 
            self.p_filesz, self.p_memsz, self.p_align) = \
            unpack('IIIIIIII', data)

    def __len__(self):
        return 32

class Elf64_Phdr(Elf_Phdr):
    def from_FP(self, FP):
        self.offset = FP.tell()

        data = FP.read(56)
        (self.p_type, self.p_flags, self.p_offset, self.p_vaddr, self.p_paddr, 
            self.p_filesz, self.p_memsz, self.p_align) = \
            unpack('IIQQQQQQ', data)

    def __len__(self):
        return 56

class Elf_Ehdr:
    def __init__(self, FP):
        if type(FP).__name__ == 'file':
            self.from_FP(FP)

    def from_FP(self, FP):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

    def __str_short__(self):
        return "[%08X,%08Xh) (%Xh) %s" % \
            (self.offset, self.offset + len(self), len(self), self.__class__.__name__)

    def __str__(self):
        buff = self.__str_short__() + ":\n"
        names = ['e_ident', 'e_type', 'e_machine', 'e_version', 'e_entry', 'e_phoff', \
                'e_shoff', 'e_flags', 'e_ehsize', 'e_phentsize', 'e_phnum', 'e_shentsize', \
                'e_shnum', 'e_shstrndx']
        vals =  [self.e_ident, self.e_type, self.e_machine, self.e_version, self.e_entry, \
            self.e_phoff, self.e_shoff, self.e_flags, self.e_ehsize, self.e_phentsize, \
            self.e_phnum, self.e_shentsize, self.e_shnum, self.e_shstrndx]
        for i in range(len(names)):
            buff += (names[i] + ': ').rjust(24)
            if names[i] == 'e_ident':
                buff += repr(vals[i])
            elif type(vals[i]).__name__ == 'int':
                buff += ("0x%08X (%d)" % (vals[i], vals[i])).ljust(24)
            else:
                buff += str(vals[i]).ljust(24);
            buff += "\n"
        return buff

class Elf32_Ehdr(Elf_Ehdr):
    def from_FP(self, FP):
        self.offset = FP.tell()

        data = FP.read(len(self));
        # strip 16 bytes off for e_ident
        self.e_ident = data[0:16]
        data = data[16:]
        # parse rest
        (self.e_type, self.e_machine, self.e_version, self.e_entry, 
            self.e_phoff, self.e_shoff, self.e_flags, self.e_ehsize, self.e_phentsize, 
            self.e_phnum, self.e_shentsize, self.e_shnum, self.e_shstrndx) = \
            unpack('HHIIIIIHHHHHH', data)

    def __len__(self):
        return 52

class Elf64_Ehdr(Elf_Ehdr):
    def from_FP(self, FP):
        self.offset = FP.tell()

        data = FP.read(len(self));
        # strip 16 bytes off for e_ident
        self.e_ident = data[0:16]
        data = data[16:]
        # parse rest
        (self.e_type, self.e_machine, self.e_version, self.e_entry, 
            self.e_phoff, self.e_shoff, self.e_flags, self.e_ehsize, self.e_phentsize, 
            self.e_phnum, self.e_shentsize, self.e_shnum, self.e_shstrndx) = \
            unpack('HHIQQQIHHHHHH', data)
        return 64

    def __len__(self):
        return 64

class Elf_Shdr:
    def __init__(self, FP):
        self.FP = FP
        self.offset = FP.tell()

        if type(FP).__name__ == 'file':
            self.from_FP(FP)
       
        self.strtab = None

    def __len__(self):
        raise NotImplementedError()

    def loadStringTable(self, strtab):
        self.strtab = strtab

    def getName(self):
        if self.strtab:
            return self.strtab[self.sh_name]
        else:
            return '<unknown>'

    def getBytes(self):
        self.FP.seek(self.offset)
        return self.FP.read(len(self))

    def __str_short__(self):
        return "[%08Xh,%08Xh) (%Xh) %s \"%s\"" % \
            (self.offset, self.offset + len(self), len(self), self.__class__.__name__, self.getName())

    def __str__(self):
        buff = self.__str_short__() + ":\n"

        fieldNames = ['sh_name', 'sh_type', 'sh_flags', 'sh_addr', 'sh_offset', 'sh_size', 'sh_link', \
                    'sh_info', 'sh_addralign', 'sh_entsize' ];

        fieldValues = [self.sh_name, self.sh_type, self.sh_flags, self.sh_addr, self.sh_offset, 
            self.sh_size, self.sh_link, self.sh_info, self.sh_addralign, self.sh_entsize]

        extra = { \
            'sh_type' : sectionTypeToString(self.sh_type), \
            'sh_flags' : sectionFlagsToString(self.sh_type), \
            'sh_name' : '"%s"' % self.getName()
        }

        for i in range(len(fieldNames)):
            fieldName = fieldNames[i]
            fieldValue = fieldValues[i]

            buff += (fieldName + ': ').rjust(24)
            if type(fieldValue).__name__ == 'int':
                buff += ("%Xh (%d)" % (fieldValue, fieldValue)).ljust(24)
            else:
                buff += str(fieldValue).ljust(24)

            if fieldName in extra:
                buff += ' %s' % extra[fieldName] 

            buff += "\n"
        return buff

class Elf32_Shdr(Elf_Shdr):
    def from_FP(self, FP):
        self.offset = FP.tell()

        # name set later when strings available
        data = FP.read(len(self));
        # parse rest
        (self.sh_name, self.sh_type, self.sh_flags, self.sh_addr, self.sh_offset, 
            self.sh_size, self.sh_link, self.sh_info, self.sh_addralign, self.sh_entsize) = \
            unpack('IIIIIIIIII', data)

    def __len__(self):
        return 40

class Elf64_Shdr(Elf_Shdr):
    def from_FP(self, FP):
        self.offset = FP.tell()

        # name set later when strings available
        data = FP.read(len(self));
        # parse rest
        (self.sh_name, self.sh_type, self.sh_flags, self.sh_addr, self.sh_offset, 
            self.sh_size, self.sh_link, self.sh_info, self.sh_addralign, self.sh_entsize) = \
            unpack('IIQQQQIIQQ', data)

    def __len__(self):
        return 64

class Elf_Sym:
    @staticmethod
    def typeToString(t):
        # Legal values for ST_TYPE subfield of st_info (symbol type).
        lookup = { 
            0:'STT_NOTYPE', 1:'STT_OBJECT', 2:'STT_FUNC',
            3:'STT_SECTION', 4:'STT_FILE', 5:'STT_COMMON',
            6:'STT_TLS', 7:'STT_NUM', 10:'STT_GNU_IFUNC',
            12:'STT_HIOS', 13:'PROC', 14:'PROC', 15:'PROC'
        }
    
        if t in lookup:
            return lookup[t]
    
        return '<unknown>'
    @staticmethod
    def bindtoString(b):
        lookup = { 0:'STB_LOCAL', 1:'STB_GLOBAL', \
            2:'STB_WEAK', 3:'STB_NUM' }

        if b in lookup:
            return lookup[b]

        return '<unknown>'

    def __init__(self, FP):
        self.FP = FP
        self.offset = FP.tell()
        self.strtab = None
        pass

    def from_FP(self, FP):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

    def to_FP(self, FP):
        raise NotImplementedError()

    def loadStringTable(self, strtab):
        self.strtab = strtab

    def getName(self):
        if self.strtab:
            return self.strtab[self.st_name]
        else:
            return '<unknown>'

    # emulating ELF32_ST_TYPE(), returns STT_NOTYPE, STT_OBJECT, STT_FUNC, ...
    def getType(self):
        return self.st_info & 0xF 

    # emulating ELF32_ST_BIND(), returns STB_LOCAL, STB_GLOBAL, STB_WEAK, ...
    def getBind(self):
        return self.st_info >> 4

    def isHashable(self):
        #print "self.info is 0x%X" % self.st_info
        #print "self.getType() returned: %d" % self.getType()
        #print "self.getName() returned: %s" % self.getName()

        return (self.getType() == STT_FUNC and self.getName() != '<unknown>')

    def __str__(self):
        answer = ''
        answer += '     name:\"%s\"\n' % self.getName()
        answer += '     info:0x%X bind:%s type:%s\n' % (self.st_info, \
            Elf_Sym.bindtoString(self.getBind()), Elf_Sym.typeToString(self.getType()))
        answer += '    other:0x%X\n' % self.st_other
        answer += '  section:%d\n' % self.st_shndx
        answer += '    value:0x%X\n' % self.st_value
        answer += '     size:0x%X\n' % self.st_size
        answer += '     hash:0x%08X' % dl_new_hash(self.getName())
        return answer

class Elf32_Sym(Elf_Sym):
    def __init__(self, FP):
        Elf_Sym.__init__(self, FP)

        # note! the ORDER (in addition to the data size) of these members is different
        # than my 64-bit counterpart!
        (self.st_name, self.st_value, self.st_size, self.st_info, self.st_other, self.st_shndx) = \
            unpack('IIIBBH', FP.read(16))

    def __len__(self):
        return 16

    def write(self):
        self.FP.seek(self.offset, os.SEEK_SET)

        # note! the ORDER (in addition to the data size) of these members is different
        # than my 32-bit counterpart!
        self.FP.write(pack('IBBHII', self.st_name, self.st_info, self.st_other, self.st_shndx, \
            self.st_value, self.st_size))

# the last two fields (st_value, st_size) are 64-bit instead of 32-bit
class Elf64_Sym(Elf_Sym):
    def __init__(self, FP):
        Elf_Sym.__init__(self, FP)
        
        (self.st_name, self.st_info, self.st_other, self.st_shndx, self.st_value, self.st_size) = \
            unpack('IBBHQQ', FP.read(24))

    def __len__(self):
        return 24

    def to_FP(self):
        self.FP.seek(self.offset, os.SEEK_SET)

        self.FP.write(pack('IBBHQQ', self.st_name, self.st_info, self.st_other, self.st_shndx, \
            self.st_value, self.st_size))

class Elf_Dyn:
    def __init__(self, FP):
        self.FP = FP
        self.offset = FP.tell()
        pass

    def from_FP(self, FP):
        raise NotImplementedError()

    def __str_short__(self):
        return "%08Xh: %s %s" % \
            (self.offset, self.__class__.__name__, 
                dynamicTypeToString(self.d_tag))

    def __str__(self):
        buff = self.__str_short__() + ": %Xh\n" % self.d_val
        return buff

class Elf32_Dyn(Elf_Dyn):
    def __init__(self, FP):
        Elf_Dyn.__init__(self, FP)

        (self.d_tag, self.d_val) = unpack('II', FP.read(8))
        self.d_ptr = self.d_val

    def __len__(self):
        return 8

class Elf64_Dyn(Elf_Dyn):
    def __init__(self, FP):
        Elf_Dyn.__init__(self, FP)

        (self.d_tag, self.d_val) = unpack('QQ', FP.read(16))
        self.d_ptr = self.d_val

    def __len__(self):
        return 16

#------------------------------------------------------------------------------
# CLASSES REPRESENTING ELF ELEMENTS THAT AREN'T STRUCTS
# example: .dynsym is an array of ElfXX_Sym entries terminated by an entry
#          tagged with DT_NULL
#------------------------------------------------------------------------------

class StringTable:
    def __init__(self, FP, size):
        self.FP = FP
        self.offset = FP.tell()

        self.size = size
        data = FP.read(size)
        self.table = unpack(('%d'%size)+'s', data)[0]

    def __getitem__(self, offset):
        end = offset;
        while self.table[end] != '\0':
            end += 1
        return self.table[offset:end]

    def replace_string(self, oldstr, newstr, ignoreCase=False):
        flags=0

        if (ignoreCase == True):
            flags = re.IGNORECASE

        matches = set(re.findall(oldstr, self.table, flags))
        for match in matches:
            self.table = self.table.replace(match, newstr)

    def __len__(self):
        return self.size

    def __str_short__(self):
        return "[%08Xh,%08Xh) (%Xh) string table" % (self.offset, self.offset + len(self), len(self))

    def __str__(self):
        buff = self.__str_short__() + ":\n"
        buff += 'offset'.rjust(12) + ' string' + "\n"
        for i in range(self.size):
            if self.table[i] != '\0':
                if i==0 or self.table[i-1] == '\0':
                    buff += ('%Xh' % i).rjust(12) + ' ' + self[i] + "\n"
        return buff

    def write(self):
        self.FP.seek(self.offset, os.SEEK_SET)
        self.FP.write(pack(('%d'%self.size)+'s', self.table))

# eg array of ElfXX_Sym for .symtab or .dynsym
class SymTable:
    def __init__(self, FP, n):
        self.FP = FP
        self.size = n
        self.syms = []

    def __len__(self):
        # define length as the number of symbols
        return len(self.syms)

    def __getitem__(self, key):
        return self.syms[key]

    def __setitem__(self, key, value):
        self.syms[key] = value

    def loadStringTable(self, strtab):
        for s in self.syms:
            s.loadStringTable(strtab)

    def write(self):
        for sym in self.syms:
            sym.write()

    def __str__(self):
        #buff = 'name'.rjust(24) + 'hash'.rjust(10) + "\n"
        buff = ''
        for (i,s) in enumerate(self.syms):
            buff += str(s)
            if i != len(self.syms)-1:
                buff += '\n--------\n'

        return buff

class SymTable32(SymTable):
    def __init__(self, FP, n):
        SymTable.__init__(self, FP, n)

        while n:
            self.syms.append(Elf32_Sym(FP))
            n -= len(self.syms[-1])

class SymTable64(SymTable):
    def __init__(self, FP, n):
        SymTable.__init__(self, FP, n)

        while n:
            self.syms.append(Elf64_Sym(FP))
            n -= len(self.syms[-1])
    

# HIGHER LEVEL
# array of ElfXX_Dyn, each with a tag, eg:
#
# Dynamic section at offset 0x11d458 contains 32 entries:
#   Tag        Type                         Name/Value
#  0x00000001 (NEEDED)                     Shared library: [libpthread.so.0]
#  0x00000001 (NEEDED)                     Shared library: [libdl.so.2]
#  0x00000001 (NEEDED)                     Shared library: [librt.so.1]
#  0x00000001 (NEEDED)                     Shared library: [libm.so.6]
#  0x00000001 (NEEDED)                     Shared library: [libstdc++.so.6]
#  0x00000001 (NEEDED)                     Shared library: [libcrypto.so.1.0.0]
#  0x00000001 (NEEDED)                     Shared library: [libgcc_s.so.1]
#  0x00000001 (NEEDED)                     Shared library: [libc.so.6]
#  0x00000001 (NEEDED)                     Shared library: [ld-linux.so.3]
#  0x0000000c (INIT)                       0x1c7b4
#  0x0000000d (FINI)                       0x102be4
#  0x00000019 (INIT_ARRAY)                 0x120c14
#  ...
# 

class Dynamic:
    def __init__(self, FP):
        self.dyns = []
        pass

    def __len__(self):
        return len(self.dyns)

    # we define key'd access as getting the first value of an entry tagged with the sought key
    def __getitem__(self, tag):
        for e in self.dyns:
            if e.d_tag == tag:
                return e.d_val

    # more generic access is to get every Dyn entry with a certain tag
    def get_entries(self, tag):
        answer = []
        for e in self.dyns:
            if e.d_tag == tag:
                answer.append(e)
        return answer

    def __str__(self):
        answer = ''
        for dyn in self.dyns:
            answer += str(dyn)
        return answer

class Dynamic32(Dynamic):
    # this st
    def __init__(self, FP):
        # read all Dyn entries
        self.dyns = []
        self.offset = FP.tell()

        while 1:    
            dyn = Elf32_Dyn(FP)
    
            if dyn.d_tag == DT_NULL:
                break

            self.dyns.append(dyn)

class Dynamic64(Dynamic):
    # this st
    def __init__(self, FP):
        # read all Dyn entries
        self.dyns = []
        self.offset = FP.tell()

        while 1:    
            dyn = Elf64_Dyn(FP)
    
            if dyn.d_tag == DT_NULL:
                break

            self.dyns.append(dyn)

class SVR4HashTable:
    def __init__(self, FP, Dynsym):
        self.FP = FP
        self.offset = FP.tell()

        self.dynsym = Dynsym

        (self.nbucket, self.nchain) = \
            unpack('II', FP.read(8))

        self.buckets = []
        for i in range(self.nbucket):
            self.buckets.append(unpack('I', FP.read(4))[0])

        self.chain = []
        for i in range(self.nchain):
            self.chain.append(unpack('I', FP.read(4))[0])

        self.size = FP.tell() - self.offset

    def hash(self, symname):
        h = 0
        g = 0
        for c in list(symname):
            h = (h<<4) + ord(c)
            h &= 0xFFFFFFFF

            g = h & 0xF0000000

            if(g):
                h ^= (g >> 24)

            h &= (g ^ 0xFFFFFFFF)

        return h

    def verify(self):
        for (i,sym) in enumerate(self.dynsym):
            if not sym.isHashable():
                continue

            hashVal = self.hash(sym.getName())
            bucketIdx = hashVal % self.nbucket
            symIdx = self.buckets[bucketIdx]

            print "symidx:%d \"%s...\" hashed to %08X (bucket: %d) -> symidx:%d" % \
                (i, sym.getName()[0:32], hashVal, bucketIdx, symIdx)

            while self.chain[symIdx] != 0:
                print "   check symbol index %d" % self.chain[symIdx]
                symIdx = self.chain[symIdx]

            # ok, now let's see if that symbol really is there....

    def recompute(self):
        self.buckets = [0] * len(self.buckets)
        self.chain = [0] * len(self.chain)

        bi2sis = {}
        for i in range(self.nbucket):
            bi2sis[i] = []

        for (symIdx, sym) in enumerate(self.dynsym):
            if not sym.isHashable():
                continue

            bucketIdx = self.hash(sym.getName()) % self.nbucket

            # remember collisions
            bi2sis[bucketIdx].append(symIdx)

            # set initial bucket values
            if self.buckets[bucketIdx] == 0:
                self.buckets[bucketIdx] = symIdx
                #print "  placed \"%s\" at bucket %d" % (sym.getName(), bucketIdx)

        for (symIdx, sym) in enumerate(self.dynsym):
            if not sym.getName():
                continue

            bucketIdx = self.hash(sym.getName()) % self.nbucket

            symIndices = bi2sis[bucketIdx]

            # if symbol indices {5, 12, 60} have the same hash, then:
            # chain[5] = 12
            # chain[12] = 60
            # chain[60] = 0
            if len(symIndices) > 1:
                for pair in zip(symIndices, symIndices[1:] + [0]):
                    #print '%d->%d ' % (pair[0], pair[1]),
                    self.chain[pair[0]] = pair[1]

                #print ''

    def write(self):
        self.FP.seek(self.offset, os.SEEK_SET)

        self.FP.write(pack('II', self.nbucket, self.nchain))

        for value in self.buckets:
            self.FP.write(pack('I', value))

        for value in self.chain:
            self.FP.write(pack('I', value))

    def __str__(self):
        answer = ''
        answer += '[%08Xh, %08Xh) (%Xh)\n' % \
            (self.offset, self.offset + self.size, self.size)

        for bucketNum in range(self.nbucket):
            symIdx = self.buckets[bucketNum]

            answer += 'bucket[%04d] = %d: \"%s...\"\n' % \
                (bucketNum, symIdx, self.dynsym.syms[symIdx].getName()[0:16])

            while 1:
                symIdx = self.chain[symIdx]

                if not symIdx:
                    break

                answer += '    -(chain)-> %d: \"%s...\"\n' % \
                    (symIdx, self.dynsym.syms[symIdx].getName()[0:16])

        #for i in range(self.nbucket):
        #    answer += 'bucket[%d] = %d\n' % (i, self.buckets[i])
        
        #for i in range(self.nchain):
        #    answer += 'chain[%d] = %d\n' % (i, self.chain[i])

        return answer

class GnuHashTable:
    def __init__(self, FP, Dynsym):
        self.FP = FP
        self.offset = FP.tell()

        self.dynsym = Dynsym

        (self.nbuckets, self.symndx, self.nbloomwords, self.shift2) = \
            unpack('IIII', FP.read(16))
        
        self.bloomwords = []
        for i in range(self.nbloomwords):
            # TODO: resolve this
            # 64-bit
            self.bloomwords.append(unpack('Q', FP.read(8))[0])
            # 32-bit
            #self.bloomwords.append(unpack('I', FP.read(4))[0])
        
        self.bucket_to_index = []
        for i in range(self.nbuckets):
            self.bucket_to_index.append(unpack('I', FP.read(4))[0])

        self.hash_values = []
        for i in range(len(self.dynsym) - self.symndx):
            self.hash_values.append(unpack('I', FP.read(4))[0])

        self.size = FP.tell() - self.offset

    def to_FP(self, FP):
        FP.write(pack('IIII', self.nbuckets, self.symndx, self.nbloomwords, self.shift2))
        for bw in self.bloomwords:
            FP.write(pack('Q', bw))
        for bti in self.bucket_to_index:
            FP.write(pack('I', bti))
        for hv in self.hash_values:
            FP.write(pack('I', hv))

    def recompute(self):
        self.nbuckets = len(self.bucket_to_index);
        self.symndx = len(self.dynsym) - len(self.hash_values); 

        # don't touch maskwords (Set by linker)
        if self.nbloomwords != 1:
            raise Exception("not implemented yet")

        # don't touch shift2
        
        # sanity check current order of symbols
        syms_unsorted = dynsym[self.symndx:]
        syms_sorted = sorted(syms_unsorted, key = lambda x: dl_new_hash(x.getName()) % self.nbuckets)

        for s in syms_sorted:
            print "%s: has hash: %08X" % (x.getName(), dl_new_hash(x.getName()))
        time.sleep(5)

        if syms_unsorted != syms_sorted:
            raise Exception("corresponding symbol table must be sorted non-increasing by bucket position");

        # re-hash values
        for i,v in enumerate(self.hash_values):
            self.hash_values[i] = dl_new_hash(self.dynsym[i + self.symndx].getName()) & 0xFFFFFFFE

        # write stop bits
        for i in range(len(self.hash_values)-1):
            if dl_new_hash(self.dynsym[self.symndx + i].getName()) % self.nbuckets != \
               dl_new_hash(self.dynsym[self.symndx + i + 1].getName()) % self.nbuckets:
                self.hash_values[i] |= 1
        self.hash_values[-1] |= 1

        # compute hash buckets
        for lookfor in range(self.nbuckets):
            self.bucket_to_index[lookfor] = 0
            for i in range(self.symndx, len(self.dynsym)):
                if dl_new_hash(self.dynsym[i].getName()) % self.nbuckets == lookfor:
                    self.bucket_to_index[lookfor] = i
                    break

        # compute bloom filter
        for i in range(self.nbloomwords):
            self.bloomwords[i] = 0

        for i in range(len(self.hash_values)):
            h1 = dl_new_hash(self.dynsym[self.symndx + i].getName())
            h2 = h1 >> self.shift2

            # rather than the hash functions having full reign over the bloom filter's bits
            # they are both corraled into a single word
            bloomword_i = (h1/64) % self.nbloomwords

            # and then randomly (as hash) distributed within this word
            b1 = (h1 % 64);
            b2 = (h2 % 64);
            self.bloomwords[bloomword_i] |= (1<<b1);
            self.bloomwords[bloomword_i] |= (1<<b2);

    def __str__(self):
        buff = ''
        buff += "[%08X, %08X) (%d)\n" % (self.offset, self.offset + self.size, self.size)
        buff += "   nbuckets: %Xh (%d)\n" % (self.nbuckets, self.nbuckets);
        buff += "     symndx: %Xh (%d)\n" % (self.symndx, self.symndx);
        buff += "nbloomwords: %Xh (%d)\n" % (self.nbloomwords, self.nbloomwords);
        buff += "     shift2: %Xh (%d)\n" % (self.shift2, self.shift2);
        for i,w in enumerate(self.bloomwords):
            buff += ('bloomword[0x%X]:' % i) + '%X'%w + "\n"
        for i,b in enumerate(self.bucket_to_index):
            buff += ('bucket_to_index[0x%X]:' % i) + '0x%X'%b + "\n"

        buff += 'hash_values:\n'
        buff += 'index'.rjust(7) + 'hash'.rjust(11) + 'name'.rjust(20) + 'hash&~1'.rjust(11) + \
                'bucket'.rjust(7) + "\n"
        for i,v in enumerate(self.hash_values):
            buff += ('0x%X' % i).rjust(7) + ('0x%08X' % v).rjust(11) + \
                    self.dynsym[self.symndx + i].getName().rjust(20) + \
                    ('0x%08X' % v).rjust(11) + \
                    ('0x%X' % (dl_new_hash(self.dynsym[self.symndx + i].getName()) % self.nbuckets)).rjust(7)
            buff += "\n"
        return buff

#------------------------------------------------------------------------------
# TOP LEVEL ABSTRACTION 
#------------------------------------------------------------------------------
class ElfFile:
    def __init__(self, path):
        self.FP = open(path, 'rb+')

        # validate, determine the mode (32/64)
        temp = self.FP.read(EI_NIDENT)
        self.FP.seek(0, os.SEEK_SET)

        magic = temp[0:SELFMAG]
        
        if temp[0:SELFMAG] != ELFMAG:
            raise Exception("missing ELF magic")
        
        self.class_ = unpack('B', temp[EI_CLASS])[0]
        if self.class_ != ELFCLASS32:
            if self.class_ != ELFCLASS64:
                raise Exception("unknown ELF class: " + repr(self.class_))

        # 1/3 read header
        #
        if self.class_ == ELFCLASS32: self.Ehdr = Elf32_Ehdr(self.FP)
        else: self.Ehdr = Elf64_Ehdr(self.FP)

        # 2/3 read program headers
        #
        self.Phdrs = []
        self.FP.seek(self.Ehdr.e_phoff)
        for i in range(self.Ehdr.e_phnum):
            if self.class_ == ELFCLASS32:
                self.Phdrs.append(Elf32_Phdr(self.FP))
            else:
                self.Phdrs.append(Elf64_Phdr(self.FP))

        # 3/3 read section headers
        #
        self.Shdrs = []
        self.FP.seek(self.Ehdr.e_shoff)
        for i in range(self.Ehdr.e_shnum):
            if self.class_ == ELFCLASS32:
                self.Shdrs.append(Elf32_Shdr(self.FP))
            if self.class_ == ELFCLASS64:
                self.Shdrs.append(Elf64_Shdr(self.FP))

        # get section string table (probably called ".shstrtab" and type SHT_STRTAB)
        self.stringTables = {}
        shstr_section = self.Shdrs[self.Ehdr.e_shstrndx]
        self.FP.seek(shstr_section.sh_offset)
        self.stringTables['sections'] = StringTable(self.FP, shstr_section.sh_size)

        # have sections look up their names in the string table
        for s in self.Shdrs:
            s.loadStringTable(self.stringTables['sections'])

        # get other string table(s) (that symbols, etc. reference)
        sh = self.getSectionHeader('.strtab')
        if sh:
            self.FP.seek(sh.sh_offset)
            self.stringTables['strtab'] = StringTable(self.FP, sh.sh_size)
            
        sh = self.getSectionHeader('.dynstr')
        if sh:
            self.FP.seek(sh.sh_offset)
            self.stringTables['dynstr'] = StringTable(self.FP, sh.sh_size)

        # dynamic section
        self.dynamic = None
        sh = self.getSectionHeader('.dynamic')

        if sh:
            self.FP.seek(sh.sh_offset)
            if(self.class_ == ELFCLASS32):
                self.dynamic = Dynamic32(self.FP)
            else:
                self.dynamic = Dynamic64(self.FP) 

        # symbol table: static
        self.symtab = None
        sh = self.getSectionHeader('.symtab')
        if sh:
            self.FP.seek(sh.sh_offset)
            if(self.class_ == ELFCLASS32):
                self.symtab = SymTable32(self.FP, sh.sh_size)
            else:
                self.symtab = SymTable64(self.FP, sh.sh_size)

            if 'strtab' in self.stringTables:
                self.symtab.loadStringTable(self.stringTables['strtab'])

        # symbol table: dynamic
        self.dynsym = None
        sh = self.getSectionHeader('.dynsym')
        if sh:
            self.FP.seek(sh.sh_offset)
            if(self.class_ == ELFCLASS32):
                self.dynsym = SymTable32(self.FP, sh.sh_size)
            else:
                self.dynsym = SymTable64(self.FP, sh.sh_size)

            if 'dynstr' in self.stringTables:
                self.dynsym.loadStringTable(self.stringTables['dynstr'])

        # hash section (could be old style, or new gnu style)
        self.hashtable = None

        sh = self.getSectionHeader('.hash')
        if sh:
            self.FP.seek(sh.sh_offset)
            self.hashtable = SVR4HashTable(self.FP, self.dynsym)

        sh = self.getSectionHeader('.GnuHashTable')
        if sh:
            self.FP.seek(sh.sh_offset)
            # TODO: make 32/64 GnuHashTable as bloom word size is dependent
            # on underlying arch
            self.hashtable = GnuHashTable(self.FP, self.dynsym)

    # access dynamic entry
    #
    def getDyns(self, d_type):
        result = []

        for d in self.dynamic:
            if d.d_tag == d_type:
                result.append(d)

        return result

    def getDyn(self, d_type):
        result = getDyns(self, d_type)

        if len(result) > 1:
            raise ValueError("ambiguous request for dyn entry (multiple entries of this type)")

        return result[0]

    # access section stuff
    #
    def getSectionHeader(self, x):
        answer = None

        if type(x) == type(1):
            answer = self.Shdrs[x]

        elif type(x) == type('a'):
            for s in self.Shdrs:
                if s.getName() == x:
                    answer = s
                    break
       
        return answer

    def getSection(self, x):
        if type(x) == type(1):
            self.FP.seek(self.Shdrs[x].sh_offset)
            return FP.read(self.Shdrs[x].sh_size)

        if type(x) == type('a'):
            for s in self.Shdrs:
                if s.getName() == x:
                    self.FP.seek(s.sh_offset)
                    return self.FP.read(s.sh_size)

        raise Exception("couldn't find section " + str(name))

    def __del__(self):
        self.FP.close()

    def __str__(self):
        answer = ''

        answer += "ELF Header\n"
        answer += "==========\n"
        answer += str(self.Ehdr)

        answer += '\n'
        answer += "Program Headers\n"
        answer += "===============\n"
        for phdr in self.Phdrs:
            answer += str(phdr)
            answer += '\n'

        answer += '\n'
        answer += "Section Headers\n"
        answer += "===============\n"
        for shdr in self.Shdrs:
            answer += str(shdr)
            answer += '\n'

        answer += '\n'
        answer += "Section Bodies\n"
        answer += "==============\n"
        for s in self.Shdrs:
            answer += "[%08Xh, %08Xh) section \"%s\" contents\n" % \
                (s.sh_offset, s.sh_offset + s.sh_size, s.getName())

        answer += '\n'
        answer += "Section String Table\n"
        answer += "====================\n"
        answer += str(self.stringTables['sections'])

        if self.symtab:
            answer += '\n'
            answer += 'Symbol Table\n'
            answer += '============\n'
            answer += str(self.symtab)

        if self.dynsym:
            answer += '\n'
            answer += 'Dynamic Symbol Table\n'
            answer += '====================\n'
            answer += str(self.dynsym)

        if self.dynamic:
            answer += '\n'
            answer += "Dynamic Section\n"
            answer += "===============\n"
            answer += str(self.dynamic)

        if self.hashtable:
            answer += '\n'
            answer += "Dynamic Hash Table\n"
            answer += "==================\n"
            answer += str(self.hashtable)

        return answer

#------------------------------------------------------------------------------
# GET-FROM-FILE CONVENIENCE FUNCTIONS
#------------------------------------------------------------------------------

# expects 32-bit little-endian ARM
def getScn(fname, scnname):
    ef = ElfFile(fname)
    return ef.getSection(scnname)

def setScnByName(fname, scnname, data):
    (shdr, contents) = getScn(fname, scnname)
    (z,z,z,z,sh_offset,sh_size) = struct.unpack("IIIIII", shdr[:24])
    if sh_size != len(data):
        print "major section replacement error!"
        return

    FP = open(fname, "r+b")
    if not FP:
        return
    #print "Seeking to: %X" % sh_offset
    FP.seek(sh_offset)
    FP.write(data)
    FP.close()

# expects 32-bit little-endian ARM elf executable
def getSym(fname, symname):
    (tmp,strtab) = getScn(fname, ".strtab");
    (tmp,symtab) = getScn(fname, ".symtab");

    if not strtab:
        return
    if not symtab:
        return

    # loop over symbols, searching
    value = None
    while symtab:
        (st_name,st_value,st_size,st_info,st_other,st_shndx) = \
            struct.unpack("IIIBBH", symtab[0:16])
        strname = strtab[st_name:].split('\0')[0]
        #print "on symbol -%s- (looking for -%s-)" % (strname, symname)
        if strname == symname:
            value = st_value
            break
        symtab = symtab[16:]

    if value == None:
        print "couldn't find symbol %s" % symname
        return;

    #print "returning %Xh" % value
    return value;

def replaceStrtabString(fname, symold, symnew):
    ef = ElfFile(fname)
    sh = ef.getSectionHeader('.strtab')
    sc = ef.getSection('.strtab')

    #print "old section: -%s-" % sc
    sc = string.replace(sc, symold, symnew)
    #print "new section: -%s-" % sc

    fobj = open(fname, 'r+b')
    fobj.seek(sh.sh_offset)
    fobj.write(sc)
    fobj.close()

# given a symbol foo, a symbol foo_len, and the fact that it exists
# in the text section, return this shit
def getTextElement(fname, sym):
    offs = getSym(fname, sym)
    leng = getSym(fname, sym+"_len");
    #print "symbol \"%s\" at offset: %Xh" % (sym, offs)
    #print "symbol \"%s_len\": %Xh" % (sym, leng)
    (tmp,text) = getScn(fname, ".text");
    return text[offs:offs+leng]

#------------------------------------------------------------------------------
# MISC 
#------------------------------------------------------------------------------
def dl_new_hash(s):
        h = 5381
        for c in s:
            h = (h*33 + ord(c)) % 4294967296 
        return h

#------------------------------------------------------------------------------
# MAIN 
#------------------------------------------------------------------------------
if __name__ == "__main__":

    if len(sys.argv) == 1:
        print "provide argument"
        sys.exit(-1)

    if sys.argv[1] == 'info':
        ef = ElfFile(sys.argv[2])
        print ef

    if sys.argv[1] == 'verifyhash':
        ef = ElfFile(sys.argv[2])
        ef.hashtable.verify()
        print ef.hashtable

    elif sys.argv[1] == 'rehash':
        print "%s -> %s" % (sys.argv[2], sys.argv[3])
        shutil.copy(sys.argv[2], sys.argv[3])
        ef = ElfFile(sys.argv[3])
        ef.hashtable.recompute()
        ef.hashtable.write()
        print ef.hashtable
        
    elif sys.argv[1] == 'scrub':
        print "%s -> %s" % (sys.argv[2], sys.argv[3])
        shutil.copy(sys.argv[2], sys.argv[3])
        ef = ElfFile(sys.argv[3])

        # replace the string in the string tables
        ef.stringTables['dynstr'].table = \
            ef.stringTables['dynstr'].table.replace('before', 'afterr')
        ef.stringTables['dynstr'].write()

        # recompute the hash table
        ef.hashtable.recompute()
        ef.hashtable.write()
        print ef.hashtable

    # eg: ./elf.py zerosect before.so after.so .debug_line
    # eg: ./elf.py zerosect before.so after.so .debug_line
    elif sys.argv[1] == 'zerosect':
        (fileA, fileB, secName) = sys.argv[2:]
        print "%s -> %s" % (fileA, fileB)
        #shutil.copy(fileA, fileB)

        (offs, size) = (0, 0)

        ef = ElfFile(fileA)
        hdr = ef.getSectionHeader(secName)
        if not hdr:
            raise Exception("ERROR: couldn't find section \"%s\"\n" % secName)
        offs = hdr.sh_offset
        size = hdr.sh_size
        ef = None

        fobj = open(fileA, 'rb+')
        fobj.seek(offs, os.SEEK_SET)
        fobj.write('\x00'*size)
        fobj.close()

    elif sys.argv[1] == 'wherestring':
        (fname, string) = sys.argv[2:]

        # first, find the offset:
        fobj = open(fname, 'rb')
        stuff = fobj.read()
        fobj.close()

        # collect all file offsets where string appears
        offsets = []
        curr = -1
        while 1:
            curr = stuff.find(string, curr+1)
            if curr == -1:
                break

            offsets.append(curr)

        # get section headers
        ef = ElfFile(fname)

        for o in offsets:
            # in which section?
            scnName = '<unknown>'
            for hdr in ef.Shdrs:
                if o >= hdr.sh_offset and o < (hdr.sh_offset + hdr.sh_size):
                    scnName = hdr.getName()
                    break

            print "found at offset %08X (%d) in section \"%s\"" % (o, o, scnName)




