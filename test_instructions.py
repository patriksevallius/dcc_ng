from nose.tools import istest, eq_

from instructions import Instruction


@istest
def add_03_2():
    instruction = Instruction.decode(b'\x03\xc2', 0)
    eq_(str(instruction), 'add ax, dx')
    eq_(len(instruction), 2)


@istest
def add_03_4():
    instruction = Instruction.decode(b'\x03\x06\x56\x43', 0)
    eq_(str(instruction), 'add ax, 4356h')
    eq_(len(instruction), 4)


@istest
def add_05():
    instruction = Instruction.decode(b'\x05\x13\x00', 0)
    eq_(str(instruction), 'add ax, 13h')
    eq_(len(instruction), 3)


@istest
def sub_2b():
    instruction = Instruction.decode(b'\x2b\xc8', 0)
    eq_(str(instruction), 'sub cx, ax')
    eq_(len(instruction), 2)


@istest
def sub_2d():
    instruction = Instruction.decode(b'\x2d\x00\x10', 0)
    eq_(str(instruction), 'sub ax, 1000h')
    eq_(len(instruction), 3)


@istest
def sub_2e():
    instruction = Instruction.decode(b'\x2e\xac', 0)
    eq_(str(instruction), 'lods byte ptr cs:[si]')
    eq_(len(instruction), 2)


@istest
def xor_33():
    instruction = Instruction.decode(b'\x33\xed', 0)
    eq_(str(instruction), 'xor bp, bp')
    eq_(len(instruction), 2)


@istest
def cmp_3b():
    instruction = Instruction.decode(b'\x3b\xda', 0)
    eq_(str(instruction), 'cmp bx, dx')
    eq_(len(instruction), 2)


@istest
def mov_80():
    instruction = Instruction.decode(b'\x80\x7e\xfe\x13', 0)
    eq_(str(instruction), 'mov [bp+254], 13h')
    eq_(len(instruction), 4)


@istest
def add_83_c7():
    instruction = Instruction.decode(b'\x83\xc7\x04', 0)
    eq_(str(instruction), 'add di, 4')
    eq_(len(instruction), 3)


@istest
def mov_89():
    instruction = Instruction.decode(b'\x89\x1d', 0)
    eq_(str(instruction), 'mov [di], bx')
    eq_(len(instruction), 2)


@istest
def mov_8b():
    instruction = Instruction.decode(b'\x8b\xc4', 0)
    eq_(str(instruction), 'mov ax, sp')
    eq_(len(instruction), 2)


@istest
def mov_8b_5d():
    instruction = Instruction.decode(b'\x8b\x5d\x08', 0)
    eq_(str(instruction), 'mov bx, [di+8]')
    eq_(len(instruction), 3)


@istest
def mov_8c_06():
    instruction = Instruction.decode(b'\x8c\x06\x84\x43', 0)
    eq_(str(instruction), 'mov 4384h, es')
    eq_(len(instruction), 4)


@istest
def mov_8c_45():
    instruction = Instruction.decode(b'\x8c\x45\x02', 0)
    eq_(str(instruction), 'mov word ptr [di+2], es')
    eq_(len(instruction), 3)


@istest
def mov_8e():
    instruction = Instruction.decode(b'\x8e\xda', 0)
    eq_(str(instruction), 'mov ds, dx')
    eq_(len(instruction), 2)


@istest
def nop_90():
    instruction = Instruction.decode(b'\x90', 0)
    eq_(str(instruction), 'nop')
    eq_(len(instruction), 1)


@istest
def call_9a():
    instruction = Instruction.decode(b'\x9a\x00\x00\xbb\x15', 0)
    eq_(str(instruction), 'call 15bb:0000')
    eq_(len(instruction), 5)


@istest
def mov_26_a1():
    instruction = Instruction.decode(b'\x26\xa1\x02\x00', 0)
    eq_(str(instruction), 'mov ax, es:2')
    eq_(len(instruction), 4)


@istest
def mov_a0():
    instruction = Instruction.decode(b'\xa0\xc9\x82', 0)
    eq_(str(instruction), 'mov al, 82C9h')
    eq_(len(instruction), 3)


@istest
def mov_a3():
    instruction = Instruction.decode(b'\xa3\x5c\x43', 0)
    eq_(str(instruction), 'mov 435Ch, ax')
    eq_(len(instruction), 3)


@istest
def mov_b1():
    instruction = Instruction.decode(b'\xb1\x04', 0)
    eq_(str(instruction), 'mov cl, 4')
    eq_(len(instruction), 2)


@istest
def mov_b4():
    instruction = Instruction.decode(b'\xb4\x35', 0)
    eq_(str(instruction), 'mov ah, 35h')
    eq_(len(instruction), 2)


@istest
def mov_b9():
    instruction = Instruction.decode(b'\xb9\x12\x00', 0)
    eq_(str(instruction), 'mov cx, 12h')
    eq_(len(instruction), 3)


@istest
def mov_ba():
    instruction = Instruction.decode(b'\xba\x40\x17', 0)
    eq_(str(instruction), 'mov dx, 1740h')
    eq_(len(instruction), 3)


@istest
def mov_be():
    instruction = Instruction.decode(b'\xbe\xdd\x01', 0)
    eq_(str(instruction), 'mov si, 01DDh')
    eq_(len(instruction), 3)


@istest
def mov_bf():
    instruction = Instruction.decode(b'\xbf\xd0\x84', 0)
    eq_(str(instruction), 'mov di, 84D0h')
    eq_(len(instruction), 3)


@istest
def les_c4():
    instruction = Instruction.decode(b'\xc4\x7d\x0c', 0)
    eq_(str(instruction), 'les di, [di+0Ch]')
    eq_(len(instruction), 3)


@istest
def int_cd():
    instruction = Instruction.decode(b'\xcd\x21', 0)
    eq_(str(instruction), 'int 21h')
    eq_(len(instruction), 2)


@istest
def shr_d3():
    instruction = Instruction.decode(b'\xd3\xe8', 0)
    eq_(str(instruction), 'shr ax, cl')
    eq_(len(instruction), 2)


@istest
def loop_e2():
    instruction = Instruction.decode(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe2\xf0', 16)
    eq_(str(instruction), 'loop 0') # loop 16 steps back
    eq_(len(instruction), 2)


@istest
def jcxz_e3():
    instruction = Instruction.decode(b'\xe3\x07', 0)
    eq_(str(instruction), 'jcxz 7')
    eq_(len(instruction), 2)


@istest
def call_e8_negative():
    instruction = Instruction.decode(b'\xe8\x9f\xf8', 0)
    eq_(str(instruction), 'call 0761h')
    eq_(len(instruction), 3)


@istest
def cld_fc():
    instruction = Instruction.decode(b'\xfc', 0)
    eq_(str(instruction), 'cld')
    eq_(len(instruction), 1)


@istest
def push_ff():
    instruction = Instruction.decode(b'\xff\x36\x26\x26', 0)
    eq_(str(instruction), 'push 2626h')
    eq_(len(instruction), 4)
