import struct
from loader import Loader

if __name__ == "__main__":
    loader = Loader("start.exe")
    loader.fetch_header()
    header = loader.header
    exe = loader.exe
    print(header)
#        relocator = Relocator(header)
    exe.seek(header.reloc_table_offset)
    reloc_table = []
    for x in range(0, header.num_relocs):
        (offset, segment) = struct.unpack("<HH", exe.read(4))
        reloc_table.append((offset, segment))

    # for x in range(0,header.num_relocs):
    #     print("Reloc %u" % (int(x) + 1))
    #     print("offset: %04x" % reloc_table[x][0])
    #     print("segment: %04x" % reloc_table[x][1])

    program = loader.load_program()
    for instruction in program:
        print("%s %s" % (instruction.address, instruction))
