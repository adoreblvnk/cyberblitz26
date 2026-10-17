An Orchid operator appears twice in a signed share registry. Keep the public handouts from Same Kopi, Different Cup and The Rain Has a Public Key to recover the token.

Orchid share protocol

    Each operator has an independent degree-one polynomial f(slot) = secret + slope*slot mod p, where p is modulus.
    The registry assigns each raw UTF-8 identity a new slot. The gateway authenticates operators by their Unicode-normalized (canonical) identity, so only shares with the same canonical identity belong to the same polynomial.
    The share-wrap key is the 32 raw bytes of the receipt key from The Rain Has a Public Key: SHA256(ASCII(decimal(signing x)) || first 16 raw keystream bytes from the Same Kopi, Different Cup known receipt).digest().
    For each record, message bytes = ASCII('ORCHID-SHARE-V2') || 0x00 || UTF-8(canonical identity). HMAC-SHA256(key=share-wrap key, message=message bytes) produces a raw digest. Interpret it as a big-endian integer, reduce mod p, and integer-XOR that mask with masked_share to recover the share.
    For the target secret, SHA256(ASCII('ORCHID-CHECK-V2') || 0x00 || secret.to_bytes(16, 'big')).hexdigest() equals secret_commitment.
    The sealed token is base64 of the UTF-8 flag bytes repeating-XORed with SHA256(secret.to_bytes(16, 'big')).digest().
