import struct


class Immediate8(object):
    def __init__(self, immediate8):
        self.immediate8 = immediate8

    def __str__(self):
        if self.immediate8 <= 8:
            return '%d' % self.immediate8
        return '%02Xh' % self.immediate8


class Immediate16(object):
    def __init__(self, immediate16):
        self.immediate16 = immediate16

    def __str__(self):
        if self.immediate16 < 16:
            return '%d' % self.immediate16
        elif self.immediate16 < 256:
            return '%02Xh' % self.immediate16
        return '%04Xh' % self.immediate16


class CallInstruction(object):
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


class CbwInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'cbw'

    def __len__(self):
        return 1


class CwdInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'cwd'

    def __len__(self):
        return 1


class PushfInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'pushf'

    def __len__(self):
        return 1


class PopfInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'pophf'

    def __len__(self):
        return 1


class CallNearInstruction(object):
    def __init__(self, data):
        self.data = data
        # TODO: can this be replaced with '<h'?
        self.offset = struct.unpack('<H', self.data)[0]
        if self.offset & 0x8000:
            self.offset = -(0x10000 - self.offset)

    def __str__(self):
        return 'call %04Xh' % (self.offset)

    def __len__(self):
        return 3


class JumpNearInstruction(object):
    def __init__(self, data):
        self.data = data
        (self.offset) = struct.unpack('<h', self.data)[0]

    def __str__(self):
        return 'jmp %04x' % (self.offset)

    def __len__(self):
        return 3


class JumpLongInstruction(object):
    def __init__(self, data):
        self.data = data
        (self.offset, self.segment) = struct.unpack('<HH', self.data)

    def __str__(self):
        return 'jmp %04x:%04x' % (self.segment, self.offset)

    def __len__(self):
        return 5


class JumpShortInstruction(object):
    def __init__(self, data):
        self.data = data
        self.offset = struct.unpack('<b', self.data)[0]

    def __str__(self):
        return 'jmp %02x' % (self.offset)

    def __len__(self):
        return 2


class AddAxInstruction(object):
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'add ax, %xh' % (self.immediate16)

    def __len__(self):
        return 3


class AddInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, data[2:])

    def __str__(self):
        return 'add %s' % (self.modreg)

    def __len__(self):
        return len(self.modreg)


class SubInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, data[2:])

    def __str__(self):
        return 'sub %s' % (self.modreg)

    def __len__(self):
        return len(self.modreg)


class SubAlImm8Instruction(object):
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'sub al, %02Xh' % (self.immediate8)

    def __len__(self):
        return 3


class SubAxImm16Instruction(object):
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'sub ax, %04Xh' % (self.immediate16)

    def __len__(self):
        return 3


class Register(object):
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


class SegmentRegister(object):
    def __init__(self, register):
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
        print('Unknown segment register %d' % self.register)
        raise Exception


class PushInstruction(object):
    def __init__(self, register):
        self.register = Register(register, word=True)

    def __str__(self):
        return 'push %s' % self.register

    def __len__(self):
        return 1


class PopInstruction(object):
    def __init__(self, register):
        self.register = Register(register, word=True)

    def __str__(self):
        return 'pop %s' % self.register

    def __len__(self):
        return 1


class ModReg(object):
    def __init__(self, modreg, direction, word, extra=None):
        self.mod = (modreg & 0xc0) >> 6
        self.reg = (modreg & 0x38) >> 3
        self.rm = modreg & 0x07
        self.direction = direction
        self.word = word
        self.extra = extra

    def __str__(self):
        if self.mod == 0:
            if self.direction == 0:
                if self.rm == 0:
                    return '[bx+si], %s' % (Register(self.reg, self.word))
                elif self.rm == 1:
                    return '[bx+di], %s' % (Register(self.reg, self.word))
                elif self.rm == 4:
                    return '[si], %s' % (Register(self.reg, self.word))
                elif self.rm == 5:
                    return '[di], %s' % (Register(self.reg, self.word))
                elif self.rm == 6:
                    return '%04Xh, %s' % (struct.unpack('<H', self.extra[:2])[0], Register(self.reg, self.word))
            elif self.direction == 2:
                if self.rm == 0:
                    return '%s, [bx+si]' % (Register(self.reg, self.word))
                elif self.rm == 1:
                    return '%s, [bx+di]' % (Register(self.reg, self.word))
                elif self.rm == 4:
                    return '%s, [si]' % (Register(self.reg, self.word))
                elif self.rm == 5:
                    return '%s, [di]' % (Register(self.reg, self.word))
                elif self.rm == 6:
                    return '%s, %04Xh' % (Register(self.reg, self.word), struct.unpack('<H', self.extra[:2])[0])
                elif self.rm == 7:
                    return '%s, bx' % Register(self.reg, self.word)
            elif self.direction == 4:
                if self.rm == 5:
                    return '[di]'
                elif self.rm == 6:
                    return '%04Xh' % struct.unpack('<H', self.extra[:2])[0]
            elif self.direction == 8:
                if self.rm == 5:
                    return '[di], %s' % Immediate8(struct.unpack('<B', self.extra[:1])[0])
                elif self.rm == 6:
                    return '%04Xh, %s' % (struct.unpack('<H', self.extra[:2])[0], Immediate8(struct.unpack('<B', self.extra[2:3])[0]))
        elif self.mod == 1:
            if self.direction == 0:
                if self.rm == 4:
                    return '[si+%s], %s' % (Immediate8(struct.unpack('<B', self.extra[:1])[0]),
                                            Register(self.reg, self.word))
                elif self.rm == 5:
                    return '[di+%s], %s' % (Immediate8(struct.unpack('<B', self.extra[:1])[0]),
                                            Register(self.reg, self.word))
                elif self.rm == 6:
                    return '[bp+%s], %s' % (Immediate8(struct.unpack('<B', self.extra[:1])[0]),
                                            Register(self.reg, self.word))
                elif self.rm == 7:
                    return '[bx+%s], %s' % (Immediate8(struct.unpack('<B', self.extra[:1])[0]),
                                            Register(self.reg, self.word))
            elif self.direction == 2:
                if self.rm == 3:
                    return '%s, [bp+di+%s]' % (Register(self.reg, self.word),
                                            Immediate8(struct.unpack('<B', self.extra[:1])[0]))
                elif self.rm == 4:
                    return '%s, [si+%s]' % (Register(self.reg, self.word),
                                            Immediate8(struct.unpack('<B', self.extra[:1])[0]))
                elif self.rm == 5:
                    return '%s, [di+%s]' % (Register(self.reg, self.word),
                                            Immediate8(struct.unpack('<B', self.extra[:1])[0]))
                elif self.rm == 6:
                    return '%s, [bp+%s]' % (Register(self.reg, self.word),
                                            Immediate8(struct.unpack('<B', self.extra[:1])[0]))
                elif self.rm == 7:
                    return '%s, [bx+%s]' % (Register(self.reg, self.word),
                                            Immediate8(struct.unpack('<B', self.extra[:1])[0]))
            elif self.direction == 4:
                if self.rm == 5:
                    return '[di+%s]' % Immediate8(struct.unpack('<B', self.extra[:1])[0])
                elif self.rm == 6:
                    return '[bp+%s]' % Immediate8(struct.unpack('<B', self.extra[:1])[0])
            elif self.direction == 8:
                if self.rm == 3:
                    return '[bp+di+%s], %s' % (Immediate8(struct.unpack('<B', self.extra[:1])[0]),
                                            Immediate8(struct.unpack('<B', self.extra[1:2])[0]))
                elif self.rm == 5:
                    return '[di+%s], %s' % (Immediate8(struct.unpack('<B', self.extra[:1])[0]),
                                            Immediate8(struct.unpack('<B', self.extra[1:2])[0]))
                elif self.rm == 6:
                    return '[bp+%s], %s' % (Immediate8(struct.unpack('<b', self.extra[:1])[0]),
                                            Immediate8(struct.unpack('<B', self.extra[1:2])[0]))
        elif self.mod == 2:
            if self.direction == 0:
                if self.rm == 5:
                    return '[di+%xh], %s' % (struct.unpack('<H', self.extra[:2])[0], Register(self.reg, 1))
                elif self.rm == 6:
                    return '[bp-%xh], %s' % (0x10000 - struct.unpack('<H', self.extra[:2])[0], Register(self.reg, 1))
            elif self.direction == 2:
                if self.rm == 2:
                    return '%s, [bp+si+%xh]' % (Register(self.reg, 1), struct.unpack('<h', self.extra[:2])[0])
                elif self.rm == 3:
                    return '%s, [bp+di+%xh]' % (Register(self.reg, 1), struct.unpack('<h', self.extra[:2])[0])
                elif self.rm == 5:
                    return '%s, [di+%xh]' % (Register(self.reg, 1), struct.unpack('<H', self.extra[:2])[0])
                elif self.rm == 6:
                    return '%s, [bp-%xh]' % (Register(self.reg, 1), 0x10000-struct.unpack('<H', self.extra[:2])[0])
            elif self.direction == 4:
                if self.rm == 5:
                    return '[di+%s]' % (Immediate8(struct.unpack('<b', self.extra[:1])[0]))
                elif self.rm == 6:
                    return '[bp+%s]' % (Immediate8(struct.unpack('<b', self.extra[:1])[0]))
            elif self.direction == 8:
                if self.rm == 5:
                    return 'byte ptr [di+%xh], %s' % (struct.unpack('<H', self.extra[:2])[0], Immediate8(struct.unpack('<B', self.extra[2:3])[0]))
                elif self.rm == 6:
                    return 'byte ptr [bp+%xh], %s' % (struct.unpack('<H', self.extra[:2])[0], Immediate8(struct.unpack('<B', self.extra[2:3])[0]))
        elif self.mod == 3:
            if self.direction == 0:
                return '%s, %s' % (Register(self.rm, self.word), Register(self.reg, self.word))
            elif self.direction == 2:
                return '%s, %s' % (Register(self.reg, self.word), Register(self.rm, self.word))
            elif self.direction == 4:
                return '%s' % Register(self.rm, self.word)
        raise Exception('Unimplemented', self)

    def __repr__(self):
        return 'ModReg(mod=%d, reg=%d, rm=%d, direction=%d, word=%s)' %\
               (self.mod, self.reg, self.rm, self.direction, self.word)

    def __len__(self):
        if not self.direction == 8:
            if self.mod == 0:
                if self.rm == 6:
                    return 4
                else:
                    return 2
            elif self.mod == 1:
                return 3
            elif self.mod == 2:
                return 4
            elif self.mod == 3:
                return 2
        else:
            if self.mod == 0:
                if self.rm == 5:
                    return 3
                elif self.rm == 6:
                    return 5
            elif self.mod == 1:
                if self.rm == 3:
                    return 5
                if self.rm == 5:
                    return 5
                elif self.rm == 6:
                    return 4
            elif self.mod == 2:
                if self.rm == 5:
                    return 5
                elif self.rm == 6:
                    return 5
        raise Exception('Unimplemented', self)


class ModSr(object):
    def __init__(self, modsr, direction, word, extra=None):
        self.mod = (modsr & 0xc0) >> 6
        self.sr = (modsr & 0x38) >> 3
        self.rm = modsr & 0x07
        self.direction = direction
        self.word = word
        self.extra = extra

    def __str__(self):
        if self.sr > 3:
            raise Exception('Invalid sr', self.sr)
        if self.mod == 0:
            if self.rm == 6:
                return '%04xh, %s' % (struct.unpack('<H', self.extra[:2])[0], SegmentRegister(self.sr))
        elif self.mod == 1:
            if self.rm == 5:
                return 'word ptr [di+%d], %s' % (struct.unpack('<b', self.extra[:1])[0], SegmentRegister(self.sr))
            elif self.rm == 6:
                return 'word ptr [bp+%d], %s' % (struct.unpack('<b', self.extra[:1])[0], SegmentRegister(self.sr))
        elif self.mod == 2:
            if self.rm == 0:
                return 'word ptr [bx+si+%d], %s' % (struct.unpack('<h', self.extra[:2])[0], SegmentRegister(self.sr))
            elif self.rm == 6:
                return 'word ptr [bp+%d], %s' % (struct.unpack('<h', self.extra[:2])[0], SegmentRegister(self.sr))
        elif self.mod == 3:
            if self.direction == 0:
                return '%s, %s' % (Register(self.rm, self.word), SegmentRegister(self.sr))
            else:
                return '%s, %s' % (SegmentRegister(self.sr), Register(self.rm, self.word))
        raise Exception('Unimplemented', self.mod, self.rm)

    def __len__(self):
        if self.mod == 0:
            return 4
        elif self.mod == 1:
            return 3
        elif self.mod == 2:
            return 4
        elif self.mod == 3:
            return 2
        raise Exception('Unimplemented', self.mod)


class MovInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, data[2:])

    def __str__(self):
        return 'mov %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class MovMem8Imm8Instruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], 8, data[0] & 0x01, data[2:])

    def __str__(self):
        return 'mov %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class MovMem16Imm16Instruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, data[2:])
        self.mem16 = struct.unpack('<H', self.data[2:4])[0]
        self.immediate16 = struct.unpack('<H', self.data[4:])[0]

    def __str__(self):
        if self.modreg.mod == 0:
            return 'mov %04Xh, %04Xh' % (self.mem16, self.immediate16)
        elif self.modreg.mod == 1:
            if self.modreg.rm == 5:
                return 'mov [di+%02X], %04Xh' % (struct.unpack('<b', self.data[2:3])[0],
                                                 struct.unpack('<H', self.data[3:5])[0])
        elif self.modreg.mod == 2:
            if self.modreg.rm == 5:
                return 'mov [di+%04X], %04Xh' % (struct.unpack('<h', self.data[2:4])[0],
                                                 struct.unpack('<H', self.data[4:6])[0])
            elif self.modreg.rm == 6:
                return 'mov [bp+%04X], %04Xh' % (struct.unpack('<h', self.data[2:4])[0],
                                                 struct.unpack('<H', self.data[4:6])[0])

        raise Exception('Unimplemented', self.modreg)

    def __len__(self):
        if self.modreg.mod == 0:
            return 6
        elif self.modreg.mod == 1:
            return 5
        elif self.modreg.mod == 2:
            return 6
        raise Exception('Unimplemented', self.modreg)


class XorInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01)

    def __str__(self):
        return 'xor %s' % self.modreg

    def __len__(self):
        return 2


class IntermediateInstruction:
    def __init__(self, data, instruction_type):
        self.data = data
        self.type = instruction_type
        if instruction_type == 0:
            self.src_word = False
            self.dst_word = False
            self.imm = Immediate8(struct.unpack('<B', self.data[1:2])[0])
        elif instruction_type == 1:
            self.src_word = True
            self.dst_word = True
            self.imm = Immediate16(struct.unpack('<H', self.data[1:3])[0])
        elif instruction_type == 2:
            self.src_word = False
            self.dst_word = False
            self.imm = Immediate8(struct.unpack('<B', self.data[1:2])[0])
        elif instruction_type == 3:
            self.src_word = False
            self.dst_word = True
            self.imm = Immediate8(struct.unpack('<B', self.data[1:2])[0])
        self.modreg = ModReg(data[0], 0, self.src_word)

    def __str__(self):
        if self.modreg.mod == 0:
            if self.modreg.rm == 5:
                if self.modreg.reg == 0:
                    return 'add [di], %s' % (Immediate8(struct.unpack('<B', self.data[1:2])[0]))
                elif self.modreg.reg == 7:
                    return 'cmp [di], %s' % (Immediate8(struct.unpack('<B', self.data[1:2])[0]))
            elif self.modreg.rm == 6:
                if self.modreg.reg == 1:
                    return 'or %04Xh, %s' % (struct.unpack('<H', self.data[1:3])[0],
                                             Immediate8(struct.unpack('<B', self.data[3:4])[0]))
                elif self.modreg.reg == 4:
                    return 'and %04Xh, %s' % (struct.unpack('<H', self.data[1:3])[0],
                                              Immediate8(struct.unpack('<B', self.data[3:4])[0]))
                elif self.modreg.reg == 7:
                    return 'cmp %04Xh, %s' % (struct.unpack('<H', self.data[1:3])[0],
                                              Immediate8(struct.unpack('<B', self.data[3:4])[0]))
        elif self.modreg.mod == 1:
            if self.modreg.rm == 5:
                if self.modreg.reg == 5:
                    return 'sub %s, %s' % (Register(self.modreg.rm, self.dst_word), self.imm)
                elif self.modreg.reg == 7:
                    return 'cmp [di+%d], %s' % (struct.unpack('<B', self.data[1:2])[0],
                                                Immediate16(struct.unpack('<H', self.data[2:4])[0]))
            if self.modreg.rm == 6:
                if self.modreg.reg == 0:
                    if self.src_word:
                        return 'add [bp+%d], %s' % (struct.unpack('<B', self.data[1:2])[0],
                                                    Immediate16(struct.unpack('<H', self.data[2:4])[0]))
                    else:
                        return 'add [bp+%s], %s' % (Immediate8(struct.unpack('<B', self.data[1:2])[0]),
                                                    Immediate8(struct.unpack('<B', self.data[2:3])[0]))
                elif self.modreg.reg == 7:
                    if self.src_word:
                        return 'cmp [bp+%d], %s' % (struct.unpack('<B', self.data[1:2])[0],
                                                    Immediate16(struct.unpack('<H', self.data[2:4])[0]))
                    else:
                        return 'cmp [bp+%s], %s' % (Immediate8(struct.unpack('<B', self.data[1:2])[0]),
                                                    Immediate8(struct.unpack('<B', self.data[2:3])[0]))
        elif self.modreg.mod == 2:
            if self.modreg.rm == 6:
                if self.modreg.reg == 7:
                    return 'cmp [bp+%d], %s' % (struct.unpack('<B', self.data[1:2])[0],
                                                Immediate16(struct.unpack('<H', self.data[2:4])[0]))

        elif self.modreg.mod == 3:
            if self.modreg.reg == 0:
                return 'add %s, %s' % (Register(self.modreg.rm, self.dst_word), self.imm)
            elif self.modreg.reg == 2:
                return 'adc %s, %s' % (Register(self.modreg.rm, self.dst_word), self.imm)
            elif self.modreg.reg == 4:
                return 'and %s, %s' % (Register(self.modreg.rm, self.dst_word), self.imm)
            elif self.modreg.reg == 5:
                return 'sub %s, %s' % (Register(self.modreg.rm, self.dst_word), self.imm)
            elif self.modreg.reg == 7:
                return 'cmp %s, %s' % (Register(self.modreg.rm, self.dst_word), self.imm)
        raise Exception('Unimplemented', self.modreg)

    def __len__(self):
        if self.modreg.mod == 0:
            if self.modreg.rm == 5:
                ret = 3
                if self.src_word:
                    return ret + 1
                else:
                    return ret
            elif self.modreg.rm == 6:
                ret = 4
                if self.src_word:
                    return ret + 2
                else:
                    return ret + 1
        elif self.modreg.mod == 1:
            if self.src_word:
                return 5
            else:
                return 4
        elif self.modreg.mod == 2:
            return 4
        elif self.modreg.mod == 3:
            if self.src_word:
                return 4
            else:
                return 3
        raise Exception('Unimplemented', self.modreg)


class LoadEffectiveAddressInstruction():
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, data[2:])

    def __str__(self):
        return 'lea %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class PushESInstruction():
    def __str__(self):
        return 'push es'

    def __len__(self):
        return 1


class PopESInstruction():
    def __str__(self):
        return 'pop es'

    def __len__(self):
        return 1


class PushCSInstruction():
    def __str__(self):
        return 'push cs'

    def __len__(self):
        return 1


class AdcInstruction():
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, data[2:])

    def __str__(self):
        return 'adc %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class PushSSInstruction():
    def __str__(self):
        return 'push ss'

    def __len__(self):
        return 1


class SBBInstruction():
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, data[2:])

    def __str__(self):
        return 'sbb %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class PushDSInstruction():
    def __str__(self):
        return 'push ds'

    def __len__(self):
        return 1


class PopDSInstruction():
    def __str__(self):
        return 'pop ds'

    def __len__(self):
        return 1


class AndInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, data[2:])

    def __str__(self):
        return 'and %s' % (self.modreg)

    def __len__(self):
        return len(self.modreg)


class MoveAlInstruction():
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov al, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveAhInstruction():
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov ah, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveBhInstruction():
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov bh, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveMem16AxInstruction():
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov %04Xh, ax' % self.immediate16

    def __len__(self):
        return 3


class MoveAlMem8Instruction():
    def __init__(self, data):
        self.immediate16 = Immediate16(struct.unpack('<H', data)[0])

    def __str__(self):
        return 'mov al, %s' % self.immediate16

    def __len__(self):
        return 3


class MoveAxMem16Instruction():
    def __init__(self, data):
        self.immediate16 = Immediate16(struct.unpack('<H', data)[0])
        self.segment = None

    def __str__(self):
        return 'mov ax, %s%s' % (self.get_segment(), self.immediate16)

    def get_segment(self):
        return '%s:' % self.segment if self.segment else ''

    def __len__(self):
        return 3


class MoveMem8AlInstruction():
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov %04Xh, al' % self.immediate8

    def __len__(self):
        return 3


class MoveCLInstruction():
    def __init__(self, data):
        self.immediate8 = Immediate8(struct.unpack('<B', data)[0])

    def __str__(self):
        return 'mov cl, %s' % self.immediate8

    def __len__(self):
        return 2


class MoveDLInstruction():
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov dl, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveBLInstruction():
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'mov bl, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class MoveAXInstruction():
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov ax, %xh' % self.immediate16

    def __len__(self):
        return 3


class MoveCXInstruction():
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov cx, %xh' % self.immediate16

    def __len__(self):
        return 3


class MoveDXInstruction():
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov dx, %xh' % self.immediate16

    def __len__(self):
        return 3


class MoveBXInstruction():
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov bx, %xh' % self.immediate16

    def __len__(self):
        return 3


class MoveDIInstruction():
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'mov di, %Xh' % self.immediate16

    def __len__(self):
        return 3


class MoveBPInstruction():
    def __init__(self, data):
        self.immediate16 = Immediate16(struct.unpack('<H', data)[0])

    def __str__(self):
        return 'mov bp, %s' % self.immediate16

    def __len__(self):
        return 3


class MoveSIInstruction():
    def __init__(self, data):
        self.immediate16 = Immediate16(struct.unpack('<H', data)[0])

    def __str__(self):
        return 'mov si, %s' % self.immediate16

    def __len__(self):
        return 3


class MoveSegRegInstruction():
    def __init__(self, data):
        self.data = data
        self.modsr = ModSr(data[1], data[0] & 0x02, word=True, extra=data[2:])

    def __str__(self):
        return 'mov %s' % self.modsr

    def __len__(self):
        return len(self.modsr)


class JbInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jb %02Xh' % self.offset

    def __len__(self):
        return 2


class JnbInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jnb %02Xh' % self.offset

    def __len__(self):
        return 2


class JzInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jz %02Xh' % self.offset

    def __len__(self):
        return 2


class JnzInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jnz %02Xh' % self.offset

    def __len__(self):
        return 2


class JbeInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jbe %02Xh' % self.offset

    def __len__(self):
        return 2


class JaInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'ja %02Xh' % self.offset

    def __len__(self):
        return 2


class JnsInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jns %02Xh' % self.offset

    def __len__(self):
        return 2


class JlInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jl %02Xh' % self.offset

    def __len__(self):
        return 2


class JgeInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jge %02Xh' % self.offset

    def __len__(self):
        return 2


class JleInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jle %02Xh' % self.offset

    def __len__(self):
        return 2


class JgInstruction():
    def __init__(self, data):
        self.offset = struct.unpack('B', data)[0]

    def __str__(self):
        return 'jg %02Xh' % self.offset

    def __len__(self):
        return 2


class ShiftInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01)

    def __str__(self):
        if self.modreg.direction == 0:
            if self.modreg.reg == 2:
                return 'rcl %s, 1' % Register(self.modreg.rm, self.modreg.word)
            elif self.modreg.reg == 4:
                return 'shl %s, 1' % Register(self.modreg.rm, self.modreg.word)
            elif self.modreg.reg == 5:
                return 'shr %s, 1' % Register(self.modreg.rm, self.modreg.word)
        elif self.modreg.direction == 2:
            if self.modreg.reg == 0:
                return 'rol %s, cl' % Register(self.modreg.rm, self.modreg.word)
            elif self.modreg.reg == 1:
                return 'ror %s, cl' % Register(self.modreg.rm, self.modreg.word)
            elif self.modreg.reg == 3:
                return 'rcr %s, cl' % Register(self.modreg.rm, self.modreg.word)
            elif self.modreg.reg == 4:
                return 'shl %s, cl' % Register(self.modreg.rm, self.modreg.word)
            elif self.modreg.reg == 5:
                return 'shr %s, cl' % Register(self.modreg.rm, self.modreg.word)
        raise Exception('Unimplemented shift instruction', self.modreg)

    def __len__(self):
        return 2


class ESSegmentOverride(object):
    def __init__(self, instruction):
        self.instruction = instruction
        self.instruction.segment = 'es'

    def __str__(self):
        return str(self.instruction)

    def __len__(self):
        return len(self.instruction) + 1


class CSSegmentOverride(object):
    def __init__(self, instruction):
        self.instruction = instruction
        self.instruction.segment = 'cs'

    def __str__(self):
        return str(self.instruction)

    def __len__(self):
        return len(self.instruction) + 1


class SSSegmentOverride(object):
    def __init__(self, instruction):
        self.instruction = instruction
        self.instruction.segment = 'ss'

    def __str__(self):
        return str(self.instruction)

    def __len__(self):
        return len(self.instruction) + 1


class NopInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'nop'

    def __len__(self):
        return 1


class CLCInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'clc'

    def __len__(self):
        return 1


class STCInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'stc'

    def __len__(self):
        return 1


class CLIInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'cli'

    def __len__(self):
        return 1


class STIInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'sti'

    def __len__(self):
        return 1


class CLDInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'cld'

    def __len__(self):
        return 1


class STDInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'std'

    def __len__(self):
        return 1


class LodsInstruction(object):
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


class StosInstruction(object):
    def __init__(self, word):
        self.word = word

    def __str__(self):
        if self.word:
            return 'stosw'
        else:
            return 'stosb'

    def __len__(self):
        return 1


class MovsInstruction(object):
    def __init__(self, word):
        self.word = word

    def __str__(self):
        if self.word:
            return 'movsw'
        else:
            return 'movsb'

    def __len__(self):
        return 1


class CmpsInstruction(object):
    def __init__(self, word):
        self.word = word

    def __str__(self):
        if self.word:
            return 'cmpsw'
        else:
            return 'cmpsb'

    def __len__(self):
        return 1


class InterruptInstruction(object):
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'int %02Xh' % (self.immediate8)

    def __len__(self):
        return 2


class LoopInstruction(object):
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'loop %02Xh' % (self.immediate8)

    def __len__(self):
        return 2


class JcxzInstruction(object):
    def __init__(self, data):
        self.immediate8 = Immediate8(struct.unpack('<B', data)[0])

    def __str__(self):
        return 'jcxz %s' % (self.immediate8)

    def __len__(self):
        return 2


class LesInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], 2, word=True, extra=data[2:])

    def __str__(self):
        return 'les %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class LdsInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], 2, word=True, extra=data[2:])

    def __str__(self):
        return 'lds %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class RepInstruction(object):
    def __init__(self, instruction):
        self.instruction = instruction

    def __str__(self):
        return 'rep %s' % self.instruction

    def __len__(self):
        return 1 + len(self.instruction)


class CmpInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, data[2:])

    def __str__(self):
        return 'cmp %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class CmpAlImm8Instruction(object):
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'cmp al, %02Xh' % self.immediate8

    def __len__(self):
        return 2


class CmpAxImm16Instruction(object):
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'cmp ax, %04Xh' % self.immediate16

    def __len__(self):
        return 3


class ReturnImm16Instruction(object):
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'ret %d' % (self.immediate16)

    def __len__(self):
        return 3


class ReturnInstruction(object):
    def __init__(self, data):
        pass

    def __str__(self):
        return 'ret'

    def __len__(self):
        return 1


class ReturnIntraInstruction(object):
    def __init__(self, data):
        pass

    def __str__(self):
        return 'ret'

    def __len__(self):
        return 1


class OrInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, data[2:])

    def __str__(self):
        return 'or %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class AndALImm8Instruction(object):
    def __init__(self, data):
        self.immediate8 = struct.unpack('<B', data)[0]

    def __str__(self):
        return 'and ax, %02Xh' % (self.immediate8)

    def __len__(self):
        return 2


class AndAXImm16Instruction(object):
    def __init__(self, data):
        self.immediate16 = struct.unpack('<H', data)[0]

    def __str__(self):
        return 'and ax, %04Xh' % (self.immediate16)

    def __len__(self):
        return 3


class IncAXInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'inc ax'

    def __len__(self):
        return 1


class IncCXInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'inc cx'

    def __len__(self):
        return 1


class IncDXInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'inc cx'

    def __len__(self):
        return 1


class IncBXInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'inc bx'

    def __len__(self):
        return 1


class IncSIInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'inc si'

    def __len__(self):
        return 1


class IncDIInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'inc di'

    def __len__(self):
        return 1


class DecAXInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'dec ax'

    def __len__(self):
        return 1


class DecDXInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'dec dx'

    def __len__(self):
        return 1


class DecBXInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'dec bx'

    def __len__(self):
        return 1


class DecBPInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'dec bp'

    def __len__(self):
        return 1


class DecSIInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'dec si'

    def __len__(self):
        return 1


class DecDIInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'dec di'

    def __len__(self):
        return 1


class XchgAxCxInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'xchg ax,cx'

    def __len__(self):
        return 1


class XchgAxDxInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'xchg ax,dx'

    def __len__(self):
        return 1


class CMCInstruction(object):
    def __init__(self):
        pass

    def __str__(self):
        return 'cmc'

    def __len__(self):
        return 1


class NotIstruction(object):
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'not %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class DivInstruction(object):
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'div %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class IdivInstruction(object):
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'idiv %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class MulInstruction(object):
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'mul %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class ImulInstruction(object):
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'imul %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


def Grp1Instruction(data):
    modreg = ModReg(data[1], 4, data[0] & 0x01, data[2:])

    if modreg.reg == 2:
        return NotIstruction(modreg)
    elif modreg.reg == 4:
        return MulInstruction(modreg)
    elif modreg.reg == 5:
        return ImulInstruction(modreg)
    elif modreg.reg == 6:
        return DivInstruction(modreg)
    elif modreg.reg == 7:
        return IdivInstruction(modreg)
    raise Exception('Unimplemented', modreg)


class PushMem16Instruction(object):
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'push %s' % self.modreg

    def __len__(self):
        return len(self.modreg)



class IncInstruction(object):
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'inc %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class DecInstruction(object):
    def __init__(self, modreg):
        self.modreg = modreg

    def __str__(self):
        return 'dec %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class Grp2CallNearInstruction(CallNearInstruction):
    def __len__(self):
        return 4


def Grp2Instruction(data):
    #todo return the correct type of instruction here
    modreg = ModReg(data[1], 4, data[0] & 0x01, data[2:])

    if modreg.reg == 0:
        return IncInstruction(modreg)
    elif modreg.reg == 1:
        return DecInstruction(modreg)
    elif modreg.reg == 3:
        return Grp2CallNearInstruction(modreg.extra)
    elif modreg.reg == 6:
        return PushMem16Instruction(modreg)
    raise Exception('Grp2Instruction', modreg)


class TestInstruction():
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, data[0] & 0x01, extra=data[2:])

    def __str__(self):
        return 'test %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class XchgInstruction(object):
    def __init__(self, data):
        self.data = data
        self.modreg = ModReg(data[1], data[0] & 0x02, word=False, extra=data[2:])

    def __str__(self):
        return 'xchg %s' % self.modreg

    def __len__(self):
        return len(self.modreg)


class Instruction(object):
    @staticmethod
    def decode(program, offset):
        code = program[offset]
        if 0x0 <= code <= 0x3:
            return AddInstruction(program[offset:offset+5])
        elif code == 0x4:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x5:
            return AddAxInstruction(program[offset+1:offset+3])
        elif code == 0x6:
            return PushESInstruction()
        elif code == 0x7:
            return PopESInstruction()
        elif 0x8 <= code <= 0xb:
            return OrInstruction(program[offset:offset+5])
        elif code == 0xc:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xe:
            return PushCSInstruction()
        elif code == 0xf:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x10:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x11:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x12:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x13:
            return AdcInstruction(program[offset:offset+4])
        elif code == 0x14:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x15:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x16:
            return PushSSInstruction()
        elif code == 0x17:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x18:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x19:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x1a:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x1b:
            return SBBInstruction(program[offset:offset+4])
        elif code == 0x1c:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x1d:
            raise Exception('Unimplemented op-code: %x' % code)
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
            raise Exception('Unimplemented op-code: %x' % code)
        elif 0x28 <= code == 0x2b:
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
            raise Exception('Unimplemented op-code: %x' % code)
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
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x45:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x46:
            return IncSIInstruction()
        elif code == 0x47:
            return IncDIInstruction()
        elif code == 0x48:
            return DecAXInstruction()
        elif code == 0x49:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x4a:
            return DecDXInstruction()
        elif code == 0x4b:
            return DecBXInstruction()
        elif code == 0x4c:
            raise Exception('Unimplemented op-code: %x' % code)
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
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x71:
            raise Exception('Unimplemented op-code: %x' % code)
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
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x79:
            return JnsInstruction(program[offset+1:offset+2])
        elif code == 0x7a:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x7b:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x7c:
            return JlInstruction(program[offset+1:offset+2])
        elif code == 0x7d:
            return JgeInstruction(program[offset+1:offset+2])
        elif code == 0x7e:
            return JleInstruction(program[offset+1:offset+2])
        elif code == 0x7f:
            return JgInstruction(program[offset+1:offset+2])
        elif 0x80 <= code <= 0x83:
            return IntermediateInstruction(program[offset+1:offset+5], code - 0x80)
        elif code == 0x84:
            return TestInstruction(program[offset:offset+5])
        elif code == 0x85:
            return TestInstruction(program[offset:offset+5])
        elif code == 0x86:
            raise Exception('Unimplemented op-code: %x' % code)
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
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x94:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x95:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x96:
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0x97:
            raise Exception('Unimplemented op-code: %x' % code)
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
            raise Exception('Unimplemented op-code: %x' % code)
        elif code == 0xb6:
            raise Exception('Unimplemented op-code: %x' % code)
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
            raise Exception('Unimplemented op-code: %x' % code)
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
            return ReturnIntraInstruction(program[offset:offset+3])
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
            return ReturnInstruction(program[offset+1:offset+3])
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
            raise Exception('Unimplemented op-code: %x' % code)
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
