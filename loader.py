import io

from address import Address
from instructions import *


class HeaderFactory:
    def __init__(self,exe):
        self.exe = exe
        self.signature = None
        signature = list(self.exe.read(4))
        if( signature[0] == ord('M') and
            signature[1] == ord('Z')):
            exe.seek(0)
            exe_header = exe.read(28)
            (self.signature, self.bytes_in_last_block, self.blocks_in_file, self.num_relocs, self.header_paragraphs,
             self.min_extra_paragraphs, self.max_extra_paragraphs, self.ss, self.sp, self.checksum, self.ip, self.cs,
             self.reloc_table_offset, self.overlay_number ) = struct.unpack('<HHHHHHHHHHHHHH',exe_header)
        else:
            print('signature mismatch')
            print(signature[0], ord('M'))
        print(self.signature)

    def __str__(self):
        return "signature: %x\n" % (self.signature) + "bytes in last block: %u\n" % (self.bytes_in_last_block) +\
               "blocks in file: %u\n" % (self.blocks_in_file) + "num relocs: %u\n" % (self.num_relocs) +\
               "header paragraphs: %u\n" % (self.header_paragraphs) +\
               "min_extra_paragraphs: %u\n" % (self.min_extra_paragraphs) +\
               "max_extra_paragraphs: %u\n" % (self.max_extra_paragraphs) +\
               "ss: %04x\n" % (self.ss) + "sp: %04x\n" % (self.sp) +\
               "checksum: %04x\n" % (self.checksum) + "ip: %04x\n" % (self.ip) +\
               "cs: %04x\n" % (self.cs) + "reloc table offset: %u\n" % (self.reloc_table_offset) +\
               "overlay number: %u\n" % (self.overlay_number)


class ProgramIterator(object):
    def __init__(self, program, address):
        self.program = program
        self.addresses = [address]

    def __next__(self):
        address = self.addresses.pop()
        instruction = Instruction.decode(self.program, address.segment * 16 + address.offset)
        instruction.address = address

        if not (isinstance(instruction, ReturnImm16Instruction) or
                    isinstance(instruction, ReturnInstruction) or
                    isinstance(instruction, ReturnIntraInstruction) or
                    isinstance(instruction, JumpShortInstruction)):
            self.addresses.append(address+len(instruction))

        if isinstance(instruction, CallInstruction):
            self.addresses.append(Address(instruction.segment_address, instruction.offset))
        elif isinstance(instruction, CallNearInstruction):
            self.addresses.append(address + (len(instruction) + instruction.offset))
        elif isinstance(instruction, JumpShortInstruction):
            self.addresses.append(Address(address.segment, address.offset + len(instruction) + instruction.offset))

        return instruction


class Program(object):
    def __init__(self, exe, size, address):
        self.program = exe.read(size)
        self.address = address

    def __iter__(self):
        return ProgramIterator(self.program, self.address)


class Loader:
    def __init__(self, filename):
        self.exe = io.open(filename, 'rb')

    def fetch_header(self):
        self.header = HeaderFactory(self.exe)

    def load_program(self):
        if( self.header.bytes_in_last_block ):
            total_size = (self.header.blocks_in_file - 1) * 512 + self.header.bytes_in_last_block
        else:
            total_size = self.header.blocks_in_file * 512
        header_size = self.header.header_paragraphs * 16
        program_size = total_size - header_size
        
        self.exe.seek(header_size)
        self.program = Program(self.exe, program_size, Address(0, self.header.ip))
        return self.program
    