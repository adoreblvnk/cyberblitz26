#!/usr/bin/env python3
import hashlib

# NIST P-256 (secp256r1) curve order
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

def solve():
    # Read parameters from distrib.txt
    with open("distrib.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    data = {}
    for line in lines:
        k, v = line.split(" = ", 1)
        data[k] = v

    m1 = data["m1"].encode()
    r1 = int(data["r1"])
    s1 = int(data["s1"])
    m2 = data["m2"].encode()
    r2 = int(data["r2"])
    s2 = int(data["s2"])
    ciphertext = bytes.fromhex(data["ciphertext"])

    h1 = int(hashlib.sha256(m1).hexdigest(), 16)
    h2 = int(hashlib.sha256(m2).hexdigest(), 16)

    # In ECDSA:
    # s1 * k1 = h1 + r1 * d (mod n)
    # s2 * k2 = h2 + r2 * d (mod n)
    # With nonces off-by-one: k2 = k1 + 1
    # r2 * (s1 * k1 - h1) == r1 * (s2 * (k1 + 1) - h2) (mod n)
    # (r2 * s1 - r1 * s2) * k1 == r2 * h1 - r1 * h2 + r1 * s2 (mod n)
    coeff_k1 = (r2 * s1 - r1 * s2) % n
    rhs = (r2 * h1 - r1 * h2 + r1 * s2) % n
    k1 = (rhs * pow(coeff_k1, -1, n)) % n
    k2 = (k1 + 1) % n

    # Recover private key d
    d = ((s1 * k1 - h1) * pow(r1, -1, n)) % n
    d_check = ((s2 * k2 - h2) * pow(r2, -1, n)) % n
    assert d == d_check, "Private key recovery mismatch"

    # Flag is obtained by XORing ciphertext with retrieved key (32 bytes big-endian)
    key_bytes = d.to_bytes(32, "big")
    flag = bytes([c ^ k for c, k in zip(ciphertext, key_bytes)]).decode()
    
    print(f"Private key: {hex(d)}")
    print(f"Flag: {flag}")
    return flag

if __name__ == "__main__":
    solve()
