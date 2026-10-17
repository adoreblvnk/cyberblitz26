#!/usr/bin/env python3
"""Local-only instrumentation patch for karaoke: print hash_state at the
setlist check so we can measure it without gdb (ptrace is unavailable)."""
import struct, sys

SRC = "karaoke"
OUT = "/tmp/karaoke_dbg"

data = bytearray(open(SRC, "rb").read())


def off(vaddr):
    return vaddr - 0x401000 + 0x1000


PRINTF_PLT = 0x401070

# 1) reuse the success format string slot as a plain "%u\n"
o = off(0x40323D)
data[o:o + 19] = b"%u\n" + b"\x00" * 16

# 2) 0x401d06 .. 0x401d19  (20 bytes) -> printf(hash_state)
#    0x401d00 already did: movl 0x405088,%eax   (eax = hash_state)
ins = bytearray()
ins += b"\xbf" + struct.pack("<I", 0x40323D)   # mov $fmt,%edi
ins += b"\x89\xc6"                              # mov %eax,%esi
ins += b"\x31\xc0"                              # xor %eax,%eax
call_at = 0x401D06 + len(ins)                   # rel32 is relative to next insn
ins += b"\xe8" + struct.pack("<i", PRINTF_PLT - (call_at + 5))
ins += b"\x90" * (20 - len(ins))
assert len(ins) == 20, len(ins)
o = off(0x401D06)
print("patch at file off 0x%x  vaddr 0x401d06" % o)
data[o:o + 20] = ins

open(OUT, "wb").write(bytes(data))
print("wrote", OUT)