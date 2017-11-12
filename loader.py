import io

from address import Address
from instructions import *


class HeaderFactory:
    def __init__(self, exe):
        self.exe = exe
        self.signature = None
        signature = list(self.exe.read(4))
        if(signature[0] == ord('M') and
           signature[1] == ord('Z')):
            exe.seek(0)
            exe_header = exe.read(28)
            (self.signature, self.bytes_in_last_block, self.blocks_in_file, self.num_relocs, self.header_paragraphs,
             self.min_extra_paragraphs, self.max_extra_paragraphs, self.ss, self.sp, self.checksum, self.ip, self.cs,
             self.reloc_table_offset, self.overlay_number) = struct.unpack('<HHHHHHHHHHHHHH', exe_header)
        else:
            print('signature mismatch')
            print(signature[0], ord('M'))

    def __str__(self):
        return "signature: %x\n" % self.signature +\
               "bytes in last block: %u\n" % self.bytes_in_last_block +\
               "blocks in file: %u\n" % self.blocks_in_file +\
               "num relocs: %u\n" % self.num_relocs +\
               "header paragraphs: %u\n" % self.header_paragraphs +\
               "min_extra_paragraphs: %u\n" % self.min_extra_paragraphs +\
               "max_extra_paragraphs: %u\n" % self.max_extra_paragraphs +\
               "ss: %04x\n" % self.ss +\
               "sp: %04x\n" % self.sp +\
               "checksum: %04x\n" % self.checksum +\
               "ip: %04x\n" % self.ip +\
               "cs: %04x\n" % self.cs +\
               "reloc table offset: %u\n" % self.reloc_table_offset +\
               "overlay number: %u\n" % self.overlay_number


class ProgramIterator(object):
    def __init__(self, program, address):
        self.program = program
        self.addresses = [address]
        self.visited = [address]

    def __next__(self):
        address = self.addresses.pop()
        instruction = Instruction.decode(self.program, address.segment * 16 + address.offset)
        instruction.address = address
        self.visited.append(address)

        if not (isinstance(instruction, ReturnImm16Instruction) or
                isinstance(instruction, ReturnInstruction) or
                isinstance(instruction, ReturnIntraInstruction) or
                isinstance(instruction, JumpShortInstruction)):
            next_address = address + len(instruction)
            self.addresses.append(next_address)

        if isinstance(instruction, CallInstruction):
            address = Address(instruction.segment_address, instruction.offset)
        elif (isinstance(instruction, CallNearInstruction) or
              isinstance(instruction, JumpShortInstruction)):
            address += len(instruction) + instruction.offset
        else:
            address = None
        if address and address not in self.visited:
            self.addresses.append(address)

        return instruction


class Program(object):
    def __init__(self, exe, size, address):
        self.size = size
        self.program = bytearray(exe.read(size))
        self.address = address

    def __iter__(self):
        return ProgramIterator(self.program, self.address)

    def append_unit(self, unit):
        adjustment = (16 - (len(self.program) & 0xf)) % 16
        if adjustment:
            self.program += bytes(adjustment)
        unit_address = Address(len(self.program) >> 4, len(self.program) & 0xf)
        self.program += unit.code
        return unit_address


class Loader:
    def __init__(self, filename):
        self.exe = io.open(filename, 'rb')
        self.header = None
        self.program = None
        self.header_size = 0

    def fetch_header(self):
        self.header = HeaderFactory(self.exe)
        if self.header.bytes_in_last_block:
            self.total_size = (self.header.blocks_in_file - 1) * 512 + self.header.bytes_in_last_block
        else:
            self.total_size = self.header.blocks_in_file * 512
        self.header_size = self.header.header_paragraphs * 16
        self.program_size = self.total_size - self.header_size

    def load_program(self):
        self.exe.seek(self.header_size)
        self.program = Program(self.exe, self.program_size, Address(0, self.header.ip))
        return self.program
