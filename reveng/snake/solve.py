"""solve snake.pyc - lazy obfuscator with junk branches + swap + xor + RC4"""
import base64
import marshal
from pathlib import Path

pyc = Path(__file__).with_name("snake.pyc").read_bytes()
code = marshal.loads(pyc[16:])
s = code.co_consts[2]  # swapped base64
q = code.co_consts[3]  # hex key "da39a3ee..."

def unswap(x: str) -> str:
    l = list(x)
    for i in range(0, len(l) - 1, 2):
        l[i], l[i + 1] = l[i + 1], l[i]
    return "".join(l)

d = base64.b64decode(unswap(s).encode())
key = bytes.fromhex(q)
stage1 = bytes(b ^ key[i % len(key)] for i, b in enumerate(d))
print(stage1.decode())

# stage1 is RC4 with key b"opcodeopcodeopco", ct hex 6b71030a...
def rc4(key: bytes, data: bytes) -> bytes:
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(byte ^ S[(S[i] + S[j]) % 256])
    return bytes(out)

k = b"opcodeopcodeopco"
ct = bytes.fromhex("6b71030aee4b9241454b681386778f3a615b660d0d2f47f4")
flag = rc4(k, ct)
print(flag.decode())
assert rc4(k, flag).hex() == "6b71030aee4b9241454b681386778f3a615b660d0d2f47f4"
