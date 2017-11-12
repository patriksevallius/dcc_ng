import io

import struct

from address import Address


def is_unit_stub(program, offset):
    return program[offset] == 0xcd and \
        program[offset + 1] == 0x3f and \
        program[offset + 2] == 0x00 and \
        program[offset + 3] == 0x00


class Unit(object):
    def __init__(self, program, offset, overlay):
        self.program = program
        self.offset = Address(offset >> 4, offset & 0xf)
        (_, _, self.file_offset, self.code_size, self.relocation_size, self.entries) = \
            struct.unpack('<HHIHHH', self.program[offset:offset + 14])
        self.__extract_code(overlay)
        self.__extract_fixup_table(overlay)

    def __extract_code(self, overlay):
        overlay.seek(self.file_offset)
        self.code = overlay.read(self.code_size)

    def __extract_fixup_table(self, overlay):
        overlay.seek(self.file_offset + self.code_size)
        self.fixup_table = []
        for x in range(0, self.relocation_size // 2):
            (offset,) = struct.unpack("<H", overlay.read(2))
            self.fixup_table.append(offset)

    def fixup(self, address):
        for fixup in self.fixup_table:
            pass # no need to fixup since we place program at 0000:0000

    def __str__(self):
        return 'Unit: %s offset: %08X code size: %04X relocation size: %04X entries: %d\nFixup table:\n%s' % \
               (self.offset,
                self.file_offset,
                self.code_size,
                self.relocation_size,
                self.entries,
                '\n'.join(['%04x' % offset for offset in self.fixup_table]))


class Overlay(object):
    def __init__(self, filename, program):
        self.program = program
        self.overlay = io.open(filename, 'rb')

    def overlay_code(self):
        units = self.__extract_units()
        for unit in units:
            print(unit)
            unit_address = self.program.append_unit(unit)
            unit.fixup(unit_address)
            self.fix_jumps(unit, unit_address.segment)

    def __extract_units(self):
        program = self.program.program
        units = []
        offset = 0
        while offset < self.program.size:
            if is_unit_stub(program, offset):
                unit = Unit(program, offset, self.overlay)
                units.append(unit)
                offset += 32 + unit.entries * 5
            else:
                offset += 1
        return units

    def fix_jumps(self, unit, segment):
        for i in range(unit.entries):
            program_offset = unit.offset.segment * 16 + i * 5 + 32
            (_, offset) = struct.unpack('<HH', self.program.program[program_offset:program_offset+4])
            self.program.program[program_offset:program_offset+5] = struct.pack('<BHH', 0xEA, offset, segment)
