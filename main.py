from loader import Loader
from overlay import Overlay
from relocator import Relocator

if __name__ == "__main__":
    loader = Loader("start.exe")
    loader.fetch_header()
    relocator = Relocator(loader)
    overlay = Overlay("game.ovr")
    header = loader.header
    exe = loader.exe
    print(header)

    program = loader.load_program()
    for instruction in program:
        print("%s %s" % (instruction.address, instruction))
