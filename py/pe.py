#!/usr/bin/python
#------------------------------------------------------------------------------
#
#    Copyright 2011-2014 Andrew Lamoureux
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

#------------------------------------------------------------------------------
# globals
#------------------------------------------------------------------------------
IMAGE_NUMBEROF_DIRECTORY_ENTRIES = 16
IMAGE_SIZEOF_SHORT_NAME = 8
IMAGE_SIEOF_SECTION_HEADER = 40
IMAGE_SIZEOF_FILE_HEADER = 20
IMAGE_SIZEOF_SECTION_HEADER = 40
IMAGE_SIZEOF_SYMBOL = 18
IMAGE_SIZEOF_ARCHIVE_MEMBER_HDR = 60

#------------------------------------------------------------------------------
# classes representing PE structs
#------------------------------------------------------------------------------
class image_dos_header:
    def __init__(self, FP):
        self.FP = FP
        self.offset = FP.tell()
        
        self.e_magic = unpack('<H', FP.read(2))[0]
        self.e_cblp = unpack('<H', FP.read(2))[0]
        self.e_cp = unpack('<H', FP.read(2))[0]
        self.e_crlc = unpack('<H', FP.read(2))[0]
        self.e_cparhdr = unpack('<H', FP.read(2))[0]
        self.e_minalloc = unpack('<H', FP.read(2))[0]
        self.e_maxalloc = unpack('<H', FP.read(2))[0]
        self.e_ss = unpack('<H', FP.read(2))[0]
        self.e_sp = unpack('<H', FP.read(2))[0]
        self.e_csum = unpack('<H', FP.read(2))[0]
        self.e_ip = unpack('<H', FP.read(2))[0]
        self.e_cs = unpack('<H', FP.read(2))[0]
        self.e_lfarlc = unpack('<H', FP.read(2))[0]
        self.e_ovno = unpack('<H', FP.read(2))[0]
        self.e_res = FP.read(2 * 4) # WORD e_res[4]
        self.e_oemid = unpack('<H', FP.read(2))[0]
        self.e_oeminfo = unpack('<H', FP.read(2))[0]
        self.e_res2 = FP.read(2 * 10) # WORD e_res2[10]
        self.e_lfanew = unpack('<I', FP.read(4))[0]

#    def toNode(self, root):
#        self.FP.seek(self.offset)
#        subnode = root.addNode("image_dos_header", self.offset, 0, self.FP)
#
#        subnode.data16("e_magic")
#        subnode.data16("e_cblp")
#        subnode.data16("e_cp")
#        subnode.data16("e_crlc")
#        subnode.data16("e_cparhdr")
#        subnode.data16("e_minalloc")
#        subnode.data16("e_maxalloc")
#        subnode.data16("e_ss")
#        subnode.data16("e_sp")
#        subnode.data16("e_csum")
#        subnode.data16("e_ip")
#        subnode.data16("e_cs")
#        subnode.data16("e_lfarlc")
#        subnode.data16("e_ovno")
#        subnode.data16("e_res[0]")
#        subnode.data16("e_res[1]")
#        subnode.data16("e_res[2]")
#        subnode.data16("e_res[3]")
#        subnode.data16("e_oemid")
#        subnode.data16("e_oeminfo")
#        subnode.data16("e_res2[0]")
#        subnode.data16("e_res2[1]")
#        subnode.data16("e_res2[2]")
#        subnode.data16("e_res2[3]")
#        subnode.data16("e_res2[4]")
#        subnode.data16("e_res2[5]")
#        subnode.data16("e_res2[6]")
#        subnode.data16("e_res2[7]")
#        subnode.data16("e_res2[8]")
#        subnode.data16("e_res2[9]")
#        subnode.data32("e_lfanew")
#
#        subnode.setLen(self.FP.tell() - self.offset)

class image_nt_headers:
   def __init__(self, FP):
        self.FP = FP
        self.offset = FP.tell()
       
        self.signature = unpack('<I', FP.read(4))[0];
        self.image_file_header = image_file_header(self.FP);
        self.image_optional_header = image_optional_header(self.FP);

#   def toNode(self, root):
#        self.FP.seek(self.offset)
#
#        subnode = root.addNode("image_nt_headers", self.offset, 0, self.FP)
#
#        subnode.DATA32("Signature")
#
#        self.image_file_header.toNode(subnode);
#        self.image_optional_header.toNode(subnode);
#
#        subnode.setLen(self.FP.tell() - self.offset)

class image_file_header:
    def __init__(self, FP):
        self.FP = FP
        self.offset = FP.tell()

        self.Machine = unpack('<H', FP.read(2))[0]
        self.NumberOfSections = unpack('<H', FP.read(2))[0]
        self.TimeDateStamp = unpack('<I', FP.read(4))[0]
        self.PointerToSymbolTable = unpack('<I', FP.read(4))[0]
        self.NumberOfSymbols = unpack('<I', FP.read(4))[0]
        self.SizeOfOptionalHeader = unpack('<H', FP.read(2))[0]
        self.Characteristics = unpack('<H', FP.read(2))[0]

#    def toNode(self, root):
#        self.FP.seek(self.offset)
#        subnode = root.addNode("image_file_header", self.offset, 0, self.FP)
#
#        subnode.data16("Machine")
#        subnode.data16("NumberOfSections")
#        subnode.data32("TimeDateStamp")
#        subnode.data32("PointerToSymbolTable")
#        subnode.data32("NumberOfSymbols")
#        subnode.data16("SizeOfOptionalHeader")
#        subnode.data16("Characteristics")
#
#        subnode.setLen(self.FP.tell() - self.offset)

class image_data_directory:
    def __init__(self, FP):
        self.FP = FP
        self.offset = FP.tell()
        
        self.VirtualAddress = unpack('<I', FP.read(4))[0]
        self.Size = unpack('<I', FP.read(4))[0]

#    def toNode(self, root):
#        self.FP.seek(self.offset)
#        subnode = root.addNode("image_data_directory", self.offset, 8, self.FP)
#
#        subnode.data32("VirtualAddress")
#        subnode.data32("Size")
        
class image_optional_header:
    def __init__(self, FP):
        self.FP = FP
        self.offset = FP.tell()

        self.Magic = unpack('<H', FP.read(2))[0]
        self.MajorLinkerVersion = unpack('<B', FP.read(1))[0]
        self.MinorLinkerVersion = unpack('<B', FP.read(1))[0]
        self.SizeOfCode = unpack('<I', FP.read(4))[0]
        self.SizeOfInitializedData = unpack('<I', FP.read(4))[0]
        self.SizeOfUninitializedData = unpack('<I', FP.read(4))[0]
        self.AddressOfEntryPoint = unpack('<I', FP.read(4))[0]
        self.BaseOfCode = unpack('<I', FP.read(4))[0]
        self.BaseOfData = unpack('<I', FP.read(4))[0]
        self.ImageBase = unpack('<I', FP.read(4))[0]
        self.SectionAlignment = unpack('<I', FP.read(4))[0]
        self.FileAlignment = unpack('<I', FP.read(4))[0]
        self.MajorOperatingSystemVersion = unpack('<H', FP.read(2))[0]
        self.MinorOperatingSystemVersion = unpack('<H', FP.read(2))[0]
        self.MajorImageVersion = unpack('<H', FP.read(2))[0]
        self.MinorImageVersion = unpack('<H', FP.read(2))[0]
        self.MajorSubsystemVersion = unpack('<H', FP.read(2))[0]
        self.MinorSubsystemVersion = unpack('<H', FP.read(2))[0]
        self.Win32VersionValue = unpack('<I', FP.read(4))[0]
        self.SizeOfImage = unpack('<I', FP.read(4))[0]
        self.SizeOfHeaders = unpack('<I', FP.read(4))[0]
        self.CheckSum = unpack('<I', FP.read(4))[0]
        self.Subsystem = unpack('<H', FP.read(2))[0]
        print "at offset 0x%X" % FP.tell()
        self.DllCharacteristics = unpack('<H', FP.read(2))[0]
        print "characteristics is: 0x%X" % self.DllCharacteristics
        self.SizeOfStackReserve = unpack('<I', FP.read(4))[0]
        self.SizeOfStackCommit = unpack('<I', FP.read(4))[0]
        self.SizeOfHeapReserve = unpack('<I', FP.read(4))[0]
        self.SizeOfHeapCommit = unpack('<I', FP.read(4))[0]
        self.LoaderFlags = unpack('<I', FP.read(4))[0]
        self.NumberOfRvaAndSizes = unpack('<I', FP.read(4))[0]

        # DataDirectory is just an array of IMAGE_DATA_DIRECTORY where
        # each index of the array has a assigned meaning
        self.DataDirectory = []
        for i in range(IMAGE_NUMBEROF_DIRECTORY_ENTRIES):
            self.DataDirectory.append(image_data_directory(self.FP));

    def dataDirIndexToString(self, index):
        lookup = [ "IMAGE_DIRECTORY_ENTRY_EXPORT", "IMAGE_DIRECTORY_ENTRY_IMPORT", 
                        "IMAGE_DIRECTORY_ENTRY_RESOURCE", "IMAGE_DIRECTORY_ENTRY_EXCEPTION", 
                        "IMAGE_DIRECTORY_ENTRY_SECURITY", "IMAGE_DIRECTORY_ENTRY_BASERELOC", 
                        "IMAGE_DIRECTORY_ENTRY_DEBUG", "IMAGE_DIRECTORY_ENTRY_ARCHITECTURE", 
                        "IMAGE_DIRECTORY_ENTRY_GLOBALPTR", "IMAGE_DIRECTORY_ENTRY_TLS", 
                        "IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG", "IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT", 
                        "IMAGE_DIRECTORY_ENTRY_IAT", "IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT", 
                        "IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR"  ]

        if index < 0 or index > 14:
            return "UNKNOWN"

        return lookup[index]

#    def toNode(self, root):
#        self.FP.seek(self.offset)
#        subnode = root.addNode("image_optional_header", self.offset, 0, self.FP)
#
#        subnode.data32("ImageBase")
#        subnode.data32("SectionAlignment")
#        subnode.data32("FileAlignment")
#        subnode.data16("MajorOperatingSystemVersion")
#        subnode.data16("MinorOperatingSystemVersion")
#        subnode.data16("MajorImageVersion")
#        subnode.data16("MinorImageVersion")
#        subnode.data16("MajorSubsystemVersion")
#        subnode.data16("MinorSubsystemVersion")
#        subnode.data32("Win32VersionValue")
#        subnode.data32("SizeOfImage")
#        subnode.data32("SizeOfHeaders")
#        subnode.data32("CheckSum")
#        subnode.data16("Subsystem")
#        subnode.data16("DllCharacteristics")
#        subnode.data32("SizeOfStackReserve")
#        subnode.data32("SizeOfStackCommit")
#        subnode.data32("SizeOfHeapReserve")
#        subnode.data32("SizeOfHeapCommit")
#        subnode.data32("LoaderFlags")
#        subnode.data32("NumberOfRvaAndSizes")
#
#        for i in range(IMAGE_NUMBEROF_DIRECTORY_ENTRIES):
#            ddnode = subnode.addNode("DataDirectory[%d] (%s)" % (i, self.dataDirIndexToString(i)), self.FP.tell(), 8, self.FP)
#            self.DataDirectory[i].toNode(ddnode);
#
#        subnode.setLen(self.FP.tell() - self.offset)

class image_section_header:
    def __init__(self, FP):
        self.FP = FP
        self.offset = FP.tell()

        self.Name = FP.read(IMAGE_SIZEOF_SHORT_NAME)
        self.VirtualSize = unpack('<I', FP.read(4))[0];
        self.VirtualAddress = unpack('<I', FP.read(4))[0];
        self.SizeOfRawData = unpack('<I', FP.read(4))[0]
        self.PointerToRawData = unpack('<I', FP.read(4))[0]
        self.PointerToRelocations = unpack('<I', FP.read(4))[0]
        self.PointerToLineNumbers = unpack('<I', FP.read(4))[0]
        self.NumberOfRelocations = unpack('<H', FP.read(2))[0]
        self.NumberOfLineNumbers = unpack('<H', FP.read(2))[0]
        self.Characteristics = unpack('<I', FP.read(4))[0]

#    def toNode(self, root):
#        self.FP.seek(self.offset)
#        subnode = root.addNode("image_section_header", self.offset, IMAGE_SIZEOF_SECTION_HEADER, self.FP)
#
#        print "offset now: %d" % self.FP.tell()
#        subnode.addNode("Name: \"%s\"" % self.Name, self.FP.tell(), IMAGE_SIZEOF_SHORT_NAME, self.FP)
#        self.FP.seek(IMAGE_SIZEOF_SHORT_NAME, os.SEEK_CUR)
#        print "offset now: %d" % self.FP.tell()
#        subnode.data32("VirtualSize")
#        subnode.data32("VirtualAddress")
#        subnode.data32("SizeOfRawData")
#        subnode.data32("PointerToRawData")
#        subnode.data32("PointerToRelocations")
#        subnode.data32("PointerToLineNumbers")
#        subnode.data16("NumberOfRelocations")
#        subnode.data16("NumberOfLineNumbers")
#        subnode.data32("Characteristics")
#
#        subnode.setLabel("image_section_header \"%s\"" % self.Name);

#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    FP = open(sys.argv[1], 'rb')

    # read image dos header
    idh = image_dos_header(FP)

    # seek to image optional headers, parse
    FP.seek(idh.e_lfanew)
    inh = image_nt_headers(FP)

    # immediately following is the section header table
    section_headers_n = inh.image_file_header.NumberOfSections
    section_headers = []
    for i in range(section_headers_n):
        section_headers.append(image_section_header(FP))

    

