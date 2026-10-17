#!/usr/bin/env python3
"""
Solution for crypto/same-kopi-different-cup

Vulnerability:
The kopitiam terminal reuses the same keystream / XOR key across all receipt encryptions (Many-Time Pad / OTP key reuse).
Given a known plaintext and its ciphertext:
    keystream = known_plaintext ^ known_ciphertext
We can recover any other receipt plaintext by XORing its ciphertext with the recovered keystream:
    midnight_plaintext = midnight_ciphertext ^ keystream
"""

def solve():
    with open("known_order.txt", "rb") as f:
        known_order = f.read().strip()

    receipts = {}
    with open("receipts.txt", "r") as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue
            name, hex_ct = line.split("=", 1)
            receipts[name] = bytes.fromhex(hex_ct)

    known_ct = receipts["known"]

    # Recover keystream from known plaintext and known ciphertext
    keystream = bytes([p ^ c for p, c in zip(known_order, known_ct)])

    # Decrypt all orders
    for name, ct in receipts.items():
        pt = bytes([c ^ k for c, k in zip(ct, keystream)])
        print(f"[{name}] {pt}")

    midnight_pt = bytes([c ^ k for c, k in zip(receipts["midnight"], keystream)]).decode("latin-1")
    print(f"\nFlag: {midnight_pt}")
    return midnight_pt

if __name__ == "__main__":
    solve()
