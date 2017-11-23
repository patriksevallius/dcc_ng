import struct


class Immediate8:
    def __init__(self, immediate8):
        self.immediate8 = immediate8

    def __str__(self):
        if self.immediate8 <= 8:
            return '%d' % self.immediate8
        return '%02Xh' % self.immediate8

    def __len__(self):
        return 1


class Immediate16:
    def __init__(self, immediate16):
        self.immediate16 = immediate16

    def __str__(self):
        if self.immediate16 < 16:
            return '%d' % self.immediate16
        elif self.immediate16 < 256:
            return '%02Xh' % self.immediate16
        return '%04Xh' % self.immediate16

    def __len__(self):
        return 2


class Register:
    def __init__(self, register, word):
        self.register = register
        self.word = word

    def __str__(self):
        if self.register == 0:
            return 'ax' if self.word else 'al'
        elif self.register == 1:
            return 'cx' if self.word else 'cl'
        elif self.register == 2:
            return 'dx' if self.word else 'dl'
        elif self.register == 3:
            return 'bx' if self.word else 'bl'
        elif self.register == 4:
            return 'sp' if self.word else 'ah'
        elif self.register == 5:
            return 'bp' if self.word else 'ch'
        elif self.register == 6:
            return 'si' if self.word else 'dh'
        elif self.register == 7:
            return 'di' if self.word else 'bh'
        print('Unknown register %d' % self.register)
        raise Exception


class SegmentRegister:
    def __init__(self, register):
        if register > 3:
            raise Exception('Invalid sr', register)
        self.register = register

    def __str__(self):
        if self.register == 0:
            return 'es'
        elif self.register == 1:
            return 'cs'
        elif self.register == 2:
            return 'ss'
        elif self.register == 3:
            return 'ds'


class ModReg:
    def __init__(self, modreg, word, extra=None):
        self.mod = (modreg & 0xc0) >> 6
        self.reg = (modreg & 0x38) >> 3
        self.rm = modreg & 0x07
        self.word = word
        self.extra = extra

    def __str__(self):
        if self.mod == 0:
            if self.rm == 0:
                return '[bx+si]'
            elif self.rm == 1:
                return '[bx+di]'
            elif self.rm == 2:
                return '[bp+si]'
            elif self.rm == 3:
                return '[bp+di]'
            elif self.rm == 4:
                return '[si]'
            elif self.rm == 5:
                return '[di]'
            elif self.rm == 6:
                return '%s' % Immediate16(struct.unpack('<H', self.extra[:2])[0])
            elif self.rm == 7:
                return '[bx]'
        elif self.mod == 1:
            disposition = Immediate8(struct.unpack('<b', self.extra[:1])[0])
            if self.rm == 0:
                return '[bx+si+%s]' % disposition
            elif self.rm == 1:
                return '[bx+di+%s]' % disposition
            elif self.rm == 2:
                return '[bp+si+%s]' % disposition
            elif self.rm == 3:
                return '[bp+si+%s]' % disposition
            elif self.rm == 4:
                return '[si+%s]' % disposition
            elif self.rm == 5:
                return '[di+%s]' % disposition
            elif self.rm == 6:
                return '[bp+%s]' % disposition
            elif self.rm == 7:
                return '[bx+%s]' % disposition
        elif self.mod == 2:
            disposition = Immediate16(struct.unpack('<h', self.extra[:2])[0])
            if self.rm == 0:
                return '[bx+si+%s]' % disposition
            elif self.rm == 1:
                return '[bx+di+%s]' % disposition
            elif self.rm == 2:
                return '[bp+si+%s]' % disposition
            elif self.rm == 3:
                return '[bp+si+%s]' % disposition
            elif self.rm == 4:
                return '[si+%s]' % disposition
            elif self.rm == 5:
                return '[di+%s]' % disposition
            elif self.rm == 6:
                return '[bp+%s]' % disposition
            elif self.rm == 7:
                return '[bx+%s]' % disposition
        elif self.mod == 3:
            return '%s' % Register(self.rm, self.word)

    def __repr__(self):
        return 'ModReg(mod=%d, reg=%d, rm=%d, word=%s)' %\
               (self.mod, self.reg, self.rm, self.word)

    def __len__(self):
        if self.mod == 0:
            if self.rm == 6:
                return 3
            else:
                return 1
        elif self.mod == 1:
            return 2
        elif self.mod == 2:
            return 3
        elif self.mod == 3:
            return 1


class RegToRegMemBaseInstruction:
    def __init__(self, data):
        self.data = data
        self.direction = self.get_direction()
        self.word = self.get_size()
        self.modreg = ModReg(data[1], self.word, data[2:])

        self.source = self.get_source()
        self.dest = self.get_destination()

    def get_size(self):
        return self.data[0] & 0x01 == 0x01

    def get_direction(self):
        return self.data[0] & 0x02 == 0x02

    def get_source(self):
        if self.direction == 0:
            return self.modreg
        else:
            return Register(self.modreg.reg, self.word)

    def get_destination(self):
        if self.direction == 0:
            return Register(self.modreg.reg, self.word)
        else:
            return self.modreg

    def __len__(self):
        return 1 + len(self.modreg)


class AddInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'add %s, %s' % (self.source, self.dest)


class AddAlInstruction:
    def __init__(self, data):
        self.immediate = Immediate8(struct.unpack('<B', data)[0])

    def __str__(self):
        return 'add al, %s' % self.immediate

    def __len__(self):
        return 2


class AddAxInstruction:
    def __init__(self, data):
        self.immediate = Immediate16(struct.unpack('<H', data)[0])

    def __str__(self):
        return 'add ax, %s' % self.immediate

    def __len__(self):
        return 3


class PushESInstruction:
    def __str__(self):
        return 'push es'

    def __len__(self):
        return 1


class PopESInstruction:
    def __str__(self):
        return 'pop es'

    def __len__(self):
        return 1


class OrInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'or %s, %s' % (self.source, self.dest)


class OrAlImm8Instruction:
    def __init__(self, data):
        self.immediate = Immediate8(struct.unpack('<B', data)[0])

    def __str__(self):
        return 'or al, %s' % self.immediate

    def __len__(self):
        return 2


class OrAxImm16Instruction:
    def __init__(self, data):
        self.immediate = Immediate16(struct.unpack('<H', data)[0])

    def __str__(self):
        return 'or ax, %s' % self.immediate

    def __len__(self):
        return 3


class PushCSInstruction:
    def __str__(self):
        return 'push cs'

    def __len__(self):
        return 1


class AdcInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'adc %s, %s' % (self.source, self.dest)


class AdcAlImm8Instruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'adc al, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class AdcAxImm16Instruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'adc ax, %04Xh' % self.immediate16

    def __len__(self):
        return 3


class PushSSInstruction:
    def __str__(self):
        return 'push ss'

    def __len__(self):
        return 1


class PopSSInstruction:
    def __str__(self):
        return 'pop ss'

    def __len__(self):
        return 1


class SBBInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'sbb %s, %s' % (self.source, self.dest)


class SBBAlImm8Instruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'sbb al, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class SBBAxImm16Instruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'sbb ax, %04Xh' % self.immediate16

    def __len__(self):
        return 3


class PushDSInstruction:
    def __str__(self):
        return 'push ds'

    def __len__(self):
        return 1


class PopDSInstruction:
    def __str__(self):
        return 'pop ds'

    def __len__(self):
        return 1


class AndInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'and %s, %s' % (self.source, self.dest)


class AndALImm8Instruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'and al, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class AndAXImm16Instruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'and ax, %04Xh' % self.immediate16

    def __len__(self):
        return 3


class ESSegmentOverride:
    def __init__(self, instruction):
        self.instruction = instruction
        self.instruction.segment = 'es'

    def __str__(self):
        return str(self.instruction)

    def __len__(self):
        return len(self.instruction) + 1


class DAAInstruction:
    def __str__(self):
        return 'daa'

    def __len__(self):
        return 1


class SubInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'sub %s, %s' % (self.source, self.dest)


class SubAlImm8Instruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'sub al, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class SubAxImm16Instruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'sub ax, %04Xh' % self.immediate16

    def __len__(self):
        return 3


class CSSegmentOverride:
    def __init__(self, instruction):
        self.instruction = instruction
        self.instruction.segment = 'cs'

    def __str__(self):
        return str(self.instruction)

    def __len__(self):
        return len(self.instruction) + 1


class XorInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'xor %s, %s' % (self.source, self.dest)


class SSSegmentOverride:
    def __init__(self, instruction):
        self.instruction = instruction
        self.instruction.segment = 'ss'

    def __str__(self):
        return str(self.instruction)

    def __len__(self):
        return len(self.instruction) + 1


class CmpInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'cmp %s, %s' % (self.source, self.dest)


class CmpAlImm8Instruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'cmp al, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class CmpAxImm16Instruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'cmp ax, %04Xh' % self.immediate16

    def __len__(self):
        return 3


class DSSegmentOverride:
    def __init__(self, instruction):
        self.instruction = instruction
        self.instruction.segment = 'ds'

    def __str__(self):
        return str(self.instruction)

    def __len__(self):
        return len(self.instruction) + 1


class IncAXInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'inc ax'

    def __len__(self):
        return 1


class IncCXInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'inc cx'

    def __len__(self):
        return 1


class IncDXInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'inc cx'

    def __len__(self):
        return 1


class IncBXInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'inc bx'

    def __len__(self):
        return 1


class IncSIInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'inc si'

    def __len__(self):
        return 1


class IncSPInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'inc sp'

    def __len__(self):
        return 1


class IncBPInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'inc bp'

    def __len__(self):
        return 1


class IncDIInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'inc di'

    def __len__(self):
        return 1


class DecAXInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'dec ax'

    def __len__(self):
        return 1


class DecCXInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'dec cx'

    def __len__(self):
        return 1


class DecDXInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'dec dx'

    def __len__(self):
        return 1


class DecBXInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'dec bx'

    def __len__(self):
        return 1


class DecSPInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'dec sp'

    def __len__(self):
        return 1


class DecBPInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'dec bp'

    def __len__(self):
        return 1


class DecSIInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'dec si'

    def __len__(self):
        return 1


class DecDIInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'dec di'

    def __len__(self):
        return 1


class PushInstruction:
    def __init__(self, register):
        self.register = Register(register, word=True)

    def __str__(self):
        return 'push %s' % self.register

    def __len__(self):
        return 1


class PopInstruction:
    def __init__(self, register):
        self.register = Register(register, word=True)

    def __str__(self):
        return 'pop %s' % self.register

    def __len__(self):
        return 1


class JoInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jo %02Xh' % self.offset

    def __len__(self):
        return 2


class JnoInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jno %02Xh' % self.offset

    def __len__(self):
        return 2


class JbInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jb %02Xh' % self.offset

    def __len__(self):
        return 2


class JnbInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jnb %02Xh' % self.offset

    def __len__(self):
        return 2


class JzInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jz %02Xh' % self.offset

    def __len__(self):
        return 2


class JnzInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jnz %02Xh' % self.offset

    def __len__(self):
        return 2


class JbeInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jbe %02Xh' % self.offset

    def __len__(self):
        return 2


class JaInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'ja %02Xh' % self.offset

    def __len__(self):
        return 2


class JsInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'js %02Xh' % self.offset

    def __len__(self):
        return 2


class JnsInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jns %02Xh' % self.offset

    def __len__(self):
        return 2


class JpeInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jpe %02Xh' % self.offset

    def __len__(self):
        return 2


class JpoInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jpo %02Xh' % self.offset

    def __len__(self):
        return 2


class JlInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jl %02Xh' % self.offset

    def __len__(self):
        return 2


class JgeInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jge %02Xh' % self.offset

    def __len__(self):
        return 2


class JleInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jle %02Xh' % self.offset

    def __len__(self):
        return 2


class JgInstruction:
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jg %02Xh' % self.offset

    def __len__(self):
        return 2


class IntermediateInstruction:
    def __init__(self, data):
        instruction_type = data[0] & 0x3
        self.data = data[1:]
        self.type = instruction_type
        self.dst_word = data[0] & 0x1
        self.modreg = ModReg(self.data[0], self.dst_word, self.data[1:])
        offset = len(self.modreg)
        if instruction_type == 0:
            self.src_word = False
            self.imm = Immediate8(struct.unpack('<B', self.data[offset:offset+1])[0])
        elif instruction_type == 1:
            self.src_word = True
            self.imm = Immediate16(struct.unpack('<H', self.data[offset:offset + 2])[0])
        elif instruction_type == 2:
            self.src_word = False
            self.imm = Immediate8(struct.unpack('<B', self.data[offset:offset+1])[0])
        elif instruction_type == 3:
            self.src_word = False
            self.imm = Immediate8(struct.unpack('<B', self.data[offset:offset+1])[0])

    def __str__(self):
        if self.modreg.reg == 0:
            return 'add %s, %s' % (self.modreg, self.imm)
        elif self.modreg.reg == 1:
            return 'or %s, %s' % (self.modreg, self.imm)
        elif self.modreg.reg == 2:
            return 'adc %s, %s' % (self.modreg, self.imm)
        elif self.modreg.reg == 3:
            return 'sbb %s, %s' % (self.modreg, self.imm)
        elif self.modreg.reg == 4:
            return 'and %s, %s' % (self.modreg, self.imm)
        elif self.modreg.reg == 5:
            return 'sub %s, %s' % (self.modreg, self.imm)
        elif self.modreg.reg == 6:
            return 'xor %s, %s' % (self.modreg, self.imm)
        elif self.modreg.reg == 7:
            return 'cmp %s, %s' % (self.modreg, self.imm)

    def __len__(self):
        return 1 + len(self.modreg) + len(self.imm)


class TestInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'test %s, %s' % (self.source, self.dest)


class XchgInstruction(RegToRegMemBaseInstruction):
    def get_size(self):
        return False

    def __str__(self):
        return 'xchg %s, %s' % (self.source, self.dest)


class MovInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'mov %s, %s' % (self.source, self.dest)


class MoveSegRegInstruction(RegToRegMemBaseInstruction):
    def get_size(self):
        return True

    def get_source(self):
        if self.direction:
            return SegmentRegister(self.modreg.reg)
        else:
            return self.modreg

    def get_destination(self):
        if self.direction:
            return self.modreg
        else:
            return SegmentRegister(self.modreg.reg)

    def __str__(self):
        return 'mov %s, %s' % (self.source, self.dest)

class LoadEffectiveAddressInstruction(RegToRegMemBaseInstruction):
    def __str__(self):
        return 'lea %s, %s' % (self.source, self.dest)


class NopInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'nop'

    def __len__(self):
        return 1


class XchgAxCxInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'xchg ax,cx'

    def __len__(self):
        return 1


class XchgAxDxInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'xchg ax,dx'

    def __len__(self):
        return 1


class XchgAxBxInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'xchg ax,bx'

    def __len__(self):
        return 1


class XchgAxSpInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'xchg ax,sp'

    def __len__(self):
        return 1


class XchgAxBpInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'xchg ax,bp'

    def __len__(self):
        return 1


class XchgAxSiInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'xchg ax,si'

    def __len__(self):
        return 1


class XchgAxDiInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'xchg ax,di'

    def __len__(self):
        return 1


class CbwInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'cbw'

    def __len__(self):
        return 1


class CwdInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'cwd'

    def __len__(self):
        return 1


class CallInstruction:
    def __init__(self, data):
        self.data = data
        self.offset, self.segment_address = struct.unpack('<HH', self.data)
        self.segment = None

    def __str__(self):
        if self.segment:
            return 'call %s %04x:%04x' % (self.segment, self.segment_address, self.offset)
        return 'call %04x:%04x' % (self.segment_address, self.offset)

    def __len__(self):
        return 5


class PushfInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'pushf'

    def __len__(self):
        return 1


class PopfInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'pophf'

    def __len__(self):
        return 1


class MoveAlMem8Instruction:
    def __init__(self, data):
        self.immediate16 = Immediate16(struct.unpack('<H', data)[0])

    def __str__(self):
        return 'mov al, %s' % self.immediate16

    def __len__(self):
        return 3


class MoveAxMem16Instruction:
    def __init__(self, data):
        self.immediate16 = Immediate16(struct.unpack('<H', data)[0])
        self.segment = None

    def __str__(self):
        return 'mov ax, %s%s' % (self.get_segment(), self.immediate16)

    def get_segment(self):
        return '%s:' % self.segment if self.segment else ''

    def __len__(self):
        return 3


class MoveMem8AlInstruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov %04Xh, al' % self.immediate8

    def __len__(self):
        return 3


class MoveMem16AxInstruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov %04Xh, ax' % self.immediate16

    def __len__(self):
        return 3


class MovsInstruction:
    def __init__(self, word):
        self.word = word

    def __str__(self):
        if self.word:
            return 'movsw'
        else:
            return 'movsb'

    def __len__(self):
        return 1


class CmpsInstruction:
    def __init__(self, word):
        self.word = word

    def __str__(self):
        if self.word:
            return 'cmpsw'
        else:
            return 'cmpsb'

    def __len__(self):
        return 1


class StosInstruction:
    def __init__(self, word):
        self.word = word

    def __str__(self):
        if self.word:
            return 'stosw'
        else:
            return 'stosb'

    def __len__(self):
        return 1


class LodsInstruction:
    def __init__(self, word):
        self.word = word
        self.segment = 'ds'

    def __str__(self):
        if self.word:
            return 'lods byte ptr %s:[si]' % self.segment
        else:
            return 'lods word ptr %s:[si]' % self.segment

    def __len__(self):
        return 1


class MoveAlInstruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov al, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveCLInstruction:
    def __init__(self, data):
        self.immediate8 = Immediate8(struct.unpack('<B', data)[0])

    def __str__(self):
        return 'mov cl, %s' % self.immediate8

    def __len__(self):
        return 2


class MoveDLInstruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov dl, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveBLInstruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov bl, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveAhInstruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov ah, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveChInstruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov ch, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveDhInstruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov dh, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveBhInstruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov bh, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveAXInstruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov ax, %xh' % self.immediate16

    def __len__(self):
        return 3


class MoveCXInstruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov cx, %xh' % self.immediate16

    def __len__(self):
        return 3


class MoveDXInstruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov dx, %xh' % self.immediate16

    def __len__(self):
        return 3


class MoveBXInstruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov bx, %xh' % self.immediate16

    def __len__(self):
        return 3


class MoveSPInstruction:
    def __init__(self, data):
        self.immediate16 = Immediate16(struct.unpack('<H', data)[0])

    def __str__(self):
        return 'mov sp, %s' % self.immediate16

    def __len__(self):
        return 3


class MoveBPInstruction:
    def __init__(self, data):
        self.immediate16 = Immediate16(struct.unpack('<H', data)[0])

    def __str__(self):
        return 'mov bp, %s' % self.immediate16

    def __len__(self):
        return 3


class MoveSIInstruction:
    def __init__(self, data):
        self.immediate16 = Immediate16(struct.unpack('<H', data)[0])

    def __str__(self):
        return 'mov si, %s' % self.immediate16

    def __len__(self):
        return 3


class MoveDIInstruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov di, %Xh' % self.immediate16

    def __len__(self):
        return 3


class ReturnIntraInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'ret'

    def __len__(self):
        return 1


class LesInstruction(RegToRegMemBaseInstruction):
    def get_size(self):
        return True

    def get_direction(self):
        return True

    def __str__(self):
        return 'les %s, %s' % (self.source, self.dest)


class LdsInstruction(RegToRegMemBaseInstruction):
    def get_size(self):
        return True

    def get_direction(self):
        return True

    def __str__(self):
        return 'lds %s, %s' % (self.source, self.dest)


class MovMem8Imm8Instruction(RegToRegMemBaseInstruction):
    def __str__(self):
        offset = 1+len(self.modreg)
        imm = Immediate8(struct.unpack('<B', self.data[offset:offset+1])[0])
        return 'mov %s, %s' % (self.source, imm)

    def get_direction(self):
        return False

    def __len__(self):
        return 1 + len(self.modreg) + 1


class MovMem16Imm16Instruction(RegToRegMemBaseInstruction):
    def __str__(self):
        offset = 1+len(self.modreg)
        imm = Immediate16(struct.unpack('<H', self.data[offset:offset + 2])[0])
        return 'mov %s, %s' % (self.source, imm)

    def get_direction(self):
        return False

    def __len__(self):
        return 1 + len(self.modreg) + 2


class ReturnImm16Instruction:
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'ret %d' % self.immediate16

    def __len__(self):
        return 3


class ReturnInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'ret'

    def __len__(self):
        return 1


class InterruptInstruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'int %02Xh' % self.immediate8

    def __len__(self):
        return 2


class ShiftInstruction(RegToRegMemBaseInstruction):
    def get_source(self):
        return self.modreg

    def get_destination(self):
        if self.direction == 0:
            return Immediate8(1)
        elif self.direction == 1:
            return Register(1, 0)

    def __str__(self):
        if self.modreg.reg == 0:
            return 'rol %s, %s' % (self.source, self.dest)
        elif self.modreg.reg == 1:
            return 'ror %s, %s' % (self.source, self.dest)
        elif self.modreg.reg == 2:
            return 'rcl %s, %s' % (self.source, self.dest)
        elif self.modreg.reg == 3:
            return 'rcr %s, %s' % (self.source, self.dest)
        elif self.modreg.reg == 4:
            return 'shl %s, %s' % (self.source, self.dest)
        elif self.modreg.reg == 5:
            return 'shr %s, %s' % (self.source, self.dest)
        elif self.modreg.reg == 7:
            return 'sar %s, %s' % (self.source, self.dest)

        raise Exception('Unimplemented shift instruction', self.modreg)

    def __len__(self):
        return 2


class LoopInstruction:
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'loop %02Xh' % self.immediate8

    def __len__(self):
        return 2


class JcxzInstruction:
    def __init__(self, data):
        self.immediate8 = Immediate8(struct.unpack('<B', data)[0])

    def __str__(self):
        return 'jcxz %s' % self.immediate8

    def __len__(self):
        return 2


class CallNearInstruction:
    def __init__(self, data):
        self.data = data
        self.offset = struct.unpack('<h', self.data)[0]

    def __str__(self):
        return 'call %04Xh' % self.offset

    def __len__(self):
        return 3


class JumpNearInstruction:
    def __init__(self, data):
        self.data = data
        self.offset = struct.unpack('<h', self.data)[0]

    def __str__(self):
        return 'jmp %04x' % self.offset

    def __len__(self):
        return 3


class JumpLongInstruction:
    def __init__(self, data):
        self.data = data
        (self.offset, self.segment) = struct.unpack('<HH', self.data)

    def __str__(self):
        return 'jmp %04x:%04x' % (self.segment, self.offset)

    def __len__(self):
        return 5


class JumpShortInstruction:
    def __init__(self, data):
        self.data = data
        self.offset = struct.unpack('<b', self.data)[0]

    def __str__(self):
        return 'jmp %02x' % self.offset

    def __len__(self):
        return 2


class OutAlDxInstruction:
    def __str__(self):
        return 'out al, dx'

    def __len__(self):
        return 1


class RepInstruction:
    def __init__(self, instruction):
        self.instruction = instruction

    def __str__(self):
        return 'rep %s' % self.instruction

    def __len__(self):
        return 1 + len(self.instruction)


class CMCInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'cmc'

    def __len__(self):
        return 1


class NotInstruction:
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'not %s' % self.modreg

    def __len__(self):
        return 1 + len(self.modreg)


class TestImmInstruction:
    def __init__(self, modreg):
        self.modreg = modreg
        if self.modreg.word:
            self.imm = Immediate16(struct.unpack('<H', self.modreg.extra[:2])[0])
        else:
            self.imm = Immediate8(struct.unpack('<B', self.modreg.extra[:1])[0])

    def __str__(self):
        return 'not %s, %s' % (self.modreg, self.imm)

    def __len__(self):
        return 1 + len(self.modreg) + len(self.imm)


class NegInstruction:
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'not %s' % self.modreg

    def __len__(self):
        return 1 + len(self.modreg)


class DivInstruction:
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'div %s' % self.modreg

    def __len__(self):
        return 1 + len(self.modreg)


class IdivInstruction:
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'idiv %s' % self.modreg

    def __len__(self):
        return 1 + len(self.modreg)


class MulInstruction:
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'mul %s' % self.modreg

    def __len__(self):
        return 1 + len(self.modreg)


class ImulInstruction:
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'imul %s' % self.modreg

    def __len__(self):
        return 1 + len(self.modreg)


def Grp1Instruction(data):
    modreg = ModReg(data[1], data[0] & 0x01, data[2:])

    if modreg.reg == 0:
        return TestImmInstruction(modreg)
    elif modreg.reg == 2:
        return NotInstruction(modreg)
    elif modreg.reg == 3:
        return NegInstruction(modreg)
    elif modreg.reg == 4:
        return MulInstruction(modreg)
    elif modreg.reg == 5:
        return ImulInstruction(modreg)
    elif modreg.reg == 6:
        return DivInstruction(modreg)
    elif modreg.reg == 7:
        return IdivInstruction(modreg)
    raise Exception('Unimplemented', modreg)


class CLCInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'clc'

    def __len__(self):
        return 1


class STCInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'stc'

    def __len__(self):
        return 1


class CLIInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'cli'

    def __len__(self):
        return 1


class STIInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'sti'

    def __len__(self):
        return 1


class CLDInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'cld'

    def __len__(self):
        return 1


class STDInstruction:
    def __init__(self):
        pass

    def __str__(self):
        return 'std'

    def __len__(self):
        return 1


class PushMem16Instruction:
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'push %s' % self.modreg

    def __len__(self):
        return 1 + len(self.modreg)


class IncInstruction:
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'inc %s' % self.modreg

    def __len__(self):
        return 1 + len(self.modreg)


class DecInstruction:
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'dec %s' % self.modreg

    def __len__(self):
        return 1 + len(self.modreg)


class Grp2CallNearInstruction(CallNearInstruction):
    def __len__(self):
        return 4


def Grp2Instruction(data):
    modreg = ModReg(data[1], data[0] & 0x01, data[2:])

    if modreg.reg == 0:
        return IncInstruction(modreg)
    elif modreg.reg == 1:
        return DecInstruction(modreg)
    elif modreg.reg == 3:
        return Grp2CallNearInstruction(modreg.extra)
    elif modreg.reg == 6:
        return PushMem16Instruction(modreg)
    raise Exception('Grp2Instruction', modreg)


class Instruction:
    @staticmethod
    def decode(program, offset):
        code = program[offset]
        if 0x0 <= code <= 0x3:
            return AddInstruction(program[offset:offset+5])
        elif code == 0x4:
            return AddAlInstruction(program[offset+1:offset+2])
        elif code == 0x5:
            return AddAxInstruction(program[offset+1:offset+3])
        elif code == 0x6:
            return PushESInstruction()
        elif code == 0x7:
            return PopESInstruction()
        elif 0x8 <= code <= 0xb:
            return OrInstruction(program[offset:offset+5])
        elif code == 0xc:
            return OrAlImm8Instruction(program[offset+1:offset+2])
        elif code == 0xd:
            return OrAxImm16Instruction(program[offset+1:offset+3])
        elif code == 0xe:
            return PushCSInstruction()
        elif code == 0xf:
            raise Exception('Unimplemented op-code: %x' % code)
        elif 0x10 <= code <= 0x13:
            return AdcInstruction(program[offset:offset+4])
        elif code == 0x14:
            return AdcAlImm8Instruction(program[offset+1:offset+2])
        elif code == 0x15:
            return AdcAxImm16Instruction(program[offset+1:offset+3])
        elif code == 0x16:
            return PushSSInstruction()
        elif code == 0x17:
            return PopSSInstruction()
        elif 0x18 <= code <= 0x1b:
            return SBBInstruction(program[offset:offset+4])
        elif code == 0x1c:
            return SBBAlImm8Instruction(program[offset+1:offset+2])
        elif code == 0x1d:
            return SBBAxImm16Instruction(program[offset+1:offset+3])
        elif code == 0x1e:
            return PushDSInstruction()
        elif code == 0x1f:
            return PopDSInstruction()
        elif 0x20 <= code <= 0x23:
            return AndInstruction(program[offset:offset+5])
        elif code == 0x24:
            return AndALImm8Instruction(program[offset+1:offset+2])
        elif code == 0x25:
            return AndAXImm16Instruction(program[offset+1:offset+3])
        elif code == 0x26:
            return ESSegmentOverride(Instruction.decode(program, offset+1))
        elif code == 0x27:
            return DAAInstruction()
        elif 0x28 <= code <= 0x2b:
            return SubInstruction(program[offset:offset+5])
        elif code == 0x2c:
            return SubAlImm8Instruction(program[offset+1:offset+2])
        elif code == 0x2d:
            return SubAxImm16Instruction(program[offset+1:offset+3])
        elif code == 0x2e:
            return CSSegmentOverride(Instruction.decode(program, offset+1))
        elif code == 0x2f:
            raise Exception('Unimplemented op-code: %x' % code)
        elif 0x30 <= code <= 0x33:
            return XorInstruction(program[offset:offset+5])
        elif code == 0x34:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x35:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x36:
            return SSSegmentOverride(Instruction.decode(program, offset+1))
        elif code == 0x37:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x38:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x39:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x3a:
            return CmpInstruction(program[offset:offset+5])
        elif code == 0x3b:
            return CmpInstruction(program[offset:offset+5])
        elif code == 0x3c:
            return CmpAlImm8Instruction(program[offset+1:offset+2])
        elif code == 0x3d:
            return CmpAxImm16Instruction(program[offset+1:offset+3])
        elif code == 0x3e:
            return DSSegmentOverride(Instruction.decode(program, offset+1))
        elif code == 0x3f:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x40:
            return IncAXInstruction()
        elif code == 0x41:
            return IncCXInstruction()
        elif code == 0x42:
            return IncDXInstruction()
        elif code == 0x43:
            return IncBXInstruction()
        elif code == 0x44:
            return IncSPInstruction()
        elif code == 0x45:
            return IncBPInstruction()
        elif code == 0x46:
            return IncSIInstruction()
        elif code == 0x47:
            return IncDIInstruction()
        elif code == 0x48:
            return DecAXInstruction()
        elif code == 0x49:
            return DecCXInstruction()
        elif code == 0x4a:
            return DecDXInstruction()
        elif code == 0x4b:
            return DecBXInstruction()
        elif code == 0x4c:
            return DecSPInstruction()
        elif code == 0x4d:
            return DecBPInstruction()
        elif code == 0x4e:
            return DecSIInstruction()
        elif code == 0x4f:
            return DecDIInstruction()
        elif 0x50 <= code <= 0x57:
            return PushInstruction(code-0x50)
        elif 0x58 <= code <= 0x5f:
            return PopInstruction(code-0x58)
        elif code == 0x60:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x61:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x62:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x63:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x64:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x65:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x66:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x67:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x68:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x69:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x6a:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x6b:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x6c:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x6d:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x6e:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x6f:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x70:
            return JoInstruction(program[offset+1:offset+2])
        elif code == 0x71:
            return JnoInstruction(program[offset+1:offset+2])
        elif code == 0x72:
            return JbInstruction(program[offset+1:offset+2])
        elif code == 0x73:
            return JnbInstruction(program[offset+1:offset+2])
        elif code == 0x74:
            return JzInstruction(program[offset+1:offset+2])
        elif code == 0x75:
            return JnzInstruction(program[offset + 1:offset + 2])
        elif code == 0x76:
            return JbeInstruction(program[offset+1:offset+2])
        elif code == 0x77:
            return JaInstruction(program[offset+1:offset+2])
        elif code == 0x78:
            return JsInstruction(program[offset+1:offset+2])
        elif code == 0x79:
            return JnsInstruction(program[offset+1:offset+2])
        elif code == 0x7a:
            return JpeInstruction(program[offset+1:offset+2])
        elif code == 0x7b:
            return JpoInstruction(program[offset+1:offset+2])
        elif code == 0x7c:
            return JlInstruction(program[offset+1:offset+2])
        elif code == 0x7d:
            return JgeInstruction(program[offset+1:offset+2])
        elif code == 0x7e:
            return JleInstruction(program[offset+1:offset+2])
        elif code == 0x7f:
            return JgInstruction(program[offset+1:offset+2])
        elif 0x80 <= code <= 0x83:
            return IntermediateInstruction(program[offset:offset+6])
        elif code == 0x84:
            return TestInstruction(program[offset:offset+5])
        elif code == 0x85:
            return TestInstruction(program[offset:offset+5])
        elif code == 0x86:
            return XchgInstruction(program[offset:offset+6])
        elif code == 0x87:
            return XchgInstruction(program[offset:offset+6])
        elif code == 0x88:
            return MovInstruction(program[offset:offset+6])
        elif code == 0x89:
            return MovInstruction(program[offset:offset+6])
        elif code == 0x8a:
            return MovInstruction(program[offset:offset+6])
        elif code == 0x8b:
            return MovInstruction(program[offset:offset+6])
        elif code == 0x8c:
            return MoveSegRegInstruction(program[offset:offset+6])
        elif code == 0x8d:
            return LoadEffectiveAddressInstruction(program[offset:offset+6])
        elif code == 0x8e:
            return MoveSegRegInstruction(program[offset:offset+6])
        elif code == 0x8f:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x90:
            return NopInstruction()
        elif code == 0x91:
            return XchgAxCxInstruction()
        elif code == 0x92:
            return XchgAxDxInstruction()
        elif code == 0x93:
            return XchgAxBxInstruction()
        elif code == 0x94:
            return XchgAxSpInstruction()
        elif code == 0x95:
            return XchgAxBpInstruction()
        elif code == 0x96:
            return XchgAxSiInstruction()
        elif code == 0x97:
            return XchgAxDiInstruction()
        elif code == 0x98:
            return CbwInstruction()
        elif code == 0x99:
            return CwdInstruction()
        elif code == 0x9a:
            return CallInstruction(program[offset+1:offset+5])
        elif code == 0x9b:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x9c:
            return PushfInstruction()
        elif code == 0x9d:
            return PopfInstruction()
        elif code == 0x9e:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x9f:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xa0:
            return MoveAlMem8Instruction(program[offset+1:offset+3])
        elif code == 0xa1:
            return MoveAxMem16Instruction(program[offset + 1:offset + 3])
        elif code == 0xa2:
            return MoveMem8AlInstruction(program[offset+1:offset+2])
        elif code == 0xa3:
            return MoveMem16AxInstruction(program[offset + 1:offset + 3])
        elif code == 0xa4:
            return MovsInstruction(word=False)
        elif code == 0xa5:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xa6:
            return CmpsInstruction(word=False)
        elif code == 0xa7:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xa8:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xa9:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xaa:
            return StosInstruction(word=False)
        elif code == 0xab:
            return StosInstruction(word=True)
        elif code == 0xac:
            return LodsInstruction(word=False)
        elif code == 0xad:
            return LodsInstruction(word=True)
        elif code == 0xae:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xaf:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xb0:
            return MoveAlInstruction(program[offset + 1:offset + 2])
        elif code == 0xb1:
            return MoveCLInstruction(program[offset+1:offset+2])
        elif code == 0xb2:
            return MoveDLInstruction(program[offset+1:offset+2])
        elif code == 0xb3:
            return MoveBLInstruction(program[offset+1:offset+2])
        elif code == 0xb4:
            return MoveAhInstruction(program[offset+1:offset+2])
        elif code == 0xb5:
            return MoveChInstruction(program[offset+1:offset+2])
        elif code == 0xb6:
            return MoveDhInstruction(program[offset+1:offset+2])
        elif code == 0xb7:
            return MoveBhInstruction(program[offset+1:offset+2])
        elif code == 0xb8:
            return MoveAXInstruction(program[offset+1:offset+3])
        elif code == 0xb9:
            return MoveCXInstruction(program[offset+1:offset+3])
        elif code == 0xba:
            return MoveDXInstruction(program[offset+1:offset+3])
        elif code == 0xbb:
            return MoveBXInstruction(program[offset+1:offset+3])
        elif code == 0xbc:
            return MoveSPInstruction(program[offset+1:offset+3])
        elif code == 0xbd:
            return MoveBPInstruction(program[offset+1:offset+3])
        elif code == 0xbe:
            return MoveSIInstruction(program[offset+1:offset+3])
        elif code == 0xbf:
            return MoveDIInstruction(program[offset+1:offset+3])
        elif code == 0xc0:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xc1:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xc2:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xc3:
            return ReturnIntraInstruction()
        elif code == 0xc4:
            return LesInstruction(program[offset:offset+4])
        elif code == 0xc5:
            return LdsInstruction(program[offset:offset+3])
        elif code == 0xc6:
            return MovMem8Imm8Instruction(program[offset+0:offset+6])
        elif code == 0xc7:
            return MovMem16Imm16Instruction(program[offset:offset+6])
        elif code == 0xc8:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xc9:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xca:
            return ReturnImm16Instruction(program[offset+1:offset+3])
        elif code == 0xcb:
            return ReturnInstruction()
        elif code == 0xcd:
            return InterruptInstruction(program[offset+1:offset+2])
        elif code == 0xce:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xcf:
            raise Exception('Unimplemented op-code: %x' % code)
        elif 0xd0 <= code <= 0xd3:
            return ShiftInstruction(program[offset:offset+5])
        elif code == 0xd4:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xd5:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xd6:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xd7:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xd8:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xd9:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xda:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xdb:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xdc:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xdd:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xde:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xdf:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xe0:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xe1:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xe2:
            return LoopInstruction(program[offset+1:offset+2])
        elif code == 0xe3:
            return JcxzInstruction(program[offset+1:offset+2])
        elif code == 0xe4:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xe5:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xe6:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xe7:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xe8:
            return CallNearInstruction(program[offset+1:offset+3])
        elif code == 0xe9:
            return JumpNearInstruction(program[offset+1:offset+3])
        elif code == 0xea:
            return JumpLongInstruction(program[offset+1:offset+5])
        elif code == 0xeb:
            return JumpShortInstruction(program[offset+1:offset+2])
        elif code == 0xec:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xed:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xee:
            return OutAlDxInstruction()
        elif code == 0xef:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xf0:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xf1:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xf2:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xf3:
            return RepInstruction(Instruction.decode(program, offset+1))
        elif code == 0xf4:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xf5:
            return CMCInstruction()
        elif code == 0xf6:
            return Grp1Instruction(program[offset:offset+5])
        elif code == 0xf7:
            return Grp1Instruction(program[offset:offset+5])
        elif code == 0xf8:
            return CLCInstruction()
        elif code == 0xf9:
            return STCInstruction()
        elif code == 0xfa:
            return CLIInstruction()
        elif code == 0xfb:
            return STIInstruction()
        elif code == 0xfc:
            return CLDInstruction()
        elif code == 0xfd:
            return STDInstruction()
        elif code == 0xfe:
            return Grp2Instruction(program[offset:offset+4])
        elif code == 0xff:
            return Grp2Instruction(program[offset:offset+4])
        raise Exception('Unimplemented op-code: %x' % code)
