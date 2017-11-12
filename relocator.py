import struct


class Relocator(object):
    def __init__(self, loader):
        self.header = loader.header
        self.exe = loader.exe

    def __create_relocation_table(self):
        self.exe.seek(self.header.reloc_table_offset)
        self.reloc_table = []
        for x in range(0, self.header.num_relocs):
            (offset, segment) = struct.unpack("<HH", exe.read(4))
            self.reloc_table.append((offset, segment))

    def __str__(self):
        self.__create_relocation_table()
        str = ''
        for x in range(0, header.num_relocs):
            str += "Reloc %u\n" % (int(x) + 1)
            str += "offset: %04x\n" % self.reloc_table[x][0]
            str += "segment: %04x\n" % self.reloc_table[x][1]
        return str
