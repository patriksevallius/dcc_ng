from loader import Loader
from overlay import Overlay
from relocator import Relocator

if __name__ == "__main__":
    loader = Loader("start.exe")
    loader.fetch_header()
    relocator = Relocator(loader)
    program = loader.load_program()
    overlay = Overlay("game.ovr", program)
    overlay.overlay_code()
    header = loader.header
    print(header)

    for instruction in program:
        print("%s %s" % (instruction.address, instruction))
